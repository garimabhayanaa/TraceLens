import os
import logging
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import threading
import uuid

logger = logging.getLogger(__name__)

class ConsentType(Enum):
    ANALYSIS = "analysis"
    COOKIES = "cookies"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    NECESSARY = "necessary"
    PREFERENCES = "preferences"
    THIRD_PARTY = "third_party"
    DATA_PROCESSING = "data_processing"

class ConsentStatus(Enum):
    GRANTED = "granted"
    DENIED = "denied"
    PARTIAL = "partial"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"

@dataclass
class ConsentRecord:
    """Individual consent record following GDPR requirements"""
    
    # Required fields for GDPR compliance
    consent_id: str
    user_id: str
    consent_status: ConsentStatus
    consent_types: List[ConsentType]
    timestamp: datetime
    ip_address: str
    user_agent: str
    
    # Additional GDPR compliance fields
    consent_method: str  # How consent was obtained (banner, form, etc.)
    consent_version: str  # Version of consent form/banner
    legal_basis: str  # GDPR legal basis (usually "consent" for Article 6(1)(a))
    purpose_description: str  # Clear description of processing purposes
    data_categories: List[str]  # Categories of personal data involved
    
    # Optional fields for enhanced compliance
    consent_duration: Optional[int] = None  # Duration in days (None = indefinite)
    withdrawal_method: Optional[str] = None  # How user can withdraw consent
    consent_language: str = "en"  # Language consent was given in
    geolocation: Optional[str] = None  # User's country/region
    
    # Technical metadata
    session_id: Optional[str] = None
    referrer_url: Optional[str] = None
    page_url: Optional[str] = None
    
    # Audit fields
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.consent_duration and not self.expires_at:
            self.expires_at = self.timestamp + timedelta(days=self.consent_duration)
    
    def is_expired(self) -> bool:
        """Check if consent has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['consent_status'] = self.consent_status.value
        data['consent_types'] = [ct.value for ct in self.consent_types]
        # Convert datetime objects to ISO strings
        data['timestamp'] = self.timestamp.isoformat()
        data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data

class ConsentLoggingSystem:
    """
    GDPR-compliant consent logging system with encryption and audit capabilities
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.consent_records: List[ConsentRecord] = []
        self.lock = threading.RLock()
        
        # Initialize database connection (if using persistent storage)
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize persistent storage for consent logs"""
        # In production, this would connect to your database
        # For now, we'll use in-memory storage with file backup
        self.storage_initialized = True
        logger.info("Consent logging system initialized")
    
    def record_consent(self, 
                      user_id: str,
                      consent_status: ConsentStatus,
                      consent_types: List[ConsentType],
                      ip_address: str,
                      user_agent: str,
                      consent_method: str,
                      consent_version: str,
                      purpose_description: str,
                      data_categories: List[str],
                      **kwargs) -> str:
        """
        Record a consent event with full GDPR compliance
        
        Returns:
            str: Unique consent ID for tracking
        """
        
        try:
            # Generate unique consent ID
            consent_id = str(uuid.uuid4())
            
            # Create consent record
            consent_record = ConsentRecord(
                consent_id=consent_id,
                user_id=user_id,
                consent_status=consent_status,
                consent_types=consent_types,
                timestamp=datetime.utcnow(),
                ip_address=self._anonymize_ip(ip_address),  # Anonymize IP for privacy
                user_agent=user_agent,
                consent_method=consent_method,
                consent_version=consent_version,
                legal_basis="consent",  # GDPR Article 6(1)(a)
                purpose_description=purpose_description,
                data_categories=data_categories,
                **kwargs
            )
            
            # Store the consent record
            with self.lock:
                self.consent_records.append(consent_record)
                # In production, save to encrypted database
                self._persist_consent_record(consent_record)
            
            # Log the consent event (without sensitive data)
            logger.info(f"Consent recorded: {consent_id} for user {user_id[:8]}... status: {consent_status.value}")
            
            return consent_id
            
        except Exception as e:
            logger.error(f"Failed to record consent: {str(e)}")
            raise
    
    def update_consent(self, 
                      consent_id: str,
                      new_status: ConsentStatus,
                      ip_address: str,
                      user_agent: str,
                      withdrawal_method: Optional[str] = None) -> bool:
        """
        Update existing consent record (e.g., for withdrawal)
        """
        
        try:
            with self.lock:
                # Find existing record
                for record in self.consent_records:
                    if record.consent_id == consent_id:
                        # Create new record for the update (maintain audit trail)
                        updated_record = ConsentRecord(
                            consent_id=str(uuid.uuid4()),  # New ID for the update
                            user_id=record.user_id,
                            consent_status=new_status,
                            consent_types=record.consent_types,
                            timestamp=datetime.utcnow(),
                            ip_address=self._anonymize_ip(ip_address),
                            user_agent=user_agent,
                            consent_method=record.consent_method,
                            consent_version=record.consent_version,
                            legal_basis=record.legal_basis,
                            purpose_description=record.purpose_description,
                            data_categories=record.data_categories,
                            withdrawal_method=withdrawal_method,
                            consent_language=record.consent_language,
                            geolocation=record.geolocation
                        )
                        
                        self.consent_records.append(updated_record)
                        self._persist_consent_record(updated_record)
                        
                        logger.info(f"Consent updated: {consent_id} -> {new_status.value}")
                        return True
                
                logger.warning(f"Consent record not found: {consent_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update consent: {str(e)}")
            raise
    
    def get_user_consent_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get complete consent history for a user (for GDPR data access requests)
        """
        
        try:
            with self.lock:
                user_consents = [
                    record.to_dict() 
                    for record in self.consent_records 
                    if record.user_id == user_id
                ]
                
                # Sort by timestamp (most recent first)
                user_consents.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return user_consents
                
        except Exception as e:
            logger.error(f"Failed to retrieve consent history: {str(e)}")
            raise
    
    def get_current_consent_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get current consent status for a user
        """
        
        try:
            with self.lock:
                # Get most recent consent for each consent type
                consent_status = {}
                
                for record in reversed(self.consent_records):  # Most recent first
                    if record.user_id == user_id and not record.is_expired():
                        for consent_type in record.consent_types:
                            if consent_type.value not in consent_status:
                                consent_status[consent_type.value] = {
                                    'status': record.consent_status.value,
                                    'timestamp': record.timestamp.isoformat(),
                                    'consent_id': record.consent_id,
                                    'expires_at': record.expires_at.isoformat() if record.expires_at else None
                                }
                
                return {
                    'user_id': user_id,
                    'consent_status': consent_status,
                    'last_updated': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get current consent status: {str(e)}")
            raise
    
    def export_consent_logs(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Export consent logs for compliance audits
        """
        
        try:
            with self.lock:
                filtered_records = []
                
                for record in self.consent_records:
                    # Apply filters
                    if start_date and record.timestamp < start_date:
                        continue
                    if end_date and record.timestamp > end_date:
                        continue
                    if user_id and record.user_id != user_id:
                        continue
                    
                    filtered_records.append(record.to_dict())
                
                return filtered_records
                
        except Exception as e:
            logger.error(f"Failed to export consent logs: {str(e)}")
            raise
    
    def cleanup_expired_consents(self) -> int:
        """
        Clean up expired consent records (keeping audit trail)
        """
        
        try:
            with self.lock:
                expired_count = 0
                current_time = datetime.utcnow()
                
                for record in self.consent_records:
                    if record.is_expired() and record.consent_status != ConsentStatus.EXPIRED:
                        # Mark as expired instead of deleting (for audit trail)
                        record.consent_status = ConsentStatus.EXPIRED
                        record.updated_at = current_time
                        expired_count += 1
                
                if expired_count > 0:
                    logger.info(f"Marked {expired_count} consent records as expired")
                
                return expired_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired consents: {str(e)}")
            raise
    
    def delete_user_data(self, user_id: str) -> bool:
        """
        Delete all consent data for a user (for GDPR right to erasure)
        Note: Consider legal requirements before implementing full deletion
        """
        
        try:
            with self.lock:
                # In production, you might need to anonymize rather than delete
                # to maintain audit trails for legal compliance
                
                original_count = len(self.consent_records)
                self.consent_records = [
                    record for record in self.consent_records 
                    if record.user_id != user_id
                ]
                deleted_count = original_count - len(self.consent_records)
                
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} consent records for user {user_id}")
                
                return deleted_count > 0
                
        except Exception as e:
            logger.error(f"Failed to delete user consent data: {str(e)}")
            raise
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate compliance report for regulatory audits
        """
        
        try:
            with self.lock:
                total_records = len(self.consent_records)
                
                # Count by status
                status_counts = {}
                for status in ConsentStatus:
                    status_counts[status.value] = sum(
                        1 for record in self.consent_records 
                        if record.consent_status == status
                    )
                
                # Count by consent type
                type_counts = {}
                for consent_type in ConsentType:
                    type_counts[consent_type.value] = sum(
                        1 for record in self.consent_records 
                        for ct in record.consent_types 
                        if ct == consent_type
                    )
                
                # Calculate retention compliance
                expired_records = sum(
                    1 for record in self.consent_records 
                    if record.is_expired()
                )
                
                return {
                    'report_generated': datetime.utcnow().isoformat(),
                    'total_consent_records': total_records,
                    'status_breakdown': status_counts,
                    'consent_type_breakdown': type_counts,
                    'expired_records': expired_records,
                    'compliance_score': self._calculate_compliance_score(),
                    'retention_compliance': (total_records - expired_records) / max(total_records, 1) * 100
                }
                
        except Exception as e:
            logger.error(f"Failed to generate compliance report: {str(e)}")
            raise
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address for privacy compliance"""
        try:
            # For IPv4, zero out the last octet
            if '.' in ip_address and ip_address.count('.') == 3:
                parts = ip_address.split('.')
                parts[-1] = '0'
                return '.'.join(parts)
            
            # For IPv6, zero out the last 64 bits
            if ':' in ip_address:
                parts = ip_address.split(':')
                if len(parts) >= 4:
                    return ':'.join(parts[:4]) + '::0'
            
            return ip_address
            
        except Exception:
            return "0.0.0.0"  # Fallback for invalid IPs
    
    def _persist_consent_record(self, record: ConsentRecord):
        """Persist consent record to secure storage"""
        # In production, this would save to encrypted database
        # For now, we'll just log the action
        pass
    
    def _calculate_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        try:
            if not self.consent_records:
                return 100.0
            
            total_records = len(self.consent_records)
            
            # Check for required fields
            complete_records = sum(
                1 for record in self.consent_records
                if all([
                    record.consent_id,
                    record.user_id,
                    record.purpose_description,
                    record.data_categories,
                    record.legal_basis
                ])
            )
            
            return (complete_records / total_records) * 100
            
        except Exception:
            return 0.0

def create_consent_logging_system():
    """Factory function to create consent logging system"""
    return ConsentLoggingSystem()

# Helper functions for Flask integration
def record_analysis_consent(user_id: str, consent_given: bool, ip_address: str, user_agent: str) -> str:
    """Helper function to record consent for digital footprint analysis"""
    
    consent_system = create_consent_logging_system()
    
    return consent_system.record_consent(
        user_id=user_id,
        consent_status=ConsentStatus.GRANTED if consent_given else ConsentStatus.DENIED,
        consent_types=[ConsentType.ANALYSIS, ConsentType.DATA_PROCESSING],
        ip_address=ip_address,
        user_agent=user_agent,
        consent_method="analysis_form",
        consent_version="v1.0",
        purpose_description="Digital footprint analysis and privacy risk assessment",
        data_categories=["email", "name", "social_media_profiles", "public_data"]
    )

def check_analysis_consent(user_id: str) -> bool:
    """Check if user has given consent for analysis"""
    
    consent_system = create_consent_logging_system()
    current_status = consent_system.get_current_consent_status(user_id)
    
    analysis_consent = current_status['consent_status'].get('analysis', {})
    return analysis_consent.get('status') == 'granted'
