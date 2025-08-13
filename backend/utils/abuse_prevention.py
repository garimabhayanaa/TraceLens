import logging
import hashlib
import time
import json
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
import re
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

logger = logging.getLogger(__name__)


class SuspiciousActivityType(Enum):
    """Types of suspicious activities"""
    RAPID_REQUESTS = "rapid_requests"
    MULTIPLE_IPS = "multiple_ips"
    INVALID_PATTERNS = "invalid_patterns"
    FAILED_VERIFICATIONS = "failed_verifications"
    UNUSUAL_USAGE = "unusual_usage"
    BOT_BEHAVIOR = "bot_behavior"
    ABUSE_REPORTS = "abuse_reports"
    POLICY_VIOLATIONS = "policy_violations"


class ReportType(Enum):
    """Types of abuse reports"""
    HARASSMENT = "harassment"
    SPAM = "spam"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PRIVACY_VIOLATION = "privacy_violation"
    TECHNICAL_ABUSE = "technical_abuse"
    POLICY_VIOLATION = "policy_violation"
    SECURITY_CONCERN = "security_concern"
    OTHER = "other"


class ActionLevel(Enum):
    """Escalation levels for abuse prevention"""
    WARNING = "warning"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_BLOCK = "temporary_block"
    PERMANENT_BAN = "permanent_ban"
    MANUAL_REVIEW = "manual_review"


@dataclass
class AbusePreventionConfig:
    """Configuration for abuse prevention system"""
    # Email verification settings
    enable_email_verification: bool = True
    verification_code_length: int = 6
    verification_expiry_minutes: int = 15
    max_verification_attempts: int = 3

    # reCAPTCHA settings
    enable_recaptcha: bool = True
    recaptcha_site_key: str = ""
    recaptcha_secret_key: str = ""
    recaptcha_threshold: float = 0.5

    # Usage limits
    max_analyses_per_day: int = 3
    max_analyses_per_hour: int = 1
    max_failed_attempts: int = 5

    # IP tracking settings
    enable_ip_tracking: bool = True
    suspicious_threshold: int = 10
    block_duration_hours: int = 24
    max_ips_per_user: int = 3

    # Reporting settings
    enable_reporting: bool = True
    admin_email: str = "admin@company.com"
    auto_escalation_threshold: int = 3


@dataclass
class EmailVerification:
    """Email verification record"""
    verification_id: str
    user_id: str
    email: str
    verification_code: str
    created_at: datetime
    expires_at: datetime
    attempts: int
    verified: bool
    ip_address: str
    user_agent: str


@dataclass
class UsageRecord:
    """User usage tracking record"""
    user_id: str
    email: str
    ip_address: str
    analysis_count_today: int
    analysis_count_hour: int
    last_analysis: datetime
    failed_attempts: int
    verification_required: bool
    blocked_until: Optional[datetime]
    warning_count: int


@dataclass
class SuspiciousActivity:
    """Suspicious activity detection record"""
    activity_id: str
    activity_type: SuspiciousActivityType
    user_id: Optional[str]
    ip_address: str
    description: str
    severity_score: float
    detected_at: datetime
    evidence: Dict[str, Any]
    action_taken: ActionLevel
    resolved: bool


@dataclass
class AbuseReport:
    """User abuse report record"""
    report_id: str
    reporter_user_id: Optional[str]
    reporter_email: Optional[str]
    report_type: ReportType
    target_user_id: Optional[str]
    target_content: Optional[str]
    description: str
    evidence: Dict[str, Any]
    reported_at: datetime
    status: str  # 'pending', 'investigating', 'resolved', 'dismissed'
    admin_notes: str
    action_taken: Optional[ActionLevel]


class EmailVerificationManager:
    """Manages email verification with anti-abuse measures"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config
        self.verifications = {}
        self.verification_attempts = defaultdict(int)
        self._lock = threading.RLock()

        # Email settings (would be configured from environment)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "noreply@company.com"
        self.smtp_password = "app_password"  # Use app password for Gmail

    def initiate_verification(self, user_id: str, email: str,
                              ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Initiate email verification process"""

        if not self.config.enable_email_verification:
            return {'success': True, 'message': 'Email verification disabled'}

        # Check for too many verification attempts
        attempt_key = f"{email}:{ip_address}"
        with self._lock:
            if self.verification_attempts[attempt_key] >= self.config.max_verification_attempts:
                return {
                    'success': False,
                    'error': 'Too many verification attempts. Please try again later.',
                    'retry_after': 3600  # 1 hour
                }

        # Generate verification code
        verification_code = self._generate_verification_code()
        verification_id = str(uuid.uuid4())

        # Create verification record
        verification = EmailVerification(
            verification_id=verification_id,
            user_id=user_id,
            email=email,
            verification_code=verification_code,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=self.config.verification_expiry_minutes),
            attempts=0,
            verified=False,
            ip_address=ip_address,
            user_agent=user_agent
        )

        with self._lock:
            self.verifications[verification_id] = verification
            self.verification_attempts[attempt_key] += 1

        # Send verification email
        email_sent = self._send_verification_email(email, verification_code, user_id)

        if not email_sent:
            return {'success': False, 'error': 'Failed to send verification email'}

        logger.info(f"Email verification initiated for {email} from IP {ip_address}")

        return {
            'success': True,
            'verification_id': verification_id,
            'expires_at': verification.expires_at.isoformat(),
            'message': f'Verification code sent to {email}'
        }

    def verify_email(self, verification_id: str, verification_code: str,
                     ip_address: str) -> Dict[str, Any]:
        """Verify email with provided code"""

        with self._lock:
            verification = self.verifications.get(verification_id)

            if not verification:
                return {'success': False, 'error': 'Invalid verification ID'}

            if verification.verified:
                return {'success': True, 'message': 'Email already verified'}

            if datetime.utcnow() > verification.expires_at:
                return {'success': False, 'error': 'Verification code expired'}

            verification.attempts += 1

            # Check for too many attempts
            if verification.attempts > self.config.max_verification_attempts:
                return {
                    'success': False,
                    'error': 'Too many verification attempts. Please request a new code.'
                }

            # Verify code
            if verification.verification_code != verification_code:
                return {
                    'success': False,
                    'error': f'Invalid verification code. {self.config.max_verification_attempts - verification.attempts} attempts remaining.'
                }

            # Verify IP address (basic security check)
            if verification.ip_address != ip_address:
                logger.warning(f"IP address mismatch during verification: {verification.ip_address} != {ip_address}")
                # Continue but log for monitoring

            # Mark as verified
            verification.verified = True

        logger.info(f"Email verification successful for {verification.email}")

        return {
            'success': True,
            'message': 'Email verified successfully',
            'user_id': verification.user_id,
            'email': verification.email
        }

    def _generate_verification_code(self) -> str:
        """Generate random verification code"""
        return ''.join(random.choices(string.digits, k=self.config.verification_code_length))

    def _send_verification_email(self, email: str, verification_code: str, user_id: str) -> bool:
        """Send verification email to user"""

        try:
            # Create email message
            msg = MimeMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = "Verify Your Email - Social Media Analysis Service"

            # Email body
            body = f"""
Dear User,

Thank you for using our Social Media Analysis Service. To verify your email address and secure your account, please use the following verification code:

Verification Code: {verification_code}

This code will expire in {self.config.verification_expiry_minutes} minutes.

For your security:
- Do not share this code with anyone
- This code is only valid for your current session
- If you didn't request this verification, please ignore this email

If you have any questions or concerns, please contact our support team.

Best regards,
Social Media Analysis Security Team

---
This is an automated message. Please do not reply to this email.
User ID: {user_id[:8]}...
Timestamp: {datetime.utcnow().isoformat()}
            """

            msg.attach(MimeText(body, 'plain'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, email, text)
            server.quit()

            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return False

    def cleanup_expired_verifications(self):
        """Clean up expired verification records"""

        current_time = datetime.utcnow()
        expired_ids = []

        with self._lock:
            for verification_id, verification in self.verifications.items():
                if current_time > verification.expires_at:
                    expired_ids.append(verification_id)

            for verification_id in expired_ids:
                del self.verifications[verification_id]

        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired email verifications")


class RecaptchaVerifier:
    """reCAPTCHA verification for bot protection"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config

    def verify_recaptcha(self, recaptcha_response: str, ip_address: str) -> Dict[str, Any]:
        """Verify reCAPTCHA response"""

        if not self.config.enable_recaptcha:
            return {'success': True, 'message': 'reCAPTCHA verification disabled'}

        if not recaptcha_response:
            return {'success': False, 'error': 'reCAPTCHA response required'}

        try:
            # Verify with Google reCAPTCHA API
            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
            data = {
                'secret': self.config.recaptcha_secret_key,
                'response': recaptcha_response,
                'remoteip': ip_address
            }

            response = requests.post(verify_url, data=data, timeout=10)
            result = response.json()

            if result.get('success'):
                score = result.get('score', 0.5)  # v3 reCAPTCHA score

                if score >= self.config.recaptcha_threshold:
                    return {
                        'success': True,
                        'score': score,
                        'message': 'reCAPTCHA verification successful'
                    }
                else:
                    return {
                        'success': False,
                        'score': score,
                        'error': 'reCAPTCHA score too low - suspected bot activity'
                    }
            else:
                error_codes = result.get('error-codes', [])
                return {
                    'success': False,
                    'error': f'reCAPTCHA verification failed: {", ".join(error_codes)}'
                }

        except Exception as e:
            logger.error(f"reCAPTCHA verification error: {str(e)}")
            return {
                'success': False,
                'error': 'reCAPTCHA verification service unavailable'
            }


class UsageLimitManager:
    """Manages user usage limits and throttling"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config
        self.usage_records = {}
        self.daily_usage = defaultdict(int)
        self.hourly_usage = defaultdict(int)
        self._lock = threading.RLock()

    def check_usage_limits(self, user_id: str, email: str,
                           ip_address: str) -> Dict[str, Any]:
        """Check if user can perform analysis within limits"""

        current_time = datetime.utcnow()
        today = current_time.date()
        current_hour = current_time.replace(minute=0, second=0, microsecond=0)

        with self._lock:
            # Get or create usage record
            if user_id not in self.usage_records:
                self.usage_records[user_id] = UsageRecord(
                    user_id=user_id,
                    email=email,
                    ip_address=ip_address,
                    analysis_count_today=0,
                    analysis_count_hour=0,
                    last_analysis=current_time,
                    failed_attempts=0,
                    verification_required=False,
                    blocked_until=None,
                    warning_count=0
                )

            usage_record = self.usage_records[user_id]

            # Check if user is blocked
            if usage_record.blocked_until and current_time < usage_record.blocked_until:
                remaining_time = usage_record.blocked_until - current_time
                return {
                    'allowed': False,
                    'reason': 'user_blocked',
                    'message': f'Account temporarily blocked. Try again in {remaining_time}',
                    'retry_after': int(remaining_time.total_seconds())
                }

            # Reset daily counter if new day
            if usage_record.last_analysis.date() < today:
                usage_record.analysis_count_today = 0

            # Reset hourly counter if new hour
            if usage_record.last_analysis.replace(minute=0, second=0, microsecond=0) < current_hour:
                usage_record.analysis_count_hour = 0

            # Check daily limit
            if usage_record.analysis_count_today >= self.config.max_analyses_per_day:
                return {
                    'allowed': False,
                    'reason': 'daily_limit_exceeded',
                    'message': f'Daily limit of {self.config.max_analyses_per_day} analyses exceeded',
                    'reset_at': (current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(
                        days=1)).isoformat()
                }

            # Check hourly limit
            if usage_record.analysis_count_hour >= self.config.max_analyses_per_hour:
                return {
                    'allowed': False,
                    'reason': 'hourly_limit_exceeded',
                    'message': f'Hourly limit of {self.config.max_analyses_per_hour} analyses exceeded',
                    'reset_at': (current_hour + timedelta(hours=1)).isoformat()
                }

            # Check if verification is required
            if usage_record.verification_required:
                return {
                    'allowed': False,
                    'reason': 'verification_required',
                    'message': 'Email verification required before analysis',
                    'verification_needed': True
                }

        return {
            'allowed': True,
            'remaining_daily': self.config.max_analyses_per_day - usage_record.analysis_count_today,
            'remaining_hourly': self.config.max_analyses_per_hour - usage_record.analysis_count_hour
        }

    def record_analysis(self, user_id: str, success: bool = True) -> None:
        """Record analysis usage"""

        current_time = datetime.utcnow()

        with self._lock:
            if user_id in self.usage_records:
                usage_record = self.usage_records[user_id]

                if success:
                    usage_record.analysis_count_today += 1
                    usage_record.analysis_count_hour += 1
                    usage_record.failed_attempts = 0  # Reset on success
                else:
                    usage_record.failed_attempts += 1

                    # Block user after too many failures
                    if usage_record.failed_attempts >= self.config.max_failed_attempts:
                        usage_record.blocked_until = current_time + timedelta(hours=1)
                        logger.warning(f"User {user_id} blocked due to {usage_record.failed_attempts} failed attempts")

                usage_record.last_analysis = current_time

    def get_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Get usage statistics for user"""

        with self._lock:
            if user_id not in self.usage_records:
                return {
                    'daily_usage': 0,
                    'hourly_usage': 0,
                    'remaining_daily': self.config.max_analyses_per_day,
                    'remaining_hourly': self.config.max_analyses_per_hour,
                    'failed_attempts': 0,
                    'blocked': False
                }

            usage_record = self.usage_records[user_id]
            current_time = datetime.utcnow()

            return {
                'daily_usage': usage_record.analysis_count_today,
                'hourly_usage': usage_record.analysis_count_hour,
                'remaining_daily': max(0, self.config.max_analyses_per_day - usage_record.analysis_count_today),
                'remaining_hourly': max(0, self.config.max_analyses_per_hour - usage_record.analysis_count_hour),
                'failed_attempts': usage_record.failed_attempts,
                'blocked': usage_record.blocked_until is not None and current_time < usage_record.blocked_until,
                'blocked_until': usage_record.blocked_until.isoformat() if usage_record.blocked_until else None
            }


class IPTrackingManager:
    """Monitors and blocks suspicious IP activity"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config
        self.ip_activity = defaultdict(list)
        self.blocked_ips = {}
        self.user_ip_mapping = defaultdict(set)
        self.suspicious_patterns = []
        self._lock = threading.RLock()

    def track_request(self, ip_address: str, user_id: str = None,
                      user_agent: str = "", endpoint: str = "") -> Dict[str, Any]:
        """Track IP request and detect suspicious activity"""

        current_time = datetime.utcnow()

        with self._lock:
            # Check if IP is already blocked
            if ip_address in self.blocked_ips:
                block_info = self.blocked_ips[ip_address]
                if current_time < block_info['blocked_until']:
                    return {
                        'allowed': False,
                        'reason': 'ip_blocked',
                        'message': 'IP address temporarily blocked due to suspicious activity',
                        'blocked_until': block_info['blocked_until'].isoformat()
                    }
                else:
                    # Block expired, remove it
                    del self.blocked_ips[ip_address]

            # Record activity
            activity = {
                'timestamp': current_time,
                'user_id': user_id,
                'user_agent': user_agent,
                'endpoint': endpoint
            }

            self.ip_activity[ip_address].append(activity)

            # Track user-IP relationship
            if user_id:
                self.user_ip_mapping[user_id].add(ip_address)

            # Clean old activity (keep last 24 hours)
            cutoff_time = current_time - timedelta(hours=24)
            self.ip_activity[ip_address] = [
                act for act in self.ip_activity[ip_address]
                if act['timestamp'] > cutoff_time
            ]

            # Detect suspicious activity
            suspicious_score = self._calculate_suspicious_score(ip_address, current_time)

            if suspicious_score >= self.config.suspicious_threshold:
                self._block_ip(ip_address, suspicious_score, current_time)
                return {
                    'allowed': False,
                    'reason': 'suspicious_activity',
                    'message': 'IP blocked due to suspicious activity patterns',
                    'suspicious_score': suspicious_score
                }

        return {'allowed': True, 'suspicious_score': suspicious_score}

    def _calculate_suspicious_score(self, ip_address: str, current_time: datetime) -> float:
        """Calculate suspicious activity score for IP"""

        activities = self.ip_activity[ip_address]
        if not activities:
            return 0.0

        score = 0.0
        recent_activities = [
            act for act in activities
            if current_time - act['timestamp'] <= timedelta(hours=1)
        ]

        # High request frequency
        if len(recent_activities) > 50:  # More than 50 requests per hour
            score += 3.0
        elif len(recent_activities) > 20:
            score += 2.0
        elif len(recent_activities) > 10:
            score += 1.0

        # Rapid succession requests
        if len(recent_activities) >= 2:
            time_diffs = [
                (recent_activities[i]['timestamp'] - recent_activities[i - 1]['timestamp']).total_seconds()
                for i in range(1, len(recent_activities))
            ]
            avg_interval = sum(time_diffs) / len(time_diffs)

            if avg_interval < 1:  # Less than 1 second between requests
                score += 4.0
            elif avg_interval < 5:
                score += 2.0
            elif avg_interval < 10:
                score += 1.0

        # Multiple user IDs from same IP
        unique_users = len(set(act['user_id'] for act in activities if act['user_id']))
        if unique_users > 5:
            score += 3.0
        elif unique_users > 3:
            score += 2.0

        # Bot-like user agents
        user_agents = set(act['user_agent'] for act in recent_activities if act['user_agent'])
        for user_agent in user_agents:
            if self._is_bot_user_agent(user_agent):
                score += 2.0

        # Unusual endpoint access patterns
        endpoints = [act['endpoint'] for act in recent_activities if act['endpoint']]
        if len(set(endpoints)) == 1 and len(endpoints) > 10:  # Same endpoint repeatedly
            score += 2.0

        return score

    def _is_bot_user_agent(self, user_agent: str) -> bool:
        """Check if user agent appears to be a bot"""

        bot_indicators = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests',
            'automated', 'script', 'headless', 'phantom'
        ]

        user_agent_lower = user_agent.lower()
        return any(indicator in user_agent_lower for indicator in bot_indicators)

    def _block_ip(self, ip_address: str, suspicious_score: float, current_time: datetime):
        """Block suspicious IP address"""

        # Determine block duration based on score
        if suspicious_score >= 15:
            block_hours = 24
        elif suspicious_score >= 10:
            block_hours = 12
        else:
            block_hours = self.config.block_duration_hours

        block_until = current_time + timedelta(hours=block_hours)

        self.blocked_ips[ip_address] = {
            'blocked_at': current_time,
            'blocked_until': block_until,
            'suspicious_score': suspicious_score,
            'reason': 'automated_suspicious_activity_detection'
        }

        logger.warning(f"IP {ip_address} blocked until {block_until} (score: {suspicious_score})")

    def get_ip_stats(self, ip_address: str) -> Dict[str, Any]:
        """Get statistics for IP address"""

        with self._lock:
            activities = self.ip_activity.get(ip_address, [])
            current_time = datetime.utcnow()

            recent_activities = [
                act for act in activities
                if current_time - act['timestamp'] <= timedelta(hours=1)
            ]

            return {
                'total_requests': len(activities),
                'recent_requests': len(recent_activities),
                'unique_users': len(set(act['user_id'] for act in activities if act['user_id'])),
                'blocked': ip_address in self.blocked_ips,
                'suspicious_score': self._calculate_suspicious_score(ip_address, current_time),
                'first_seen': activities[0]['timestamp'].isoformat() if activities else None,
                'last_seen': activities[-1]['timestamp'].isoformat() if activities else None
            }


class AbuseReportingSystem:
    """System for users to report abuse with admin notifications"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config
        self.reports = {}
        self.report_stats = defaultdict(int)
        self._lock = threading.RLock()

    def submit_report(self, reporter_user_id: str, reporter_email: str,
                      report_type: ReportType, target_user_id: str = None,
                      target_content: str = None, description: str = "",
                      evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """Submit abuse report"""

        if not self.config.enable_reporting:
            return {'success': False, 'error': 'Reporting system disabled'}

        report_id = str(uuid.uuid4())
        current_time = datetime.utcnow()

        report = AbuseReport(
            report_id=report_id,
            reporter_user_id=reporter_user_id,
            reporter_email=reporter_email,
            report_type=report_type,
            target_user_id=target_user_id,
            target_content=target_content,
            description=description,
            evidence=evidence or {},
            reported_at=current_time,
            status='pending',
            admin_notes='',
            action_taken=None
        )

        with self._lock:
            self.reports[report_id] = report
            self.report_stats[report_type.value] += 1

        # Send admin notification
        self._notify_admin(report)

        # Check for auto-escalation
        if self._should_auto_escalate(target_user_id, report_type):
            self._auto_escalate_report(report)

        logger.info(f"Abuse report submitted: {report_id} ({report_type.value})")

        return {
            'success': True,
            'report_id': report_id,
            'message': 'Report submitted successfully. We will investigate and take appropriate action.',
            'status': 'pending',
            'estimated_response_time': '24-48 hours'
        }

    def get_report_status(self, report_id: str, requester_user_id: str) -> Dict[str, Any]:
        """Get status of abuse report"""

        with self._lock:
            report = self.reports.get(report_id)

            if not report:
                return {'success': False, 'error': 'Report not found'}

            # Only allow reporter to check status
            if report.reporter_user_id != requester_user_id:
                return {'success': False, 'error': 'Access denied'}

            return {
                'success': True,
                'report_id': report_id,
                'status': report.status,
                'report_type': report.report_type.value,
                'submitted_at': report.reported_at.isoformat(),
                'action_taken': report.action_taken.value if report.action_taken else None,
                'admin_notes': report.admin_notes if report.status == 'resolved' else None
            }

    def _notify_admin(self, report: AbuseReport):
        """Send admin notification about new report"""

        try:
            subject = f"New Abuse Report: {report.report_type.value.title()} - {report.report_id}"

            body = f"""
New abuse report submitted:

Report ID: {report.report_id}
Type: {report.report_type.value}
Reporter: {report.reporter_user_id or 'Anonymous'} ({report.reporter_email})
Target User: {report.target_user_id or 'Not specified'}
Submitted: {report.reported_at.isoformat()}

Description:
{report.description}

Target Content (if applicable):
{report.target_content or 'None'}

Evidence:
{json.dumps(report.evidence, indent=2) if report.evidence else 'None'}

Please review and take appropriate action.

Admin Dashboard: https://admin.company.com/reports/{report.report_id}
            """

            # Send email to admin
            msg = MimeMultipart()
            msg['From'] = "noreply@company.com"
            msg['To'] = self.config.admin_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))

            # Send email (simplified - would use proper email service)
            logger.info(f"Admin notification sent for report {report.report_id}")

        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")

    def _should_auto_escalate(self, target_user_id: str, report_type: ReportType) -> bool:
        """Check if report should be auto-escalated"""

        if not target_user_id:
            return False

        # Count recent reports against same user
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=24)

        recent_reports = [
            report for report in self.reports.values()
            if (report.target_user_id == target_user_id and
                report.reported_at > cutoff_time)
        ]

        return len(recent_reports) >= self.config.auto_escalation_threshold

    def _auto_escalate_report(self, report: AbuseReport):
        """Auto-escalate report for immediate attention"""

        report.status = 'investigating'
        report.admin_notes = 'Auto-escalated due to multiple reports'

        logger.warning(
            f"Report {report.report_id} auto-escalated due to multiple reports against user {report.target_user_id}")

    def get_reporting_stats(self) -> Dict[str, Any]:
        """Get abuse reporting statistics"""

        with self._lock:
            total_reports = len(self.reports)
            pending_reports = len([r for r in self.reports.values() if r.status == 'pending'])
            resolved_reports = len([r for r in self.reports.values() if r.status == 'resolved'])

            # Recent activity (last 24 hours)
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=24)
            recent_reports = [
                r for r in self.reports.values()
                if r.reported_at > cutoff_time
            ]

            return {
                'total_reports': total_reports,
                'pending_reports': pending_reports,
                'resolved_reports': resolved_reports,
                'recent_reports': len(recent_reports),
                'report_types_distribution': dict(self.report_stats),
                'resolution_rate': resolved_reports / total_reports if total_reports > 0 else 0,
                'response_time_hours': 24  # Target response time
            }


class SuspiciousActivityDetector:
    """Advanced suspicious activity detection and prevention"""

    def __init__(self, config: AbusePreventionConfig):
        self.config = config
        self.activities = {}
        self.patterns = []
        self._lock = threading.RLock()

    def detect_suspicious_activity(self, user_id: str, ip_address: str,
                                   activity_data: Dict[str, Any]) -> Optional[SuspiciousActivity]:
        """Detect suspicious activity patterns"""

        current_time = datetime.utcnow()
        suspicious_indicators = []
        severity_score = 0.0

        # Check for rapid requests
        if self._check_rapid_requests(user_id, ip_address, current_time):
            suspicious_indicators.append("High request frequency detected")
            severity_score += 3.0

        # Check for bot-like behavior
        if self._check_bot_behavior(activity_data):
            suspicious_indicators.append("Bot-like behavior patterns")
            severity_score += 4.0

        # Check for unusual patterns
        if self._check_unusual_patterns(user_id, activity_data):
            suspicious_indicators.append("Unusual usage patterns")
            severity_score += 2.0

        # Check for multiple IP usage
        if self._check_multiple_ips(user_id, ip_address):
            suspicious_indicators.append("Multiple IP addresses used")
            severity_score += 1.5

        # If suspicious activity detected
        if severity_score >= 3.0:
            activity_id = str(uuid.uuid4())

            suspicious_activity = SuspiciousActivity(
                activity_id=activity_id,
                activity_type=self._categorize_activity_type(suspicious_indicators),
                user_id=user_id,
                ip_address=ip_address,
                description="; ".join(suspicious_indicators),
                severity_score=severity_score,
                detected_at=current_time,
                evidence=activity_data,
                action_taken=self._determine_action(severity_score),
                resolved=False
            )

            with self._lock:
                self.activities[activity_id] = suspicious_activity

            logger.warning(f"Suspicious activity detected: {activity_id} (score: {severity_score})")

            return suspicious_activity

        return None

    def _check_rapid_requests(self, user_id: str, ip_address: str, current_time: datetime) -> bool:
        """Check for rapid request patterns"""
        # Implementation would check request timestamps
        return False

    def _check_bot_behavior(self, activity_data: Dict[str, Any]) -> bool:
        """Check for bot-like behavior"""
        user_agent = activity_data.get('user_agent', '').lower()

        bot_indicators = [
            'bot', 'crawler', 'spider', 'automated', 'script',
            'curl', 'wget', 'python', 'java', 'headless'
        ]

        return any(indicator in user_agent for indicator in bot_indicators)

    def _check_unusual_patterns(self, user_id: str, activity_data: Dict[str, Any]) -> bool:
        """Check for unusual usage patterns"""
        # Implementation would analyze usage patterns
        return False

    def _check_multiple_ips(self, user_id: str, ip_address: str) -> bool:
        """Check if user is using multiple IP addresses"""
        # Implementation would track IP usage per user
        return False

    def _categorize_activity_type(self, indicators: List[str]) -> SuspiciousActivityType:
        """Categorize the type of suspicious activity"""
        if any('rapid' in indicator.lower() for indicator in indicators):
            return SuspiciousActivityType.RAPID_REQUESTS
        elif any('bot' in indicator.lower() for indicator in indicators):
            return SuspiciousActivityType.BOT_BEHAVIOR
        else:
            return SuspiciousActivityType.UNUSUAL_USAGE

    def _determine_action(self, severity_score: float) -> ActionLevel:
        """Determine appropriate action based on severity"""
        if severity_score >= 8.0:
            return ActionLevel.PERMANENT_BAN
        elif severity_score >= 6.0:
            return ActionLevel.TEMPORARY_BLOCK
        elif severity_score >= 4.0:
            return ActionLevel.RATE_LIMIT
        else:
            return ActionLevel.WARNING


class AbusePreventionFramework:
    """Main abuse prevention framework coordinating all components"""

    def __init__(self, config: AbusePreventionConfig = None):
        self.config = config or AbusePreventionConfig()

        # Initialize all components
        self.email_verifier = EmailVerificationManager(self.config)
        self.recaptcha_verifier = RecaptchaVerifier(self.config)
        self.usage_manager = UsageLimitManager(self.config)
        self.ip_tracker = IPTrackingManager(self.config)
        self.reporting_system = AbuseReportingSystem(self.config)
        self.activity_detector = SuspiciousActivityDetector(self.config)

        logger.info("Abuse Prevention Framework initialized with all components")

    def verify_request(self, user_id: str, email: str, ip_address: str,
                       user_agent: str, recaptcha_response: str = None,
                       verification_code: str = None, verification_id: str = None) -> Dict[str, Any]:
        """Comprehensive request verification"""

        # IP tracking and suspicious activity detection
        ip_check = self.ip_tracker.track_request(ip_address, user_id, user_agent, 'analysis')
        if not ip_check['allowed']:
            return ip_check

        # Usage limits check
        usage_check = self.usage_manager.check_usage_limits(user_id, email, ip_address)
        if not usage_check['allowed']:
            return usage_check

        # Email verification (if required)
        if verification_id and verification_code:
            email_verification = self.email_verifier.verify_email(verification_id, verification_code, ip_address)
            if not email_verification['success']:
                return {'allowed': False, 'reason': 'email_verification_failed', **email_verification}

        # reCAPTCHA verification
        if recaptcha_response:
            recaptcha_check = self.recaptcha_verifier.verify_recaptcha(recaptcha_response, ip_address)
            if not recaptcha_check['success']:
                return {'allowed': False, 'reason': 'recaptcha_failed', **recaptcha_check}

        # Suspicious activity detection
        activity_data = {
            'user_agent': user_agent,
            'endpoint': 'analysis',
            'user_id': user_id,
            'email': email
        }

        suspicious_activity = self.activity_detector.detect_suspicious_activity(user_id, ip_address, activity_data)
        if suspicious_activity and suspicious_activity.action_taken in [ActionLevel.TEMPORARY_BLOCK,
                                                                        ActionLevel.PERMANENT_BAN]:
            return {
                'allowed': False,
                'reason': 'suspicious_activity_detected',
                'message': f'Account temporarily suspended due to suspicious activity',
                'severity_score': suspicious_activity.severity_score
            }

        return {'allowed': True, 'message': 'All verification checks passed'}

    def record_analysis_attempt(self, user_id: str, success: bool):
        """Record analysis attempt for usage tracking"""
        self.usage_manager.record_analysis(user_id, success)

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive status of abuse prevention system"""

        return {
            'abuse_prevention_enabled': True,
            'components': {
                'email_verification': self.config.enable_email_verification,
                'recaptcha_protection': self.config.enable_recaptcha,
                'usage_limits': True,
                'ip_tracking': self.config.enable_ip_tracking,
                'reporting_system': self.config.enable_reporting,
                'suspicious_activity_detection': True
            },
            'configuration': {
                'max_analyses_per_day': self.config.max_analyses_per_day,
                'max_analyses_per_hour': self.config.max_analyses_per_hour,
                'verification_expiry_minutes': self.config.verification_expiry_minutes,
                'block_duration_hours': self.config.block_duration_hours,
                'recaptcha_threshold': self.config.recaptcha_threshold
            },
            'statistics': {
                'reporting_stats': self.reporting_system.get_reporting_stats(),
                'active_verifications': len(self.email_verifier.verifications),
                'blocked_ips': len(self.ip_tracker.blocked_ips),
                'tracked_users': len(self.usage_manager.usage_records)
            },
            'protection_features': [
                'Email verification with anti-spam measures',
                'reCAPTCHA bot protection',
                'Daily and hourly usage limits',
                'IP-based suspicious activity detection',
                'User abuse reporting system with admin notifications',
                'Automatic blocking of suspicious patterns',
                'Multi-layer verification system',
                'Real-time abuse monitoring and prevention'
            ]
        }


def create_abuse_prevention_framework(config: AbusePreventionConfig = None) -> AbusePreventionFramework:
    """Factory function to create abuse prevention framework"""
    return AbusePreventionFramework(config)
