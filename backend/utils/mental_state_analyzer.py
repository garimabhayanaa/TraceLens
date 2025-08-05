import logging
import re
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

@dataclass
class LanguagePattern:
    """Language pattern analysis result"""
    complexity_score: float  # 0-1, higher = more complex language
    formality_level: str  # 'very_formal', 'formal', 'neutral', 'informal', 'very_informal'
    cognitive_load_indicators: List[str]
    linguistic_markers: Dict[str, float]  # Various linguistic markers
    vocabulary_diversity: float
    sentence_structure_complexity: float
    temporal_references: Dict[str, int]  # past, present, future focus

@dataclass
class EmojiUsagePattern:
    """Emoji usage pattern analysis"""
    emoji_frequency: float  # Emojis per message
    emotional_emoji_ratio: float  # Ratio of emotional vs neutral emojis
    dominant_emoji_categories: List[str]  # Most used emoji categories
    emoji_sentiment_distribution: Dict[str, float]
    emoji_complexity: str  # 'simple', 'moderate', 'complex'
    emoji_consistency: float  # How consistent emoji usage is
    mental_state_indicators: List[str]  # Potential mental state indicators

@dataclass
class SocialInteractionFrequency:
    """Social interaction frequency analysis"""
    interaction_rate: float  # Interactions per time period
    interaction_types: Dict[str, int]  # mentions, replies, shares, etc.
    social_engagement_level: str  # 'high', 'medium', 'low', 'isolated'
    reciprocity_score: float  # How much user reciprocates interactions
    social_network_diversity: float
    isolation_indicators: List[str]
    social_energy_pattern: str  # 'consistent', 'declining', 'irregular'

@dataclass
class ContentToneAnalysis:
    """Content tone analysis result"""
    overall_tone: str  # 'positive', 'negative', 'neutral', 'mixed'
    tone_consistency: float  # How consistent the tone is
    emotional_volatility: float  # How much emotional state varies
    tone_progression: List[float]  # Tone changes over time
    dominant_emotions: List[str]
    stress_indicators: List[str]
    wellbeing_indicators: List[str]
    tone_stability_score: float

@dataclass
class MentalHealthRiskFactors:
    """Mental health risk factor assessment"""
    depression_indicators: Dict[str, float]
    anxiety_indicators: Dict[str, float]
    stress_indicators: Dict[str, float]
    social_withdrawal_score: float
    emotional_regulation_score: float
    cognitive_function_indicators: Dict[str, float]
    crisis_warning_signals: List[str]
    protective_factors: List[str]

@dataclass
class MentalStateProfile:
    """Comprehensive mental state profile"""
    overall_mental_state: str  # 'positive', 'stable', 'concerning', 'critical'
    emotional_stability_score: float
    social_connectivity_level: str
    cognitive_function_level: str
    stress_level: str  # 'low', 'moderate', 'high', 'severe'
    wellbeing_trajectory: str  # 'improving', 'stable', 'declining'
    resilience_indicators: List[str]
    support_system_strength: float

@dataclass
class MentalStateAssessmentResult:
    """Complete mental state assessment"""
    language_patterns: LanguagePattern
    emoji_patterns: EmojiUsagePattern
    social_interaction: SocialInteractionFrequency
    content_tone: ContentToneAnalysis
    risk_factors: MentalHealthRiskFactors
    mental_state_profile: MentalStateProfile
    assessment_confidence: float
    recommendations: List[str]
    privacy_considerations: List[str]

class LanguagePatternAnalyzer:
    """Analyzes language patterns for mental state indicators"""
    
    def __init__(self):
        # Cognitive load indicators
        self.cognitive_load_markers = {
            'high_complexity': ['moreover', 'furthermore', 'consequently', 'nevertheless', 'notwithstanding'],
            'low_complexity': ['so', 'but', 'and', 'then', 'now'],
            'uncertainty': ['maybe', 'perhaps', 'possibly', 'might', 'could be', 'not sure'],
            'certainty': ['definitely', 'absolutely', 'certainly', 'obviously', 'clearly']
        }
        
        # Temporal reference patterns
        self.temporal_markers = {
            'past_focused': ['was', 'were', 'had', 'used to', 'before', 'yesterday', 'last week'],
            'present_focused': ['am', 'is', 'are', 'now', 'today', 'currently', 'right now'],
            'future_focused': ['will', 'going to', 'tomorrow', 'next', 'plan to', 'hope to']
        }
        
        # Linguistic markers for mental state
        self.mental_state_markers = {
            'depression_language': ['tired', 'exhausted', 'hopeless', 'worthless', 'empty', 'numb'],
            'anxiety_language': ['worried', 'anxious', 'nervous', 'scared', 'overwhelmed', 'panic'],
            'stress_language': ['pressure', 'burden', 'overwhelmed', 'stressed', 'chaotic', 'hectic'],
            'positive_language': ['grateful', 'blessed', 'excited', 'happy', 'content', 'peaceful']
        }
    
    def analyze_language_patterns(self, content_data: List[Dict[str, Any]]) -> LanguagePattern:
        """Analyze language patterns from content"""
        
        if not content_data:
            return self._create_empty_language_pattern()
        
        all_text = []
        for content in content_data:
            text = content.get('text', content.get('content', ''))
            if text and len(text.strip()) > 10:
                all_text.append(text.lower())
        
        if not all_text:
            return self._create_empty_language_pattern()
        
        combined_text = ' '.join(all_text)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(combined_text)
        
        # Determine formality level
        formality_level = self._determine_formality_level(combined_text)
        
        # Identify cognitive load indicators
        cognitive_load_indicators = self._identify_cognitive_load_indicators(combined_text)
        
        # Calculate linguistic markers
        linguistic_markers = self._calculate_linguistic_markers(combined_text)
        
        # Calculate vocabulary diversity
        vocabulary_diversity = self._calculate_vocabulary_diversity(combined_text)
        
        # Calculate sentence structure complexity
        sentence_complexity = self._calculate_sentence_complexity(all_text)
        
        # Analyze temporal references
        temporal_references = self._analyze_temporal_references(combined_text)
        
        return LanguagePattern(
            complexity_score=complexity_score,
            formality_level=formality_level,
            cognitive_load_indicators=cognitive_load_indicators,
            linguistic_markers=linguistic_markers,
            vocabulary_diversity=vocabulary_diversity,
            sentence_structure_complexity=sentence_complexity,
            temporal_references=temporal_references
        )
    
    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate language complexity score"""
        
        if not text:
            return 0.0
        
        words = text.split()
        if len(words) == 0:
            return 0.0
        
        # Average word length
        avg_word_length = np.mean([len(word) for word in words])
        
        # Sentence length variation
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_sentence_length = np.mean(sentence_lengths)
            sentence_length_variation = np.std(sentence_lengths) if len(sentence_lengths) > 1 else 0
        else:
            avg_sentence_length = 0
            sentence_length_variation = 0
        
        # Complex word ratio (words > 6 characters)
        complex_words = [word for word in words if len(word) > 6]
        complex_word_ratio = len(complex_words) / len(words)
        
        # Normalize and combine factors
        complexity_factors = [
            min(avg_word_length / 8, 1.0),  # Normalize to 8 chars max
            min(avg_sentence_length / 25, 1.0),  # Normalize to 25 words max
            min(sentence_length_variation / 10, 1.0),  # Normalize variation
            complex_word_ratio
        ]
        
        return np.mean(complexity_factors)
    
    def _determine_formality_level(self, text: str) -> str:
        """Determine formality level of language"""
        
        formal_indicators = ['furthermore', 'moreover', 'consequently', 'therefore', 'however']
        informal_indicators = ['gonna', 'wanna', 'yeah', 'nah', 'cool', 'awesome', 'lol']
        contractions = ["don't", "won't", "can't", "isn't", "aren't", "wasn't", "weren't"]
        
        formal_count = sum(1 for indicator in formal_indicators if indicator in text)
        informal_count = sum(1 for indicator in informal_indicators if indicator in text)
        contraction_count = sum(1 for contraction in contractions if contraction in text)
        
        total_words = len(text.split())
        if total_words == 0:
            return 'neutral'
        
        formal_ratio = formal_count / total_words
        informal_ratio = (informal_count + contraction_count) / total_words
        
        if formal_ratio > 0.02:
            return 'very_formal' if formal_ratio > 0.05 else 'formal'
        elif informal_ratio > 0.02:
            return 'very_informal' if informal_ratio > 0.05 else 'informal'
        else:
            return 'neutral'
    
    def _identify_cognitive_load_indicators(self, text: str) -> List[str]:
        """Identify cognitive load indicators in text"""
        
        indicators = []
        
        for category, markers in self.cognitive_load_markers.items():
            if any(marker in text for marker in markers):
                indicators.append(category)
        
        # Additional cognitive load indicators
        if len(re.findall(r'\([^)]*\)', text)) > 2:  # Many parentheses
            indicators.append('detailed_elaboration')
        
        if len(re.findall(r',', text)) / len(text.split()) > 0.1:  # Many commas
            indicators.append('complex_sentence_structure')
        
        return indicators
    
    def _calculate_linguistic_markers(self, text: str) -> Dict[str, float]:
        """Calculate various linguistic markers"""
        
        markers = {}
        total_words = len(text.split())
        
        if total_words == 0:
            return {}
        
        for category, words in self.mental_state_markers.items():
            count = sum(1 for word in words if word in text)
            markers[category] = count / total_words
        
        # First person pronoun usage (self-focus)
        first_person_pronouns = ['i', 'me', 'my', 'myself', 'mine']
        first_person_count = sum(1 for pronoun in first_person_pronouns 
                               if f' {pronoun} ' in f' {text} ')
        markers['self_focus'] = first_person_count / total_words
        
        # Negative emotion words
        negative_words = ['sad', 'angry', 'frustrated', 'disappointed', 'upset', 'hurt']
        negative_count = sum(1 for word in negative_words if word in text)
        markers['negative_emotion'] = negative_count / total_words
        
        # Social connection words
        social_words = ['friend', 'family', 'together', 'we', 'us', 'our', 'shared']
        social_count = sum(1 for word in social_words if word in text)
        markers['social_connection'] = social_count / total_words
        
        return markers
    
    def _calculate_vocabulary_diversity(self, text: str) -> float:
        """Calculate vocabulary diversity (type-token ratio)"""
        
        words = [word.strip('.,!?";:') for word in text.split()]
        words = [word for word in words if word and len(word) > 2]
        
        if len(words) == 0:
            return 0.0
        
        unique_words = set(words)
        return len(unique_words) / len(words)
    
    def _calculate_sentence_complexity(self, texts: List[str]) -> float:
        """Calculate sentence structure complexity"""
        
        if not texts:
            return 0.0
        
        complexity_scores = []
        
        for text in texts:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentences:
                for sentence in sentences:
                    # Count clauses (approximated by conjunctions)
                    conjunctions = ['and', 'but', 'or', 'because', 'since', 'while', 'although']
                    clause_count = 1 + sum(1 for conj in conjunctions if conj in sentence.lower())
                    
                    # Normalize clause count
                    complexity_scores.append(min(clause_count / 5, 1.0))
        
        return np.mean(complexity_scores) if complexity_scores else 0.0
    
    def _analyze_temporal_references(self, text: str) -> Dict[str, int]:
        """Analyze temporal reference patterns"""
        
        temporal_counts = {'past': 0, 'present': 0, 'future': 0}
        
        for focus, markers in self.temporal_markers.items():
            count = sum(1 for marker in markers if marker in text)
            if focus == 'past_focused':
                temporal_counts['past'] = count
            elif focus == 'present_focused':
                temporal_counts['present'] = count
            elif focus == 'future_focused':
                temporal_counts['future'] = count
        
        return temporal_counts
    
    def _create_empty_language_pattern(self) -> LanguagePattern:
        """Create empty language pattern for no data case"""
        
        return LanguagePattern(
            complexity_score=0.0,
            formality_level='neutral',
            cognitive_load_indicators=[],
            linguistic_markers={},
            vocabulary_diversity=0.0,
            sentence_structure_complexity=0.0,
            temporal_references={'past': 0, 'present': 0, 'future': 0}
        )

class EmojiPatternAnalyzer:
    """Analyzes emoji usage patterns for emotional state indicators"""
    
    def __init__(self):
        # Emoji categories for mental state analysis
        self.emoji_categories = {
            'positive_emotion': ['😊', '😄', '😃', '🙂', '😌', '🥰', '😍', '🤗', '🎉', '🎊', '❤️', '💖'],
            'negative_emotion': ['😢', '😭', '😞', '😔', '😟', '😨', '😰', '😱', '💔', '😩', '😫', '😤'],
            'anxiety_stress': ['😰', '😨', '😱', '🤯', '😵', '🤪', '😖', '😣', '😤', '😠'],
            'depression_indicators': ['😢', '😭', '😞', '😔', '💔', '😪', '😴', '🖤', '⚫', '😑'],
            'social_positive': ['🤗', '👥', '👫', '👬', '👭', '🤝', '👋', '🙏', '💕', '🥰'],
            'isolation_indicators': ['😶', '😐', '😑', '🤐', '😞', '😔', '🚪', '🏠', '🛏️'],
            'energy_high': ['⚡', '🔥', '💪', '🚀', '⭐', '✨', '🌟', '💫', '🎯', '🏆'],
            'energy_low': ['😴', '😪', '🥱', '😑', '😐', '🔋', '📉', '⬇️', '💤'],
            'health_wellness': ['🏃', '🧘', '🍃', '🌱', '💚', '✅', '👍', '💯', '🎯'],
            'crisis_warning': ['🆘', '⚠️', '🚨', '💀', '⚰️', '🔪', '💊', '🍷', '🚬']
        }
        
        # Emoji complexity levels
        self.emoji_complexity = {
            'simple': ['😊', '😢', '❤️', '👍', '👎', '😍', '😭', '🙂'],
            'moderate': ['🤗', '😌', '🥰', '😰', '🤯', '😱', '💔', '✨'],
            'complex': ['🧘‍♀️', '🤷‍♂️', '💆‍♀️', '🏃‍♂️', '🧠', '🔄', '⚖️', '🎭']
        }
    
    def analyze_emoji_patterns(self, content_data: List[Dict[str, Any]]) -> EmojiUsagePattern:
        """Analyze emoji usage patterns"""
        
        if not content_data:
            return self._create_empty_emoji_pattern()
        
        all_emojis = []
        total_messages = 0
        
        # Extract all emojis from content
        for content in content_data:
            text = content.get('text', content.get('content', ''))
            if text:
                total_messages += 1
                emojis = self._extract_emojis(text)
                all_emojis.extend(emojis)
        
        if not all_emojis or total_messages == 0:
            return self._create_empty_emoji_pattern()
        
        # Calculate emoji frequency
        emoji_frequency = len(all_emojis) / total_messages
        
        # Analyze emoji categories
        category_counts = defaultdict(int)
        for emoji in all_emojis:
            for category, emoji_list in self.emoji_categories.items():
                if emoji in emoji_list:
                    category_counts[category] += 1
        
        # Calculate emotional emoji ratio
        emotional_emojis = (category_counts['positive_emotion'] + 
                          category_counts['negative_emotion'] + 
                          category_counts['anxiety_stress'] + 
                          category_counts['depression_indicators'])
        emotional_emoji_ratio = emotional_emojis / len(all_emojis) if all_emojis else 0
        
        # Determine dominant categories
        dominant_categories = sorted(category_counts.items(), 
                                   key=lambda x: x[1], reverse=True)[:3]
        dominant_category_names = [cat[0] for cat in dominant_categories if cat[1] > 0]
        
        # Calculate emoji sentiment distribution
        sentiment_distribution = self._calculate_emoji_sentiment_distribution(category_counts, len(all_emojis))
        
        # Determine emoji complexity
        emoji_complexity = self._determine_emoji_complexity(all_emojis)
        
        # Calculate emoji consistency
        emoji_consistency = self._calculate_emoji_consistency(all_emojis)
        
        # Identify mental state indicators
        mental_state_indicators = self._identify_mental_state_indicators(category_counts)
        
        return EmojiUsagePattern(
            emoji_frequency=emoji_frequency,
            emotional_emoji_ratio=emotional_emoji_ratio,
            dominant_emoji_categories=dominant_category_names,
            emoji_sentiment_distribution=sentiment_distribution,
            emoji_complexity=emoji_complexity,
            emoji_consistency=emoji_consistency,
            mental_state_indicators=mental_state_indicators
        )
    
    def _extract_emojis(self, text: str) -> List[str]:
        """Extract emojis from text using regex"""
        
        # Simple emoji pattern - in a real implementation, use a proper emoji library
        emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|'  # emoticons
            r'[\U0001F300-\U0001F5FF]|'  # symbols & pictographs
            r'[\U0001F680-\U0001F6FF]|'  # transport & map symbols
            r'[\U0001F1E0-\U0001F1FF]|'  # flags
            r'[\U00002702-\U000027B0]|'  # dingbats
            r'[\U000024C2-\U0001F251]'   # enclosed characters
        )
        
        return emoji_pattern.findall(text)
    
    def _calculate_emoji_sentiment_distribution(self, category_counts: Dict[str, int], 
                                              total_emojis: int) -> Dict[str, float]:
        """Calculate emoji sentiment distribution"""
        
        if total_emojis == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
        
        positive_count = (category_counts['positive_emotion'] + 
                         category_counts['social_positive'] + 
                         category_counts['energy_high'] + 
                         category_counts['health_wellness'])
        
        negative_count = (category_counts['negative_emotion'] + 
                         category_counts['anxiety_stress'] + 
                         category_counts['depression_indicators'] + 
                         category_counts['isolation_indicators'] + 
                         category_counts['energy_low'])
        
        neutral_count = total_emojis - positive_count - negative_count
        
        return {
            'positive': positive_count / total_emojis,
            'negative': negative_count / total_emojis,
            'neutral': max(0, neutral_count / total_emojis)
        }
    
    def _determine_emoji_complexity(self, emojis: List[str]) -> str:
        """Determine emoji complexity level"""
        
        if not emojis:
            return 'simple'
        
        complexity_scores = []
        
        for emoji in emojis:
            if any(emoji in emoji_list for emoji_list in [self.emoji_complexity['complex']]):
                complexity_scores.append(3)
            elif any(emoji in emoji_list for emoji_list in [self.emoji_complexity['moderate']]):
                complexity_scores.append(2)
            else:
                complexity_scores.append(1)
        
        avg_complexity = np.mean(complexity_scores)
        
        if avg_complexity > 2.5:
            return 'complex'
        elif avg_complexity > 1.5:
            return 'moderate'
        else:
            return 'simple'
    
    def _calculate_emoji_consistency(self, emojis: List[str]) -> float:
        """Calculate how consistent emoji usage is"""
        
        if len(emojis) <= 1:
            return 1.0
        
        emoji_counts = Counter(emojis)
        unique_emojis = len(emoji_counts)
        total_emojis = len(emojis)
        
        # Higher consistency = fewer unique emojis relative to total
        consistency = 1.0 - (unique_emojis / total_emojis)
        return max(0.0, consistency)
    
    def _identify_mental_state_indicators(self, category_counts: Dict[str, int]) -> List[str]:
        """Identify potential mental state indicators from emoji usage"""
        
        indicators = []
        total_emotional_emojis = sum(category_counts.values())
        
        if total_emotional_emojis == 0:
            return ['minimal_emoji_usage']
        
        # Depression indicators
        depression_ratio = category_counts['depression_indicators'] / total_emotional_emojis
        if depression_ratio > 0.3:
            indicators.append('high_depression_emoji_usage')
        elif depression_ratio > 0.15:
            indicators.append('moderate_depression_emoji_usage')
        
        # Anxiety indicators
        anxiety_ratio = category_counts['anxiety_stress'] / total_emotional_emojis
        if anxiety_ratio > 0.25:
            indicators.append('high_anxiety_emoji_usage')
        elif anxiety_ratio > 0.1:
            indicators.append('moderate_anxiety_emoji_usage')
        
        # Social isolation indicators
        isolation_ratio = category_counts['isolation_indicators'] / total_emotional_emojis
        social_positive_ratio = category_counts['social_positive'] / total_emotional_emojis
        
        if isolation_ratio > 0.2 and social_positive_ratio < 0.1:
            indicators.append('social_isolation_patterns')
        
        # Energy level indicators
        energy_low_ratio = category_counts['energy_low'] / total_emotional_emojis
        if energy_low_ratio > 0.3:
            indicators.append('low_energy_patterns')
        
        # Crisis warning signals
        if category_counts['crisis_warning'] > 0:
            indicators.append('crisis_warning_emojis')
        
        # Positive indicators
        positive_ratio = category_counts['positive_emotion'] / total_emotional_emojis
        if positive_ratio > 0.6:
            indicators.append('positive_emotional_expression')
        
        return indicators
    
    def _create_empty_emoji_pattern(self) -> EmojiUsagePattern:
        """Create empty emoji pattern for no data case"""
        
        return EmojiUsagePattern(
            emoji_frequency=0.0,
            emotional_emoji_ratio=0.0,
            dominant_emoji_categories=[],
            emoji_sentiment_distribution={'positive': 0.0, 'negative': 0.0, 'neutral': 0.0},
            emoji_complexity='simple',
            emoji_consistency=0.0,
            mental_state_indicators=['no_emoji_data']
        )

class SocialInteractionAnalyzer:
    """Analyzes social interaction patterns for mental health indicators"""
    
    def __init__(self):
        self.interaction_types = ['mentions', 'replies', 'shares', 'likes', 'comments']
        self.isolation_thresholds = {
            'critical': 0.1,    # Very low interaction
            'concerning': 0.3,  # Low interaction
            'moderate': 0.6,    # Moderate interaction
            'healthy': 1.0      # High interaction
        }
    
    def analyze_social_interaction(self, content_data: List[Dict[str, Any]], 
                                 social_data: Dict[str, Any]) -> SocialInteractionFrequency:
        """Analyze social interaction frequency and patterns"""
        
        if not content_data and not social_data:
            return self._create_empty_interaction_pattern()
        
        # Calculate interaction metrics
        interaction_rate = self._calculate_interaction_rate(content_data, social_data)
        interaction_types = self._analyze_interaction_types(content_data, social_data)
        social_engagement_level = self._determine_social_engagement_level(interaction_rate)
        reciprocity_score = self._calculate_reciprocity_score(content_data)
        social_network_diversity = self._calculate_network_diversity(content_data)
        isolation_indicators = self._identify_isolation_indicators(
            interaction_rate, interaction_types, content_data
        )
        social_energy_pattern = self._analyze_social_energy_pattern(content_data)
        
        return SocialInteractionFrequency(
            interaction_rate=interaction_rate,
            interaction_types=interaction_types,
            social_engagement_level=social_engagement_level,
            reciprocity_score=reciprocity_score,
            social_network_diversity=social_network_diversity,
            isolation_indicators=isolation_indicators,
            social_energy_pattern=social_energy_pattern
        )
    
    def _calculate_interaction_rate(self, content_data: List[Dict[str, Any]], 
                                  social_data: Dict[str, Any]) -> float:
        """Calculate overall interaction rate"""
        
        total_interactions = 0
        total_content = len(content_data)
        
        # Count interactions from content
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Count mentions
            mentions = len(re.findall(r'@\w+', text))
            total_interactions += mentions
            
            # Count replies (indicated by reply keywords)
            reply_indicators = ['replying to', 'in response to', '@']
            if any(indicator in text for indicator in reply_indicators):
                total_interactions += 1
        
        # Add interactions from social profile data
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})
                    
                    # Estimate interactions from follower/following ratios
                    followers = inferred_data.get('followers', 0)
                    following = inferred_data.get('following', 0)
                    
                    if isinstance(followers, int) and isinstance(following, int):
                        # Higher following suggests more social interaction
                        total_interactions += min(following / 100, 10)  # Normalize
        
        # Normalize by content volume and time
        if total_content == 0:
            return 0.0
        
        return total_interactions / max(total_content, 1)
    
    def _analyze_interaction_types(self, content_data: List[Dict[str, Any]], 
                                 social_data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze different types of social interactions"""
        
        interaction_counts = defaultdict(int)
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Count mentions
            mentions = len(re.findall(r'@\w+', text))
            interaction_counts['mentions'] += mentions
            
            # Count hashtags (form of social engagement)
            hashtags = len(re.findall(r'#\w+', text))
            interaction_counts['hashtags'] += hashtags
            
            # Detect replies
            if any(indicator in text for indicator in ['replying', 'response', 'reply']):
                interaction_counts['replies'] += 1
            
            # Detect sharing behavior
            if any(indicator in text for indicator in ['share', 'sharing', 'shared', 'repost']):
                interaction_counts['shares'] += 1
        
        # Add engagement from social profiles
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})
                    
                    # Estimate likes/comments from engagement metrics
                    followers = inferred_data.get('followers', 0)
                    if isinstance(followers, int) and followers > 0:
                        interaction_counts['likes'] += min(followers // 10, 50)
                        interaction_counts['comments'] += min(followers // 50, 10)
        
        return dict(interaction_counts)
    
    def _determine_social_engagement_level(self, interaction_rate: float) -> str:
        """Determine social engagement level"""
        
        if interaction_rate >= 2.0:
            return 'high'
        elif interaction_rate >= 1.0:
            return 'medium'
        elif interaction_rate >= 0.3:
            return 'low'
        else:
            return 'isolated'
    
    def _calculate_reciprocity_score(self, content_data: List[Dict[str, Any]]) -> float:
        """Calculate social reciprocity score"""
        
        if not content_data:
            return 0.0
        
        reciprocal_interactions = 0
        total_interactions = 0
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Count outgoing interactions
            mentions = len(re.findall(r'@\w+', text))
            total_interactions += mentions
            
            # Count reciprocal indicators
            reciprocal_keywords = ['thanks', 'thank you', 'replying', 'response', 'back to you']
            if any(keyword in text for keyword in reciprocal_keywords):
                reciprocal_interactions += 1
        
        if total_interactions == 0:
            return 0.0
        
        return reciprocal_interactions / total_interactions
    
    def _calculate_network_diversity(self, content_data: List[Dict[str, Any]]) -> float:
        """Calculate social network diversity"""
        
        unique_mentions = set()
        total_mentions = 0
        
        for content in content_data:
            text = content.get('text', content.get('content', ''))
            mentions = re.findall(r'@(\w+)', text)
            
            for mention in mentions:
                unique_mentions.add(mention.lower())
                total_mentions += 1
        
        if total_mentions == 0:
            return 0.0
        
        return len(unique_mentions) / total_mentions
    
    def _identify_isolation_indicators(self, interaction_rate: float, 
                                     interaction_types: Dict[str, int],
                                     content_data: List[Dict[str, Any]]) -> List[str]:
        """Identify social isolation indicators"""
        
        indicators = []
        
        # Low interaction rate
        if interaction_rate < self.isolation_thresholds['critical']:
            indicators.append('very_low_social_interaction')
        elif interaction_rate < self.isolation_thresholds['concerning']:
            indicators.append('low_social_interaction')
        
        # Lack of mentions/replies
        if interaction_types.get('mentions', 0) == 0 and len(content_data) > 5:
            indicators.append('no_direct_social_mentions')
        
        if interaction_types.get('replies', 0) == 0 and len(content_data) > 5:
            indicators.append('no_conversational_engagement')
        
        # Isolation language patterns
        isolation_keywords = ['alone', 'lonely', 'isolated', 'nobody', 'no one', 'by myself']
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            if any(keyword in text for keyword in isolation_keywords):
                indicators.append('isolation_language_patterns')
                break
        
        # Social withdrawal language
        withdrawal_keywords = ['staying in', 'avoiding', 'cancelled', 'don\'t want to see']
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            if any(keyword in text for keyword in withdrawal_keywords):
                indicators.append('social_withdrawal_language')
                break
        
        return indicators
    
    def _analyze_social_energy_pattern(self, content_data: List[Dict[str, Any]]) -> str:
        """Analyze social energy patterns over time"""
        
        if len(content_data) < 3:
            return 'insufficient_data'
        
        # Calculate interaction energy for each piece of content
        energy_scores = []
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            energy_score = 0
            
            # Positive social indicators
            social_positive = ['excited', 'happy', 'fun', 'amazing', 'great time', 'love']
            energy_score += sum(1 for word in social_positive if word in text)
            
            # Negative social indicators
            social_negative = ['tired', 'exhausted', 'drained', 'overwhelmed', 'stressed']
            energy_score -= sum(1 for word in social_negative if word in text)
            
            # Interaction indicators
            mentions = len(re.findall(r'@\w+', text))
            energy_score += mentions * 0.5
            
            energy_scores.append(energy_score)
        
        # Analyze pattern
        if len(energy_scores) < 2:
            return 'insufficient_data'
        
        # Calculate trend
        x = np.arange(len(energy_scores))
        slope = np.polyfit(x, energy_scores, 1)[0]
        
        # Calculate consistency
        variance = np.var(energy_scores)
        
        if slope < -0.1:
            return 'declining'
        elif variance > 2.0:
            return 'irregular'
        else:
            return 'consistent'
    
    def _create_empty_interaction_pattern(self) -> SocialInteractionFrequency:
        """Create empty interaction pattern for no data case"""
        
        return SocialInteractionFrequency(
            interaction_rate=0.0,
            interaction_types={},
            social_engagement_level='isolated',
            reciprocity_score=0.0,
            social_network_diversity=0.0,
            isolation_indicators=['no_social_data'],
            social_energy_pattern='insufficient_data'
        )

class ContentToneAnalyzer:
    """Analyzes content tone for mental state assessment"""
    
    def __init__(self):
        self.tone_keywords = {
            'positive': ['happy', 'excited', 'grateful', 'blessed', 'amazing', 'wonderful', 'great'],
            'negative': ['sad', 'angry', 'frustrated', 'disappointed', 'upset', 'horrible', 'terrible'],
            'anxious': ['worried', 'nervous', 'anxious', 'scared', 'panicked', 'overwhelmed'],
            'depressed': ['hopeless', 'worthless', 'empty', 'numb', 'tired', 'exhausted'],
            'stressed': ['pressure', 'burden', 'chaotic', 'hectic', 'overwhelming', 'too much'],
            'calm': ['peaceful', 'serene', 'relaxed', 'calm', 'tranquil', 'content']
        }
        
        self.wellbeing_indicators = {
            'positive': ['exercise', 'meditation', 'therapy', 'self-care', 'growth', 'healing'],
            'negative': ['insomnia', 'appetite loss', 'isolation', 'giving up', 'hopeless']
        }
    
    def analyze_content_tone(self, content_data: List[Dict[str, Any]]) -> ContentToneAnalysis:
        """Analyze content tone for mental state indicators"""
        
        if not content_data:
            return self._create_empty_tone_analysis()
        
        # Analyze tone for each piece of content
        tone_scores = []
        emotional_scores = []
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            if text:
                tone_score = self._calculate_tone_score(text)
                emotional_score = self._calculate_emotional_score(text)
                
                tone_scores.append(tone_score)
                emotional_scores.append(emotional_score)
        
        if not tone_scores:
            return self._create_empty_tone_analysis()
        
        # Calculate overall metrics
        overall_tone = self._determine_overall_tone(tone_scores)
        tone_consistency = self._calculate_tone_consistency(tone_scores)
        emotional_volatility = self._calculate_emotional_volatility(emotional_scores)
        tone_progression = tone_scores  # Simplified - would need timestamps for real progression
        dominant_emotions = self._identify_dominant_emotions(content_data)
        stress_indicators = self._identify_stress_indicators(content_data)
        wellbeing_indicators = self._identify_wellbeing_indicators(content_data)
        tone_stability_score = self._calculate_tone_stability(tone_scores)
        
        return ContentToneAnalysis(
            overall_tone=overall_tone,
            tone_consistency=tone_consistency,
            emotional_volatility=emotional_volatility,
            tone_progression=tone_progression,
            dominant_emotions=dominant_emotions,
            stress_indicators=stress_indicators,
            wellbeing_indicators=wellbeing_indicators,
            tone_stability_score=tone_stability_score
        )
    
    def _calculate_tone_score(self, text: str) -> float:
        """Calculate tone score for a piece of text"""
        
        if not text:
            return 0.0
        
        tone_score = 0.0
        word_count = 0
        
        for tone_category, keywords in self.tone_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if tone_category in ['positive', 'calm']:
                        tone_score += 1
                    elif tone_category in ['negative', 'anxious', 'depressed', 'stressed']:
                        tone_score -= 1
                    word_count += 1
        
        # Normalize score
        total_words = len(text.split())
        if total_words > 0:
            return tone_score / total_words
        else:
            return 0.0
    
    def _calculate_emotional_score(self, text: str) -> float:
        """Calculate emotional intensity score"""
        
        if not text:
            return 0.0
        
        # Count emotional intensity indicators
        intensity_indicators = ['very', 'extremely', 'so', 'really', 'absolutely', 'completely']
        emotional_words = ['happy', 'sad', 'angry', 'excited', 'worried', 'scared']
        
        intensity_count = sum(1 for indicator in intensity_indicators if indicator in text)
        emotional_count = sum(1 for word in emotional_words if word in text)
        
        total_words = len(text.split())
        if total_words > 0:
            return (intensity_count + emotional_count) / total_words
        else:
            return 0.0
    
    def _determine_overall_tone(self, tone_scores: List[float]) -> str:
        """Determine overall tone from individual scores"""
        
        if not tone_scores:
            return 'neutral'
        
        avg_tone = np.mean(tone_scores)
        
        if avg_tone > 0.05:
            return 'positive'
        elif avg_tone < -0.05:
            return 'negative'
        else:
            # Check for mixed emotions
            positive_count = sum(1 for score in tone_scores if score > 0)
            negative_count = sum(1 for score in tone_scores if score < 0)
            
            if positive_count > 0 and negative_count > 0:
                return 'mixed'
            else:
                return 'neutral'
    
    def _calculate_tone_consistency(self, tone_scores: List[float]) -> float:
        """Calculate how consistent the tone is"""
        
        if len(tone_scores) <= 1:
            return 1.0
        
        # Lower variance = higher consistency
        variance = np.var(tone_scores)
        consistency = 1.0 / (1.0 + variance)
        
        return consistency
    
    def _calculate_emotional_volatility(self, emotional_scores: List[float]) -> float:
        """Calculate emotional volatility"""
        
        if len(emotional_scores) <= 1:
            return 0.0
        
        # Calculate standard deviation as volatility measure
        return np.std(emotional_scores)
    
    def _identify_dominant_emotions(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Identify dominant emotions in content"""
        
        emotion_counts = defaultdict(int)
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for emotion, keywords in self.tone_keywords.items():
                if any(keyword in text for keyword in keywords):
                    emotion_counts[emotion] += 1
        
        # Return top 3 emotions
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        return [emotion[0] for emotion in sorted_emotions[:3] if emotion[1] > 0]
    
    def _identify_stress_indicators(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Identify stress indicators in content"""
        
        stress_indicators = []
        
        stress_patterns = {
            'time_pressure': ['deadline', 'running out of time', 'rush', 'hurry', 'late'],
            'overwhelm': ['too much', 'can\'t handle', 'overwhelming', 'drowning'],
            'sleep_issues': ['can\'t sleep', 'insomnia', 'tired', 'exhausted', 'sleepless'],
            'physical_symptoms': ['headache', 'stomach', 'tension', 'pain', 'sick'],
            'cognitive_load': ['can\'t think', 'confused', 'foggy', 'scattered', 'forgetful']
        }
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for pattern, keywords in stress_patterns.items():
                if any(keyword in text for keyword in keywords):
                    if pattern not in stress_indicators:
                        stress_indicators.append(pattern)
        
        return stress_indicators
    
    def _identify_wellbeing_indicators(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Identify wellbeing indicators in content"""
        
        wellbeing_indicators = []
        
        wellbeing_patterns = {
            'self_care': ['meditation', 'exercise', 'therapy', 'self-care', 'relax'],
            'social_support': ['friends', 'family', 'support', 'help', 'together'],
            'growth_mindset': ['learning', 'growing', 'improving', 'progress', 'better'],
            'gratitude': ['grateful', 'thankful', 'blessed', 'appreciate', 'lucky'],
            'achievement': ['accomplished', 'proud', 'success', 'achieved', 'completed']
        }
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for pattern, keywords in wellbeing_patterns.items():
                if any(keyword in text for keyword in keywords):
                    if pattern not in wellbeing_indicators:
                        wellbeing_indicators.append(pattern)
        
        return wellbeing_indicators
    
    def _calculate_tone_stability(self, tone_scores: List[float]) -> float:
        """Calculate tone stability score"""
        
        if len(tone_scores) <= 1:
            return 1.0
        
        # Calculate how much tone varies from the mean
        mean_tone = np.mean(tone_scores)
        deviations = [abs(score - mean_tone) for score in tone_scores]
        avg_deviation = np.mean(deviations)
        
        # Convert to stability score (lower deviation = higher stability)
        stability = 1.0 / (1.0 + avg_deviation)
        
        return stability
    
    def _create_empty_tone_analysis(self) -> ContentToneAnalysis:
        """Create empty tone analysis for no data case"""
        
        return ContentToneAnalysis(
            overall_tone='neutral',
            tone_consistency=0.0,
            emotional_volatility=0.0,
            tone_progression=[],
            dominant_emotions=[],
            stress_indicators=[],
            wellbeing_indicators=[],
            tone_stability_score=0.0
        )

class MentalStateAnalyzer:
    """Main mental state analyzer combining all components"""
    
    def __init__(self):
        self.language_analyzer = LanguagePatternAnalyzer()
        self.emoji_analyzer = EmojiPatternAnalyzer()
        self.social_analyzer = SocialInteractionAnalyzer()
        self.tone_analyzer = ContentToneAnalyzer()
    
    def analyze_mental_state(self, social_data: Dict[str, Any]) -> MentalStateAssessmentResult:
        """Comprehensive mental state assessment"""
        
        logger.info("Starting comprehensive mental state assessment")
        
        # Extract content data
        content_data = self._extract_content_data(social_data)
        
        if not content_data:
            return self._create_empty_mental_state_assessment()
        
        # Perform all analyses
        language_patterns = self.language_analyzer.analyze_language_patterns(content_data)
        emoji_patterns = self.emoji_analyzer.analyze_emoji_patterns(content_data)
        social_interaction = self.social_analyzer.analyze_social_interaction(content_data, social_data)
        content_tone = self.tone_analyzer.analyze_content_tone(content_data)
        
        # Assess risk factors
        risk_factors = self._assess_mental_health_risk_factors(
            language_patterns, emoji_patterns, social_interaction, content_tone
        )
        
        # Generate mental state profile
        mental_state_profile = self._generate_mental_state_profile(
            language_patterns, emoji_patterns, social_interaction, content_tone, risk_factors
        )
        
        # Calculate assessment confidence
        assessment_confidence = self._calculate_assessment_confidence(content_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(mental_state_profile, risk_factors)
        
        # Assess privacy considerations
        privacy_considerations = self._assess_privacy_considerations(
            language_patterns, emoji_patterns, social_interaction, content_tone
        )
        
        logger.info(f"Mental state assessment completed: "
                   f"State: {mental_state_profile.overall_mental_state}, "
                   f"Confidence: {assessment_confidence:.2f}")
        
        return MentalStateAssessmentResult(
            language_patterns=language_patterns,
            emoji_patterns=emoji_patterns,
            social_interaction=social_interaction,
            content_tone=content_tone,
            risk_factors=risk_factors,
            mental_state_profile=mental_state_profile,
            assessment_confidence=assessment_confidence,
            recommendations=recommendations,
            privacy_considerations=privacy_considerations
        )
    
    def _extract_content_data(self, social_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content data from social profiles"""
        
        content_list = []
        
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})
                    
                    # Add profile bio/description
                    if 'bio' in inferred_data:
                        content_list.append({
                            'text': inferred_data['bio'],
                            'source': 'bio',
                            'platform': profile.get('platform')
                        })
                    
                    if 'page_description' in inferred_data:
                        content_list.append({
                            'text': inferred_data['page_description'],
                            'source': 'description',
                            'platform': profile.get('platform')
                        })
                    
                    # Add posts if available
                    if 'posts' in inferred_data:
                        for post in inferred_data['posts'][:20]:  # Limit posts
                            if isinstance(post, dict):
                                content_list.append({
                                    'text': post.get('text', ''),
                                    'source': 'post',
                                    'platform': profile.get('platform'),
                                    'timestamp': post.get('timestamp')
                                })
                            elif isinstance(post, str):
                                content_list.append({
                                    'text': post,
                                    'source': 'post',
                                    'platform': profile.get('platform')
                                })
        
        return content_list
    
    def _assess_mental_health_risk_factors(self, language_patterns: LanguagePattern,
                                         emoji_patterns: EmojiUsagePattern,
                                         social_interaction: SocialInteractionFrequency,
                                         content_tone: ContentToneAnalysis) -> MentalHealthRiskFactors:
        """Assess mental health risk factors"""
        
        # Depression indicators
        depression_indicators = {
            'language_markers': language_patterns.linguistic_markers.get('depression_language', 0.0),
            'negative_tone': 1.0 if content_tone.overall_tone == 'negative' else 0.0,
            'social_isolation': 1.0 if social_interaction.social_engagement_level == 'isolated' else 0.0,
            'past_focus': language_patterns.temporal_references.get('past', 0) / 
                         max(sum(language_patterns.temporal_references.values()), 1),
            'depression_emojis': 1.0 if 'depression_indicators' in emoji_patterns.dominant_emoji_categories else 0.0
        }
        
        # Anxiety indicators
        anxiety_indicators = {
            'anxiety_language': language_patterns.linguistic_markers.get('anxiety_language', 0.0),
            'uncertainty_markers': 1.0 if 'uncertainty' in language_patterns.cognitive_load_indicators else 0.0,
            'emotional_volatility': content_tone.emotional_volatility,
            'anxiety_emojis': 1.0 if 'anxiety_stress' in emoji_patterns.dominant_emoji_categories else 0.0,
            'future_worry': language_patterns.temporal_references.get('future', 0) / 
                           max(sum(language_patterns.temporal_references.values()), 1)
        }
        
        # Stress indicators
        stress_indicators = {
            'stress_language': language_patterns.linguistic_markers.get('stress_language', 0.0),
            'cognitive_overload': 1.0 if 'high_complexity' in language_patterns.cognitive_load_indicators else 0.0,
            'tone_instability': 1.0 - content_tone.tone_stability_score,
            'stress_content': len(content_tone.stress_indicators) / 10.0,  # Normalize
            'low_energy_emojis': 1.0 if 'energy_low' in emoji_patterns.dominant_emoji_categories else 0.0
        }
        
        # Social withdrawal score
        social_withdrawal_score = 0.0
        if social_interaction.social_engagement_level == 'isolated':
            social_withdrawal_score += 0.4
        if 'social_isolation_patterns' in emoji_patterns.mental_state_indicators:
            social_withdrawal_score += 0.3
        if 'isolation_language_patterns' in social_interaction.isolation_indicators:
            social_withdrawal_score += 0.3
        
        # Emotional regulation score
        emotional_regulation_score = content_tone.tone_stability_score * (1.0 - content_tone.emotional_volatility)
        
        # Cognitive function indicators
        cognitive_function_indicators = {
            'complexity_decline': 1.0 - language_patterns.complexity_score,
            'vocabulary_limitation': 1.0 - language_patterns.vocabulary_diversity,
            'cognitive_load_issues': len(language_patterns.cognitive_load_indicators) / 5.0
        }
        
        # Crisis warning signals
        crisis_warning_signals = []
        if 'crisis_warning_emojis' in emoji_patterns.mental_state_indicators:
            crisis_warning_signals.append('crisis_emoji_usage')
        if any('hopeless' in indicator for indicator in content_tone.stress_indicators):
            crisis_warning_signals.append('hopelessness_language')
        if social_withdrawal_score > 0.8:
            crisis_warning_signals.append('severe_social_isolation')
        
        # Protective factors
        protective_factors = []
        if content_tone.wellbeing_indicators:
            protective_factors.extend(content_tone.wellbeing_indicators)
        if social_interaction.social_engagement_level in ['medium', 'high']:
            protective_factors.append('social_connectivity')
        if language_patterns.linguistic_markers.get('positive_language', 0) > 0.05:
            protective_factors.append('positive_language_use')
        
        return MentalHealthRiskFactors(
            depression_indicators=depression_indicators,
            anxiety_indicators=anxiety_indicators,
            stress_indicators=stress_indicators,
            social_withdrawal_score=min(social_withdrawal_score, 1.0),
            emotional_regulation_score=max(0.0, min(emotional_regulation_score, 1.0)),
            cognitive_function_indicators=cognitive_function_indicators,
            crisis_warning_signals=crisis_warning_signals,
            protective_factors=protective_factors
        )
    
    def _generate_mental_state_profile(self, language_patterns: LanguagePattern,
                                     emoji_patterns: EmojiUsagePattern,
                                     social_interaction: SocialInteractionFrequency,
                                     content_tone: ContentToneAnalysis,
                                     risk_factors: MentalHealthRiskFactors) -> MentalStateProfile:
        """Generate comprehensive mental state profile"""
        
        # Calculate overall mental state
        overall_mental_state = self._determine_overall_mental_state(risk_factors)
        
        # Calculate emotional stability score
        emotional_stability_score = (
            risk_factors.emotional_regulation_score * 0.4 +
            content_tone.tone_stability_score * 0.3 +
            (1.0 - content_tone.emotional_volatility) * 0.3
        )
        
        # Determine social connectivity level
        social_connectivity_level = social_interaction.social_engagement_level
        
        # Determine cognitive function level
        avg_cognitive_decline = np.mean(list(risk_factors.cognitive_function_indicators.values()))
        if avg_cognitive_decline < 0.3:
            cognitive_function_level = 'high'
        elif avg_cognitive_decline < 0.6:
            cognitive_function_level = 'moderate'
        else:
            cognitive_function_level = 'concerning'
        
        # Determine stress level
        avg_stress = np.mean(list(risk_factors.stress_indicators.values()))
        if avg_stress < 0.2:
            stress_level = 'low'
        elif avg_stress < 0.4:
            stress_level = 'moderate'
        elif avg_stress < 0.7:
            stress_level = 'high'
        else:
            stress_level = 'severe'
        
        # Determine wellbeing trajectory
        wellbeing_trajectory = self._determine_wellbeing_trajectory(content_tone, social_interaction)
        
        # Identify resilience indicators
        resilience_indicators = []
        if risk_factors.protective_factors:
            resilience_indicators.extend(risk_factors.protective_factors)
        if emotional_stability_score > 0.6:
            resilience_indicators.append('emotional_stability')
        if language_patterns.complexity_score > 0.6:
            resilience_indicators.append('cognitive_clarity')
        
        # Calculate support system strength
        support_system_strength = self._calculate_support_system_strength(social_interaction)
        
        return MentalStateProfile(
            overall_mental_state=overall_mental_state,
            emotional_stability_score=emotional_stability_score,
            social_connectivity_level=social_connectivity_level,
            cognitive_function_level=cognitive_function_level,
            stress_level=stress_level,
            wellbeing_trajectory=wellbeing_trajectory,
            resilience_indicators=resilience_indicators,
            support_system_strength=support_system_strength
        )
    
    def _determine_overall_mental_state(self, risk_factors: MentalHealthRiskFactors) -> str:
        """Determine overall mental state from risk factors"""
        
        # Calculate risk scores
        depression_risk = np.mean(list(risk_factors.depression_indicators.values()))
        anxiety_risk = np.mean(list(risk_factors.anxiety_indicators.values()))
        stress_risk = np.mean(list(risk_factors.stress_indicators.values()))
        
        overall_risk = (depression_risk + anxiety_risk + stress_risk) / 3
        
        # Factor in crisis warnings
        if risk_factors.crisis_warning_signals:
            overall_risk = max(overall_risk, 0.8)
        
        # Factor in protective factors
        protection_score = len(risk_factors.protective_factors) / 10.0  # Normalize
        adjusted_risk = overall_risk * (1.0 - protection_score * 0.3)
        
        # Classify mental state
        if adjusted_risk > 0.7:
            return 'critical'
        elif adjusted_risk > 0.5:
            return 'concerning'
        elif adjusted_risk > 0.3:
            return 'stable'
        else:
            return 'positive'
    
    def _determine_wellbeing_trajectory(self, content_tone: ContentToneAnalysis,
                                      social_interaction: SocialInteractionFrequency) -> str:
        """Determine wellbeing trajectory"""
        
        # Analyze tone progression if available
        if len(content_tone.tone_progression) > 2:
            recent_tone = np.mean(content_tone.tone_progression[-3:])
            earlier_tone = np.mean(content_tone.tone_progression[:3])
            
            if recent_tone > earlier_tone + 0.1:
                return 'improving'
            elif recent_tone < earlier_tone - 0.1:
                return 'declining'
        
        # Analyze social energy pattern
        if social_interaction.social_energy_pattern == 'declining':
            return 'declining'
        elif social_interaction.social_energy_pattern == 'irregular':
            return 'unstable'
        
        # Default based on current state
        if content_tone.wellbeing_indicators:
            return 'stable'
        else:
            return 'stable'
    
    def _calculate_support_system_strength(self, social_interaction: SocialInteractionFrequency) -> float:
        """Calculate support system strength"""
        
        strength_score = 0.0
        
        # Social engagement level
        engagement_scores = {'high': 1.0, 'medium': 0.7, 'low': 0.4, 'isolated': 0.0}
        strength_score += engagement_scores.get(social_interaction.social_engagement_level, 0.0) * 0.4
        
        # Reciprocity score
        strength_score += social_interaction.reciprocity_score * 0.3
        
        # Network diversity
        strength_score += social_interaction.social_network_diversity * 0.3
        
        return min(strength_score, 1.0)
    
    def _calculate_assessment_confidence(self, content_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence in the assessment"""
        
        if not content_data:
            return 0.0
        
        # Base confidence on amount of data
        data_volume_score = min(len(content_data) / 10, 1.0)  # Normalize to 10 pieces of content
        
        # Factor in content quality/length
        total_words = sum(len(content.get('text', '').split()) for content in content_data)
        content_quality_score = min(total_words / 500, 1.0)  # Normalize to 500 words
        
        # Factor in data recency (if timestamps available)
        recency_score = 0.8  # Default score
        
        # Combined confidence
        confidence = (data_volume_score * 0.4 + content_quality_score * 0.4 + recency_score * 0.2)
        
        return confidence
    
    def _generate_recommendations(self, mental_state_profile: MentalStateProfile,
                                risk_factors: MentalHealthRiskFactors) -> List[str]:
        """Generate recommendations based on assessment"""
        
        recommendations = []
        
        # Crisis recommendations
        if risk_factors.crisis_warning_signals:
            recommendations.append("⚠️ CRITICAL: Crisis warning signals detected - immediate professional support recommended")
            recommendations.append("Contact emergency services or crisis hotline if in immediate danger")
        
        # Mental state based recommendations
        if mental_state_profile.overall_mental_state == 'concerning':
            recommendations.append("Consider consulting with a mental health professional")
        elif mental_state_profile.overall_mental_state == 'critical':
            recommendations.append("Seek immediate professional mental health support")
        
        # Specific risk factor recommendations
        if np.mean(list(risk_factors.depression_indicators.values())) > 0.5:
            recommendations.append("Depression indicators detected - consider therapy or counseling")
        
        if np.mean(list(risk_factors.anxiety_indicators.values())) > 0.5:
            recommendations.append("Anxiety patterns detected - consider stress management techniques")
        
        if mental_state_profile.stress_level in ['high', 'severe']:
            recommendations.append("High stress levels detected - prioritize stress reduction activities")
        
        # Social recommendations
        if mental_state_profile.social_connectivity_level == 'isolated':
            recommendations.append("Social isolation detected - consider reaching out to friends/family")
        
        # Positive reinforcement
        if mental_state_profile.resilience_indicators:
            recommendations.append("Positive coping strategies detected - continue current wellness practices")
        
        # General wellness
        recommendations.append("Maintain regular self-care routines and healthy lifestyle habits")
        
        return recommendations
    
    def _assess_privacy_considerations(self, language_patterns: LanguagePattern,
                                     emoji_patterns: EmojiUsagePattern,
                                     social_interaction: SocialInteractionFrequency,
                                     content_tone: ContentToneAnalysis) -> List[str]:
        """Assess privacy considerations for mental state data"""
        
        considerations = []
        
        # Sensitive mental health data
        considerations.append("⚠️ Mental state analysis contains sensitive psychological information")
        
        # Language pattern risks
        if language_patterns.linguistic_markers:
            considerations.append("⚠️ Language patterns may reveal mental health conditions")
        
        # Emotional expression risks
        if emoji_patterns.mental_state_indicators:
            considerations.append("⚠️ Emoji usage patterns may indicate emotional/mental state")
        
        # Social isolation risks
        if social_interaction.social_engagement_level == 'isolated':
            considerations.append("⚠️ Social interaction patterns may reveal isolation or withdrawal")
        
        # Tone analysis risks
        if content_tone.overall_tone in ['negative', 'mixed']:
            considerations.append("⚠️ Content tone analysis may reveal emotional distress")
        
        # General privacy notice
        considerations.append("🔒 This analysis should be kept confidential and used responsibly")
        considerations.append("📋 Mental health data requires special privacy protections")
        
        return considerations
    
    def _create_empty_mental_state_assessment(self) -> MentalStateAssessmentResult:
        """Create empty mental state assessment for no data case"""
        
        return MentalStateAssessmentResult(
            language_patterns=LanguagePattern(0.0, 'neutral', [], {}, 0.0, 0.0, {}),
            emoji_patterns=EmojiUsagePattern(0.0, 0.0, [], {}, 'simple', 0.0, []),
            social_interaction=SocialInteractionFrequency(0.0, {}, 'isolated', 0.0, 0.0, [], 'insufficient_data'),
            content_tone=ContentToneAnalysis('neutral', 0.0, 0.0, [], [], [], [], 0.0),
            risk_factors=MentalHealthRiskFactors({}, {}, {}, 0.0, 0.0, {}, [], []),
            mental_state_profile=MentalStateProfile('stable', 0.5, 'isolated', 'unknown', 'low', 'stable', [], 0.0),
            assessment_confidence=0.0,
            recommendations=['Insufficient data for comprehensive mental state assessment'],
            privacy_considerations=['✅ No mental state data available for analysis']
        )

def create_mental_state_analyzer():
    """Factory function to create mental state analyzer"""
    return MentalStateAnalyzer()
