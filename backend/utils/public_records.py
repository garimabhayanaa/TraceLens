import logging
import re
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import quote_plus
import json

logger = logging.getLogger(__name__)

@dataclass
class PublicRecord:
    record_type: str
    source: str
    data: Dict[str, Any]
    confidence_score: float
    verification_status: str
    privacy_impact: float

class PublicRecordsScanner:
    """Limited scope public records scanning (ethical and legal compliance)"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; LeakPeek/1.0; Privacy Analysis Tool)'
        })
        
        # Only scan publicly available, non-sensitive sources
        self.allowed_sources = {
            'professional_directories',
            'academic_publications',
            'open_government_data',
            'business_registrations',
            'patent_databases',
            'professional_licenses'
        }
        
        # Rate limiting for respectful scanning
        self.rate_limit_delay = 2.0  # Seconds between requests
    
    def scan_public_records(self, name: str, email: str, 
                          location_hint: Optional[str] = None) -> List[PublicRecord]:
        """
        Scan public records with strict ethical and legal compliance
        """
        
        records = []
        
        # Only proceed if we have valid inputs
        if not name or len(name.strip()) < 2:
            logger.warning("Invalid name provided for public records scan")
            return records
        
        logger.info(f"Starting ethical public records scan for: {name[:10]}...")
        
        try:
            # Scan professional directories
            professional_records = self._scan_professional_directories(name, email)
            records.extend(professional_records)
            
            # Scan academic publications
            academic_records = self._scan_academic_publications(name)
            records.extend(academic_records)
            
            # Scan business registrations (public only)
            business_records = self._scan_business_registrations(name)
            records.extend(business_records)
            
            # Scan patent databases
            patent_records = self._scan_patent_databases(name)
            records.extend(patent_records)
            
        except Exception as e:
            logger.error(f"Error during public records scan: {str(e)}")
        
        # Filter and validate records
        validated_records = self._validate_and_filter_records(records)
        
        logger.info(f"Found {len(validated_records)} validated public records")
        
        return validated_records
    
    def _scan_professional_directories(self, name: str, email: str) -> List[PublicRecord]:
        """Scan publicly available professional directories"""
        
        records = []
        
        # Example: Professional licensing boards (public information only)
        # This would typically integrate with official APIs
        
        professional_indicators = self._check_professional_indicators(name, email)
        
        if professional_indicators:
            record = PublicRecord(
                record_type='professional_directory',
                source='professional_indicators',
                data={
                    'indicators': professional_indicators,
                    'detection_method': 'pattern_analysis',
                    'privacy_note': 'Inferred from publicly available patterns only'
                },
                confidence_score=60.0,
                verification_status='inferred',
                privacy_impact=2.0  # Low impact - publicly available info
            )
            records.append(record)
        
        return records
    
    def _check_professional_indicators(self, name: str, email: str) -> Dict[str, Any]:
        """Check for professional indicators in name and email"""
        
        indicators = {}
        
        # Check email domain for professional indicators
        if '@' in email:
            domain = email.split('@')[1].lower()
            
            # Educational domains
            if any(edu_pattern in domain for edu_pattern in ['.edu', '.ac.', 'university', 'college']):
                indicators['academic_affiliation'] = {
                    'type': 'educational_email',
                    'domain': domain,
                    'confidence': 90
                }
            
            # Government domains
            if any(gov_pattern in domain for gov_pattern in ['.gov', '.mil', 'government']):
                indicators['government_affiliation'] = {
                    'type': 'government_email',
                    'domain': domain,
                    'confidence': 95
                }
            
            # Corporate domains (non-free email providers)
            free_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            if domain not in free_providers and '.' in domain:
                indicators['corporate_affiliation'] = {
                    'type': 'corporate_email',
                    'domain': domain,
                    'confidence': 70
                }
        
        # Check name for professional titles
        name_lower = name.lower()
        professional_titles = {
            'dr': 'medical_or_academic',
            'prof': 'academic',
            'ceo': 'executive',
            'cto': 'technology_executive',
            'md': 'medical',
            'phd': 'academic'
        }
        
        for title, category in professional_titles.items():
            if title in name_lower:
                indicators['professional_title'] = {
                    'title': title,
                    'category': category,
                    'confidence': 80
                }
                break
        
        return indicators
    
    def _scan_academic_publications(self, name: str) -> List[PublicRecord]:
        """Scan academic publication databases (public access only)"""
        
        records = []
        
        # This would integrate with public academic databases like:
        # - arXiv (open access)
        # - PubMed (public abstracts)
        # - Google Scholar (public profiles)
        # - ORCID (public profiles)
        
        # Placeholder implementation for academic publication detection
        academic_pattern_score = self._calculate_academic_likelihood(name)
        
        if academic_pattern_score > 60:
            record = PublicRecord(
                record_type='academic_publication',
                source='academic_pattern_analysis',
                data={
                    'likelihood_score': academic_pattern_score,
                    'indicators': 'Name pattern suggests potential academic background',
                    'note': 'Requires manual verification through public academic databases'
                },
                confidence_score=academic_pattern_score,
                verification_status='requires_verification',
                privacy_impact=1.5  # Low impact - academic work is typically public
            )
            records.append(record)
        
        return records
    
    def _calculate_academic_likelihood(self, name: str) -> float:
        """Calculate likelihood of academic background based on name patterns"""
        
        score = 0.0
        name_lower = name.lower()
        
        # Academic title indicators
        academic_titles = ['dr', 'prof', 'professor', 'phd', 'ph.d']
        for title in academic_titles:
            if title in name_lower:
                score += 30
        
        # Common academic name patterns
        if len(name.split()) >= 3:  # Full names more common in academia
            score += 10
        
        # Reduce score if obviously non-academic patterns
        non_academic_patterns = ['123', 'xxx', 'test']
        for pattern in non_academic_patterns:
            if pattern in name_lower:
                score -= 20
        
        return max(0, min(100, score))
    
    def _scan_business_registrations(self, name: str) -> List[PublicRecord]:
        """Scan public business registration databases"""
        
        records = []
        
        # This would integrate with public business registration APIs
        # Many jurisdictions provide public access to business registrations
        
        business_likelihood = self._calculate_business_likelihood(name)
        
        if business_likelihood > 50:
            record = PublicRecord(
                record_type='business_registration',
                source='business_pattern_analysis',
                data={
                    'likelihood_score': business_likelihood,
                    'note': 'Pattern suggests potential business registration',
                    'requires_verification': 'Check public business registries'
                },
                confidence_score=business_likelihood,
                verification_status='requires_verification',
                privacy_impact=2.5  # Medium impact - business info is public but more detailed
            )
            records.append(record)
        
        return records
    
    def _calculate_business_likelihood(self, name: str) -> float:
        """Calculate likelihood of business registration"""
        
        score = 0.0
        name_lower = name.lower()
        
        # Business entity indicators
        business_suffixes = ['llc', 'inc', 'corp', 'ltd', 'company', 'enterprises']
        for suffix in business_suffixes:
            if suffix in name_lower:
                score += 40
        
        # Executive title indicators
        exec_titles = ['ceo', 'cto', 'president', 'founder']
        for title in exec_titles:
            if title in name_lower:
                score += 20
        
        return max(0, min(100, score))
    
    def _scan_patent_databases(self, name: str) -> List[PublicRecord]:
        """Scan public patent databases"""
        
        records = []
        
        # Patent databases are typically public information
        # This would integrate with USPTO, WIPO, or other patent APIs
        
        patent_likelihood = self._calculate_patent_likelihood(name)
        
        if patent_likelihood > 40:
            record = PublicRecord(
                record_type='patent_database',
                source='patent_pattern_analysis',
                data={
                    'likelihood_score': patent_likelihood,
                    'note': 'Pattern suggests potential patent filings',
                    'databases_to_check': ['USPTO', 'Google Patents', 'WIPO']
                },
                confidence_score=patent_likelihood,
                verification_status='requires_verification',
                privacy_impact=2.0  # Medium-low impact - patents are public but show innovation
            )
            records.append(record)
        
        return records
    
    def _calculate_patent_likelihood(self, name: str) -> float:
        """Calculate likelihood of patent filings"""
        
        score = 0.0
        name_lower = name.lower()
        
        # Technical/engineering indicators
        tech_indicators = ['engineer', 'scientist', 'researcher', 'inventor', 'phd', 'dr']
        for indicator in tech_indicators:
            if indicator in name_lower:
                score += 15
        
        # Industry indicators
        industry_terms = ['tech', 'bio', 'pharma', 'medical', 'software']
        for term in industry_terms:
            if term in name_lower:
                score += 10
        
        return max(0, min(100, score))
    
    def _validate_and_filter_records(self, records: List[PublicRecord]) -> List[PublicRecord]:
        """Validate and filter records for ethical compliance"""
        
        validated_records = []
        
        for record in records:
            # Filter out high privacy impact records
            if record.privacy_impact > 5.0:
                logger.warning(f"Filtering out high privacy impact record: {record.record_type}")
                continue
            
            # Ensure record type is allowed
            if record.record_type not in ['professional_directory', 'academic_publication', 
                                       'business_registration', 'patent_database']:
                logger.warning(f"Filtering out non-allowed record type: {record.record_type}")
                continue
            
            # Validate confidence score
            if record.confidence_score < 30.0:
                logger.debug(f"Filtering out low confidence record: {record.confidence_score}")
                continue
            
            validated_records.append(record)
        
        return validated_records

def create_public_records_scanner():
    """Factory function to create public records scanner"""
    return PublicRecordsScanner()
