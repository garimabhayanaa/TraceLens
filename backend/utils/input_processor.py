import re
import logging
import dns.resolver
import tldextract
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
import requests
import json

logger = logging.getLogger(__name__)

@dataclass
class NameValidationResult:
    """Result of name validation with detailed analysis"""
    is_valid: bool
    original_name: str
    cleaned_name: str
    variants: List[str]
    confidence_score: float
    issues: List[str]
    name_type: str  # personal, business, username, etc.

@dataclass
class EmailDomainAnalysis:
    """Comprehensive email domain analysis result"""
    is_valid: bool
    email: str
    local_part: str
    domain: str
    domain_type: str  # free, corporate, educational, government, disposable, suspicious
    provider: str
    mx_exists: bool
    is_disposable: bool
    is_academic: bool
    is_government: bool
    risk_score: float
    country: Optional[str]
    issues: List[str]

class NameValidator:
    """Advanced name validation with international support"""
    
    def __init__(self):
        # Common name patterns for different cultures
        self.name_patterns = {
            'western': r'^[a-zA-ZÀ-ÿ\s\'-\.]{1,100}$',
            'international': r'^[\w\s\'-\.À-ÿÀ-ž\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]{1,100}$',
            'username': r'^[a-zA-Z0-9_\-\.]{1,50}$'
        }
        
        # Common nickname mappings
        self.nickname_map = {
            'william': ['bill', 'will', 'willy', 'billy'],
            'robert': ['bob', 'rob', 'bobby', 'robbie'],
            'richard': ['rick', 'rich', 'dick', 'richie'],
            'margaret': ['meg', 'maggie', 'peggy', 'marge'],
            'elizabeth': ['liz', 'beth', 'betty', 'libby', 'eliza'],
            'katherine': ['kate', 'katie', 'kathy', 'kitty'],
            'michael': ['mike', 'mick', 'mickey'],
            'christopher': ['chris', 'christie'],
            'jennifer': ['jen', 'jenny', 'jenn'],
            'matthew': ['matt', 'matty'],
            'andrew': ['andy', 'drew'],
            'joseph': ['joe', 'joey'],
            'anthony': ['tony', 'ant'],
            'stephanie': ['steph', 'steffi']
        }
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\d{3,}',  # Too many numbers
            r'[!@#$%^&*()_+=\[\]{}|;:"<>?,./]',  # Special characters
            r'^[a-z]{1,2}$',  # Too short
            r'(.)\1{3,}',  # Repeated characters
            r'^(test|admin|user|guest|demo)$'  # Generic names
        ]
    
    def validate_name(self, name: str, name_type: str = 'personal') -> NameValidationResult:
        """
        Comprehensive name validation with cultural awareness
        """
        
        if not name or not isinstance(name, str):
            return NameValidationResult(
                is_valid=False,
                original_name=name or '',
                cleaned_name='',
                variants=[],
                confidence_score=0.0,
                issues=['Empty or invalid input'],
                name_type=name_type
            )
        
        original_name = name
        cleaned_name = self._clean_name(name)
        issues = []
        confidence_score = 100.0
        
        # Length validation
        if len(cleaned_name) < 1:
            issues.append('Name too short')
            confidence_score -= 50
        elif len(cleaned_name) > 100:
            issues.append('Name too long')
            confidence_score -= 30
        
        # Pattern validation based on type
        pattern_key = 'international' if name_type == 'personal' else 'username'
        pattern = self.name_patterns.get(pattern_key, self.name_patterns['international'])
        
        if not re.match(pattern, cleaned_name):
            issues.append('Contains invalid characters')
            confidence_score -= 40
        
        # Check for suspicious patterns
        for suspicious_pattern in self.suspicious_patterns:
            if re.search(suspicious_pattern, cleaned_name.lower()):
                issues.append('Contains suspicious patterns')
                confidence_score -= 20
                break
        
        # Generate variants
        variants = self._generate_name_variants(cleaned_name, name_type)
        
        # Final validation
        is_valid = len(issues) == 0 and confidence_score >= 60
        
        return NameValidationResult(
            is_valid=is_valid,
            original_name=original_name,
            cleaned_name=cleaned_name,
            variants=variants,
            confidence_score=max(0.0, confidence_score),
            issues=issues,
            name_type=name_type
        )
    
    def _clean_name(self, name: str) -> str:
        """Clean and normalize name input"""
        # Remove extra whitespace
        cleaned = ' '.join(name.split())
        
        # Remove leading/trailing special characters
        cleaned = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', cleaned)
        
        # Normalize case (Title case for names)
        if re.match(r'^[a-zA-Z\s\'-\.]+$', cleaned):
            cleaned = cleaned.title()
        
        return cleaned
    
    def _generate_name_variants(self, name: str, name_type: str) -> List[str]:
        """Generate comprehensive name variants"""
        variants = set()
        
        # Add original name
        variants.add(name)
        variants.add(name.lower())
        variants.add(name.upper())
        
        if name_type == 'personal':
            variants.update(self._generate_personal_name_variants(name))
        elif name_type == 'username':
            variants.update(self._generate_username_variants(name))
        
        return list(variants)
    
    def _generate_personal_name_variants(self, name: str) -> Set[str]:
        """Generate variants for personal names"""
        variants = set()
        
        # Split into parts
        parts = name.split()
        
        if len(parts) >= 2:
            # First and last name only
            variants.add(f"{parts[0]} {parts[-1]}")
            
            # Initials
            initials = ''.join([part[0] for part in parts if part])
            variants.add(initials)
            variants.add(initials.lower())
            variants.add(initials.upper())
            
            # First name + middle initial + last name
            if len(parts) >= 3:
                variants.add(f"{parts[0]} {parts[1][0]}. {parts[-1]}")
        
        # Nickname variations
        name_lower = name.lower()
        for formal_name, nicknames in self.nickname_map.items():
            if formal_name in name_lower:
                for nickname in nicknames:
                    # Replace formal name with nickname
                    variant = name_lower.replace(formal_name, nickname)
                    variants.add(variant)
                    variants.add(variant.title())
        
        # Common variations
        if len(parts) == 1:
            # Single name variations
            single_name = parts[0].lower()
            if single_name in self.nickname_map:
                variants.update(self.nickname_map[single_name])
        
        return variants
    
    def _generate_username_variants(self, username: str) -> Set[str]:
        """Generate variants for usernames"""
        variants = set()
        
        # Common username patterns
        base = username.lower()
        variants.add(base)
        
        # With numbers
        for i in range(10):
            variants.add(f"{base}{i}")
        
        # With underscores and dots
        variants.add(base.replace(' ', '_'))
        variants.add(base.replace(' ', '.'))
        variants.add(base.replace(' ', ''))
        
        return variants

class EmailDomainAnalyzer:
    """Advanced email domain analysis with comprehensive validation"""
    
    def __init__(self):
        # Known disposable email providers
        self.disposable_domains = {
            '10minutemail.com', 'mailinator.com', 'tempmail.com', 'guerrillamail.com',
            'yopmail.com', 'temp-mail.org', 'throwaway.email', 'maildrop.cc',
            'trashmail.com', 'getnada.com', 'tempmail.de', 'temp-mail.ru'
        }
        
        # Known email providers
        self.email_providers = {
            # Free providers
            'gmail.com': {'provider': 'Google', 'type': 'free', 'country': 'US'},
            'yahoo.com': {'provider': 'Yahoo', 'type': 'free', 'country': 'US'},
            'outlook.com': {'provider': 'Microsoft', 'type': 'free', 'country': 'US'},
            'hotmail.com': {'provider': 'Microsoft', 'type': 'free', 'country': 'US'},
            'aol.com': {'provider': 'AOL', 'type': 'free', 'country': 'US'},
            'icloud.com': {'provider': 'Apple', 'type': 'free', 'country': 'US'},
            'protonmail.com': {'provider': 'ProtonMail', 'type': 'free', 'country': 'CH'},
            
            # International providers
            'yandex.com': {'provider': 'Yandex', 'type': 'free', 'country': 'RU'},
            'mail.ru': {'provider': 'Mail.ru', 'type': 'free', 'country': 'RU'},
            'qq.com': {'provider': 'Tencent QQ', 'type': 'free', 'country': 'CN'},
            '163.com': {'provider': 'NetEase', 'type': 'free', 'country': 'CN'},
        }
        
        # Academic domain patterns
        self.academic_tlds = {'.edu', '.ac.uk', '.edu.au', '.ac.jp', '.ac.kr'}
        
        # Government domain patterns
        self.government_tlds = {'.gov', '.gov.uk', '.gc.ca', '.gov.au'}
    
    def analyze_email_domain(self, email: str) -> EmailDomainAnalysis:
        """
        Comprehensive email domain analysis
        """
        
        if not email or not isinstance(email, str):
            return EmailDomainAnalysis(
                is_valid=False,
                email=email or '',
                local_part='',
                domain='',
                domain_type='invalid',
                provider='',
                mx_exists=False,
                is_disposable=False,
                is_academic=False,
                is_government=False,
                risk_score=100.0,
                country=None,
                issues=['Invalid email input']
            )
        
        # Basic email parsing
        email = email.strip().lower()
        
        if '@' not in email:
            return self._create_invalid_result(email, 'Missing @ symbol')
        
        try:
            local_part, domain = email.rsplit('@', 1)
        except ValueError:
            return self._create_invalid_result(email, 'Invalid email format')
        
        issues = []
        risk_score = 0.0
        
        # Validate local part
        if not self._validate_local_part(local_part):
            issues.append('Invalid local part')
            risk_score += 30
        
        # Validate domain
        if not self._validate_domain_format(domain):
            issues.append('Invalid domain format')
            risk_score += 40
        
        # Extract domain information
        extracted = tldextract.extract(domain)
        
        # Analyze domain type
        domain_analysis = self._analyze_domain_type(domain, extracted)
        
        # Check MX records
        mx_exists = self._check_mx_records(domain)
        if not mx_exists:
            issues.append('No MX records found')
            risk_score += 25
        
        # Disposable email check
        is_disposable = self._check_disposable_domain(domain)
        if is_disposable:
            issues.append('Disposable email detected')
            risk_score += 50
        
        # Academic domain check
        is_academic = self._check_academic_domain(domain)
        
        # Government domain check
        is_government = self._check_government_domain(domain)
        
        # Provider information
        provider_info = self.email_providers.get(domain, {})
        provider = provider_info.get('provider', 'Unknown')
        country = provider_info.get('country')
        
        # Final validation
        is_valid = len([issue for issue in issues if 'Invalid' in issue]) == 0
        
        return EmailDomainAnalysis(
            is_valid=is_valid,
            email=email,
            local_part=local_part,
            domain=domain,
            domain_type=domain_analysis['type'],
            provider=provider,
            mx_exists=mx_exists,
            is_disposable=is_disposable,
            is_academic=is_academic,
            is_government=is_government,
            risk_score=min(100.0, risk_score),
            country=country,
            issues=issues
        )
    
    def _validate_local_part(self, local_part: str) -> bool:
        """Validate email local part"""
        if not local_part or len(local_part) > 64:
            return False
        
        # Basic pattern check
        pattern = r'^[a-zA-Z0-9._%-]+$'
        return bool(re.match(pattern, local_part))
    
    def _validate_domain_format(self, domain: str) -> bool:
        """Validate domain format"""
        if not domain or len(domain) > 253:
            return False
        
        # Basic domain pattern
        pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))
    
    def _analyze_domain_type(self, domain: str, extracted) -> Dict[str, str]:
        """Analyze domain type and characteristics"""
        
        if domain in self.email_providers:
            return {'type': self.email_providers[domain]['type']}
        
        # Check for organizational domains
        if extracted.domain and len(extracted.domain.split('.')) == 1:
            # Likely corporate domain
            return {'type': 'corporate'}
        
        # Check for free domain indicators
        free_indicators = ['mail', 'email', 'post', 'web']
        if any(indicator in domain.lower() for indicator in free_indicators):
            return {'type': 'free'}
        
        return {'type': 'unknown'}
    
    def _check_mx_records(self, domain: str) -> bool:
        """Check if domain has MX records"""
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            return len(answers) > 0
        except Exception:
            return False
    
    def _check_disposable_domain(self, domain: str) -> bool:
        """Check if domain is disposable"""
        return domain in self.disposable_domains
    
    def _check_academic_domain(self, domain: str) -> bool:
        """Check if domain is academic"""
        return any(domain.endswith(tld) for tld in self.academic_tlds)
    
    def _check_government_domain(self, domain: str) -> bool:
        """Check if domain is government"""
        return any(domain.endswith(tld) for tld in self.government_tlds)
    
    def _create_invalid_result(self, email: str, reason: str) -> EmailDomainAnalysis:
        """Create invalid email analysis result"""
        return EmailDomainAnalysis(
            is_valid=False,
            email=email,
            local_part='',
            domain='',
            domain_type='invalid',
            provider='',
            mx_exists=False,
            is_disposable=False,
            is_academic=False,
            is_government=False,
            risk_score=100.0,
            country=None,
            issues=[reason]
        )

class InputProcessor:
    """Main input processor combining name validation and email analysis"""
    
    def __init__(self):
        self.name_validator = NameValidator()
        self.email_analyzer = EmailDomainAnalyzer()
    
    def process_input(self, name: str, email: str) -> Dict[str, any]:
        """
        Process and validate name and email inputs
        """
        
        # Validate name
        name_result = self.name_validator.validate_name(name, 'personal')
        
        # Analyze email
        email_result = self.email_analyzer.analyze_email_domain(email)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(name_result, email_result)
        
        return {
            'name_validation': {
                'is_valid': name_result.is_valid,
                'original_name': name_result.original_name,
                'cleaned_name': name_result.cleaned_name,
                'variants': name_result.variants,
                'confidence_score': name_result.confidence_score,
                'issues': name_result.issues,
                'name_type': name_result.name_type
            },
            'email_analysis': {
                'is_valid': email_result.is_valid,
                'email': email_result.email,
                'local_part': email_result.local_part,
                'domain': email_result.domain,
                'domain_type': email_result.domain_type,
                'provider': email_result.provider,
                'mx_exists': email_result.mx_exists,
                'is_disposable': email_result.is_disposable,
                'is_academic': email_result.is_academic,
                'is_government': email_result.is_government,
                'risk_score': email_result.risk_score,
                'country': email_result.country,
                'issues': email_result.issues
            },
            'overall_confidence': overall_confidence
        }
    
    def _calculate_overall_confidence(self, name_result: NameValidationResult, 
                                    email_result: EmailDomainAnalysis) -> float:
        """Calculate overall confidence score"""
        
        name_weight = 0.3
        email_weight = 0.7
        
        name_score = name_result.confidence_score if name_result.is_valid else 0
        email_score = 100 - email_result.risk_score if email_result.is_valid else 0
        
        return (name_score * name_weight) + (email_score * email_weight)

def create_input_processor():
    """Factory function to create input processor"""
    return InputProcessor()
