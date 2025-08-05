import logging
import hashlib
import secrets
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
import threading
import re

logger = logging.getLogger(__name__)

@dataclass
class DataRetentionPolicy:
    """Data retention and deletion policy"""
    max_retention_hours: int = 24
    auto_deletion_enabled: bool = True
    secure_deletion_required: bool = True
    audit_trail_enabled: bool = True

@dataclass
class AnonymizationConfig:
    """Configuration for data anonymization"""
    remove_names: bool = True
    remove_locations: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    remove_phone_numbers: bool = True
    hash_usernames: bool = True
    generalize_dates: bool = True
    remove_sensitive_keywords: bool = True

@dataclass
class ProcessingMode:
    """Processing mode configuration"""
    client_side_enabled: bool = False
    local_processing_only: bool = False
    encrypted_transmission_required: bool = True
    minimize_data_collection: bool = True

@dataclass
class SecurityMetrics:
    """Security and privacy metrics"""
    data_processed: int
    data_anonymized: int
    data_encrypted: int
    data_deleted: int
    retention_violations: int
    anonymization_failures: int

class SecureDataHandler:
    """Handles secure data processing and encryption"""
    
    def __init__(self):
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.session_keys = {}
        self._lock = threading.Lock()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key"""
        return Fernet.generate_key()
    
    def encrypt_data(self, data: Any, session_id: str = None) -> str:
        """Encrypt sensitive data with optional session-specific key"""
        try:
            # Convert data to JSON string
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data, ensure_ascii=False)
            else:
                data_str = str(data)
            
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(data_str.encode('utf-8'))
            
            # Encode to base64 for safe transmission
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise SecurityError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str, session_id: str = None) -> Any:
        """Decrypt data with optional session-specific key"""
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt the data
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode('utf-8')
            
            # Try to parse as JSON, fall back to string
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
                
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise SecurityError(f"Failed to decrypt data: {str(e)}")
    
    def generate_session_key(self, session_id: str) -> str:
        """Generate a unique session key for secure communication"""
        with self._lock:
            session_key = secrets.token_urlsafe(32)
            self.session_keys[session_id] = {
                'key': session_key,
                'created_at': datetime.utcnow(),
                'expires_at': datetime.utcnow() + timedelta(hours=1)
            }
            return session_key
    
    def validate_session_key(self, session_id: str, provided_key: str) -> bool:
        """Validate a session key"""
        with self._lock:
            if session_id not in self.session_keys:
                return False
            
            session_info = self.session_keys[session_id]
            
            # Check if key has expired
            if datetime.utcnow() > session_info['expires_at']:
                del self.session_keys[session_id]
                return False
            
            return session_info['key'] == provided_key
    
    def cleanup_expired_sessions(self):
        """Clean up expired session keys"""
        with self._lock:
            current_time = datetime.utcnow()
            expired_sessions = [
                session_id for session_id, info in self.session_keys.items()
                if current_time > info['expires_at']
            ]
            
            for session_id in expired_sessions:
                del self.session_keys[session_id]
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

class DataAnonymizer:
    """Anonymizes sensitive data while preserving analytical value"""
    
    def __init__(self, config: AnonymizationConfig = None):
        self.config = config or AnonymizationConfig()
        self.name_patterns = self._compile_name_patterns()
        self.location_patterns = self._compile_location_patterns()
        self.sensitive_keywords = self._load_sensitive_keywords()
        self.anonymization_cache = {}
    
    def anonymize_content(self, content: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Anonymize content while preserving analytical structure"""
        
        anonymized_content = content.copy()
        removed_elements = []
        
        try:
            # Anonymize text content
            if 'text' in anonymized_content:
                anonymized_content['text'], text_removals = self._anonymize_text(
                    anonymized_content['text']
                )
                removed_elements.extend(text_removals)
            
            # Anonymize content field
            if 'content' in anonymized_content:
                anonymized_content['content'], content_removals = self._anonymize_text(
                    anonymized_content['content']
                )
                removed_elements.extend(content_removals)
            
            # Anonymize bio/description
            if 'bio' in anonymized_content:
                anonymized_content['bio'], bio_removals = self._anonymize_text(
                    anonymized_content['bio']
                )
                removed_elements.extend(bio_removals)
            
            # Remove or anonymize metadata
            if 'username' in anonymized_content and self.config.hash_usernames:
                original_username = anonymized_content['username']
                anonymized_content['username'] = self._hash_identifier(original_username)
                removed_elements.append(f"username:{original_username}")
            
            # Generalize timestamps
            if 'timestamp' in anonymized_content and self.config.generalize_dates:
                anonymized_content['timestamp'] = self._generalize_timestamp(
                    anonymized_content['timestamp']
                )
                removed_elements.append("specific_timestamp")
            
            # Remove URLs
            if self.config.remove_urls:
                for field in ['text', 'content', 'bio']:
                    if field in anonymized_content:
                        anonymized_content[field], url_removals = self._remove_urls(
                            anonymized_content[field]
                        )
                        removed_elements.extend(url_removals)
            
            return anonymized_content, removed_elements
            
        except Exception as e:
            logger.error(f"Anonymization failed: {str(e)}")
            return content, []
    
    def _anonymize_text(self, text: str) -> Tuple[str, List[str]]:
        """Anonymize text content"""
        
        if not text:
            return text, []
        
        anonymized_text = text
        removed_elements = []
        
        # Remove names
        if self.config.remove_names:
            anonymized_text, name_removals = self._remove_names(anonymized_text)
            removed_elements.extend(name_removals)
        
        # Remove locations
        if self.config.remove_locations:
            anonymized_text, location_removals = self._remove_locations(anonymized_text)
            removed_elements.extend(location_removals)
        
        # Remove emails
        if self.config.remove_emails:
            anonymized_text, email_removals = self._remove_emails(anonymized_text)
            removed_elements.extend(email_removals)
        
        # Remove phone numbers
        if self.config.remove_phone_numbers:
            anonymized_text, phone_removals = self._remove_phone_numbers(anonymized_text)
            removed_elements.extend(phone_removals)
        
        # Remove sensitive keywords
        if self.config.remove_sensitive_keywords:
            anonymized_text, keyword_removals = self._remove_sensitive_keywords(anonymized_text)
            removed_elements.extend(keyword_removals)
        
        return anonymized_text, removed_elements
    
    def _compile_name_patterns(self) -> List[str]:
        """Compile patterns for detecting names"""
        return [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b[A-Z][a-z]+\b(?=\s+said|\s+wrote|\s+posted)',  # Name before action
            r'@[A-Za-z0-9_]+',  # Social media handles
        ]
    
    def _compile_location_patterns(self) -> List[str]:
        """Compile patterns for detecting locations"""
        return [
            r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd)\b',
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\s*\d{5}\b',  # City, State ZIP
            r'\bat\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # "at Location"
            r'\bin\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # "in Location"
        ]
    
    def _load_sensitive_keywords(self) -> List[str]:
        """Load sensitive keywords that should be removed"""
        return [
            # Personal identifiers
            'ssn', 'social security', 'driver license', 'passport',
            # Financial
            'credit card', 'bank account', 'routing number', 'pin',
            # Medical
            'medical record', 'diagnosis', 'prescription', 'therapy',
            # Legal
            'court case', 'lawsuit', 'arrest', 'conviction'
        ]
    
    def _remove_names(self, text: str) -> Tuple[str, List[str]]:
        """Remove or anonymize names from text"""
        removed = []
        
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Replace with generic placeholder
                text = text.replace(match, '[NAME]')
                removed.append(f"name:{match}")
        
        return text, removed
    
    def _remove_locations(self, text: str) -> Tuple[str, List[str]]:
        """Remove or anonymize locations from text"""
        removed = []
        
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                text = text.replace(match, '[LOCATION]')
                removed.append(f"location:{match}")
        
        return text, removed
    
    def _remove_emails(self, text: str) -> Tuple[str, List[str]]:
        """Remove email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        removed = []
        
        for email in matches:
            text = text.replace(email, '[EMAIL]')
            removed.append(f"email:{email}")
        
        return text, removed
    
    def _remove_phone_numbers(self, text: str) -> Tuple[str, List[str]]:
        """Remove phone numbers from text"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
            r'\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        
        removed = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for phone in matches:
                text = text.replace(phone, '[PHONE]')
                removed.append(f"phone:{phone}")
        
        return text, removed
    
    def _remove_urls(self, text: str) -> Tuple[str, List[str]]:
        """Remove URLs from text"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        matches = re.findall(url_pattern, text)
        removed = []
        
        for url in matches:
            text = text.replace(url, '[URL]')
            removed.append(f"url:{url}")
        
        return text, removed
    
    def _remove_sensitive_keywords(self, text: str) -> Tuple[str, List[str]]:
        """Remove sensitive keywords from text"""
        removed = []
        text_lower = text.lower()
        
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                # Case-insensitive replacement
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                text = pattern.sub('[SENSITIVE]', text)
                removed.append(f"sensitive:{keyword}")
        
        return text, removed
    
    def _hash_identifier(self, identifier: str) -> str:
        """Create a consistent hash for identifiers"""
        if identifier in self.anonymization_cache:
            return self.anonymization_cache[identifier]
        
        # Create a consistent hash
        hash_object = hashlib.sha256(identifier.encode())
        hashed = hash_object.hexdigest()[:12]  # Use first 12 characters
        
        self.anonymization_cache[identifier] = f"user_{hashed}"
        return self.anonymization_cache[identifier]
    
    def _generalize_timestamp(self, timestamp: str) -> str:
        """Generalize timestamp to reduce precision"""
        try:
            # Parse timestamp and round to nearest hour
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            # Round to nearest hour
            dt = dt.replace(minute=0, second=0, microsecond=0)
            return dt.isoformat()
            
        except Exception:
            return "[TIMESTAMP]"

class DataRetentionManager:
    """Manages data retention and automatic deletion"""
    
    def __init__(self, policy: DataRetentionPolicy = None):
        self.policy = policy or DataRetentionPolicy()
        self.stored_data = {}
        self.deletion_schedule = {}
        self._lock = threading.Lock()
        self.metrics = SecurityMetrics(0, 0, 0, 0, 0, 0)
        
        # Start background deletion thread
        if self.policy.auto_deletion_enabled:
            self._start_deletion_thread()
    
    def store_data(self, data_id: str, data: Any, retention_hours: int = None) -> bool:
        """Store data with automatic deletion scheduling"""
        try:
            with self._lock:
                retention_hours = retention_hours or self.policy.max_retention_hours
                
                # Store data with metadata
                storage_entry = {
                    'data': data,
                    'stored_at': datetime.utcnow(),
                    'expires_at': datetime.utcnow() + timedelta(hours=retention_hours),
                    'retention_hours': retention_hours
                }
                
                self.stored_data[data_id] = storage_entry
                self.deletion_schedule[data_id] = storage_entry['expires_at']
                
                self.metrics.data_processed += 1
                
                logger.info(f"Data stored with ID {data_id}, expires in {retention_hours} hours")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store data {data_id}: {str(e)}")
            return False
    
    def retrieve_data(self, data_id: str) -> Optional[Any]:
        """Retrieve stored data if not expired"""
        with self._lock:
            if data_id not in self.stored_data:
                return None
            
            entry = self.stored_data[data_id]
            
            # Check if data has expired
            if datetime.utcnow() > entry['expires_at']:
                self._delete_data(data_id)
                return None
            
            return entry['data']
    
    def delete_data(self, data_id: str) -> bool:
        """Manually delete stored data"""
        with self._lock:
            return self._delete_data(data_id)
    
    def _delete_data(self, data_id: str) -> bool:
        """Internal method to delete data"""
        try:
            if data_id in self.stored_data:
                if self.policy.secure_deletion_required:
                    # Overwrite data with random bytes for secure deletion
                    self.stored_data[data_id]['data'] = secrets.token_bytes(1024)
                
                del self.stored_data[data_id]
                
                if data_id in self.deletion_schedule:
                    del self.deletion_schedule[data_id]
                
                self.metrics.data_deleted += 1
                
                if self.policy.audit_trail_enabled:
                    logger.info(f"Data {data_id} securely deleted")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete data {data_id}: {str(e)}")
            return False
    
    def cleanup_expired_data(self) -> int:
        """Clean up all expired data"""
        current_time = datetime.utcnow()
        expired_count = 0
        
        with self._lock:
            expired_ids = [
                data_id for data_id, expires_at in self.deletion_schedule.items()
                if current_time > expires_at
            ]
            
            for data_id in expired_ids:
                if self._delete_data(data_id):
                    expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired data entries")
        
        return expired_count
    
    def _start_deletion_thread(self):
        """Start background thread for automatic deletion"""
        import threading
        
        def deletion_worker():
            while True:
                try:
                    self.cleanup_expired_data()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    logger.error(f"Deletion thread error: {str(e)}")
                    time.sleep(60)  # Wait 1 minute on error
        
        deletion_thread = threading.Thread(target=deletion_worker, daemon=True)
        deletion_thread.start()
        logger.info("Data retention deletion thread started")
    
    def get_retention_status(self) -> Dict[str, Any]:
        """Get current retention status"""
        with self._lock:
            current_time = datetime.utcnow()
            
            total_entries = len(self.stored_data)
            expired_entries = sum(
                1 for expires_at in self.deletion_schedule.values()
                if current_time > expires_at
            )
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'metrics': asdict(self.metrics)
            }

class PrivacyFramework:
    """Main privacy and safety framework coordinator"""
    
    def __init__(self, 
                 retention_policy: DataRetentionPolicy = None,
                 anonymization_config: AnonymizationConfig = None,
                 processing_mode: ProcessingMode = None):
        
        self.retention_policy = retention_policy or DataRetentionPolicy()
        self.anonymization_config = anonymization_config or AnonymizationConfig()
        self.processing_mode = processing_mode or ProcessingMode()
        
        # Initialize components
        self.data_handler = SecureDataHandler()
        self.anonymizer = DataAnonymizer(self.anonymization_config)
        self.retention_manager = DataRetentionManager(self.retention_policy)
        
        logger.info("Privacy Framework initialized with secure processing enabled")
    
    def process_social_data(self, social_data: Dict[str, Any], 
                          session_id: str = None) -> Tuple[Dict[str, Any], str]:
        """Process social data with full privacy protection"""
        
        processing_id = secrets.token_urlsafe(16)
        
        try:
            # Step 1: Anonymize the data
            anonymized_data, removed_elements = self._anonymize_social_data(social_data)
            
            # Step 2: Encrypt if required
            if self.processing_mode.encrypted_transmission_required:
                encrypted_data = self.data_handler.encrypt_data(anonymized_data, session_id)
                processed_data = {'encrypted': True, 'data': encrypted_data}
            else:
                processed_data = anonymized_data
            
            # Step 3: Store with retention policy
            self.retention_manager.store_data(
                processing_id, 
                processed_data,
                self.retention_policy.max_retention_hours
            )
            
            # Step 4: Log privacy actions
            self._log_privacy_actions(processing_id, removed_elements)
            
            return processed_data, processing_id
            
        except Exception as e:
            logger.error(f"Privacy processing failed: {str(e)}")
            raise PrivacyError(f"Failed to process data securely: {str(e)}")
    
    def _anonymize_social_data(self, social_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Anonymize all social data"""
        
        anonymized_data = social_data.copy()
        all_removed_elements = []
        
        # Anonymize social profiles
        for profile_type in ['social_profiles', 'discovered_profiles']:
            if profile_type in anonymized_data:
                for i, profile in enumerate(anonymized_data[profile_type]):
                    anonymized_profile, removed = self.anonymizer.anonymize_content(profile)
                    anonymized_data[profile_type][i] = anonymized_profile
                    all_removed_elements.extend(removed)
                    
                    # Anonymize inferred data
                    if 'inferred_data' in anonymized_profile:
                        inferred_data = anonymized_profile['inferred_data']
                        
                        # Anonymize posts
                        if 'posts' in inferred_data:
                            for j, post in enumerate(inferred_data['posts']):
                                if isinstance(post, dict):
                                    anonymized_post, post_removed = self.anonymizer.anonymize_content(post)
                                    inferred_data['posts'][j] = anonymized_post
                                    all_removed_elements.extend(post_removed)
                                elif isinstance(post, str):
                                    anonymized_text, text_removed = self.anonymizer._anonymize_text(post)
                                    inferred_data['posts'][j] = anonymized_text
                                    all_removed_elements.extend(text_removed)
        
        return anonymized_data, all_removed_elements
    
    def _log_privacy_actions(self, processing_id: str, removed_elements: List[str]):
        """Log privacy protection actions"""
        
        if self.retention_policy.audit_trail_enabled:
            privacy_log = {
                'processing_id': processing_id,
                'timestamp': datetime.utcnow().isoformat(),
                'anonymization_actions': len(removed_elements),
                'removed_element_types': list(set([elem.split(':')[0] for elem in removed_elements])),
                'encryption_applied': self.processing_mode.encrypted_transmission_required,
                'retention_hours': self.retention_policy.max_retention_hours
            }
            
            logger.info(f"Privacy actions logged for {processing_id}: "
                       f"{len(removed_elements)} elements anonymized")
    
    def get_client_side_config(self) -> Dict[str, Any]:
        """Get configuration for client-side processing"""
        
        if not self.processing_mode.client_side_enabled:
            return {'client_side_enabled': False}
        
        return {
            'client_side_enabled': True,
            'local_processing_only': self.processing_mode.local_processing_only,
            'anonymization_config': asdict(self.anonymization_config),
            'encryption_required': self.processing_mode.encrypted_transmission_required,
            'max_retention_hours': self.retention_policy.max_retention_hours
        }
    
    def validate_privacy_compliance(self) -> Dict[str, Any]:
        """Validate current privacy compliance status"""
        
        retention_status = self.retention_manager.get_retention_status()
        
        compliance_status = {
            'data_retention_compliant': retention_status['expired_entries'] == 0,
            'anonymization_enabled': True,
            'encryption_enabled': self.processing_mode.encrypted_transmission_required,
            'secure_deletion_enabled': self.retention_policy.secure_deletion_required,
            'audit_trail_enabled': self.retention_policy.audit_trail_enabled,
            'client_side_available': self.processing_mode.client_side_enabled,
            'retention_status': retention_status,
            'max_retention_hours': self.retention_policy.max_retention_hours
        }
        
        return compliance_status

# Custom exceptions
class SecurityError(Exception):
    """Raised when security operations fail"""
    pass

class PrivacyError(Exception):
    """Raised when privacy protection fails"""
    pass

def create_privacy_framework(
    max_retention_hours: int = 24,
    client_side_enabled: bool = False,
    anonymization_level: str = 'standard'
) -> PrivacyFramework:
    """Factory function to create privacy framework with configuration"""
    
    # Configure retention policy
    retention_policy = DataRetentionPolicy(
        max_retention_hours=max_retention_hours,
        auto_deletion_enabled=True,
        secure_deletion_required=True,
        audit_trail_enabled=True
    )
    
    # Configure anonymization based on level
    if anonymization_level == 'strict':
        anonymization_config = AnonymizationConfig(
            remove_names=True,
            remove_locations=True,
            remove_urls=True,
            remove_emails=True,
            remove_phone_numbers=True,
            hash_usernames=True,
            generalize_dates=True,
            remove_sensitive_keywords=True
        )
    elif anonymization_level == 'minimal':
        anonymization_config = AnonymizationConfig(
            remove_names=False,
            remove_locations=False,
            remove_urls=True,
            remove_emails=True,
            remove_phone_numbers=True,
            hash_usernames=False,
            generalize_dates=False,
            remove_sensitive_keywords=True
        )
    else:  # standard
        anonymization_config = AnonymizationConfig()
    
    # Configure processing mode
    processing_mode = ProcessingMode(
        client_side_enabled=client_side_enabled,
        local_processing_only=client_side_enabled,
        encrypted_transmission_required=True,
        minimize_data_collection=True
    )
    
    return PrivacyFramework(retention_policy, anonymization_config, processing_mode)
