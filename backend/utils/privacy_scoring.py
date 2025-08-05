import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Tuple
import math
import logging

logger = logging.getLogger(__name__)

class AdvancedPrivacyScoring:
    """
    Advanced Privacy Scoring System with multiple risk assessment algorithms
    """
    
    def __init__(self):
        self.initialize_scoring_weights()
        self.initialize_risk_matrices()
        
    def initialize_scoring_weights(self):
        """Initialize weights for different privacy factors"""
        self.weights = {
            'data_exposure': 0.25,      # How much personal data is exposed
            'correlation_risk': 0.20,   # Risk of cross-platform correlation
            'behavioral_patterns': 0.15, # Predictable behavior patterns
            'economic_inference': 0.15,  # Economic status inferability
            'social_patterns': 0.10,     # Social behavior analysis
            'communication_style': 0.10, # Communication patterns
            'temporal_patterns': 0.05    # Time-based patterns
        }
        
    def initialize_risk_matrices(self):
        """Initialize risk assessment matrices"""
        
        # Platform risk scores (higher = more privacy risk)
        self.platform_risks = {
            'facebook': 9.0,      # High personal information sharing
            'instagram': 8.0,     # Visual lifestyle exposure
            'linkedin': 6.0,      # Professional information
            'twitter': 7.0,       # Public opinions and thoughts
            'x': 7.0,            # Same as Twitter
            'github': 4.0,        # Technical but less personal
            'tiktok': 8.5,       # High algorithmic profiling
            'snapchat': 6.5,     # Temporary but location-heavy
            'youtube': 5.0,      # Interest-based but less personal
            'pinterest': 5.5,    # Interest and lifestyle patterns
            'reddit': 6.0,       # Anonymous but behavior patterns
            'discord': 4.5,      # Gaming/community focused
        }
        
        # Data type sensitivity scores
        self.data_sensitivity = {
            'location': 9.0,
            'financial': 10.0,
            'health': 10.0,
            'relationships': 8.0,
            'political_views': 8.5,
            'employment': 7.0,
            'education': 6.0,
            'interests': 5.0,
            'schedule': 7.5,
            'communication_style': 4.0
        }
        
        # Behavioral predictability scores
        self.predictability_factors = {
            'posting_schedule': 7.0,
            'location_patterns': 9.0,
            'interaction_patterns': 6.0,
            'content_consistency': 5.0,
            'response_timing': 6.5
        }
    
    def calculate_comprehensive_privacy_score(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive privacy score using multiple algorithms
        """
        
        # Extract components for analysis
        interests = analysis_results.get('interests', [])
        schedule_patterns = analysis_results.get('schedule_patterns', {})
        economic_indicators = analysis_results.get('economic_indicators', {})
        mental_state = analysis_results.get('mental_state', {})
        data_sources = analysis_results.get('data_sources', [])
        ml_analysis = analysis_results.get('ml_analysis', {})
        
        # Calculate individual risk scores
        risk_scores = {
            'data_exposure': self._calculate_data_exposure_risk(
                interests, schedule_patterns, economic_indicators, mental_state
            ),
            'correlation_risk': self._calculate_correlation_risk(data_sources),
            'behavioral_patterns': self._calculate_behavioral_risk(
                schedule_patterns, ml_analysis
            ),
            'economic_inference': self._calculate_economic_risk(economic_indicators),
            'social_patterns': self._calculate_social_risk(mental_state, ml_analysis),
            'communication_style': self._calculate_communication_risk(mental_state, ml_analysis),
            'temporal_patterns': self._calculate_temporal_risk(schedule_patterns)
        }
        
        # Calculate weighted overall score
        overall_score = self._calculate_weighted_score(risk_scores)
        
        # Calculate confidence intervals
        confidence_intervals = self._calculate_confidence_intervals(risk_scores, analysis_results)
        
        # Generate risk breakdown
        risk_breakdown = self._generate_risk_breakdown(risk_scores)
        
        # Calculate privacy improvement potential
        improvement_potential = self._calculate_improvement_potential(risk_scores)
        
        return {
            'overall_privacy_score': overall_score,
            'risk_scores': risk_scores,
            'confidence_intervals': confidence_intervals,
            'risk_breakdown': risk_breakdown,
            'improvement_potential': improvement_potential,
            'privacy_grade': self._assign_privacy_grade(overall_score),
            'critical_risks': self._identify_critical_risks(risk_scores),
            'scoring_metadata': {
                'algorithm_version': '2.0',
                'calculation_timestamp': datetime.utcnow().isoformat(),
                'weights_used': self.weights
            }
        }
    
    def _calculate_data_exposure_risk(self, interests: List[str], schedule_patterns: Dict, 
                                    economic_indicators: Dict, mental_state: Dict) -> float:
        """Calculate risk based on amount and sensitivity of exposed data"""
        
        exposure_score = 0.0
        max_score = 10.0
        
        # Interest exposure (more interests = higher risk)
        interest_risk = min(len(interests) * 0.3, 3.0)
        exposure_score += interest_risk
        
        # Schedule pattern exposure
        schedule_risk = len(schedule_patterns) * 0.5
        exposure_score += min(schedule_risk, 2.5)
        
        # Economic data exposure
        economic_risk = len(economic_indicators) * 0.4
        exposure_score += min(economic_risk, 2.5)
        
        # Mental state/personal info exposure
        mental_risk = len(mental_state) * 0.3
        exposure_score += min(mental_risk, 2.0)
        
        # Normalize to 1-10 scale (inverted - lower exposure = higher privacy score)
        privacy_score = max_score - min(exposure_score, max_score - 1)
        return round(privacy_score, 2)
    
    def _calculate_correlation_risk(self, data_sources: List[str]) -> float:
        """Calculate risk of cross-platform data correlation"""
        
        if not data_sources:
            return 10.0  # High privacy if no sources
        
        # Calculate platform diversity risk
        unique_platforms = len(set(source.lower() for source in data_sources))
        platform_risk = min(unique_platforms * 1.5, 8.0)
        
        # Calculate weighted risk based on platform types
        weighted_risk = 0.0
        total_weight = 0.0
        
        for source in data_sources:
            platform_name = self._extract_platform_name(source)
            if platform_name in self.platform_risks:
                risk = self.platform_risks[platform_name]
                weighted_risk += risk
                total_weight += 1.0
        
        if total_weight > 0:
            avg_platform_risk = weighted_risk / total_weight
            # Combine platform diversity and individual platform risks
            correlation_risk = (platform_risk * 0.4) + (avg_platform_risk * 0.6)
        else:
            correlation_risk = platform_risk
        
        # Convert to privacy score (invert)
        privacy_score = 10.0 - min(correlation_risk, 9.0)
        return round(privacy_score, 2)
    
    def _extract_platform_name(self, source: str) -> str:
        """Extract platform name from data source string"""
        source_lower = source.lower()
        for platform in self.platform_risks.keys():
            if platform in source_lower:
                return platform
        return 'unknown'
    
    def _calculate_behavioral_risk(self, schedule_patterns: Dict, ml_analysis: Dict) -> float:
        """Calculate risk based on behavioral predictability"""
        
        behavioral_risk = 0.0
        
        # Schedule predictability
        if schedule_patterns:
            schedule_predictability = len(schedule_patterns) * 1.2
            behavioral_risk += min(schedule_predictability, 4.0)
        
        # ML-detected behavioral patterns
        if ml_analysis:
            behavioral_data = ml_analysis.get('behavioral_patterns', {})
            if isinstance(behavioral_data, dict):
                patterns = behavioral_data.get('patterns', {})
                if patterns:
                    ml_risk = len(patterns) * 0.8
                    behavioral_risk += min(ml_risk, 3.0)
        
        # Communication consistency (from ML analysis)
        comm_data = ml_analysis.get('communication_style', {})
        if comm_data and comm_data.get('style') != 'unknown':
            behavioral_risk += 1.5  # Consistent style = more predictable
        
        # Convert to privacy score
        privacy_score = 10.0 - min(behavioral_risk, 9.0)
        return round(privacy_score, 2)
    
    def _calculate_economic_risk(self, economic_indicators: Dict) -> float:
        """Calculate risk of economic status inference"""
        
        if not economic_indicators:
            return 10.0  # High privacy if no economic data
        
        # Count sensitive economic indicators
        sensitive_indicators = [
            'employment_status', 'income_level', 'luxury_brands', 
            'investment_terms', 'professional_network'
        ]
        
        risk_count = 0
        for indicator in sensitive_indicators:
            if any(indicator in key.lower() for key in economic_indicators.keys()):
                risk_count += 1
        
        # Additional risk for specific patterns
        economic_risk = risk_count * 1.5
        
        # Check for high-risk economic patterns
        if any('luxury' in str(value).lower() for value in economic_indicators.values()):
            economic_risk += 2.0
        
        if any('investment' in str(value).lower() for value in economic_indicators.values()):
            economic_risk += 1.5
        
        # Convert to privacy score
        privacy_score = 10.0 - min(economic_risk, 9.0)
        return round(privacy_score, 2)
    
    def _calculate_social_risk(self, mental_state: Dict, ml_analysis: Dict) -> float:
        """Calculate risk based on social behavior patterns"""
        
        social_risk = 0.0
        
        # Social engagement indicators
        social_indicators = [
            'social_engagement', 'networking_activity', 'family_connections',
            'personal_sharing', 'social_orientation'
        ]
        
        for indicator in social_indicators:
            if any(indicator in key.lower() for key in mental_state.keys()):
                social_risk += 0.8
        
        # ML-detected social patterns
        if ml_analysis:
            social_data = ml_analysis.get('social_patterns', {})
            if social_data and social_data.get('orientation') != 'unknown':
                social_risk += 1.2
        
        # Convert to privacy score
        privacy_score = 10.0 - min(social_risk, 9.0)
        return round(privacy_score, 2)
    
    def _calculate_communication_risk(self, mental_state: Dict, ml_analysis: Dict) -> float:
        """Calculate risk based on communication style patterns"""
        
        comm_risk = 0.0
        
        # Communication style indicators from mental state
        comm_indicators = [
            'communication_style', 'sentiment', 'primary_emotion'
        ]
        
        for indicator in comm_indicators:
            if indicator in mental_state:
                comm_risk += 0.6
        
        # ML communication analysis
        if ml_analysis:
            comm_data = ml_analysis.get('communication_style', {})
            if comm_data:
                style = comm_data.get('style', 'unknown')
                if style != 'unknown':
                    comm_risk += 1.0
                
                # Formal communication is less risky than informal
                if style == 'formal':
                    comm_risk -= 0.5
                elif style == 'casual':
                    comm_risk += 0.5
        
        # Convert to privacy score
        privacy_score = 10.0 - min(comm_risk, 9.0)
        return round(privacy_score, 2)
    
    def _calculate_temporal_risk(self, schedule_patterns: Dict) -> float:
        """Calculate risk based on temporal patterns"""
        
        if not schedule_patterns:
            return 10.0  # High privacy if no temporal data
        
        # Time-based predictability
        temporal_indicators = [
            'active_hours', 'posting_frequency', 'coding_activity', 
            'content_creation', 'work_pattern'
        ]
        
        temporal_risk = 0.0
        for pattern_key in schedule_patterns.keys():
            for indicator in temporal_indicators:
                if indicator in pattern_key.lower():
                    temporal_risk += 1.0
                    break
        
        # Convert to privacy score
        privacy_score = 10.0 - min(temporal_risk, 9.0)
        return round(privacy_score, 2)
    
    def _calculate_weighted_score(self, risk_scores: Dict[str, float]) -> float:
        """Calculate weighted overall privacy score"""
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for category, score in risk_scores.items():
            if category in self.weights:
                weight = self.weights[category]
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 5.0  # Default neutral score
        
        overall_score = weighted_sum / total_weight
        return round(overall_score, 2)
    
    def _calculate_confidence_intervals(self, risk_scores: Dict[str, float], 
                                      analysis_results: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
        """Calculate confidence intervals for risk scores"""
        
        confidence_intervals = {}
        
        # Base confidence on data availability and ML confidence
        base_confidence = 0.8
        
        # Adjust confidence based on ML analysis availability
        if 'ml_analysis' in analysis_results:
            ml_confidence = analysis_results['ml_analysis'].get('confidence_scores', {}).get('overall', 0.5)
            base_confidence = (base_confidence + ml_confidence) / 2
        
        # Calculate intervals for each risk category
        for category, score in risk_scores.items():
            margin = (1 - base_confidence) * 2  # ±2 points max uncertainty
            lower_bound = max(1.0, score - margin)
            upper_bound = min(10.0, score + margin)
            confidence_intervals[category] = (round(lower_bound, 2), round(upper_bound, 2))
        
        return confidence_intervals
    
    def _generate_risk_breakdown(self, risk_scores: Dict[str, float]) -> Dict[str, str]:
        """Generate human-readable risk breakdown"""
        
        risk_breakdown = {}
        
        for category, score in risk_scores.items():
            if score >= 8.0:
                risk_level = "Low Risk"
                description = "Good privacy protection in this area."
            elif score >= 6.0:
                risk_level = "Moderate Risk"
                description = "Some privacy concerns that could be improved."
            elif score >= 4.0:
                risk_level = "High Risk"
                description = "Significant privacy vulnerabilities detected."
            else:
                risk_level = "Critical Risk"
                description = "Immediate action needed to protect privacy."
            
            risk_breakdown[category] = {
                'risk_level': risk_level,
                'description': description,
                'score': score
            }
        
        return risk_breakdown
    
    def _calculate_improvement_potential(self, risk_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate potential for privacy improvement in each area"""
        
        improvement_potential = {}
        
        for category, score in risk_scores.items():
            # Lower scores have higher improvement potential
            if score < 4.0:
                potential = 8.0  # High potential for improvement
            elif score < 6.0:
                potential = 6.0  # Moderate potential
            elif score < 8.0:
                potential = 4.0  # Some potential
            else:
                potential = 2.0  # Limited potential (already good)
            
            improvement_potential[category] = potential
        
        return improvement_potential
    
    def _assign_privacy_grade(self, overall_score: float) -> str:
        """Assign letter grade based on overall privacy score"""
        
        if overall_score >= 9.0:
            return "A+"
        elif overall_score >= 8.5:
            return "A"
        elif overall_score >= 8.0:
            return "A-"
        elif overall_score >= 7.5:
            return "B+"
        elif overall_score >= 7.0:
            return "B"
        elif overall_score >= 6.5:
            return "B-"
        elif overall_score >= 6.0:
            return "C+"
        elif overall_score >= 5.5:
            return "C"
        elif overall_score >= 5.0:
            return "C-"
        elif overall_score >= 4.5:
            return "D+"
        elif overall_score >= 4.0:
            return "D"
        else:
            return "F"
    
    def _identify_critical_risks(self, risk_scores: Dict[str, float]) -> List[str]:
        """Identify areas with critical privacy risks"""
        
        critical_risks = []
        
        for category, score in risk_scores.items():
            if score < 4.0:  # Critical threshold
                critical_risks.append(category)
        
        return critical_risks

def create_privacy_scoring_system():
    """Factory function to create privacy scoring system"""
    return AdvancedPrivacyScoring()
