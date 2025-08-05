import logging
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
import threading

logger = logging.getLogger(__name__)

class UseCaseCategory(Enum):
    """Categories of use cases for ethical evaluation"""
    LEGITIMATE_RESEARCH = "legitimate_research"
    SECURITY_ANALYSIS = "security_analysis"
    SELF_ASSESSMENT = "self_assessment"
    EDUCATIONAL = "educational"
    MALICIOUS_STALKING = "malicious_stalking"
    HARASSMENT = "harassment"
    DISCRIMINATION = "discrimination"
    UNAUTHORIZED_PROFILING = "unauthorized_profiling"

class EthicalViolationType(Enum):
    """Types of ethical violations"""
    MALICIOUS_USE = "malicious_use"
    AGE_RESTRICTION = "age_restriction"
    SCOPE_VIOLATION = "scope_violation"
    CONSENT_VIOLATION = "consent_violation"
    DATA_MISUSE = "data_misuse"
    HARASSMENT_INTENT = "harassment_intent"

@dataclass
class AgeVerificationResult:
    """Age verification result"""
    verified: bool
    age_confirmed: Optional[int]
    verification_method: str
    confidence_score: float
    verification_timestamp: datetime
    verification_id: str

@dataclass
class EthicalAssessment:
    """Ethical assessment of analysis request"""
    approved: bool
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    violations: List[EthicalViolationType]
    use_case_category: UseCaseCategory
    justification: str
    recommendations: List[str]
    review_required: bool

@dataclass
class DataScopeValidation:
    """Validation of data scope and sources"""
    within_scope: bool
    allowed_sources: List[str]
    restricted_sources: List[str]
    data_types_approved: List[str]
    data_types_rejected: List[str]
    scope_violations: List[str]

@dataclass
class ProfessionalReview:
    """Professional ethics board review"""
    review_id: str
    reviewer_id: str
    review_date: datetime
    approval_status: str  # 'approved', 'rejected', 'conditional', 'pending'
    conditions: List[str]
    expiry_date: Optional[datetime]
    review_notes: str

@dataclass
class EthicalBoundariesResult:
    """Complete ethical boundaries assessment"""
    ethics_approved: bool
    age_verification: AgeVerificationResult
    ethical_assessment: EthicalAssessment
    scope_validation: DataScopeValidation
    professional_review: Optional[ProfessionalReview]
    usage_restrictions: List[str]
    monitoring_requirements: List[str]
    compliance_score: float

class MaliciousUseDetector:
    """Detects potential malicious use patterns"""
    
    def __init__(self):
        self.malicious_patterns = {
            'stalking_indicators': [
                'track', 'follow', 'monitor', 'watch', 'surveillance', 'stalk',
                'location', 'whereabouts', 'movement', 'activity pattern',
                'personal life', 'private information', 'intimate details'
            ],
            'harassment_indicators': [
                'harass', 'intimidate', 'threaten', 'embarrass', 'humiliate',
                'expose', 'shame', 'blackmail', 'revenge', 'get back at',
                'hurt', 'damage reputation', 'ruin life'
            ],
            'discrimination_indicators': [
                'discriminate', 'exclude', 'reject based on', 'filter out',
                'bias against', 'prejudice', 'stereotype', 'profile for exclusion'
            ],
            'unauthorized_profiling': [
                'without consent', 'secretly analyze', 'covert profiling',
                'hidden analysis', 'unauthorized investigation', 'spy on'
            ]
        }
        
        self.legitimate_patterns = {
            'research_indicators': [
                'research', 'study', 'analysis', 'academic', 'scientific',
                'investigation', 'understanding', 'insights', 'patterns'
            ],
            'security_indicators': [
                'security', 'protection', 'safety', 'threat detection',
                'risk assessment', 'vulnerability', 'fraud prevention'
            ],
            'self_assessment': [
                'self', 'my own', 'personal', 'self-reflection',
                'understand myself', 'self-improvement'
            ]
        }
    
    def assess_use_case(self, use_case_description: str, 
                       user_context: Dict[str, Any]) -> Tuple[UseCaseCategory, float]:
        """Assess the use case for potential malicious intent"""
        
        if not use_case_description:
            return UseCaseCategory.UNAUTHORIZED_PROFILING, 0.8
        
        description_lower = use_case_description.lower()
        
        # Check for malicious patterns
        malicious_scores = {}
        for category, patterns in self.malicious_patterns.items():
            score = sum(1 for pattern in patterns if pattern in description_lower)
            malicious_scores[category] = score / len(patterns)
        
        # Check for legitimate patterns
        legitimate_scores = {}
        for category, patterns in self.legitimate_patterns.items():
            score = sum(1 for pattern in patterns if pattern in description_lower)
            legitimate_scores[category] = score / len(patterns)
        
        # Determine primary category
        max_malicious = max(malicious_scores.values()) if malicious_scores.values() else 0
        max_legitimate = max(legitimate_scores.values()) if legitimate_scores.values() else 0
        
        if max_malicious > 0.3:  # High malicious indicator threshold
            if malicious_scores['stalking_indicators'] == max_malicious:
                return UseCaseCategory.MALICIOUS_STALKING, max_malicious
            elif malicious_scores['harassment_indicators'] == max_malicious:
                return UseCaseCategory.HARASSMENT, max_malicious
            elif malicious_scores['discrimination_indicators'] == max_malicious:
                return UseCaseCategory.DISCRIMINATION, max_malicious
            else:
                return UseCaseCategory.UNAUTHORIZED_PROFILING, max_malicious
        
        elif max_legitimate > 0.2:  # Lower threshold for legitimate use
            if legitimate_scores['research_indicators'] == max_legitimate:
                return UseCaseCategory.LEGITIMATE_RESEARCH, 1.0 - max_malicious
            elif legitimate_scores['security_indicators'] == max_legitimate:
                return UseCaseCategory.SECURITY_ANALYSIS, 1.0 - max_malicious
            elif legitimate_scores['self_assessment'] == max_legitimate:
                return UseCaseCategory.SELF_ASSESSMENT, 1.0 - max_malicious
            else:
                return UseCaseCategory.EDUCATIONAL, 1.0 - max_malicious
        
        # Default to unauthorized if unclear
        return UseCaseCategory.UNAUTHORIZED_PROFILING, 0.6

class AgeVerificationSystem:
    """Handles age verification with multiple methods"""
    
    def __init__(self):
        self.verification_cache = {}
        self.verification_methods = [
            'government_id',
            'credit_card',
            'phone_verification',
            'third_party_service',
            'declaration_with_validation'
        ]
    
    def verify_age(self, user_id: str, verification_data: Dict[str, Any]) -> AgeVerificationResult:
        """Verify user age with multiple verification methods"""
        
        verification_id = hashlib.sha256(f"{user_id}_{time.time()}".encode()).hexdigest()[:16]
        
        # Check cache first
        if user_id in self.verification_cache:
            cached_result = self.verification_cache[user_id]
            # Return cached result if recent (within 30 days)
            if (datetime.utcnow() - cached_result.verification_timestamp).days < 30:
                return cached_result
        
        verification_method = verification_data.get('method', 'declaration_with_validation')
        
        if verification_method == 'government_id':
            result = self._verify_with_government_id(verification_data)
        elif verification_method == 'credit_card':
            result = self._verify_with_credit_card(verification_data)
        elif verification_method == 'phone_verification':
            result = self._verify_with_phone(verification_data)
        elif verification_method == 'third_party_service':
            result = self._verify_with_third_party(verification_data)
        else:
            result = self._verify_with_declaration(verification_data)
        
        # Create verification result
        verification_result = AgeVerificationResult(
            verified=result['verified'],
            age_confirmed=result.get('age'),
            verification_method=verification_method,
            confidence_score=result['confidence'],
            verification_timestamp=datetime.utcnow(),
            verification_id=verification_id
        )
        
        # Cache successful verifications
        if result['verified']:
            self.verification_cache[user_id] = verification_result
        
        return verification_result
    
    def _verify_with_government_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify age using government ID (simulated)"""
        # In production, this would integrate with ID verification services
        
        id_number = data.get('id_number', '')
        birth_date = data.get('birth_date', '')
        
        if not id_number or not birth_date:
            return {'verified': False, 'confidence': 0.0}
        
        # Simulate ID verification
        try:
            birth_year = int(birth_date.split('-')[0]) if '-' in birth_date else int(birth_date[:4])
            current_year = datetime.utcnow().year
            age = current_year - birth_year
            
            if age >= 18:
                return {'verified': True, 'age': age, 'confidence': 0.95}
            else:
                return {'verified': False, 'age': age, 'confidence': 0.95}
                
        except (ValueError, IndexError):
            return {'verified': False, 'confidence': 0.0}
    
    def _verify_with_credit_card(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify age using credit card (requires 18+ for most cards)"""
        # In production, this would verify card ownership and age requirements
        
        card_number = data.get('card_number', '')
        expiry = data.get('expiry', '')
        
        if len(card_number) >= 15 and expiry:
            # Credit cards typically require 18+ age
            return {'verified': True, 'age': 18, 'confidence': 0.85}
        
        return {'verified': False, 'confidence': 0.0}
    
    def _verify_with_phone(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify age using phone verification"""
        # Phone verification provides lower confidence for age
        
        phone = data.get('phone', '')
        verification_code = data.get('code', '')
        
        if phone and verification_code:
            # Phone verification confirms identity but not age precisely
            return {'verified': True, 'age': None, 'confidence': 0.60}
        
        return {'verified': False, 'confidence': 0.0}
    
    def _verify_with_third_party(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify age using third-party age verification service"""
        # Integration with services like Jumio, Onfido, etc.
        
        service_response = data.get('service_response', {})
        
        if service_response.get('verified') and service_response.get('age', 0) >= 18:
            return {
                'verified': True, 
                'age': service_response['age'], 
                'confidence': service_response.get('confidence', 0.90)
            }
        
        return {'verified': False, 'confidence': 0.0}
    
    def _verify_with_declaration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify age with declaration and validation checks"""
        
        declared_age = data.get('declared_age', 0)
        email = data.get('email', '')
        
        # Basic validation
        if declared_age >= 18 and email:
            # Declaration has lower confidence
            return {'verified': True, 'age': declared_age, 'confidence': 0.40}
        
        return {'verified': False, 'confidence': 0.0}

class DataScopeValidator:
    """Validates that analysis stays within ethical data scope"""
    
    def __init__(self):
        self.allowed_sources = [
            'public_social_media_profiles',
            'publicly_available_posts',
            'public_bio_information',
            'public_follower_counts',
            'public_interaction_data',
            'publicly_visible_content'
        ]
        
        self.restricted_sources = [
            'private_messages',
            'private_posts',
            'deleted_content',
            'draft_content',
            'private_photos',
            'location_history',
            'contact_lists',
            'financial_information',
            'medical_records',
            'private_communications',
            'hacked_data',
            'leaked_databases'
        ]
        
        self.approved_data_types = [
            'public_text_content',
            'public_images',
            'hashtags',
            'mentions',
            'public_engagement_metrics',
            'posting_patterns',
            'public_profile_information'
        ]
        
        self.rejected_data_types = [
            'private_personal_data',
            'sensitive_personal_information',
            'financial_data',
            'health_data',
            'location_tracking_data',
            'biometric_data',
            'private_communications'
        ]
    
    def validate_data_scope(self, data_sources: List[str], 
                          data_types: List[str],
                          collection_method: str) -> DataScopeValidation:
        """Validate that data collection stays within ethical boundaries"""
        
        # Check data sources
        allowed_sources_used = [src for src in data_sources if src in self.allowed_sources]
        restricted_sources_used = [src for src in data_sources if src in self.restricted_sources]
        
        # Check data types
        approved_types_used = [dt for dt in data_types if dt in self.approved_data_types]
        rejected_types_used = [dt for dt in data_types if dt in self.rejected_data_types]
        
        # Identify violations
        scope_violations = []
        
        if restricted_sources_used:
            scope_violations.extend([f"Restricted source: {src}" for src in restricted_sources_used])
        
        if rejected_types_used:
            scope_violations.extend([f"Rejected data type: {dt}" for dt in rejected_types_used])
        
        if collection_method not in ['public_api', 'web_scraping_public', 'user_provided']:
            scope_violations.append(f"Unapproved collection method: {collection_method}")
        
        # Determine if within scope
        within_scope = len(scope_violations) == 0 and len(allowed_sources_used) > 0
        
        return DataScopeValidation(
            within_scope=within_scope,
            allowed_sources=allowed_sources_used,
            restricted_sources=restricted_sources_used,
            data_types_approved=approved_types_used,
            data_types_rejected=rejected_types_used,
            scope_violations=scope_violations
        )

class EthicsBoard:
    """Simulated ethics board for professional review"""
    
    def __init__(self):
        self.approved_algorithms = set()
        self.pending_reviews = {}
        self.review_history = {}
    
    def submit_for_review(self, algorithm_description: str, 
                         use_case: str,
                         risk_assessment: str) -> str:
        """Submit algorithm for ethics board review"""
        
        review_id = hashlib.sha256(f"{algorithm_description}_{time.time()}".encode()).hexdigest()[:16]
        
        review_submission = {
            'review_id': review_id,
            'algorithm_description': algorithm_description,
            'use_case': use_case,
            'risk_assessment': risk_assessment,
            'submission_date': datetime.utcnow(),
            'status': 'pending'
        }
        
        self.pending_reviews[review_id] = review_submission
        
        # Simulate automatic approval for low-risk cases
        if 'low risk' in risk_assessment.lower() and 'research' in use_case.lower():
            return self._auto_approve(review_id)
        
        return review_id
    
    def get_review_status(self, review_id: str) -> Optional[ProfessionalReview]:
        """Get status of ethics board review"""
        
        if review_id in self.review_history:
            return self.review_history[review_id]
        
        if review_id in self.pending_reviews:
            submission = self.pending_reviews[review_id]
            
            # Simulate review processing time
            hours_since_submission = (datetime.utcnow() - submission['submission_date']).total_seconds() / 3600
            
            if hours_since_submission > 24:  # Auto-process after 24 hours
                return self._process_review(review_id)
            
            return ProfessionalReview(
                review_id=review_id,
                reviewer_id='pending',
                review_date=submission['submission_date'],
                approval_status='pending',
                conditions=[],
                expiry_date=None,
                review_notes='Review in progress'
            )
        
        return None
    
    def _auto_approve(self, review_id: str) -> str:
        """Auto-approve low-risk submissions"""
        
        review = ProfessionalReview(
            review_id=review_id,
            reviewer_id='auto_system',
            review_date=datetime.utcnow(),
            approval_status='approved',
            conditions=['Standard ethical guidelines apply'],
            expiry_date=datetime.utcnow() + timedelta(days=365),
            review_notes='Auto-approved for low-risk research use'
        )
        
        self.review_history[review_id] = review
        self.approved_algorithms.add(review_id)
        
        if review_id in self.pending_reviews:
            del self.pending_reviews[review_id]
        
        return review_id
    
    def _process_review(self, review_id: str) -> ProfessionalReview:
        """Process pending review"""
        
        submission = self.pending_reviews[review_id]
        
        # Simulate ethics board decision
        risk_level = submission['risk_assessment'].lower()
        use_case = submission['use_case'].lower()
        
        if 'malicious' in use_case or 'harassment' in use_case or 'stalking' in use_case:
            approval_status = 'rejected'
            conditions = []
            review_notes = 'Rejected due to potential malicious use'
        elif 'high risk' in risk_level:
            approval_status = 'conditional'
            conditions = [
                'Enhanced monitoring required',
                'Monthly compliance reports',
                'Limited scope of analysis',
                'User consent verification required'
            ]
            review_notes = 'Conditional approval with enhanced oversight'
        else:
            approval_status = 'approved'
            conditions = ['Standard ethical guidelines apply']
            review_notes = 'Approved with standard conditions'
        
        review = ProfessionalReview(
            review_id=review_id,
            reviewer_id='ethics_board_001',
            review_date=datetime.utcnow(),
            approval_status=approval_status,
            conditions=conditions,
            expiry_date=datetime.utcnow() + timedelta(days=365) if approval_status != 'rejected' else None,
            review_notes=review_notes
        )
        
        self.review_history[review_id] = review
        
        if approval_status in ['approved', 'conditional']:
            self.approved_algorithms.add(review_id)
        
        if review_id in self.pending_reviews:
            del self.pending_reviews[review_id]
        
        return review

class EthicalBoundariesFramework:
    """Main ethical boundaries framework coordinator"""
    
    def __init__(self):
        self.malicious_detector = MaliciousUseDetector()
        self.age_verifier = AgeVerificationSystem()
        self.scope_validator = DataScopeValidator()
        self.ethics_board = EthicsBoard()
        
        # Track usage for monitoring
        self.usage_log = []
        self.violation_log = []
        
        logger.info("Ethical Boundaries Framework initialized")
    
    def evaluate_request(self, 
                        user_id: str,
                        use_case_description: str,
                        data_sources: List[str],
                        data_types: List[str],
                        collection_method: str,
                        age_verification_data: Dict[str, Any],
                        user_context: Dict[str, Any]) -> EthicalBoundariesResult:
        """Comprehensive ethical evaluation of analysis request"""
        
        logger.info(f"Starting ethical evaluation for user {user_id}")
        
        violations = []
        usage_restrictions = []
        monitoring_requirements = []
        
        # 1. Age Verification
        age_verification = self.age_verifier.verify_age(user_id, age_verification_data)
        
        if not age_verification.verified or (age_verification.age_confirmed and age_verification.age_confirmed < 18):
            violations.append(EthicalViolationType.AGE_RESTRICTION)
            
        # 2. Malicious Use Detection
        use_case_category, malicious_score = self.malicious_detector.assess_use_case(
            use_case_description, user_context
        )
        
        if use_case_category in [UseCaseCategory.MALICIOUS_STALKING, 
                                UseCaseCategory.HARASSMENT, 
                                UseCaseCategory.DISCRIMINATION]:
            violations.append(EthicalViolationType.MALICIOUS_USE)
        
        # 3. Data Scope Validation
        scope_validation = self.scope_validator.validate_data_scope(
            data_sources, data_types, collection_method
        )
        
        if not scope_validation.within_scope:
            violations.append(EthicalViolationType.SCOPE_VIOLATION)
        
        # 4. Generate Ethical Assessment
        ethical_assessment = self._generate_ethical_assessment(
            use_case_category, malicious_score, violations, scope_validation
        )
        
        # 5. Professional Review (if required)
        professional_review = None
        if ethical_assessment.review_required:
            review_id = self.ethics_board.submit_for_review(
                "Social media analysis algorithm",
                use_case_description,
                ethical_assessment.risk_level
            )
            professional_review = self.ethics_board.get_review_status(review_id)
        
        # 6. Generate Usage Restrictions and Monitoring
        usage_restrictions, monitoring_requirements = self._generate_restrictions_and_monitoring(
            ethical_assessment, scope_validation, professional_review
        )
        
        # 7. Calculate Compliance Score
        compliance_score = self._calculate_compliance_score(
            age_verification, ethical_assessment, scope_validation, professional_review
        )
        
        # 8. Final Approval Decision
        ethics_approved = (
            age_verification.verified and
            len([v for v in violations if v != EthicalViolationType.AGE_RESTRICTION]) == 0 and
            ethical_assessment.approved and
            scope_validation.within_scope and
            (professional_review is None or professional_review.approval_status in ['approved', 'conditional'])
        )
        
        # Log the evaluation
        self._log_evaluation(user_id, ethics_approved, violations, use_case_category)
        
        result = EthicalBoundariesResult(
            ethics_approved=ethics_approved,
            age_verification=age_verification,
            ethical_assessment=ethical_assessment,
            scope_validation=scope_validation,
            professional_review=professional_review,
            usage_restrictions=usage_restrictions,
            monitoring_requirements=monitoring_requirements,
            compliance_score=compliance_score
        )
        
        logger.info(f"Ethical evaluation completed for user {user_id}: "
                   f"Approved={ethics_approved}, Compliance={compliance_score:.2f}")
        
        return result
    
    def _generate_ethical_assessment(self, 
                                   use_case_category: UseCaseCategory,
                                   malicious_score: float,
                                   violations: List[EthicalViolationType],
                                   scope_validation: DataScopeValidation) -> EthicalAssessment:
        """Generate comprehensive ethical assessment"""
        
        # Determine risk level
        if malicious_score > 0.7 or use_case_category in [
            UseCaseCategory.MALICIOUS_STALKING, 
            UseCaseCategory.HARASSMENT
        ]:
            risk_level = 'critical'
        elif malicious_score > 0.5 or len(violations) > 2:
            risk_level = 'high'
        elif malicious_score > 0.3 or len(violations) > 0:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Determine approval
        approved = (
            risk_level in ['low', 'medium'] and
            use_case_category not in [
                UseCaseCategory.MALICIOUS_STALKING,
                UseCaseCategory.HARASSMENT,
                UseCaseCategory.DISCRIMINATION
            ] and
            EthicalViolationType.MALICIOUS_USE not in violations
        )
        
        # Generate justification
        if not approved:
            if use_case_category == UseCaseCategory.MALICIOUS_STALKING:
                justification = "Request rejected due to stalking indicators"
            elif use_case_category == UseCaseCategory.HARASSMENT:
                justification = "Request rejected due to harassment indicators"
            elif EthicalViolationType.MALICIOUS_USE in violations:
                justification = "Request rejected due to potential malicious use"
            else:
                justification = f"Request rejected due to {risk_level} risk level"
        else:
            justification = f"Request approved with {risk_level} risk level for {use_case_category.value}"
        
        # Generate recommendations
        recommendations = self._generate_ethical_recommendations(
            use_case_category, risk_level, violations
        )
        
        # Determine if professional review required
        review_required = (
            risk_level in ['high', 'critical'] or
            use_case_category == UseCaseCategory.SECURITY_ANALYSIS or
            len(violations) > 1
        )
        
        return EthicalAssessment(
            approved=approved,
            risk_level=risk_level,
            violations=violations,
            use_case_category=use_case_category,
            justification=justification,
            recommendations=recommendations,
            review_required=review_required
        )
    
    def _generate_ethical_recommendations(self, 
                                        use_case_category: UseCaseCategory,
                                        risk_level: str,
                                        violations: List[EthicalViolationType]) -> List[str]:
        """Generate ethical recommendations"""
        
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            "🔒 Ensure all data processing complies with privacy regulations",
            "📋 Maintain clear terms of service and user consent",
            "🛡️ Implement data minimization principles",
            "📊 Use aggregated and anonymized data when possible"
        ])
        
        # Risk-level specific recommendations
        if risk_level == 'high':
            recommendations.extend([
                "⚠️ Enhanced monitoring and audit trails required",
                "👥 Consider independent oversight of analysis results",
                "🔍 Regular ethical compliance reviews recommended"
            ])
        elif risk_level == 'critical':
            recommendations.extend([
                "🚨 Immediate ethics board review required",
                "⛔ Suspend analysis until approval obtained",
                "🔒 Enhanced data protection measures mandatory"
            ])
        
        # Use case specific recommendations
        if use_case_category == UseCaseCategory.LEGITIMATE_RESEARCH:
            recommendations.extend([
                "📚 Follow academic research ethics guidelines",
                "🔬 Ensure research methodology is sound and ethical",
                "📝 Consider publication and peer review requirements"
            ])
        elif use_case_category == UseCaseCategory.SECURITY_ANALYSIS:
            recommendations.extend([
                "🛡️ Limit analysis to security-relevant patterns only",
                "⚖️ Balance security needs with privacy rights",
                "📋 Document security justification for analysis"
            ])
        
        # Violation-specific recommendations
        if EthicalViolationType.AGE_RESTRICTION in violations:
            recommendations.append("🔞 Age verification required - restrict access to 18+ users only")
        
        if EthicalViolationType.SCOPE_VIOLATION in violations:
            recommendations.append("📏 Limit data collection to publicly available information only")
        
        return recommendations
    
    def _generate_restrictions_and_monitoring(self, 
                                            ethical_assessment: EthicalAssessment,
                                            scope_validation: DataScopeValidation,
                                            professional_review: Optional[ProfessionalReview]) -> Tuple[List[str], List[str]]:
        """Generate usage restrictions and monitoring requirements"""
        
        restrictions = [
            "🚫 No malicious use - harassment, stalking, or discrimination prohibited",
            "🔞 18+ age requirement - verified age confirmation required",
            "📊 Public data only - analysis limited to publicly available social media data",
            "⚖️ Ethical use only - must comply with terms of service and ethical guidelines"
        ]
        
        monitoring = [
            "📊 Usage analytics and audit trails maintained",
            "🔍 Regular compliance reviews and ethical assessments",
            "⚠️ Automated violation detection and alerting"
        ]
        
        # Add risk-specific restrictions
        if ethical_assessment.risk_level == 'high':
            restrictions.extend([
                "👥 Enhanced user consent requirements",
                "🔒 Additional data protection measures required",
                "📋 Detailed justification required for each analysis"
            ])
            monitoring.extend([
                "👁️ Enhanced monitoring and oversight required",
                "📝 Detailed usage reporting required"
            ])
        
        # Add professional review conditions
        if professional_review and professional_review.conditions:
            restrictions.extend([f"⚖️ Ethics board condition: {condition}" 
                               for condition in professional_review.conditions])
        
        return restrictions, monitoring
    
    def _calculate_compliance_score(self, 
                                  age_verification: AgeVerificationResult,
                                  ethical_assessment: EthicalAssessment,
                                  scope_validation: DataScopeValidation,
                                  professional_review: Optional[ProfessionalReview]) -> float:
        """Calculate overall compliance score"""
        
        score = 0.0
        
        # Age verification (25% weight)
        if age_verification.verified:
            score += 0.25 * age_verification.confidence_score
        
        # Ethical assessment (40% weight)
        if ethical_assessment.approved:
            risk_scores = {'low': 1.0, 'medium': 0.7, 'high': 0.4, 'critical': 0.1}
            score += 0.40 * risk_scores.get(ethical_assessment.risk_level, 0.1)
        
        # Scope validation (25% weight)
        if scope_validation.within_scope:
            score += 0.25
        
        # Professional review (10% weight)
        if professional_review:
            if professional_review.approval_status == 'approved':
                score += 0.10
            elif professional_review.approval_status == 'conditional':
                score += 0.05
        else:
            # No review required gets full points
            score += 0.10
        
        return min(score, 1.0)
    
    def _log_evaluation(self, user_id: str, approved: bool, 
                       violations: List[EthicalViolationType],
                       use_case_category: UseCaseCategory):
        """Log ethical evaluation for monitoring"""
        
        log_entry = {
            'user_id': hashlib.sha256(user_id.encode()).hexdigest()[:16],  # Anonymized
            'timestamp': datetime.utcnow(),
            'approved': approved,
            'violations': [v.value for v in violations],
            'use_case_category': use_case_category.value
        }
        
        self.usage_log.append(log_entry)
        
        if violations:
            self.violation_log.append(log_entry)
        
        # Keep logs limited to last 1000 entries
        if len(self.usage_log) > 1000:
            self.usage_log = self.usage_log[-1000:]
        
        if len(self.violation_log) > 100:
            self.violation_log = self.violation_log[-100:]
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        
        total_requests = len(self.usage_log)
        approved_requests = len([log for log in self.usage_log if log['approved']])
        violation_count = len(self.violation_log)
        
        # Analyze violation patterns
        violation_types = defaultdict(int)
        for log in self.violation_log:
            for violation in log['violations']:
                violation_types[violation] += 1
        
        return {
            'total_requests': total_requests,
            'approved_requests': approved_requests,
            'approval_rate': approved_requests / max(total_requests, 1),
            'violation_count': violation_count,
            'violation_rate': violation_count / max(total_requests, 1),
            'violation_types': dict(violation_types),
            'compliance_status': 'good' if violation_count / max(total_requests, 1) < 0.05 else 'concerning'
        }

def create_ethical_boundaries_framework() -> EthicalBoundariesFramework:
    """Factory function to create ethical boundaries framework"""
    return EthicalBoundariesFramework()
