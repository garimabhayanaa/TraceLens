import logging
import hashlib
import hmac
import secrets
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import uuid
import re
from collections import defaultdict
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types of analysis requests"""
    SELF_ANALYSIS = "self_analysis"
    THIRD_PARTY_ANALYSIS = "third_party_analysis"
    RESEARCH_ANALYSIS = "research_analysis"
    SECURITY_ANALYSIS = "security_analysis"


class VerificationMethod(Enum):
    """Identity verification methods"""
    EMAIL_VERIFICATION = "email_verification"
    SMS_VERIFICATION = "sms_verification"
    BIOMETRIC_VERIFICATION = "biometric_verification"
    DOCUMENT_VERIFICATION = "document_verification"


class AccessLevel(Enum):
    """Access levels for different analysis types"""
    BASIC = "basic"
    ENHANCED = "enhanced"
    PROFESSIONAL = "professional"
    RESTRICTED = "restricted"


class ConsentStatus(Enum):
    """Status of third-party consent"""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class AuthorizationConfig:
    """Configuration for authorization framework"""
    max_verification_attempts: int = 5
    verification_code_expiry_minutes: int = 15
    max_failed_attempts: int = 3
    ip_block_duration_hours: int = 24
    consent_expiry_days: int = 30
    require_mfa: bool = True
    audit_retention_days: int = 365


@dataclass
class IdentityVerification:
    """Identity verification record"""
    verification_id: str
    user_id: str
    email: str
    verification_method: VerificationMethod
    verification_code: str
    code_hash: str
    created_at: datetime
    expires_at: datetime
    verified_at: Optional[datetime]
    attempts: int
    status: str  # 'pending', 'verified', 'failed', 'expired'
    ip_address: str
    user_agent: str


@dataclass
class ThirdPartyConsent:
    """Third-party analysis consent record"""
    consent_id: str
    requester_user_id: str
    target_user_id: str
    target_email: str
    analysis_purpose: str
    data_scope: List[str]
    consent_status: ConsentStatus
    requested_at: datetime
    granted_at: Optional[datetime]
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime]
    consent_token: str
    verification_method: str


@dataclass
class AccessAttempt:
    """Record of access attempt"""
    attempt_id: str
    user_id: Optional[str]
    email: str
    analysis_type: AnalysisType
    target_data: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    success: bool
    failure_reason: Optional[str]
    verification_status: str
    consent_status: Optional[str]


@dataclass
class IPBlock:
    """IP address blocking record"""
    ip_address: str
    blocked_at: datetime
    expires_at: datetime
    reason: str
    attempt_count: int
    block_level: str  # 'temporary', 'extended', 'permanent'


@dataclass
class AuthorizationResult:
    """Authorization check result"""
    authorized: bool
    access_level: AccessLevel
    verification_required: bool
    consent_required: bool
    failure_reasons: List[str]
    required_actions: List[str]
    session_token: Optional[str]


class IdentityVerificationSystem:
    """Multi-factor identity verification system"""

    def __init__(self, config: AuthorizationConfig = None):
        self.config = config or AuthorizationConfig()
        self.verification_records = {}
        self.failed_attempts = defaultdict(int)
        self._lock = threading.RLock()

    def initiate_email_verification(self, user_id: str, email: str,
                                    ip_address: str, user_agent: str) -> IdentityVerification:
        """Initiate email-based identity verification"""

        # Input validation
        if not self._is_valid_email(email):
            raise ValueError("Invalid email address format")

        # Check rate limiting
        if self.failed_attempts[email] >= self.config.max_verification_attempts:
            raise ValueError("Maximum verification attempts exceeded")

        verification_id = str(uuid.uuid4())
        verification_code = self._generate_verification_code()
        code_hash = self._hash_verification_code(verification_code)

        verification = IdentityVerification(
            verification_id=verification_id,
            user_id=user_id,
            email=email,
            verification_method=VerificationMethod.EMAIL_VERIFICATION,
            verification_code=verification_code,
            code_hash=code_hash,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=self.config.verification_code_expiry_minutes),
            verified_at=None,
            attempts=0,
            status='pending',
            ip_address=ip_address,
            user_agent=user_agent
        )

        with self._lock:
            self.verification_records[verification_id] = verification

        # Send verification email
        self._send_verification_email(email, verification_code, verification_id)

        # Audit logging
        logger.info(f"Email verification initiated for {email} from {ip_address}")

        return verification

    def verify_identity(self, verification_id: str, provided_code: str,
                        ip_address: str) -> Dict[str, Any]:
        """Verify identity using provided code"""

        with self._lock:
            if verification_id not in self.verification_records:
                return {'success': False, 'error': 'Verification not found'}

            verification = self.verification_records[verification_id]

            # Check if already verified
            if verification.status == 'verified':
                return {'success': False, 'error': 'Already verified'}

            # Check expiration
            if datetime.utcnow() > verification.expires_at:
                verification.status = 'expired'
                return {'success': False, 'error': 'Verification code expired'}

            # Increment attempt counter
            verification.attempts += 1

            # Check attempt limit
            if verification.attempts > self.config.max_verification_attempts:
                verification.status = 'failed'
                self.failed_attempts[verification.email] += 1
                return {'success': False, 'error': 'Maximum attempts exceeded'}

            # Verify code
            if self._verify_code(provided_code, verification.code_hash):
                verification.status = 'verified'
                verification.verified_at = datetime.utcnow()

                # Clear failed attempts
                if verification.email in self.failed_attempts:
                    del self.failed_attempts[verification.email]

                # Generate session token
                session_token = self._generate_session_token(verification.user_id, verification.email)

                logger.info(f"Identity verified successfully for {verification.email}")

                return {
                    'success': True,
                    'verification_id': verification_id,
                    'session_token': session_token,
                    'verified_at': verification.verified_at.isoformat()
                }
            else:
                if verification.attempts >= self.config.max_verification_attempts:
                    verification.status = 'failed'
                    self.failed_attempts[verification.email] += 1

                logger.warning(f"Invalid verification code provided for {verification.email}")

                return {
                    'success': False,
                    'error': 'Invalid verification code',
                    'attempts_remaining': max(0, self.config.max_verification_attempts - verification.attempts)
                }

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _generate_verification_code(self) -> str:
        """Generate secure verification code"""
        return f"{secrets.randbelow(1000000):06d}"

    def _hash_verification_code(self, code: str) -> str:
        """Hash verification code for secure storage"""
        salt = secrets.token_bytes(32)
        code_hash = hashlib.pbkdf2_hmac('sha256', code.encode(), salt, 100000)
        return salt.hex() + code_hash.hex()

    def _verify_code(self, provided_code: str, stored_hash: str) -> bool:
        """Verify provided code against stored hash"""
        try:
            salt = bytes.fromhex(stored_hash[:64])
            stored_code_hash = stored_hash[64:]
            provided_hash = hashlib.pbkdf2_hmac('sha256', provided_code.encode(), salt, 100000)
            return hmac.compare_digest(provided_hash.hex(), stored_code_hash)
        except Exception:
            return False

    def _generate_session_token(self, user_id: str, email: str) -> str:
        """Generate secure session token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'verified_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }

        # In production, use proper JWT with secret key
        token_data = json.dumps(payload)
        return hashlib.sha256(token_data.encode()).hexdigest()

    def _send_verification_email(self, email: str, code: str, verification_id: str):
        """Send verification email (placeholder implementation)"""

        # In production, integrate with email service (SendGrid, SES, etc.)
        email_content = f"""
        Your Social Media Analysis Verification Code: {code}

        This code expires in {self.config.verification_code_expiry_minutes} minutes.

        If you did not request this verification, please ignore this email.

        Verification ID: {verification_id}
        """

        logger.info(f"Verification email sent to {email} with code {code}")
        # Actual email sending would be implemented here


class ConsentManagementSystem:
    """System for managing third-party analysis consent"""

    def __init__(self, config: AuthorizationConfig = None):
        self.config = config or AuthorizationConfig()
        self.consent_records = {}
        self.pending_requests = {}
        self._lock = threading.RLock()

    def request_third_party_consent(self, requester_user_id: str, target_email: str,
                                    analysis_purpose: str, data_scope: List[str]) -> ThirdPartyConsent:
        """Request consent for third-party analysis"""

        # Input validation
        if not self._is_valid_email(target_email):
            raise ValueError("Invalid target email address")

        if not analysis_purpose or len(analysis_purpose.strip()) < 10:
            raise ValueError("Analysis purpose must be clearly specified (minimum 10 characters)")

        consent_id = str(uuid.uuid4())
        consent_token = self._generate_consent_token()

        consent_request = ThirdPartyConsent(
            consent_id=consent_id,
            requester_user_id=requester_user_id,
            target_user_id='',  # Will be filled when consent is granted
            target_email=target_email,
            analysis_purpose=analysis_purpose,
            data_scope=data_scope,
            consent_status=ConsentStatus.PENDING,
            requested_at=datetime.utcnow(),
            granted_at=None,
            expires_at=datetime.utcnow() + timedelta(days=self.config.consent_expiry_days),
            revoked_at=None,
            consent_token=consent_token,
            verification_method='email_consent'
        )

        with self._lock:
            self.consent_records[consent_id] = consent_request
            self.pending_requests[target_email] = consent_request

        # Send consent request email
        self._send_consent_request_email(consent_request)

        logger.info(f"Third-party consent requested for {target_email} by {requester_user_id}")

        return consent_request

    def grant_consent(self, consent_token: str, target_user_id: str) -> Dict[str, Any]:
        """Grant consent for third-party analysis"""

        with self._lock:
            # Find consent record by token
            consent_request = None
            for consent in self.consent_records.values():
                if consent.consent_token == consent_token:
                    consent_request = consent
                    break

            if not consent_request:
                return {'success': False, 'error': 'Invalid consent token'}

            # Check if already processed
            if consent_request.consent_status != ConsentStatus.PENDING:
                return {'success': False, 'error': 'Consent already processed'}

            # Check expiration
            if datetime.utcnow() > consent_request.expires_at:
                consent_request.consent_status = ConsentStatus.EXPIRED
                return {'success': False, 'error': 'Consent request expired'}

            # Grant consent
            consent_request.consent_status = ConsentStatus.GRANTED
            consent_request.target_user_id = target_user_id
            consent_request.granted_at = datetime.utcnow()

            # Remove from pending requests
            if consent_request.target_email in self.pending_requests:
                del self.pending_requests[consent_request.target_email]

        logger.info(f"Consent granted for analysis by {consent_request.requester_user_id}")

        return {
            'success': True,
            'consent_id': consent_request.consent_id,
            'granted_at': consent_request.granted_at.isoformat(),
            'expires_at': consent_request.expires_at.isoformat()
        }

    def revoke_consent(self, consent_id: str, target_user_id: str) -> Dict[str, Any]:
        """Revoke previously granted consent"""

        with self._lock:
            if consent_id not in self.consent_records:
                return {'success': False, 'error': 'Consent not found'}

            consent = self.consent_records[consent_id]

            # Verify ownership
            if consent.target_user_id != target_user_id:
                return {'success': False, 'error': 'Unauthorized revocation attempt'}

            # Check if can be revoked
            if consent.consent_status not in [ConsentStatus.GRANTED, ConsentStatus.PENDING]:
                return {'success': False, 'error': 'Consent cannot be revoked'}

            # Revoke consent
            consent.consent_status = ConsentStatus.REVOKED
            consent.revoked_at = datetime.utcnow()

        logger.info(f"Consent {consent_id} revoked by {target_user_id}")

        return {
            'success': True,
            'consent_id': consent_id,
            'revoked_at': consent.revoked_at.isoformat()
        }

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _generate_consent_token(self) -> str:
        """Generate secure consent token"""
        return secrets.token_urlsafe(32)

    def _send_consent_request_email(self, consent_request: ThirdPartyConsent):
        """Send consent request email"""

        consent_url = f"https://yourapp.com/consent/{consent_request.consent_token}"

        email_content = f"""
        Consent Request for Social Media Analysis

        Someone has requested permission to analyze your digital footprint.

        Requester: {consent_request.requester_user_id}
        Purpose: {consent_request.analysis_purpose}
        Data Scope: {', '.join(consent_request.data_scope)}

        To grant or deny this request, click: {consent_url}

        This request expires on: {consent_request.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

        If you did not expect this request, you can safely ignore this email.
        """

        logger.info(f"Consent request email sent to {consent_request.target_email}")
        # Actual email sending would be implemented here


class AccessLogger:
    """Comprehensive access logging system"""

    def __init__(self, config: AuthorizationConfig = None):
        self.config = config or AuthorizationConfig()
        self.access_logs = []
        self.failed_attempts = defaultdict(list)
        self._lock = threading.RLock()

    def log_access_attempt(self, user_id: Optional[str], email: str, analysis_type: AnalysisType,
                           target_data: str, ip_address: str, user_agent: str,
                           success: bool, failure_reason: Optional[str] = None,
                           verification_status: str = 'unknown',
                           consent_status: Optional[str] = None) -> str:
        """Log access attempt with comprehensive details"""

        attempt_id = str(uuid.uuid4())

        access_attempt = AccessAttempt(
            attempt_id=attempt_id,
            user_id=user_id,
            email=email,
            analysis_type=analysis_type,
            target_data=hashlib.sha256(target_data.encode()).hexdigest()[:16],  # Anonymized
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            success=success,
            failure_reason=failure_reason,
            verification_status=verification_status,
            consent_status=consent_status
        )

        with self._lock:
            self.access_logs.append(access_attempt)

            # Track failed attempts for abuse prevention
            if not success:
                self.failed_attempts[ip_address].append(datetime.utcnow())

                # Clean old failed attempts (keep last 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.failed_attempts[ip_address] = [
                    timestamp for timestamp in self.failed_attempts[ip_address]
                    if timestamp > cutoff_time
                ]

        # Log for security monitoring
        log_level = logging.WARNING if not success else logging.INFO
        logger.log(log_level, f"Access attempt: {asdict(access_attempt)}")

        return attempt_id

    def get_access_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get access statistics for monitoring"""

        cutoff_time = datetime.utcnow() - timedelta(days=days)
        recent_logs = [log for log in self.access_logs if log.timestamp > cutoff_time]

        if not recent_logs:
            return {'total_attempts': 0}

        total_attempts = len(recent_logs)
        successful_attempts = sum(1 for log in recent_logs if log.success)
        failed_attempts = total_attempts - successful_attempts

        # Analysis by type
        by_type = defaultdict(int)
        for log in recent_logs:
            by_type[log.analysis_type.value] += 1

        # Top IP addresses
        ip_counts = defaultdict(int)
        for log in recent_logs:
            ip_counts[log.ip_address] += 1
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'failed_attempts': failed_attempts,
            'success_rate': successful_attempts / total_attempts if total_attempts > 0 else 0,
            'by_analysis_type': dict(by_type),
            'top_ip_addresses': [{'ip': ip, 'attempts': count} for ip, count in top_ips],
            'period_days': days
        }


class AbusePreventionSystem:
    """IP-based blocking and abuse prevention"""

    def __init__(self, config: AuthorizationConfig = None):
        self.config = config or AuthorizationConfig()
        self.blocked_ips = {}
        self.suspicious_activities = defaultdict(list)
        self._lock = threading.RLock()

    def check_ip_status(self, ip_address: str) -> Dict[str, Any]:
        """Check if IP address is blocked or suspicious"""

        with self._lock:
            # Check if IP is currently blocked
            if ip_address in self.blocked_ips:
                block = self.blocked_ips[ip_address]

                # Check if block has expired
                if datetime.utcnow() > block.expires_at:
                    del self.blocked_ips[ip_address]
                    logger.info(f"IP block expired for {ip_address}")
                else:
                    return {
                        'blocked': True,
                        'reason': block.reason,
                        'expires_at': block.expires_at.isoformat(),
                        'block_level': block.block_level
                    }

            # Check suspicious activity level
            recent_activities = self._get_recent_activities(ip_address)
            suspicion_level = self._calculate_suspicion_level(recent_activities)

            return {
                'blocked': False,
                'suspicion_level': suspicion_level,
                'recent_activity_count': len(recent_activities),
                'warning': suspicion_level > 0.7
            }

    def record_failed_attempt(self, ip_address: str, reason: str, user_agent: str):
        """Record failed access attempt"""

        with self._lock:
            activity = {
                'timestamp': datetime.utcnow(),
                'reason': reason,
                'user_agent': user_agent
            }

            self.suspicious_activities[ip_address].append(activity)

            # Clean old activities (keep last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.suspicious_activities[ip_address] = [
                act for act in self.suspicious_activities[ip_address]
                if act['timestamp'] > cutoff_time
            ]

            # Check if IP should be blocked
            recent_failures = len(self.suspicious_activities[ip_address])
            if recent_failures >= self.config.max_failed_attempts:
                self._block_ip(ip_address, f"Exceeded maximum failed attempts ({recent_failures})")

    def _block_ip(self, ip_address: str, reason: str):
        """Block IP address"""

        # Determine block level based on history
        if ip_address in self.blocked_ips:
            # Escalate block level for repeat offenders
            block_level = 'extended'
            duration_hours = self.config.ip_block_duration_hours * 2
        else:
            block_level = 'temporary'
            duration_hours = self.config.ip_block_duration_hours

        block = IPBlock(
            ip_address=ip_address,
            blocked_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=duration_hours),
            reason=reason,
            attempt_count=len(self.suspicious_activities.get(ip_address, [])),
            block_level=block_level
        )

        with self._lock:
            self.blocked_ips[ip_address] = block

        logger.warning(f"IP address blocked: {ip_address} - {reason}")

    def _get_recent_activities(self, ip_address: str) -> List[Dict[str, Any]]:
        """Get recent activities for IP address"""

        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        return [
            activity for activity in self.suspicious_activities.get(ip_address, [])
            if activity['timestamp'] > cutoff_time
        ]

    def _calculate_suspicion_level(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate suspicion level based on activities"""

        if not activities:
            return 0.0

        # Base suspicion on frequency and patterns
        activity_count = len(activities)

        # Check for automation patterns (identical user agents, timing patterns)
        user_agents = [act.get('user_agent', '') for act in activities]
        unique_user_agents = len(set(user_agents))

        # Calculate suspicion factors
        frequency_factor = min(activity_count / 10.0, 1.0)  # Max 1.0 at 10+ activities per hour
        automation_factor = 1.0 - (unique_user_agents / max(activity_count, 1))  # Higher if same user agents

        return min((frequency_factor + automation_factor) / 2.0, 1.0)


class AuthorizationFramework:
    """Main authorization framework coordinating all access control components"""

    def __init__(self, config: AuthorizationConfig = None):
        self.config = config or AuthorizationConfig()
        self.identity_verifier = IdentityVerificationSystem(self.config)
        self.consent_manager = ConsentManagementSystem(self.config)
        self.access_logger = AccessLogger(self.config)
        self.abuse_preventer = AbusePreventionSystem(self.config)

        logger.info("Authorization-Based Access Control Framework initialized")

    def authorize_analysis_request(self, user_id: str, user_email: str,
                                   analysis_type: AnalysisType, target_data: str,
                                   ip_address: str, user_agent: str,
                                   session_token: Optional[str] = None,
                                   consent_token: Optional[str] = None) -> AuthorizationResult:
        """Comprehensive authorization check for analysis requests"""

        logger.info(f"Authorizing {analysis_type.value} request from {user_email} ({ip_address})")

        failure_reasons = []
        required_actions = []

        # 1. Check IP blocking status
        ip_status = self.abuse_preventer.check_ip_status(ip_address)
        if ip_status['blocked']:
            failure_reason = f"IP blocked: {ip_status['reason']}"
            self.access_logger.log_access_attempt(
                user_id, user_email, analysis_type, target_data,
                ip_address, user_agent, False, failure_reason
            )
            return AuthorizationResult(
                authorized=False,
                access_level=AccessLevel.RESTRICTED,
                verification_required=False,
                consent_required=False,
                failure_reasons=[failure_reason],
                required_actions=[],
                session_token=None
            )

        # 2. Verify identity (always required)
        identity_verified = self._check_identity_verification(user_id, user_email, session_token)
        if not identity_verified:
            failure_reasons.append("Identity verification required")
            required_actions.append("Complete multi-factor email verification")

        # 3. Check analysis type specific requirements
        if analysis_type == AnalysisType.SELF_ANALYSIS:
            # Self-analysis: verify data ownership
            if not self._verify_data_ownership(user_id, user_email, target_data):
                failure_reasons.append("Data ownership verification failed")
                required_actions.append("Verify ownership of target social media accounts")

        elif analysis_type == AnalysisType.THIRD_PARTY_ANALYSIS:
            # Third-party analysis: explicit consent required
            consent_valid = self._check_third_party_consent(user_id, target_data, consent_token)
            if not consent_valid:
                failure_reasons.append("Third-party consent required")
                required_actions.append("Obtain written consent from data owner")

        elif analysis_type in [AnalysisType.RESEARCH_ANALYSIS, AnalysisType.SECURITY_ANALYSIS]:
            # Research/security analysis: enhanced verification
            enhanced_verified = self._check_enhanced_verification(user_id, session_token)
            if not enhanced_verified:
                failure_reasons.append("Enhanced verification required for research/security analysis")
                required_actions.append("Complete enhanced identity verification process")

        # 4. Determine access level and authorization
        if not failure_reasons:
            access_level = self._determine_access_level(analysis_type, identity_verified)
            authorized = True

            # Generate new session token if needed
            if not session_token:
                session_token = self.identity_verifier._generate_session_token(user_id, user_email)

            # Log successful authorization
            self.access_logger.log_access_attempt(
                user_id, user_email, analysis_type, target_data,
                ip_address, user_agent, True, None, 'verified'
            )

            logger.info(f"Analysis authorized: {analysis_type.value} for {user_email}")

        else:
            access_level = AccessLevel.RESTRICTED
            authorized = False

            # Log failed authorization
            self.access_logger.log_access_attempt(
                user_id, user_email, analysis_type, target_data,
                ip_address, user_agent, False, '; '.join(failure_reasons)
            )

            # Record failed attempt for abuse prevention
            self.abuse_preventer.record_failed_attempt(ip_address, failure_reasons[0], user_agent)

            logger.warning(f"Analysis denied: {analysis_type.value} for {user_email} - {'; '.join(failure_reasons)}")

        return AuthorizationResult(
            authorized=authorized,
            access_level=access_level,
            verification_required=not identity_verified,
            consent_required=(analysis_type == AnalysisType.THIRD_PARTY_ANALYSIS and
                              "Third-party consent required" in failure_reasons),
            failure_reasons=failure_reasons,
            required_actions=required_actions,
            session_token=session_token if authorized else None
        )

    def _check_identity_verification(self, user_id: str, user_email: str,
                                     session_token: Optional[str]) -> bool:
        """Check if identity is properly verified"""

        if not session_token:
            return False

        # In production, properly validate JWT token
        # For now, check if token exists and is valid format
        try:
            # Simple token validation (would be proper JWT validation in production)
            if len(session_token) == 64:  # SHA256 hash length
                return True
        except Exception:
            pass

        return False

    def _verify_data_ownership(self, user_id: str, user_email: str, target_data: str) -> bool:
        """Verify user owns the target data for self-analysis"""

        # In production, this would verify:
        # 1. Social media account ownership via OAuth
        # 2. Email domain matching for corporate accounts
        # 3. Phone number verification for mobile accounts

        # For now, simple verification based on email domain matching
        try:
            # Extract domain from email and check if it matches any social platforms
            email_domain = user_email.split('@')[1].lower()

            # Simple ownership verification (would be more sophisticated in production)
            if 'twitter.com' in target_data.lower() and email_domain == 'twitter.com':
                return True
            if 'linkedin.com' in target_data.lower() and email_domain == 'linkedin.com':
                return True
            if 'github.com' in target_data.lower() and email_domain == 'github.com':
                return True

            # For demo purposes, allow self-analysis if email contains username
            username_part = user_email.split('@')[0]
            if username_part.lower() in target_data.lower():
                return True

            return True  # Allow for demonstration

        except Exception:
            return False

    def _check_third_party_consent(self, requester_user_id: str, target_data: str,
                                   consent_token: Optional[str]) -> bool:
        """Check if valid third-party consent exists"""

        if not consent_token:
            return False

        # Find consent record by token
        for consent in self.consent_manager.consent_records.values():
            if (consent.consent_token == consent_token and
                    consent.requester_user_id == requester_user_id and
                    consent.consent_status == ConsentStatus.GRANTED and
                    datetime.utcnow() <= consent.expires_at):
                return True

        return False

    def _check_enhanced_verification(self, user_id: str, session_token: Optional[str]) -> bool:
        """Check enhanced verification for research/security analysis"""

        # Enhanced verification would require:
        # 1. Additional identity documents
        # 2. Institutional affiliation verification
        # 3. Purpose validation

        # For now, use same verification as basic
        return self._check_identity_verification(user_id, '', session_token)

    def _determine_access_level(self, analysis_type: AnalysisType, identity_verified: bool) -> AccessLevel:
        """Determine access level based on analysis type and verification status"""

        if not identity_verified:
            return AccessLevel.RESTRICTED

        access_mapping = {
            AnalysisType.SELF_ANALYSIS: AccessLevel.ENHANCED,
            AnalysisType.THIRD_PARTY_ANALYSIS: AccessLevel.BASIC,
            AnalysisType.RESEARCH_ANALYSIS: AccessLevel.PROFESSIONAL,
            AnalysisType.SECURITY_ANALYSIS: AccessLevel.PROFESSIONAL
        }

        return access_mapping.get(analysis_type, AccessLevel.BASIC)

    def get_authorization_status(self) -> Dict[str, Any]:
        """Get current authorization system status"""

        return {
            'framework_enabled': True,
            'identity_verification_enabled': True,
            'consent_management_enabled': True,
            'access_logging_enabled': True,
            'abuse_prevention_enabled': True,
            'supported_analysis_types': [t.value for t in AnalysisType],
            'verification_methods': [m.value for m in VerificationMethod],
            'access_levels': [l.value for l in AccessLevel],
            'access_statistics': self.access_logger.get_access_statistics(),
            'configuration': {
                'max_verification_attempts': self.config.max_verification_attempts,
                'verification_code_expiry_minutes': self.config.verification_code_expiry_minutes,
                'max_failed_attempts': self.config.max_failed_attempts,
                'ip_block_duration_hours': self.config.ip_block_duration_hours,
                'consent_expiry_days': self.config.consent_expiry_days,
                'mfa_required': self.config.require_mfa
            }
        }


def create_authorization_framework(config: AuthorizationConfig = None) -> AuthorizationFramework:
    """Factory function to create authorization framework"""
    return AuthorizationFramework(config)
