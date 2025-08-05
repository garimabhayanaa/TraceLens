-- =============================================================================
-- LeakPeek Database Schema for PostgreSQL
-- Features: ACID compliance, temporary storage with 24-hour TTL, efficient indexing
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- USERS TABLE
-- Permanent storage for user accounts
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token UUID,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT users_email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_name_not_empty CHECK (LENGTH(TRIM(name)) > 0)
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);
CREATE INDEX IF NOT EXISTS idx_users_verified ON users (verified) WHERE verified = FALSE;
CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users (locked_until) WHERE locked_until IS NOT NULL;

-- =============================================================================
-- TEMPORARY ANALYSIS STORAGE
-- Short-term storage with automatic 24-hour TTL cleanup
-- =============================================================================

CREATE TABLE IF NOT EXISTS temporary_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_email VARCHAR(254) NOT NULL,
    
    -- Analysis data stored as JSONB for flexibility and indexing
    analysis_results JSONB NOT NULL,
    
    -- Privacy and security metadata
    privacy_score DECIMAL(3,2) CHECK (privacy_score >= 1.0 AND privacy_score <= 10.0),
    privacy_grade VARCHAR(2),
    critical_risks TEXT[],
    
    -- Data collection metadata
    collection_metadata JSONB DEFAULT '{}',
    confidence_scores JSONB DEFAULT '{}',
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    
    -- TTL and audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    accessed_at TIMESTAMPTZ,
    access_count INTEGER NOT NULL DEFAULT 0,
    
    -- Security constraints
    CONSTRAINT temp_analyses_status_valid CHECK (status IN ('processing', 'completed', 'failed', 'expired')),
    CONSTRAINT temp_analyses_target_email_valid CHECK (target_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT temp_analyses_expires_future CHECK (expires_at > created_at)
);

-- Indexes for temporary analyses (optimized for TTL cleanup and queries)
CREATE INDEX IF NOT EXISTS idx_temp_analyses_user_id ON temporary_analyses (user_id);
CREATE INDEX IF NOT EXISTS idx_temp_analyses_target_email ON temporary_analyses (target_email);
CREATE INDEX IF NOT EXISTS idx_temp_analyses_expires_at ON temporary_analyses (expires_at);
CREATE INDEX IF NOT EXISTS idx_temp_analyses_created_at ON temporary_analyses (created_at);
CREATE INDEX IF NOT EXISTS idx_temp_analyses_status ON temporary_analyses (status);

-- Partial index for active analyses only
CREATE INDEX IF NOT EXISTS idx_temp_analyses_active ON temporary_analyses (user_id, created_at) 
WHERE status = 'completed' AND expires_at > NOW();

-- GIN index for JSONB analysis results (for efficient JSON queries)
CREATE INDEX IF NOT EXISTS idx_temp_analyses_results_gin ON temporary_analyses USING GIN (analysis_results);

-- =============================================================================
-- USER SESSIONS
-- Temporary session storage with automatic cleanup
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(64) UNIQUE NOT NULL,
    ip_address INET NOT NULL,
    user_agent TEXT,
    device_fingerprint VARCHAR(64),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    CONSTRAINT sessions_expires_future CHECK (expires_at > created_at)
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions (user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions (session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions (user_id, is_active) WHERE is_active = TRUE;

-- =============================================================================
-- AUDIT LOG
-- Permanent audit trail for security and compliance
-- =============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    CONSTRAINT audit_action_not_empty CHECK (LENGTH(TRIM(action)) > 0)
);

-- Indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs (resource_type, resource_id);

-- =============================================================================
-- CLEANUP FUNCTIONS FOR TTL IMPLEMENTATION
-- =============================================================================

-- Function to clean up expired temporary analyses
CREATE OR REPLACE FUNCTION cleanup_expired_analyses()
RETURNS TABLE(deleted_count BIGINT, oldest_deleted TIMESTAMPTZ, newest_deleted TIMESTAMPTZ) AS $$
DECLARE
    deleted_records RECORD;
BEGIN
    -- Delete expired analyses and capture statistics
    WITH deleted AS (
        DELETE FROM temporary_analyses 
        WHERE expires_at <= NOW() OR status = 'expired'
        RETURNING created_at
    ),
    stats AS (
        SELECT 
            COUNT(*) as count,
            MIN(created_at) as oldest,
            MAX(created_at) as newest
        FROM deleted
    )
    SELECT stats.count, stats.oldest, stats.newest INTO deleted_count, oldest_deleted, newest_deleted
    FROM stats;
    
    -- Log cleanup action
    INSERT INTO audit_logs (action, details) 
    VALUES ('cleanup_expired_analyses', jsonb_build_object(
        'deleted_count', deleted_count,
        'oldest_deleted', oldest_deleted,
        'newest_deleted', newest_deleted
    ));
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    deleted_sessions BIGINT;
BEGIN
    WITH deleted AS (
        DELETE FROM user_sessions 
        WHERE expires_at <= NOW() OR is_active = FALSE
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    -- Log cleanup action
    INSERT INTO audit_logs (action, details) 
    VALUES ('cleanup_expired_sessions', jsonb_build_object('deleted_count', deleted_count));
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function to mark analyses as expired (soft delete)
CREATE OR REPLACE FUNCTION mark_expired_analyses() 
RETURNS TABLE(updated_count BIGINT) AS $$
BEGIN
    WITH updated AS (
        UPDATE temporary_analyses 
        SET status = 'expired', updated_at = NOW()
        WHERE expires_at <= NOW() AND status != 'expired'
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Comprehensive cleanup function
CREATE OR REPLACE FUNCTION perform_maintenance_cleanup()
RETURNS TABLE(
    analyses_deleted BIGINT,
    sessions_deleted BIGINT, 
    analyses_expired BIGINT,
    maintenance_completed_at TIMESTAMPTZ
) AS $$
DECLARE
    analyses_count BIGINT;
    sessions_count BIGINT;
    expired_count BIGINT;
BEGIN
    -- Clean up expired analyses
    SELECT deleted_count INTO analyses_count FROM cleanup_expired_analyses();
    
    -- Clean up expired sessions  
    SELECT deleted_count INTO sessions_count FROM cleanup_expired_sessions();
    
    -- Mark expired analyses
    SELECT updated_count INTO expired_count FROM mark_expired_analyses();
    
    -- Return results
    analyses_deleted := analyses_count;
    sessions_deleted := sessions_count;
    analyses_expired := expired_count;
    maintenance_completed_at := NOW();
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC MAINTENANCE
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at for users
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically clean up on insert (lightweight cleanup)
CREATE OR REPLACE FUNCTION auto_cleanup_on_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- Perform lightweight cleanup (delete a few expired records)
    DELETE FROM temporary_analyses 
    WHERE expires_at <= NOW() - INTERVAL '1 hour'
    LIMIT 10;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic cleanup on new analysis insert
CREATE TRIGGER trigger_auto_cleanup
    AFTER INSERT ON temporary_analyses
    FOR EACH STATEMENT
    EXECUTE FUNCTION auto_cleanup_on_insert();

-- =============================================================================
-- SECURITY FUNCTIONS
-- =============================================================================

-- Function to get user analysis history (with privacy protection)
CREATE OR REPLACE FUNCTION get_user_analysis_summary(p_user_id UUID)
RETURNS TABLE(
    total_analyses BIGINT,
    analyses_last_7_days BIGINT,
    analyses_last_30_days BIGINT,
    average_privacy_score DECIMAL(3,2),
    last_analysis_date TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_analyses,
        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days')::BIGINT as analyses_last_7_days,
        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days')::BIGINT as analyses_last_30_days,
        AVG(privacy_score) as average_privacy_score,
        MAX(created_at) as last_analysis_date
    FROM temporary_analyses 
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- VIEWS FOR EASY ACCESS
-- =============================================================================

-- View for active analyses
CREATE OR REPLACE VIEW active_analyses AS
SELECT 
    id,
    user_id,
    target_email,
    privacy_score,
    privacy_grade,
    status,
    created_at,
    expires_at,
    (expires_at - NOW()) as time_remaining
FROM temporary_analyses 
WHERE expires_at > NOW() AND status = 'completed';

-- View for analysis statistics
CREATE OR REPLACE VIEW analysis_statistics AS
SELECT 
    DATE(created_at) as analysis_date,
    COUNT(*) as total_analyses,
    AVG(privacy_score) as avg_privacy_score,
    COUNT(*) FILTER (WHERE privacy_score < 5) as high_risk_count,
    COUNT(*) FILTER (WHERE privacy_score >= 8) as low_risk_count
FROM temporary_analyses 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY analysis_date DESC;

-- =============================================================================
-- INITIAL DATA AND CONFIGURATION
-- =============================================================================

-- Create a function to initialize database configuration
CREATE OR REPLACE FUNCTION initialize_database_config()
RETURNS VOID AS $$
BEGIN
    -- Set timezone to UTC for consistency
    SET timezone = 'UTC';
    
    -- Insert initial audit log
    INSERT INTO audit_logs (action, details) 
    VALUES ('database_initialized', jsonb_build_object(
        'version', '1.0',
        'initialized_at', NOW(),
        'features', ARRAY['ttl_cleanup', 'audit_logging', 'security_functions']
    ));
    
    -- Log successful initialization
    RAISE NOTICE 'Database initialized successfully with TTL cleanup and security features';
END;
$$ LANGUAGE plpgsql;

-- Run initialization
SELECT initialize_database_config();

-- =============================================================================
-- PERFORMANCE OPTIMIZATION
-- =============================================================================

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE temporary_analyses;
ANALYZE user_sessions;
ANALYZE audit_logs;

-- =============================================================================
-- GRANTS AND PERMISSIONS (adjust as needed for your application user)
-- =============================================================================

-- Example grants for application user (replace 'leakpeek_app' with your actual user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON users TO leakpeek_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON temporary_analyses TO leakpeek_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON user_sessions TO leakpeek_app;
-- GRANT SELECT, INSERT ON audit_logs TO leakpeek_app;
-- GRANT EXECUTE ON FUNCTION cleanup_expired_analyses() TO leakpeek_app;
-- GRANT EXECUTE ON FUNCTION cleanup_expired_sessions() TO leakpeek_app;
-- GRANT EXECUTE ON FUNCTION perform_maintenance_cleanup() TO leakpeek_app;

-- =============================================================================
-- CONSENT LOGS TABLE
-- GDPR-compliant consent tracking with full audit trail
-- =============================================================================

CREATE TABLE IF NOT EXISTS consent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consent_id UUID UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Core consent data
    consent_status VARCHAR(20) NOT NULL CHECK (consent_status IN ('granted', 'denied', 'partial', 'withdrawn', 'expired')),
    consent_types TEXT[] NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

     -- Technical metadata (anonymized)
    ip_address INET NOT NULL,
    user_agent TEXT,
    session_id UUID,

    -- GDPR compliance fields
    consent_method VARCHAR(50) NOT NULL,
    consent_version VARCHAR(20) NOT NULL,
    legal_basis VARCHAR(50) NOT NULL DEFAULT 'consent',
    purpose_description TEXT NOT NULL,
    data_categories TEXT[] NOT NULL,

    -- Additional compliance data
    consent_duration INTEGER, -- Duration in days
    withdrawal_method VARCHAR(50),
    consent_language VARCHAR(5) DEFAULT 'en',
    geolocation VARCHAR(10),

     -- URLs and referrer info
    page_url TEXT,
    referrer_url TEXT,
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,

    -- Constraints
    CONSTRAINT consent_logs_status_valid CHECK (consent_status IN ('granted', 'denied', 'partial', 'withdrawn', 'expired')),
    CONSTRAINT consent_logs_types_not_empty CHECK (array_length(consent_types, 1) > 0),
    CONSTRAINT consent_logs_categories_not_empty CHECK (array_length(data_categories, 1) > 0)
);

-- Indexes for consent logs
CREATE INDEX IF NOT EXISTS idx_consent_logs_user_id ON consent_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_consent_logs_consent_id ON consent_logs (consent_id);
CREATE INDEX IF NOT EXISTS idx_consent_logs_timestamp ON consent_logs (timestamp);
CREATE INDEX IF NOT EXISTS idx_consent_logs_status ON consent_logs (consent_status);
CREATE INDEX IF NOT EXISTS idx_consent_logs_expires_at ON consent_logs (expires_at) WHERE expires_at IS NOT NULL;

-- GIN index for consent types and data categories arrays
CREATE INDEX IF NOT EXISTS idx_consent_logs_types_gin ON consent_logs USING GIN (consent_types);
CREATE INDEX IF NOT EXISTS idx_consent_logs_categories_gin ON consent_logs USING GIN (data_categories);

-- Function to cleanup expired consent logs
CREATE OR REPLACE FUNCTION cleanup_expired_consent_logs()
RETURNS TABLE(updated_count BIGINT) AS $$
BEGIN
    WITH updated AS (
        UPDATE consent_logs 
        SET 
            consent_status = 'expired',
            updated_at = NOW()
        WHERE expires_at <= NOW() 
        AND consent_status != 'expired'
        RETURNING id
    )
    SELECT COUNT(*) INTO updated_count FROM updated;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

