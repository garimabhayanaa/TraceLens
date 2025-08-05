import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import ThreadedConnectionPool
import json
from contextlib import contextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CleanupStats:
    analyses_deleted: int
    sessions_deleted: int
    analyses_expired: int
    maintenance_completed_at: datetime

class DatabaseManager:
    """
    PostgreSQL database manager with automatic TTL cleanup and connection pooling
    """
    
    def __init__(self, database_url: str, min_connections: int = 5, max_connections: int = 20):
        self.database_url = database_url
        self.connection_pool = None
        self.initialize_connection_pool(min_connections, max_connections)
        
    def initialize_connection_pool(self, min_conn: int = 5, max_conn: int = 20):
        """Initialize PostgreSQL connection pool"""
        try:
            self.connection_pool = ThreadedConnectionPool(
                min_conn, max_conn,
                self.database_url,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized ({min_conn}-{max_conn} connections)")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    def store_temporary_analysis(self, user_id: str, target_email: str, 
                                analysis_results: Dict[str, Any]) -> str:
        """
        Store analysis results with automatic 24-hour TTL
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Extract key metrics for indexed columns
                    privacy_score = analysis_results.get('privacy_score', 5.0)
                    privacy_grade = analysis_results.get('privacy_grade', 'C')
                    critical_risks = analysis_results.get('critical_risks', [])
                    confidence_scores = analysis_results.get('confidence_levels', {})
                    
                    # Insert with automatic TTL
                    cursor.execute("""
                        INSERT INTO temporary_analyses 
                        (user_id, target_email, analysis_results, privacy_score, 
                         privacy_grade, critical_risks, confidence_scores)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, expires_at
                    """, (
                        user_id, target_email, Json(analysis_results),
                        privacy_score, privacy_grade, critical_risks, Json(confidence_scores)
                    ))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    logger.info(f"Analysis stored with ID: {result['id']}, expires: {result['expires_at']}")
                    return result['id']
                    
        except Exception as e:
            logger.error(f"Failed to store analysis: {str(e)}")
            raise
    
    def get_temporary_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis results if not expired
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            id, user_id, target_email, analysis_results,
                            privacy_score, privacy_grade, critical_risks,
                            created_at, expires_at, 
                            (expires_at > NOW()) as is_active,
                            EXTRACT(EPOCH FROM (expires_at - NOW())) as seconds_remaining
                        FROM temporary_analyses 
                        WHERE id = %s AND user_id = %s
                    """, (analysis_id, user_id))
                    
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
                    
                    if not result['is_active']:
                        logger.warning(f"Analysis {analysis_id} has expired")
                        return None
                    
                    # Update access tracking
                    cursor.execute("""
                        UPDATE temporary_analyses 
                        SET accessed_at = NOW(), access_count = access_count + 1
                        WHERE id = %s
                    """, (analysis_id,))
                    
                    conn.commit()
                    
                    return dict(result)
                    
        except Exception as e:
            logger.error(f"Failed to retrieve analysis: {str(e)}")
            raise
    
    def get_user_analyses(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get user's recent analyses (non-expired only)
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            id, target_email, privacy_score, privacy_grade,
                            created_at, expires_at,
                            EXTRACT(EPOCH FROM (expires_at - NOW())) as seconds_remaining
                        FROM temporary_analyses 
                        WHERE user_id = %s AND expires_at > NOW() AND status = 'completed'
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (user_id, limit))
                    
                    return [dict(row) for row in cursor.fetchall()]
                    
        except Exception as e:
            logger.error(f"Failed to retrieve user analyses: {str(e)}")
            raise
    
    def cleanup_expired_data(self) -> CleanupStats:
        """
        Perform comprehensive cleanup of expired data
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Call the comprehensive cleanup function
                    cursor.execute("SELECT * FROM perform_maintenance_cleanup()")
                    result = cursor.fetchone()
                    conn.commit()
                    
                    stats = CleanupStats(
                        analyses_deleted=result['analyses_deleted'] or 0,
                        sessions_deleted=result['sessions_deleted'] or 0,
                        analyses_expired=result['analyses_expired'] or 0,
                        maintenance_completed_at=result['maintenance_completed_at']
                    )
                    
                    logger.info(f"Cleanup completed: {stats.analyses_deleted} analyses deleted, "
                              f"{stats.sessions_deleted} sessions deleted, "
                              f"{stats.analyses_expired} analyses expired")
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics for monitoring
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get table sizes and counts
                    cursor.execute("""
                        SELECT 
                            (SELECT COUNT(*) FROM temporary_analyses WHERE expires_at > NOW()) as active_analyses,
                            (SELECT COUNT(*) FROM temporary_analyses WHERE expires_at <= NOW()) as expired_analyses,
                            (SELECT COUNT(*) FROM users) as total_users,
                            (SELECT COUNT(*) FROM user_sessions WHERE expires_at > NOW()) as active_sessions,
                            (SELECT AVG(privacy_score) FROM temporary_analyses WHERE expires_at > NOW()) as avg_privacy_score
                    """)
                    
                    result = cursor.fetchone()
                    
                    return {
                        'active_analyses': result['active_analyses'] or 0,
                        'expired_analyses': result['expired_analyses'] or 0,
                        'total_users': result['total_users'] or 0,
                        'active_sessions': result['active_sessions'] or 0,
                        'average_privacy_score': float(result['avg_privacy_score'] or 0),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            raise
    
    def store_user_session(self, user_id: str, session_token: str, 
                          ip_address: str, user_agent: str, expires_at: datetime) -> str:
        """
        Store user session with automatic cleanup
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO user_sessions 
                        (user_id, session_token, ip_address, user_agent, expires_at)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, session_token, ip_address, user_agent, expires_at))
                    
                    result = cursor.fetchone()
                    conn.commit()
                    
                    return result['id']
                    
        except Exception as e:
            logger.error(f"Failed to store session: {str(e)}")
            raise
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Validate session token and return user info if valid
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT s.user_id, s.expires_at, u.email, u.name, u.is_active
                        FROM user_sessions s
                        JOIN users u ON s.user_id = u.id
                        WHERE s.session_token = %s 
                        AND s.expires_at > NOW() 
                        AND s.is_active = TRUE 
                        AND u.is_active = TRUE
                    """, (session_token,))
                    
                    result = cursor.fetchone()
                    
                    if result:
                        # Update last accessed time
                        cursor.execute("""
                            UPDATE user_sessions 
                            SET last_accessed_at = NOW()
                            WHERE session_token = %s
                        """, (session_token,))
                        conn.commit()
                        
                        return dict(result)
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            raise
    
    def invalidate_session(self, session_token: str) -> bool:
        """
        Invalidate a user session
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE user_sessions 
                        SET is_active = FALSE 
                        WHERE session_token = %s
                    """, (session_token,))
                    
                    success = cursor.rowcount > 0
                    conn.commit()
                    
                    return success
                    
        except Exception as e:
            logger.error(f"Failed to invalidate session: {str(e)}")
            raise
    
    def close_connection_pool(self):
        """Close all database connections"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")

def create_database_manager():
    """Factory function to create database manager"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/leakpeek')
    return DatabaseManager(database_url)
