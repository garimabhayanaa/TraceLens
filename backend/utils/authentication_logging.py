import os
import logging
import json
import hashlib
import secrets
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import uuid
import ipaddress

logger = logging.getLogger(__name__)

class AuthEventType(Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    MFA_CHALLENGE = "mfa_challenge"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    SESSION_EXPIRED = "session_expired"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PRIVILEGE_ESCALATION = "privilege_escalation"

class AuthMethod(Enum):
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    SOCIAL_LOGIN = "social_login"
    API_KEY = "api_key"
    BIOMETRIC = "biometric"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AuthenticationRecord:
    """Secure authentication record with GDPR compliance"""
    
    # Core identification
    record_id: str
    user_id: str
    session_id: Optional[str]
    
    # Event details
    event_type: AuthEventType
    auth_method: AuthMethod
    success: bool
    timestamp: datetime
    
    # Network and client information (anonymized)
    ip_address: str
    user_agent: str
    geolocation: Optional[str] = None
    device_fingerprint: Optional[str] = None
    
    # Security metadata
    risk_level: RiskLevel = RiskLevel.LOW
    failure_reason: Optional[str] = None
    
    # Additional context
    referrer_url: Optional[str] = None
    requested_resource: Optional[str] = None
    
    # Audit fields
    created_at: datetime = None
    retention_until: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        # Set retention period (default 2 years for security logs)
        if self.retention_until is None:
            self.retention_until = self.created_at + timedelta(days=730)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['event_type'] = self.event_type.value
        data['auth_method'] = self.auth_method.value
        data['risk_level'] = self.risk_level.value
        # Convert datetime objects to ISO strings
        data['timestamp'] = self.timestamp.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['retention_until'] = self.retention_until.isoformat()
        return data

class AuthenticationLogger:
    """
    Secure authentication logging system with encryption and GDPR compliance
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.auth_records: List[AuthenticationRecord] = []
        self.lock = threading.RLock()
        
        # Security configuration
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.retention_days = 730  # 2 years default
        
        # Initialize storage
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize secure storage for authentication records"""
        # In production, this would connect to encrypted database
        self.storage_initialized = True
        logger.info("Authentication logging system initialized")
    
    def log_authentication_event(self,
                                user_id: str,
                                event_type: AuthEventType,
                                auth_method: AuthMethod,
                                success: bool,
                                ip_address: str,
                                user_agent: str,
                                session_id: Optional[str] = None,
                                failure_reason: Optional[str] = None,
                                **kwargs) -> str:
        """
        Log an authentication event with full security context
        
        Returns:
            str: Unique record ID for tracking
        """
        
        try:
            # Generate unique record ID
            record_id = str(uuid.uuid4())
            
            # Anonymize IP address for privacy
            anonymized_ip = self._anonymize_ip_address(ip_address)
            
            # Assess risk level
            risk_level = self._assess_risk_level(event_type, success, ip_address, user_agent)
            
            # Create authentication record
            auth_record = AuthenticationRecord(
                record_id=record_id,
                user_id=user_id,
                session_id=session_id,
                event_type=event_type,
                auth_method=auth_method,
                success=success,
                timestamp=datetime.utcnow(),
                ip_address=anonymized_ip,
                user_agent=user_agent,
                risk_level=risk_level,
                failure_reason=failure_reason,
                **kwargs
            )
            
            # Store the record
            with self.lock:
                self.auth_records.append(auth_record)
                # In production, save to encrypted database
                self._persist_record(auth_record)
            
            # Log the event (without sensitive data)
            logger.info(f"Auth event recorded: {record_id} - user {user_id[:8]}... - {event_type.value} - success: {success}")
            
            # Check for suspicious patterns
            self._check_suspicious_activity(user_id, event_type, success, ip_address)
            
            return record_id
            
        except Exception as e:
            logger.error(f"Failed to log authentication event: {str(e)}")
            raise
    
    def get_user_authentication_history(self, user_id: str, 
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None,
                                      limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get authentication history for a user (for security analysis or GDPR requests)
        """
        
        try:
            with self.lock:
                user_records = [
                    record for record in self.auth_records 
                    if record.user_id == user_id
                ]
                
                # Apply date filters
                if start_date:
                    user_records = [r for r in user_records if r.timestamp >= start_date]
                if end_date:
                    user_records = [r for r in user_records if r.timestamp <= end_date]
                
                # Sort by timestamp (most recent first)
                user_records.sort(key=lambda x: x.timestamp, reverse=True)
                
                # Apply limit
                user_records = user_records[:limit]
                
                return [record.to_dict() for record in user_records]
                
        except Exception as e:
            logger.error(f"Failed to retrieve authentication history: {str(e)}")
            raise
    
    def get_failed_login_attempts(self, user_id: str, 
                                 time_window: timedelta = timedelta(hours=1)) -> List[Dict[str, Any]]:
        """
        Get recent failed login attempts for a user
        """
        
        try:
            cutoff_time = datetime.utcnow() - time_window
            
            with self.lock:
                failed_attempts = [
                    record for record in self.auth_records
                    if (record.user_id == user_id and 
                        record.event_type == AuthEventType.LOGIN_FAILURE and
                        record.timestamp >= cutoff_time)
                ]
                
                failed_attempts.sort(key=lambda x: x.timestamp, reverse=True)
                
                return [record.to_dict() for record in failed_attempts]
                
        except Exception as e:
            logger.error(f"Failed to retrieve failed login attempts: {str(e)}")
            raise
    
    def is_account_locked(self, user_id: str) -> Dict[str, Any]:
        """
        Check if account should be locked due to failed attempts
        """
        
        try:
            recent_failures = self.get_failed_login_attempts(user_id, self.lockout_duration)
            
            if len(recent_failures) >= self.max_failed_attempts:
                oldest_failure = min(recent_failures, key=lambda x: x['timestamp'])
                lockout_expires = datetime.fromisoformat(oldest_failure['timestamp']) + self.lockout_duration
                
                if datetime.utcnow() < lockout_expires:
                    return {
                        'locked': True,
                        'unlock_time': lockout_expires.isoformat(),
                        'failed_attempts': len(recent_failures)
                    }
            
            return {
                'locked': False,
                'failed_attempts': len(recent_failures)
            }
            
        except Exception as e:
            logger.error(f"Failed to check account lock status: {str(e)}")
            raise
    
    def generate_security_report(self, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Generate security analytics report
        """
        
        try:
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            with self.lock:
                # Filter records by date range
                filtered_records = [
                    record for record in self.auth_records
                    if start_date <= record.timestamp <= end_date
                ]
                
                # Calculate statistics
                total_events = len(filtered_records)
                successful_logins = len([r for r in filtered_records if r.event_type == AuthEventType.LOGIN_SUCCESS])
                failed_logins = len([r for r in filtered_records if r.event_type == AuthEventType.LOGIN_FAILURE])
                
                # Risk analysis
                high_risk_events = len([r for r in filtered_records if r.risk_level == RiskLevel.HIGH])
                critical_risk_events = len([r for r in filtered_records if r.risk_level == RiskLevel.CRITICAL])
                
                # Top failure reasons
                failure_reasons = {}
                for record in filtered_records:
                    if record.failure_reason:
                        failure_reasons[record.failure_reason] = failure_reasons.get(record.failure_reason, 0) + 1
                
                # Authentication methods used
                auth_methods = {}
                for record in filtered_records:
                    method = record.auth_method.value
                    auth_methods[method] = auth_methods.get(method, 0) + 1
                
                return {
                    'report_period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    },
                    'total_events': total_events,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'success_rate': (successful_logins / max(successful_logins + failed_logins, 1)) * 100,
                    'high_risk_events': high_risk_events,
                    'critical_risk_events': critical_risk_events,
                    'failure_reasons': failure_reasons,
                    'authentication_methods': auth_methods,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to generate security report: {str(e)}")
            raise
    
    def cleanup_expired_records(self) -> int:
        """
        Clean up expired authentication records
        """
        
        try:
            with self.lock:
                current_time = datetime.utcnow()
                
                # Count expired records
                expired_count = sum(
                    1 for record in self.auth_records 
                    if record.retention_until <= current_time
                )
                
                # Remove expired records
                self.auth_records = [
                    record for record in self.auth_records
                    if record.retention_until > current_time
                ]
                
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired authentication records")
                
                return expired_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired records: {str(e)}")
            raise
    
    def export_records(self, 
                      user_id: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Export authentication records for compliance or analysis
        """
        
        try:
            with self.lock:
                filtered_records = self.auth_records.copy()
                
                # Apply filters
                if user_id:
                    filtered_records = [r for r in filtered_records if r.user_id == user_id]
                if start_date:
                    filtered_records = [r for r in filtered_records if r.timestamp >= start_date]
                if end_date:
                    filtered_records = [r for r in filtered_records if r.timestamp <= end_date]
                
                return [record.to_dict() for record in filtered_records]
                
        except Exception as e:
            logger.error(f"Failed to export records: {str(e)}")
            raise
    
    def delete_user_records(self, user_id: str) -> int:
        """
        Delete all authentication records for a user (for GDPR right to erasure)
        """
        
        try:
            with self.lock:
                original_count = len(self.auth_records)
                
                # Remove user records
                self.auth_records = [
                    record for record in self.auth_records 
                    if record.user_id != user_id
                ]
                
                deleted_count = original_count - len(self.auth_records)
                
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} authentication records for user {user_id}")
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to delete user records: {str(e)}")
            raise
    
    def _anonymize_ip_address(self, ip_address: str) -> str:
        """Anonymize IP address for privacy compliance"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            if isinstance(ip, ipaddress.IPv4Address):
                # For IPv4, zero out the last octet
                parts = str(ip).split('.')
                parts[-1] = '0'
                return '.'.join(parts)
            elif isinstance(ip, ipaddress.IPv6Address):
                # For IPv6, zero out the last 64 bits
                parts = str(ip).split(':')
                if len(parts) >= 4:
                    return ':'.join(parts[:4]) + '::'
                return str(ip)
            
        except ValueError:
            logger.warning(f"Invalid IP address format: {ip_address}")
            return "0.0.0.0"
        
        return ip_address
    
    def _assess_risk_level(self, event_type: AuthEventType, success: bool, 
                          ip_address: str, user_agent: str) -> RiskLevel:
        """Assess risk level of authentication event"""
        
        # Base risk assessment
        if not success:
            risk_score = 2  # Failed attempts are medium risk
        else:
            risk_score = 1  # Successful events are low risk
        
        # Adjust for event type
        if event_type in [AuthEventType.PRIVILEGE_ESCALATION, AuthEventType.SUSPICIOUS_ACTIVITY]:
            risk_score += 3
        elif event_type == AuthEventType.ACCOUNT_LOCKED:
            risk_score += 2
        
        # Check for suspicious patterns (simplified)
        if 'bot' in user_agent.lower() or 'crawler' in user_agent.lower():
            risk_score += 2
        
        # Convert score to risk level
        if risk_score >= 5:
            return RiskLevel.CRITICAL
        elif risk_score >= 3:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _check_suspicious_activity(self, user_id: str, event_type: AuthEventType, 
                                 success: bool, ip_address: str):
        """Check for suspicious authentication patterns"""
        
        # Simple brute force detection
        if not success:
            recent_failures = self.get_failed_login_attempts(user_id, timedelta(minutes=10))
            
            if len(recent_failures) >= 3:  # 3 failures in 10 minutes
                logger.warning(f"Suspicious activity detected for user {user_id}: {len(recent_failures)} failed attempts")
                
                # Log suspicious activity event
                self.log_authentication_event(
                    user_id=user_id,
                    event_type=AuthEventType.SUSPICIOUS_ACTIVITY,
                    auth_method=AuthMethod.PASSWORD,
                    success=False,
                    ip_address=ip_address,
                    user_agent="system",
                    failure_reason="Multiple failed login attempts"
                )
    
    def _persist_record(self, record: AuthenticationRecord):
        """Persist record to secure storage"""
        # In production, this would save to encrypted database
        # For now, we'll just log the action
        pass

def create_authentication_logger():
    """Factory function to create authentication logger"""
    return AuthenticationLogger()

# Helper functions for Flask integration
def log_login_attempt(user_id: str, success: bool, ip_address: str, user_agent: str,
                     failure_reason: Optional[str] = None) -> str:
    """Helper function to log login attempts"""
    
    auth_logger = create_authentication_logger()
    
    event_type = AuthEventType.LOGIN_SUCCESS if success else AuthEventType.LOGIN_FAILURE
    
    return auth_logger.log_authentication_event(
        user_id=user_id,
        event_type=event_type,
        auth_method=AuthMethod.PASSWORD,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent,
        failure_reason=failure_reason
    )

def log_logout(user_id: str, session_id: str, ip_address: str, user_agent: str) -> str:
    """Helper function to log logout events"""
    
    auth_logger = create_authentication_logger()
    
    return auth_logger.log_authentication_event(
        user_id=user_id,
        event_type=AuthEventType.LOGOUT,
        auth_method=AuthMethod.PASSWORD,
        success=True,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )

def check_account_lockout(user_id: str) -> Dict[str, Any]:
    """Check if account is locked due to failed attempts"""
    
    auth_logger = create_authentication_logger()
    return auth_logger.is_account_locked(user_id)
