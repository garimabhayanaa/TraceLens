from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass
import json
from datetime import datetime

class RiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InferenceCategory(Enum):
    DEMOGRAPHIC = "demographic"
    HEALTH = "health"
    POLITICAL_VIEWS = "political_views"
    RELIGIOUS_BELIEFS = "religious_beliefs"
    SEXUAL_ORIENTATION = "sexual_orientation"
    FINANCIAL_STATUS = "financial_status"
    BEHAVIORAL_PATTERNS = "behavioral_patterns"
    LOCATION_DATA = "location_data"
    EMPLOYMENT = "employment"
    SOCIAL_RELATIONS = "social_relations"
    PREFERENCES = "preferences"
    ONLINE_ACTIVITY = "online_activity"
    BIOMETRIC_TRAITS = "biometric_traits"
    PSYCHOLOGICAL_PROFILE = "psychological_profile"

@dataclass
class PrivacyTemplate:
    category: InferenceCategory
    name: str
    description: str
    risk_level: RiskLevel
    regulatory_frameworks: List[str]
    potential_harms: List[str]
    detection_methods: List[str]
    recommended_controls: List[str]
    examples: List[str]
    gdpr_article: Optional[str] = None
    special_category: bool = False

class PrivacyTemplateEngine:
    """
    Comprehensive privacy templates for inference categorization and risk assessment
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.risk_scoring_matrix = self._initialize_risk_matrix()
        
    def _initialize_templates(self) -> Dict[InferenceCategory, PrivacyTemplate]:
        """Initialize comprehensive privacy templates"""
        
        return {
            InferenceCategory.DEMOGRAPHIC: PrivacyTemplate(
                category=InferenceCategory.DEMOGRAPHIC,
                name="Demographic Inference",
                description="Inference of demographic attributes such as age, gender, ethnicity, nationality based on behavioral data, name patterns, or content preferences.",
                risk_level=RiskLevel.MEDIUM,
                regulatory_frameworks=["GDPR", "CCPA", "PIPEDA"],
                potential_harms=[
                    "Discriminatory profiling",
                    "Bias in automated decisions",
                    "Social stereotyping",
                    "Unfair treatment in services"
                ],
                detection_methods=[
                    "Name pattern analysis",
                    "Content consumption preferences",
                    "Language usage patterns",
                    "Social network connections",
                    "Geographic location patterns"
                ],
                recommended_controls=[
                    "Data minimization techniques",
                    "Implement fairness constraints in algorithms",
                    "Regular bias auditing",
                    "Transparent disclosure of inference practices",
                    "User consent for demographic profiling"
                ],
                examples=[
                    "Predicting ethnicity from surname patterns",
                    "Inferring age from music/content preferences",
                    "Guessing gender from communication style",
                    "Nationality inference from language patterns"
                ],
                gdpr_article="Article 9 (if revealing racial/ethnic origin)",
                special_category=False
            ),
            
            InferenceCategory.HEALTH: PrivacyTemplate(
                category=InferenceCategory.HEALTH,
                name="Health Status Inference",
                description="Inference of health conditions, medical history, mental health status, or health risks from digital activity patterns.",
                risk_level=RiskLevel.HIGH,
                regulatory_frameworks=["GDPR Article 9", "HIPAA", "CCPA", "PIPEDA"],
                potential_harms=[
                    "Insurance discrimination",
                    "Employment discrimination",
                    "Social stigmatization",
                    "Mental health privacy violations",
                    "Medical identity theft"
                ],
                detection_methods=[
                    "Health-related search queries",
                    "Medical forum participation",
                    "Symptom-related social media posts",
                    "Medication-related online activity",
                    "Healthcare provider website visits",
                    "Fitness tracker data patterns"
                ],
                recommended_controls=[
                    "Differential privacy implementation",
                    "Explicit informed consent",
                    "Strict data access controls",
                    "Pseudonymization techniques",
                    "Regular data purging",
                    "Medical ethics review"
                ],
                examples=[
                    "Detecting depression from social media sentiment",
                    "Inferring pregnancy from shopping patterns",
                    "Predicting diabetes risk from lifestyle data",
                    "Mental health condition inference from app usage"
                ],
                gdpr_article="Article 9",
                special_category=True
            ),
            
            InferenceCategory.POLITICAL_VIEWS: PrivacyTemplate(
                category=InferenceCategory.POLITICAL_VIEWS,
                name="Political Opinion Inference",
                description="Inference of political affiliations, voting preferences, or ideological beliefs from online behavior and content interactions.",
                risk_level=RiskLevel.HIGH,
                regulatory_frameworks=["GDPR Article 9", "CCPA", "First Amendment protections"],
                potential_harms=[
                    "Political discrimination",
                    "Targeted political manipulation",
                    "Social polarization",
                    "Employment consequences",
                    "Government surveillance risks"
                ],
                detection_methods=[
                    "News source preferences",
                    "Social media engagement patterns",
                    "Political content sharing",
                    "Donation pattern analysis",
                    "Event attendance tracking",
                    "Political figure following patterns"
                ],
                recommended_controls=[
                    "Explicit user consent required",
                    "Transparent political profiling policies",
                    "User control over political data",
                    "Regular deletion of political inferences",
                    "Audit trail for political data use"
                ],
                examples=[
                    "Predicting party preference from news consumption",
                    "Inferring voting behavior from social connections",
                    "Political leaning from content engagement",
                    "Issue stance prediction from online activity"
                ],
                gdpr_article="Article 9",
                special_category=True
            ),
            
            InferenceCategory.RELIGIOUS_BELIEFS: PrivacyTemplate(
                category=InferenceCategory.RELIGIOUS_BELIEFS,
                name="Religious Belief Inference",
                description="Inference of religious affiliation, spiritual beliefs, or philosophical worldviews from behavioral patterns and content preferences.",
                risk_level=RiskLevel.HIGH,
                regulatory_frameworks=["GDPR Article 9", "Religious freedom protections"],
                potential_harms=[
                    "Religious discrimination",
                    "Persecution in certain regions",
                    "Social exclusion",
                    "Employment bias",
                    "Targeted religious manipulation"
                ],
                detection_methods=[
                    "Religious content consumption",
                    "Place of worship location visits",
                    "Religious holiday activity patterns",
                    "Religious text searches",
                    "Community group participation",
                    "Dietary preference patterns"
                ],
                recommended_controls=[
                    "Strong consent mechanisms",
                    "Religious data segregation",
                    "Cultural sensitivity training",
                    "Regular bias assessment",
                    "Religious leader consultation"
                ],
                examples=[
                    "Inferring religion from name patterns",
                    "Detecting faith from dietary restrictions",
                    "Religious affiliation from location patterns",
                    "Spiritual beliefs from content preferences"
                ],
                gdpr_article="Article 9",
                special_category=True
            ),
            
            InferenceCategory.SEXUAL_ORIENTATION: PrivacyTemplate(
                category=InferenceCategory.SEXUAL_ORIENTATION,
                name="Sexual Orientation Inference",
                description="Inference of sexual orientation or preferences from social connections, content consumption, or behavioral patterns.",
                risk_level=RiskLevel.CRITICAL,
                regulatory_frameworks=["GDPR Article 9", "CCPA", "Anti-discrimination laws"],
                potential_harms=[
                    "Severe discrimination risks",
                    "Violence in intolerant regions",
                    "Family relationship damage",
                    "Professional consequences",
                    "Mental health impacts",
                    "Blackmail potential"
                ],
                detection_methods=[
                    "Dating app usage patterns",
                    "LGBTQ+ content engagement",
                    "Social network relationship analysis",
                    "Location-based service patterns",
                    "Community group participation",
                    "Content preference analysis"
                ],
                recommended_controls=[
                    "Strict prohibition of inference",
                    "Enhanced security measures",
                    "User anonymity protection",
                    "Regular security audits",
                    "Legal review requirements",
                    "Ethics committee oversight"
                ],
                examples=[
                    "Inferring orientation from dating app data",
                    "Predicting LGBTQ+ status from content engagement",
                    "Sexual preference from social connections",
                    "Orientation from location patterns"
                ],
                gdpr_article="Article 9",
                special_category=True
            ),
            
            InferenceCategory.FINANCIAL_STATUS: PrivacyTemplate(
                category=InferenceCategory.FINANCIAL_STATUS,
                name="Financial Status Inference",
                description="Inference of income level, financial stability, creditworthiness, or economic status from spending patterns and lifestyle indicators.",
                risk_level=RiskLevel.MEDIUM,
                regulatory_frameworks=["GDPR", "CCPA", "Fair Credit Reporting Act", "FCRA"],
                potential_harms=[
                    "Credit scoring bias",
                    "Financial discrimination",
                    "Predatory lending targeting",
                    "Insurance rate discrimination",
                    "Economic profiling"
                ],
                detection_methods=[
                    "Purchase pattern analysis",
                    "Location-based economic indicators",
                    "Device and technology usage",
                    "Subscription service patterns",
                    "Travel and lifestyle indicators",
                    "Employment history correlation"
                ],
                recommended_controls=[
                    "Financial data encryption",
                    "Limited retention policies",
                    "Access logging and monitoring",
                    "Fairness testing in algorithms",
                    "User control over financial profiling"
                ],
                examples=[
                    "Estimating income from spending patterns",
                    "Creditworthiness from digital behavior",
                    "Wealth status from lifestyle indicators",
                    "Financial stress from behavior changes"
                ]
            ),
            
            InferenceCategory.BEHAVIORAL_PATTERNS: PrivacyTemplate(
                category=InferenceCategory.BEHAVIORAL_PATTERNS,
                name="Behavioral Pattern Analysis",
                description="Inference of habits, routines, lifestyle patterns, and personal characteristics from digital activity tracking.",
                risk_level=RiskLevel.MEDIUM,
                regulatory_frameworks=["GDPR", "CCPA", "ePrivacy Directive"],
                potential_harms=[
                    "Behavioral manipulation",
                    "Addiction exploitation",
                    "Privacy invasion",
                    "Predictive control",
                    "Autonomy reduction"
                ],
                detection_methods=[
                    "App usage time patterns",
                    "Sleep and activity schedules",
                    "Social interaction patterns",
                    "Content consumption habits",
                    "Communication timing analysis",
                    "Location visit frequency"
                ],
                recommended_controls=[
                    "Behavioral data aggregation",
                    "Noise addition to patterns",
                    "User awareness and control",
                    "Regular pattern deletion",
                    "Behavioral ethics review"
                ],
                examples=[
                    "Sleep pattern inference from device usage",
                    "Addiction patterns from app usage",
                    "Social behavior from interaction timing",
                    "Productivity patterns from work habits"
                ]
            ),
            
            InferenceCategory.LOCATION_DATA: PrivacyTemplate(
                category=InferenceCategory.LOCATION_DATA,
                name="Location and Movement Analysis",
                description="Inference of home/work locations, travel patterns, and lifestyle from location-based data and check-ins.",
                risk_level=RiskLevel.HIGH,
                regulatory_frameworks=["GDPR", "CCPA", "Location Privacy Laws"],
                potential_harms=[
                    "Physical security risks",
                    "Stalking facilitation",
                    "Home/work location exposure",
                    "Travel pattern exploitation",
                    "Family safety risks"
                ],
                detection_methods=[
                    "GPS location tracking",
                    "Wi-Fi and Bluetooth beacons",
                    "IP address geolocation",
                    "Check-in and social media posts",
                    "Travel booking patterns",
                    "Time zone activity analysis"
                ],
                recommended_controls=[
                    "Location data minimization",
                    "Geographic generalization",
                    "Temporal data aggregation",
                    "User location controls",
                    "Secure location storage"
                ],
                examples=[
                    "Home address from frequent locations",
                    "Work location from daily patterns",
                    "Travel destinations from bookings",
                    "Lifestyle from location categories"
                ]
            ),
            
            InferenceCategory.PSYCHOLOGICAL_PROFILE: PrivacyTemplate(
                category=InferenceCategory.PSYCHOLOGICAL_PROFILE,
                name="Psychological Profiling",
                description="Inference of personality traits, emotional states, cognitive abilities, and psychological characteristics from digital behavior.",
                risk_level=RiskLevel.HIGH,
                regulatory_frameworks=["GDPR", "Psychological testing regulations"],
                potential_harms=[
                    "Psychological manipulation",
                    "Emotional exploitation",
                    "Mental health stigma",
                    "Personality-based discrimination",
                    "Cognitive bias exploitation"
                ],
                detection_methods=[
                    "Communication style analysis",
                    "Content preference patterns",
                    "Social interaction styles",
                    "Emotional expression analysis",
                    "Decision-making patterns",
                    "Stress indicator detection"
                ],
                recommended_controls=[
                    "Psychological ethics review",
                    "Professional oversight",
                    "User psychological privacy rights",
                    "Transparent profiling disclosure",
                    "Consent for psychological analysis"
                ],
                examples=[
                    "Personality traits from text analysis",
                    "Emotional state from communication patterns",
                    "Cognitive abilities from problem-solving behavior",
                    "Stress levels from activity changes"
                ]
            )
        }
    
    def _initialize_risk_matrix(self) -> Dict[str, Any]:
        """Initialize risk scoring matrix"""
        return {
            "risk_factors": {
                "data_sensitivity": {
                    "special_category": 4,
                    "personal_data": 2,
                    "public_data": 1
                },
                "inference_accuracy": {
                    "high_confidence": 3,
                    "medium_confidence": 2,
                    "low_confidence": 1
                },
                "potential_harm": {
                    "life_threatening": 5,
                    "severe_discrimination": 4,
                    "moderate_harm": 3,
                    "minor_inconvenience": 2,
                    "no_harm": 1
                },
                "regulatory_coverage": {
                    "strict_regulation": 3,
                    "moderate_regulation": 2,
                    "minimal_regulation": 1
                }
            },
            "risk_calculation": {
                "critical": {"min_score": 12, "max_score": 15},
                "high": {"min_score": 9, "max_score": 11},
                "medium": {"min_score": 6, "max_score": 8},
                "low": {"min_score": 3, "max_score": 5},
                "none": {"min_score": 0, "max_score": 2}
            }
        }
    
    def get_template(self, category: InferenceCategory) -> Optional[PrivacyTemplate]:
        """Get privacy template for a specific inference category"""
        return self.templates.get(category)
    
    def get_all_templates(self) -> Dict[InferenceCategory, PrivacyTemplate]:
        """Get all privacy templates"""
        return self.templates
    
    def categorize_inference(self, inference_text: str, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Categorize inferences from analysis results and map to privacy templates
        """
        categorized_inferences = []
        
        # Analyze interests and map to categories
        interests = analysis_results.get('interests', [])
        
        for interest in interests:
            categories = self._map_interest_to_categories(interest)
            for category in categories:
                template = self.get_template(category)
                if template:
                    categorized_inferences.append({
                        'inference': interest,
                        'category': category.value,
                        'template': template,
                        'risk_level': template.risk_level.value,
                        'special_category': template.special_category
                    })
        
        # Analyze other inference types
        economic_indicators = analysis_results.get('economic_indicators', {})
        if economic_indicators:
            template = self.get_template(InferenceCategory.FINANCIAL_STATUS)
            categorized_inferences.append({
                'inference': 'financial_status_indicators',
                'category': InferenceCategory.FINANCIAL_STATUS.value,
                'template': template,
                'risk_level': template.risk_level.value if template else 'medium',
                'special_category': False
            })
        
        # Analyze behavioral patterns
        schedule_patterns = analysis_results.get('schedule_patterns', {})
        if schedule_patterns:
            template = self.get_template(InferenceCategory.BEHAVIORAL_PATTERNS)
            categorized_inferences.append({
                'inference': 'behavioral_patterns',
                'category': InferenceCategory.BEHAVIORAL_PATTERNS.value,
                'template': template,
                'risk_level': template.risk_level.value if template else 'medium',
                'special_category': False
            })
        
        return categorized_inferences
    
    def _map_interest_to_categories(self, interest: str) -> List[InferenceCategory]:
        """Map detected interests to privacy inference categories"""
        
        interest_mapping = {
            'health': [InferenceCategory.HEALTH],
            'fitness': [InferenceCategory.HEALTH, InferenceCategory.BEHAVIORAL_PATTERNS],
            'politics': [InferenceCategory.POLITICAL_VIEWS],
            'religion': [InferenceCategory.RELIGIOUS_BELIEFS],
            'spirituality': [InferenceCategory.RELIGIOUS_BELIEFS],
            'lgbtq': [InferenceCategory.SEXUAL_ORIENTATION],
            'dating': [InferenceCategory.SEXUAL_ORIENTATION],
            'finance': [InferenceCategory.FINANCIAL_STATUS],
            'investment': [InferenceCategory.FINANCIAL_STATUS],
            'psychology': [InferenceCategory.PSYCHOLOGICAL_PROFILE],
            'mental health': [InferenceCategory.HEALTH, InferenceCategory.PSYCHOLOGICAL_PROFILE],
            'location': [InferenceCategory.LOCATION_DATA],
            'travel': [InferenceCategory.LOCATION_DATA, InferenceCategory.FINANCIAL_STATUS]
        }
        
        categories = []
        interest_lower = interest.lower()
        
        for keyword, mapped_categories in interest_mapping.items():
            if keyword in interest_lower:
                categories.extend(mapped_categories)
        
        return list(set(categories))  # Remove duplicates
    
    def calculate_risk_score(self, inference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk score for inference"""
        
        score = 0
        factors = []
        
        # Data sensitivity factor
        if inference_data.get('special_category', False):
            score += self.risk_scoring_matrix['risk_factors']['data_sensitivity']['special_category']
            factors.append('special_category_data')
        else:
            score += self.risk_scoring_matrix['risk_factors']['data_sensitivity']['personal_data']
            factors.append('personal_data')
        
        # Inference confidence factor
        confidence = inference_data.get('confidence', 0.5)
        if confidence > 0.8:
            score += self.risk_scoring_matrix['risk_factors']['inference_accuracy']['high_confidence']
            factors.append('high_confidence_inference')
        elif confidence > 0.5:
            score += self.risk_scoring_matrix['risk_factors']['inference_accuracy']['medium_confidence']
            factors.append('medium_confidence_inference')
        else:
            score += self.risk_scoring_matrix['risk_factors']['inference_accuracy']['low_confidence']
            factors.append('low_confidence_inference')
        
        # Potential harm assessment
        risk_level = inference_data.get('risk_level', 'medium')
        if risk_level == 'critical':
            score += self.risk_scoring_matrix['risk_factors']['potential_harm']['severe_discrimination']
            factors.append('critical_harm_potential')
        elif risk_level == 'high':
            score += self.risk_scoring_matrix['risk_factors']['potential_harm']['moderate_harm']
            factors.append('high_harm_potential')
        else:
            score += self.risk_scoring_matrix['risk_factors']['potential_harm']['minor_inconvenience']
            factors.append('moderate_harm_potential')
        
        # Regulatory coverage
        if inference_data.get('special_category', False):
            score += self.risk_scoring_matrix['risk_factors']['regulatory_coverage']['strict_regulation']
            factors.append('strict_regulatory_coverage')
        else:
            score += self.risk_scoring_matrix['risk_factors']['regulatory_coverage']['moderate_regulation']
            factors.append('moderate_regulatory_coverage')
        
        # Determine final risk level
        final_risk_level = self._score_to_risk_level(score)
        
        return {
            'total_score': score,
            'risk_level': final_risk_level,
            'contributing_factors': factors,
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
    
    def _score_to_risk_level(self, score: int) -> str:
        """Convert numerical score to risk level"""
        for level, range_data in self.risk_scoring_matrix['risk_calculation'].items():
            if range_data['min_score'] <= score <= range_data['max_score']:
                return level
        return 'medium'  # Default fallback
    
    def generate_privacy_report(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive privacy risk report"""
        
        # Categorize all inferences
        categorized_inferences = self.categorize_inference("", analysis_results)
        
        # Calculate risk scores
        risk_assessments = []
        overall_risk_scores = []
        
        for inference in categorized_inferences:
            risk_data = self.calculate_risk_score(inference)
            risk_assessments.append({
                'inference': inference['inference'],
                'category': inference['category'],
                'risk_assessment': risk_data
            })
            overall_risk_scores.append(risk_data['total_score'])
        
        # Calculate overall privacy risk
        avg_risk_score = sum(overall_risk_scores) / len(overall_risk_scores) if overall_risk_scores else 0
        overall_risk_level = self._score_to_risk_level(int(avg_risk_score))
        
        # Identify special category data
        special_categories = [inf for inf in categorized_inferences if inf['special_category']]
        
        # Generate recommendations
        recommendations = self._generate_privacy_recommendations(categorized_inferences, overall_risk_level)
        
        return {
            'overall_risk_level': overall_risk_level,
            'overall_risk_score': avg_risk_score,
            'total_inferences': len(categorized_inferences),
            'special_category_inferences': len(special_categories),
            'categorized_inferences': categorized_inferences,
            'risk_assessments': risk_assessments,
            'special_category_data': special_categories,
            'privacy_recommendations': recommendations,
            'regulatory_compliance': self._assess_regulatory_compliance(categorized_inferences),
            'report_timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_privacy_recommendations(self, inferences: List[Dict], risk_level: str) -> List[str]:
        """Generate privacy recommendations based on inferences and risk level"""
        
        recommendations = []
        
        # Risk-level based recommendations
        if risk_level in ['critical', 'high']:
            recommendations.extend([
                "Immediate privacy settings review required",
                "Consider limiting data sharing across platforms",
                "Enable maximum privacy controls on all accounts",
                "Review and delete unnecessary personal information"
            ])
        
        # Category-specific recommendations
        categories_found = set(inf['category'] for inf in inferences)
        
        if 'health' in categories_found:
            recommendations.append("Health-related inferences detected - review medical privacy settings")
        
        if 'political_views' in categories_found:
            recommendations.append("Political preferences may be inferable - consider limiting political content engagement")
        
        if 'financial_status' in categories_found:
            recommendations.append("Financial information may be exposed - review spending and lifestyle sharing")
        
        if 'location_data' in categories_found:
            recommendations.append("Location patterns detected - disable location sharing where possible")
        
        # Special category data recommendations
        special_categories = [inf for inf in inferences if inf.get('special_category')]
        if special_categories:
            recommendations.extend([
                "Special category data inferences detected - enhanced privacy protection recommended",
                "Consider using privacy-focused services and tools",
                "Review data processing consents and withdraw where possible"
            ])
        
        return recommendations
    
    def _assess_regulatory_compliance(self, inferences: List[Dict]) -> Dict[str, Any]:
        """Assess regulatory compliance requirements"""
        
        applicable_regulations = set()
        compliance_requirements = []
        
        for inference in inferences:
            if inference.get('template'):
                regulations = inference['template'].regulatory_frameworks
                applicable_regulations.update(regulations)
        
        # Generate compliance requirements
        if 'GDPR Article 9' in applicable_regulations:
            compliance_requirements.append({
                'regulation': 'GDPR Article 9',
                'requirement': 'Special category data processing requires explicit consent or other legal basis',
                'risk_level': 'high'
            })
        
        if 'HIPAA' in applicable_regulations:
            compliance_requirements.append({
                'regulation': 'HIPAA',
                'requirement': 'Health information requires additional security safeguards',
                'risk_level': 'high'
            })
        
        return {
            'applicable_regulations': list(applicable_regulations),
            'compliance_requirements': compliance_requirements,
            'compliance_risk_level': 'high' if any(req['risk_level'] == 'high' for req in compliance_requirements) else 'medium'
        }

def create_privacy_template_engine():
    """Factory function to create privacy template engine"""
    return PrivacyTemplateEngine()