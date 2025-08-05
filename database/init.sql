-- Create database (if needed)
-- CREATE DATABASE TraceLens;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT TRUE,
    verification_token VARCHAR(36)
);

-- Analysis table
CREATE TABLE IF NOT EXISTS analysis (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    target_email VARCHAR(120) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_expires_at ON analysis(expires_at);
CREATE INDEX IF NOT EXISTS idx_analysis_target_email ON analysis(target_email);

-- Create a cleanup function for expired analyses
CREATE OR REPLACE FUNCTION cleanup_expired_analyses()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM analysis WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
