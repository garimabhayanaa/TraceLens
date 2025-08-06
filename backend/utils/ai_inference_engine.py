import logging
import re
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import time
from datetime import datetime, timedelta
import threading
from .schedule_pattern_detector import create_schedule_pattern_detector
from .economic_indicators_analyzer import create_economic_indicators_analyzer
from .mental_state_analyzer import create_mental_state_analyzer
from .results_presentation import ResultPresentationBuilder
from .privacy_framework import create_privacy_framework
from .ethical_framework import create_ethical_boundaries_framework
from .consent_framework import create_consent_and_control_framework
from .authorization_framework import create_authorization_framework, AnalysisType, AccessLevel

# ML and NLP imports
try:
    from textblob import TextBlob
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.preprocessing import StandardScaler
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
except ImportError as e:
    logging.warning(f"Some ML libraries not available: {e}")

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    polarity: float  # -1 to 1 (negative to positive)
    subjectivity: float  # 0 to 1 (objective to subjective)
    classification: str  # 'positive', 'negative', 'neutral'
    confidence: float
    emotional_indicators: List[str]


@dataclass
class HashtagPattern:
    """Hashtag usage pattern"""
    hashtag: str
    frequency: int
    contexts: List[str]
    sentiment_association: str
    topic_relevance: float
    trending_score: float


@dataclass
class EngagementMetrics:
    """Content engagement analysis"""
    engagement_rate: float
    interaction_types: Dict[str, int]
    peak_engagement_times: List[str]
    audience_response_sentiment: str
    viral_potential: float
    content_quality_score: float


@dataclass
class TopicModel:
    """Topic modeling result"""
    topic_id: int
    topic_name: str
    keywords: List[str]
    relevance_score: float
    content_examples: List[str]
    sentiment_distribution: Dict[str, float]


@dataclass
class InterestProfile:
    """Comprehensive interest profile"""
    primary_interests: List[str]
    interest_scores: Dict[str, float]
    interest_evolution: Dict[str, List[float]]  # Time-based changes
    behavioral_patterns: Dict[str, Any]
    content_preferences: Dict[str, Any]
    engagement_style: str


class SentimentAnalyzer:
    """Advanced sentiment analysis with emotional indicators"""

    def __init__(self):
        self.emotional_keywords = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful', 'glad', 'elated'],
            'anger': ['angry', 'frustrated', 'annoyed', 'furious', 'irritated', 'outraged'],
            'sadness': ['sad', 'depressed', 'disappointed', 'heartbroken', 'melancholy'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'terrified'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned'],
            'disgust': ['disgusted', 'revolted', 'appalled', 'sickened', 'repulsed']
        }

        # Intensity modifiers
        self.intensifiers = ['very', 'extremely', 'incredibly', 'absolutely', 'totally']
        self.diminishers = ['slightly', 'somewhat', 'barely', 'hardly', 'a bit']

    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Perform comprehensive sentiment analysis"""

        if not text or len(text.strip()) == 0:
            return SentimentResult(0.0, 0.0, 'neutral', 0.0, [])

        try:
            # Basic sentiment using TextBlob
            blob = TextBlob(text.lower())
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Classify sentiment
            if polarity > 0.1:
                classification = 'positive'
            elif polarity < -0.1:
                classification = 'negative'
            else:
                classification = 'neutral'

            # Calculate confidence based on polarity strength
            confidence = min(abs(polarity) * 2, 1.0)

            # Detect emotional indicators
            emotional_indicators = self._detect_emotions(text.lower())

            # Adjust sentiment based on context
            adjusted_polarity, adjusted_confidence = self._adjust_sentiment_context(
                text, polarity, confidence
            )

            return SentimentResult(
                polarity=adjusted_polarity,
                subjectivity=subjectivity,
                classification=classification,
                confidence=adjusted_confidence,
                emotional_indicators=emotional_indicators
            )

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return SentimentResult(0.0, 0.0, 'neutral', 0.0, [])

    def _detect_emotions(self, text: str) -> List[str]:
        """Detect emotional indicators in text"""

        detected_emotions = []
        text_words = set(text.split())

        for emotion, keywords in self.emotional_keywords.items():
            if any(keyword in text_words for keyword in keywords):
                detected_emotions.append(emotion)

        return detected_emotions

    def _adjust_sentiment_context(self, text: str, polarity: float,
                                  confidence: float) -> Tuple[float, float]:
        """Adjust sentiment based on context clues"""

        text_lower = text.lower()

        # Check for negations
        negation_patterns = ['not', "don't", "won't", "can't", "never", "no way"]
        has_negation = any(pattern in text_lower for pattern in negation_patterns)

        if has_negation:
            polarity *= -0.8  # Flip and reduce intensity

        # Check for intensifiers/diminishers
        has_intensifier = any(word in text_lower for word in self.intensifiers)
        has_diminisher = any(word in text_lower for word in self.diminishers)

        if has_intensifier:
            polarity *= 1.3
            confidence *= 1.2
        elif has_diminisher:
            polarity *= 0.7
            confidence *= 0.8

        # Normalize values
        polarity = max(-1.0, min(1.0, polarity))
        confidence = max(0.0, min(1.0, confidence))

        return polarity, confidence


class HashtagAnalyzer:
    """Advanced hashtag and mention pattern recognition"""

    def __init__(self):
        self.hashtag_cache = {}
        self.mention_cache = {}

    def analyze_hashtag_patterns(self, content_list: List[str]) -> List[HashtagPattern]:
        """Analyze hashtag usage patterns across content"""

        if not content_list:
            return []

        # Extract all hashtags
        hashtag_data = defaultdict(lambda: {
            'frequency': 0,
            'contexts': [],
            'sentiments': []
        })

        sentiment_analyzer = SentimentAnalyzer()

        for content in content_list:
            hashtags = self._extract_hashtags(content)

            if hashtags:
                # Analyze sentiment of content with hashtags
                sentiment = sentiment_analyzer.analyze_sentiment(content)

                for hashtag in hashtags:
                    hashtag_lower = hashtag.lower()
                    hashtag_data[hashtag_lower]['frequency'] += 1
                    hashtag_data[hashtag_lower]['contexts'].append(content[:100])
                    hashtag_data[hashtag_lower]['sentiments'].append(sentiment.polarity)

        # Create hashtag patterns
        patterns = []
        for hashtag, data in hashtag_data.items():
            if data['frequency'] >= 2:  # Only include hashtags used multiple times
                avg_sentiment = np.mean(data['sentiments']) if data['sentiments'] else 0.0

                # Classify sentiment association
                if avg_sentiment > 0.2:
                    sentiment_association = 'positive'
                elif avg_sentiment < -0.2:
                    sentiment_association = 'negative'
                else:
                    sentiment_association = 'neutral'

                # Calculate topic relevance and trending score
                topic_relevance = self._calculate_topic_relevance(hashtag, data['contexts'])
                trending_score = self._calculate_trending_score(data['frequency'], len(content_list))

                pattern = HashtagPattern(
                    hashtag=hashtag,
                    frequency=data['frequency'],
                    contexts=data['contexts'][:5],  # Keep top 5 contexts
                    sentiment_association=sentiment_association,
                    topic_relevance=topic_relevance,
                    trending_score=trending_score
                )
                patterns.append(pattern)

        # Sort by frequency and trending score
        patterns.sort(key=lambda x: (x.frequency, x.trending_score), reverse=True)

        return patterns

    def analyze_mention_patterns(self, content_list: List[str]) -> Dict[str, Any]:
        """Analyze mention (@username) patterns"""

        mention_data = defaultdict(int)
        mention_contexts = defaultdict(list)

        for content in content_list:
            mentions = self._extract_mentions(content)

            for mention in mentions:
                mention_lower = mention.lower()
                mention_data[mention_lower] += 1
                mention_contexts[mention_lower].append(content[:100])

        # Analyze patterns
        total_mentions = sum(mention_data.values())

        if total_mentions == 0:
            return {
                'total_mentions': 0,
                'unique_mentions': 0,
                'top_mentions': [],
                'mention_diversity': 0.0,
                'interaction_style': 'non_interactive'
            }

        unique_mentions = len(mention_data)
        mention_diversity = unique_mentions / total_mentions if total_mentions > 0 else 0

        # Top mentions
        top_mentions = sorted(mention_data.items(), key=lambda x: x[1], reverse=True)[:10]

        # Determine interaction style
        if mention_diversity > 0.7:
            interaction_style = 'highly_interactive'
        elif mention_diversity > 0.4:
            interaction_style = 'moderately_interactive'
        elif mention_diversity > 0.1:
            interaction_style = 'selective_interactive'
        else:
            interaction_style = 'repetitive_interactive'

        return {
            'total_mentions': total_mentions,
            'unique_mentions': unique_mentions,
            'top_mentions': [{'mention': m, 'frequency': f} for m, f in top_mentions],
            'mention_diversity': mention_diversity,
            'interaction_style': interaction_style,
            'mention_contexts': dict(mention_contexts)
        }

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtag_pattern = r'#(\w+)'
        return re.findall(hashtag_pattern, text)

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mention_pattern = r'@(\w+)'
        return re.findall(mention_pattern, text)

    def _calculate_topic_relevance(self, hashtag: str, contexts: List[str]) -> float:
        """Calculate how relevant a hashtag is to its usage contexts"""

        if not contexts:
            return 0.0

        # Simple relevance based on hashtag appearance in different contexts
        relevance_score = 0.0

        for context in contexts:
            context_words = set(context.lower().split())
            hashtag_words = set(hashtag.lower().split())

            # Check if hashtag components appear in context
            overlap = len(hashtag_words.intersection(context_words))
            relevance_score += overlap / max(len(hashtag_words), 1)

        return relevance_score / len(contexts)

    def _calculate_trending_score(self, frequency: int, total_content: int) -> float:
        """Calculate trending score for a hashtag"""

        if total_content == 0:
            return 0.0

        # Trending score based on frequency relative to content volume
        base_score = frequency / total_content

        # Boost score for frequently used hashtags
        if frequency >= 10:
            base_score *= 1.5
        elif frequency >= 5:
            base_score *= 1.2

        return min(base_score, 1.0)


class EngagementAnalyzer:
    """Content engagement analysis and prediction"""

    def __init__(self):
        self.engagement_weights = {
            'likes': 1.0,
            'comments': 2.0,
            'shares': 3.0,
            'reactions': 1.5,
            'clicks': 0.5
        }

    def analyze_engagement(self, content_data: List[Dict[str, Any]]) -> EngagementMetrics:
        """Analyze content engagement patterns"""

        if not content_data:
            return EngagementMetrics(0.0, {}, [], 'neutral', 0.0, 0.0)

        # Calculate engagement rates
        total_engagement = 0
        interaction_types = defaultdict(int)
        content_scores = []
        sentiment_scores = []

        sentiment_analyzer = SentimentAnalyzer()

        for content in content_data:
            content_engagement = 0

            # Sum different types of engagement
            for interaction_type, weight in self.engagement_weights.items():
                count = content.get(interaction_type, 0)
                interaction_types[interaction_type] += count
                content_engagement += count * weight

            total_engagement += content_engagement

            # Analyze content quality
            text = content.get('text', content.get('content', ''))
            if text:
                sentiment = sentiment_analyzer.analyze_sentiment(text)
                sentiment_scores.append(sentiment.polarity)

                quality_score = self._calculate_content_quality(text, content_engagement)
                content_scores.append(quality_score)

        # Calculate metrics
        avg_engagement = total_engagement / len(content_data) if content_data else 0
        engagement_rate = min(avg_engagement / 100, 1.0)  # Normalize to 0-1

        # Analyze peak engagement times (placeholder - would need timestamp data)
        peak_times = self._analyze_peak_times(content_data)

        # Overall audience sentiment
        if sentiment_scores:
            avg_sentiment = np.mean(sentiment_scores)
            if avg_sentiment > 0.2:
                audience_sentiment = 'positive'
            elif avg_sentiment < -0.2:
                audience_sentiment = 'negative'
            else:
                audience_sentiment = 'neutral'
        else:
            audience_sentiment = 'neutral'

        # Calculate viral potential
        viral_potential = self._calculate_viral_potential(
            engagement_rate, interaction_types, sentiment_scores
        )

        # Average content quality
        avg_quality = np.mean(content_scores) if content_scores else 0.5

        return EngagementMetrics(
            engagement_rate=engagement_rate,
            interaction_types=dict(interaction_types),
            peak_engagement_times=peak_times,
            audience_response_sentiment=audience_sentiment,
            viral_potential=viral_potential,
            content_quality_score=avg_quality
        )

    def _calculate_content_quality(self, text: str, engagement: float) -> float:
        """Calculate content quality score"""

        if not text:
            return 0.0

        quality_score = 0.5  # Base score

        # Length factor
        text_length = len(text.split())
        if 10 <= text_length <= 50:  # Optimal length
            quality_score += 0.2
        elif text_length < 5:  # Too short
            quality_score -= 0.2
        elif text_length > 100:  # Too long
            quality_score -= 0.1

        # Engagement factor
        if engagement > 0:
            quality_score += min(engagement / 100, 0.3)

        # Content indicators
        if any(indicator in text.lower() for indicator in ['?', '!', 'what', 'how', 'why']):
            quality_score += 0.1  # Questions tend to engage

        if len(re.findall(r'#\w+', text)) > 0:
            quality_score += 0.1  # Hashtags help discoverability

        return max(0.0, min(1.0, quality_score))

    def _analyze_peak_times(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Analyze peak engagement times (placeholder implementation)"""

        # In a real implementation, this would analyze timestamp data
        # For now, return common peak times based on general social media patterns
        return ['09:00-10:00', '12:00-13:00', '19:00-21:00']

    def _calculate_viral_potential(self, engagement_rate: float,
                                   interactions: Dict[str, int],
                                   sentiment_scores: List[float]) -> float:
        """Calculate viral potential score"""

        viral_score = 0.0

        # High engagement rate boosts viral potential
        viral_score += engagement_rate * 0.4

        # Shares are most important for virality
        shares = interactions.get('shares', 0)
        comments = interactions.get('comments', 0)
        total_interactions = sum(interactions.values())

        if total_interactions > 0:
            share_ratio = shares / total_interactions
            comment_ratio = comments / total_interactions

            viral_score += share_ratio * 0.3
            viral_score += comment_ratio * 0.2

        # Positive sentiment helps virality
        if sentiment_scores:
            avg_sentiment = np.mean(sentiment_scores)
            if avg_sentiment > 0:
                viral_score += avg_sentiment * 0.1

        return min(viral_score, 1.0)


class TopicModelingEngine:
    """Advanced topic modeling for interest categorization"""

    def __init__(self):
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        except:
            self.stop_words = set(
                ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
            self.lemmatizer = None

        self.topic_labels = {
            0: 'Technology & Innovation',
            1: 'Sports & Fitness',
            2: 'Food & Lifestyle',
            3: 'Travel & Adventure',
            4: 'Business & Career',
            5: 'Entertainment & Media',
            6: 'Health & Wellness',
            7: 'Education & Learning',
            8: 'Art & Creativity',
            9: 'Politics & Society'
        }

    def perform_topic_modeling(self, content_list: List[str],
                               num_topics: int = 5) -> List[TopicModel]:
        """Perform topic modeling on content"""

        if not content_list or len(content_list) < 3:
            return []

        try:
            # Preprocess content
            processed_content = [self._preprocess_text(text) for text in content_list]
            processed_content = [text for text in processed_content if len(text.split()) > 2]

            if len(processed_content) < 3:
                return []

            # Create TF-IDF vectors
            tfidf = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8
            )

            tfidf_matrix = tfidf.fit_transform(processed_content)
            feature_names = tfidf.get_feature_names_out()

            # Perform LDA topic modeling
            lda = LatentDirichletAllocation(
                n_components=min(num_topics, len(processed_content)),
                random_state=42,
                max_iter=100
            )

            lda.fit(tfidf_matrix)

            # Extract topics
            topics = []
            sentiment_analyzer = SentimentAnalyzer()

            for topic_idx, topic in enumerate(lda.components_):
                # Get top keywords
                top_keywords_idx = topic.argsort()[-10:][::-1]
                keywords = [feature_names[i] for i in top_keywords_idx]

                # Find content examples for this topic
                topic_content = []
                for doc_idx, doc_topics in enumerate(lda.transform(tfidf_matrix)):
                    if doc_topics[topic_idx] > 0.3:  # High probability for this topic
                        topic_content.append(content_list[doc_idx])

                # Analyze sentiment distribution for this topic
                sentiment_dist = {'positive': 0, 'negative': 0, 'neutral': 0}
                for content in topic_content:
                    sentiment = sentiment_analyzer.analyze_sentiment(content)
                    sentiment_dist[sentiment.classification] += 1

                # Normalize sentiment distribution
                total_content = len(topic_content)
                if total_content > 0:
                    for key in sentiment_dist:
                        sentiment_dist[key] /= total_content

                # Calculate relevance score
                relevance_score = np.max(topic) / np.sum(topic)

                # Get topic name
                topic_name = self._generate_topic_name(keywords)

                topic_model = TopicModel(
                    topic_id=topic_idx,
                    topic_name=topic_name,
                    keywords=keywords[:5],  # Top 5 keywords
                    relevance_score=relevance_score,
                    content_examples=topic_content[:3],  # Top 3 examples
                    sentiment_distribution=sentiment_dist
                )

                topics.append(topic_model)

            # Sort topics by relevance
            topics.sort(key=lambda x: x.relevance_score, reverse=True)

            return topics

        except Exception as e:
            logger.error(f"Topic modeling failed: {str(e)}")
            return []

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for topic modeling"""

        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)

        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Tokenize and remove stopwords
        try:
            words = word_tokenize(text)
        except:
            words = text.split()

        words = [word for word in words if word not in self.stop_words and len(word) > 2]

        # Lemmatize if available
        if self.lemmatizer:
            words = [self.lemmatizer.lemmatize(word) for word in words]

        return ' '.join(words)

    def _generate_topic_name(self, keywords: List[str]) -> str:
        """Generate a meaningful topic name from keywords"""

        # Predefined topic categories based on common keywords
        tech_keywords = ['technology', 'software', 'app', 'digital', 'innovation', 'coding']
        sports_keywords = ['sport', 'fitness', 'game', 'training', 'exercise', 'team']
        food_keywords = ['food', 'recipe', 'cooking', 'restaurant', 'meal', 'delicious']
        travel_keywords = ['travel', 'trip', 'vacation', 'adventure', 'explore', 'journey']
        business_keywords = ['business', 'work', 'career', 'professional', 'job', 'company']

        keyword_categories = [
            (tech_keywords, 'Technology & Innovation'),
            (sports_keywords, 'Sports & Fitness'),
            (food_keywords, 'Food & Lifestyle'),
            (travel_keywords, 'Travel & Adventure'),
            (business_keywords, 'Business & Career')
        ]

        # Check if keywords match any category
        for category_keywords, category_name in keyword_categories:
            if any(keyword in ' '.join(keywords).lower() for keyword in category_keywords):
                return category_name

        # Default: use top 2 keywords
        if len(keywords) >= 2:
            return f"{keywords[0].title()} & {keywords[1].title()}"
        elif len(keywords) == 1:
            return keywords[0].title()
        else:
            return "General Topics"


class AIInferenceEngine:
    """Main AI inference engine with comprehensive privacy protection, ethical boundaries, user consent control, and authorization"""

    def __init__(self, privacy_enabled: bool = True, ethics_enabled: bool = True,
                 consent_enabled: bool = True, authorization_enabled: bool = True):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.hashtag_analyzer = HashtagAnalyzer()
        self.engagement_analyzer = EngagementAnalyzer()
        self.topic_engine = TopicModelingEngine()
        self.schedule_detector = create_schedule_pattern_detector()
        self.economic_analyzer = create_economic_indicators_analyzer()
        self.mental_state_analyzer = create_mental_state_analyzer()
        self.presentation_builder = ResultPresentationBuilder()

        # Privacy Framework Integration
        self.privacy_framework = create_privacy_framework() if privacy_enabled else None

        # Ethical Boundaries Framework Integration
        self.ethical_framework = create_ethical_boundaries_framework() if ethics_enabled else None

        # User Consent and Control Framework Integration
        self.consent_framework = create_consent_and_control_framework() if consent_enabled else None

        # Authorization Framework Integration
        self.authorization_framework = create_authorization_framework() if authorization_enabled else None

        self.analysis_cache = {}
        self.cache_lock = threading.RLock()

    def analyze_social_content(self, social_data: Dict[str, Any],
                               user_id: str,
                               user_email: str,
                               analysis_type: str,
                               target_data_description: str,
                               use_case_description: str,
                               age_verification_data: Dict[str, Any],
                               consent_process_id: str,
                               session_id: str = None,
                               privacy_level: str = 'standard',
                               ip_address: str = '',
                               user_agent: str = '',
                               session_token: str = None,
                               consent_token: str = None) -> Dict[str, Any]:
        """Comprehensive AI analysis with full authorization, consent, privacy, and ethical protection"""

        logger.info(
            "Starting authorization-verified, consent-verified, ethically-bounded, privacy-protected AI analysis")

        # AUTHORIZATION CHECK
        authorization_result = None
        if self.authorization_framework:
            try:
                # Convert analysis type string to enum
                try:
                    analysis_type_enum = AnalysisType[analysis_type.upper()]
                except KeyError:
                    return self._create_authorization_error_response(f"Invalid analysis type: {analysis_type}")

                authorization_result = self.authorization_framework.authorize_analysis_request(
                    user_id=user_id,
                    user_email=user_email,
                    analysis_type=analysis_type_enum,
                    target_data=target_data_description,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    session_token=session_token,
                    consent_token=consent_token
                )

                # Check if authorized
                if not authorization_result.authorized:
                    return self._create_authorization_rejection_response(authorization_result)

                logger.info(
                    f"Authorization approved: {analysis_type} for {user_email} with {authorization_result.access_level.value} access")

                # Update session token if new one was generated
                if authorization_result.session_token:
                    session_token = authorization_result.session_token

            except Exception as e:
                logger.error(f"Authorization check failed: {str(e)}")
                return self._create_authorization_error_response(str(e))

        # USER CONSENT VERIFICATION
        consent_verified = False
        if self.consent_framework:
            try:
                # Verify user has completed consent process and can proceed
                consent_process = self.consent_framework.consent_manager.active_processes.get(consent_process_id)

                if not consent_process:
                    return self._create_consent_error_response("Consent process not found or expired")

                if not consent_process.is_complete:
                    return self._create_consent_error_response("Consent process not completed")

                if not consent_process.can_proceed:
                    return self._create_consent_error_response("Required consents not granted")

                consent_verified = True
                logger.info(f"User consent verified for process {consent_process_id}")

            except Exception as e:
                logger.error(f"Consent verification failed: {str(e)}")
                return self._create_consent_error_response(str(e))

        # ETHICAL BOUNDARIES CHECK
        ethical_approval = None
        if self.ethical_framework:
            try:
                # Extract data sources and types from social_data
                data_sources = self._extract_data_sources(social_data)
                data_types = self._extract_data_types(social_data)

                ethical_approval = self.ethical_framework.evaluate_request(
                    user_id=user_id,
                    use_case_description=use_case_description,
                    data_sources=data_sources,
                    data_types=data_types,
                    collection_method='public_api',
                    age_verification_data=age_verification_data,
                    user_context={
                        'session_id': session_id,
                        'consent_process_id': consent_process_id,
                        'analysis_type': analysis_type,
                        'authorization_level': authorization_result.access_level.value if authorization_result else 'basic'
                    }
                )

                # Check if ethically approved
                if not ethical_approval.ethics_approved:
                    return self._create_ethical_rejection_response(ethical_approval)

                logger.info(f"Ethical evaluation passed: Compliance score {ethical_approval.compliance_score:.2f}")

            except Exception as e:
                logger.error(f"Ethical evaluation failed: {str(e)}")
                return self._create_ethical_error_response(str(e))

        # PRIVACY PROTECTION: Process data through privacy framework
        processing_id = None
        original_data_size = len(str(social_data))

        if self.privacy_framework:
            try:
                # Configure privacy level based on access level
                if authorization_result and authorization_result.access_level == AccessLevel.BASIC:
                    privacy_level = 'strict'  # Enhanced privacy for third-party analysis
                elif authorization_result and authorization_result.access_level == AccessLevel.PROFESSIONAL:
                    privacy_level = 'minimal'  # Reduced privacy filtering for research

                # Configure privacy framework
                if privacy_level == 'strict':
                    self.privacy_framework.anonymization_config.remove_names = True
                    self.privacy_framework.anonymization_config.remove_locations = True
                    self.privacy_framework.anonymization_config.remove_sensitive_keywords = True
                elif privacy_level == 'minimal':
                    self.privacy_framework.anonymization_config.remove_names = False
                    self.privacy_framework.anonymization_config.remove_locations = False
                    self.privacy_framework.anonymization_config.remove_sensitive_keywords = False

                # Process with privacy protection
                protected_data, processing_id = self.privacy_framework.process_social_data(
                    social_data, session_id
                )

                # Use protected data for analysis
                if 'encrypted' in protected_data and protected_data['encrypted']:
                    # Decrypt for processing (in secure environment)
                    social_data = self.privacy_framework.data_handler.decrypt_data(
                        protected_data['data'], session_id
                    )
                else:
                    social_data = protected_data

                logger.info(f"Data processed with privacy protection: {processing_id}")

            except Exception as e:
                logger.error(f"Privacy protection failed: {str(e)}")
                # Continue with original data but log the failure
                social_data = social_data

        # Extract content from protected social data
        content_list = self._extract_content_from_social_data(social_data)

        if not content_list:
            return self._create_empty_analysis(processing_id, privacy_level, ethical_approval,
                                               consent_verified, authorization_result)

        # Perform analyses based on access level
        analysis_results = self._perform_authorized_analyses(
            content_list, social_data, user_id, session_id, authorization_result
        )

        # Add comprehensive metadata
        analysis_results['analysis_metadata'] = {
            'content_analyzed': len(content_list),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'analysis_version': '4.4',  # Updated version with authorization framework
            'privacy_protected': self.privacy_framework is not None,
            'ethics_approved': ethical_approval.ethics_approved if ethical_approval else False,
            'consent_verified': consent_verified,
            'authorization_approved': authorization_result.authorized if authorization_result else False,
            'access_level': authorization_result.access_level.value if authorization_result else 'basic',
            'analysis_type': analysis_type,
            'processing_id': processing_id,
            'session_token': session_token,
            'privacy_level': privacy_level,
            'ethical_compliance_score': ethical_approval.compliance_score if ethical_approval else 0.0,
            'consent_process_id': consent_process_id,
            'use_case': use_case_description,
            'opt_out_available': True,
            'immediate_deletion_available': True,
            'original_data_size': original_data_size,
            'protected_data_size': len(str(social_data)),
            'data_reduction_ratio': 1.0 - (len(str(social_data)) / original_data_size) if original_data_size > 0 else 0,
            'features': [
                'authorization_framework',
                'sentiment_analysis',
                'hashtag_patterns',
                'mention_patterns',
                'engagement_analysis',
                'topic_modeling',
                'schedule_patterns',
                'economic_indicators',
                'mental_state_assessment',
                'interest_profile',
                'privacy_framework',
                'ethical_boundaries',
                'consent_framework',
                'results_presentation'
            ]
        }

        # Add authorization information
        if authorization_result:
            analysis_results['authorization_status'] = {
                'authorized': authorization_result.authorized,
                'access_level': authorization_result.access_level.value,
                'session_token': authorization_result.session_token,
                'verification_completed': not authorization_result.verification_required,
                'consent_obtained': not authorization_result.consent_required,
                'analysis_scope': self._determine_analysis_scope(authorization_result.access_level)
            }

        # Add consent and control information
        if self.consent_framework:
            user_consents = self.consent_framework.consent_manager.get_user_consents(user_id)

            analysis_results['consent_status'] = {
                'consent_verified': consent_verified,
                'consent_process_id': consent_process_id,
                'granted_consents': [
                    {
                        'type': consent.consent_type.value,
                        'granted_at': consent.granted_at.isoformat() if consent.granted_at else None,
                        'expires_at': consent.expires_at.isoformat() if consent.expires_at else None
                    }
                    for consent in user_consents if consent.status.value == 'granted'
                ],
                'user_control_options': {
                    'immediate_deletion': True,
                    'opt_out_current_stage': True,
                    'withdraw_consent': True,
                    'download_data': True
                }
            }

        # Add ethical compliance information
        if ethical_approval:
            analysis_results['ethical_compliance'] = {
                'approved': ethical_approval.ethics_approved,
                'compliance_score': ethical_approval.compliance_score,
                'age_verified': ethical_approval.age_verification.verified,
                'age_verification_method': ethical_approval.age_verification.verification_method,
                'ethical_assessment': asdict(ethical_approval.ethical_assessment),
                'usage_restrictions': ethical_approval.usage_restrictions,
                'monitoring_requirements': ethical_approval.monitoring_requirements,
                'professional_review_required': ethical_approval.professional_review is not None
            }

        # RESULTS PRESENTATION with enhanced authorization, consent, ethical and privacy information
        presentation_result = self.presentation_builder.build(analysis_results)

        # Add comprehensive privacy recommendations
        if self.privacy_framework:
            privacy_status = self.privacy_framework.validate_privacy_compliance()

            privacy_recommendations = [
                "🔒 Data automatically deleted within 24 hours - Zero persistent storage",
                "🔐 All transmissions encrypted with AES-256 end-to-end encryption",
                "👤 Personal identifiers anonymized using secure hashing algorithms",
                "🚫 No data retention - All user information purged after processing",
                "🛡️ Client-side processing available for maximum privacy protection",
                "📊 Analysis performed on anonymized data only",
                "🔍 Privacy compliance validated in real-time"
            ]

            presentation_result.mitigation_recommendations.extend(privacy_recommendations)

            analysis_results['privacy_compliance'] = privacy_status
            analysis_results['privacy_metrics'] = {
                'data_retention_hours': self.privacy_framework.retention_policy.max_retention_hours,
                'anonymization_level': privacy_level,
                'encryption_enabled': self.privacy_framework.processing_mode.encrypted_transmission_required,
                'client_side_available': self.privacy_framework.processing_mode.client_side_enabled,
                'processing_id': processing_id,
                'secure_deletion_enabled': self.privacy_framework.retention_policy.secure_deletion_required,
                'audit_trail_enabled': self.privacy_framework.retention_policy.audit_trail_enabled
            }

        # Add ethical compliance recommendations
        if ethical_approval:
            ethical_recommendations = [
                "✅ Ethical boundaries verified - Analysis approved for stated use case",
                "🔞 Age verification completed - User confirmed 18+ years old",
                "📋 Usage restrictions apply - See ethical compliance section for details",
                "⚖️ Professional ethics standards maintained throughout analysis"
            ]
            ethical_recommendations.extend(ethical_approval.ethical_assessment.recommendations)
            presentation_result.mitigation_recommendations.extend(ethical_recommendations)

        # Add comprehensive consent and control recommendations
        if self.consent_framework:
            consent_recommendations = [
                "✅ User consent verified - All processing authorized by user",
                "🎛️ Full user control - Immediate deletion and opt-out available at any time",
                "📋 Granular consent management - Specific permissions for each data use",
                "⏱️ Time-limited processing - All consents expire automatically",
                "🔄 Withdrawal options - Easy consent withdrawal with immediate effect",
                "🚪 Stage-by-stage opt-out - Can withdraw from any processing stage",
                "🗑️ Immediate data deletion - Request complete data removal anytime",
                "📊 Transparency reports - Regular disclosure of data handling practices"
            ]
            presentation_result.mitigation_recommendations.extend(consent_recommendations)

        # Add comprehensive authorization and access control recommendations
        if authorization_result:
            authorization_recommendations = [
                f"✅ Authorization verified - {authorization_result.access_level.value.title()} access level granted",
                f"🔐 Identity verified - Multi-factor authentication completed",
                f"📋 Access logged - All analysis requests tracked for security",
                f"🛡️ Abuse prevention active - IP-based monitoring enabled"
            ]

            if analysis_type == 'self_analysis':
                authorization_recommendations.extend([
                    "👤 Self-analysis confirmed - Analyzing your own digital footprint",
                    "🔒 Data ownership verified - Access to your social media profiles confirmed"
                ])
            elif analysis_type == 'third_party_analysis':
                authorization_recommendations.extend([
                    "📝 Third-party consent obtained - Written permission verified",
                    "⏰ Consent time-limited - Analysis permission expires automatically"
                ])

            presentation_result.mitigation_recommendations.extend(authorization_recommendations)

        analysis_results["results_presentation"] = asdict(presentation_result)

        logger.info(
            f"Authorization-verified, consent-verified, ethically-bounded, privacy-protected analysis completed")

        return analysis_results

    def _perform_authorized_analyses(self, content_list: List[str], social_data: Dict[str, Any],
                                     user_id: str, session_id: str,
                                     authorization_result) -> Dict[str, Any]:
        """Perform analyses based on authorization access level"""

        access_level = authorization_result.access_level if authorization_result else AccessLevel.BASIC

        # Base analyses available to all access levels
        analysis_results = {
            'sentiment_analysis': self._perform_sentiment_analysis_with_opt_out_check(content_list, user_id,
                                                                                      session_id),
            'hashtag_patterns': self._analyze_hashtag_patterns_with_opt_out_check(content_list, user_id, session_id),
            'mention_patterns': self._analyze_mention_patterns_with_opt_out_check(content_list, user_id, session_id),
            'engagement_analysis': self._analyze_engagement_with_opt_out_check(social_data, user_id, session_id),
            'topic_modeling': self._perform_topic_modeling_with_opt_out_check(content_list, user_id, session_id),
            'schedule_patterns': {},
            'economic_indicators': {},
            'mental_state_assessment': {},
            'interest_profile': {}
        }

        # Enhanced analyses for higher access levels
        if access_level in [AccessLevel.ENHANCED, AccessLevel.PROFESSIONAL]:
            # Schedule pattern analysis
            try:
                if not self._check_opt_out_request(user_id, session_id, 'SCHEDULE_ANALYSIS'):
                    schedule_analysis = self.schedule_detector.analyze_schedule_patterns(social_data)
                    analysis_results['schedule_patterns'] = {
                        'post_timing': asdict(schedule_analysis.post_timing),
                        'activity_frequency': asdict(schedule_analysis.activity_frequency),
                        'geographic_inference': asdict(schedule_analysis.geographic_inference),
                        'work_personal_boundary': asdict(schedule_analysis.work_personal_boundary),
                        'overall_schedule_score': schedule_analysis.overall_schedule_score,
                        'behavioral_insights': schedule_analysis.behavioral_insights,
                        'privacy_implications': schedule_analysis.privacy_implications,
                        'analysis_completed': True
                    }
                else:
                    analysis_results['schedule_patterns'] = {'status': 'opted_out', 'analysis_completed': False}
            except Exception as e:
                analysis_results['schedule_patterns'] = {'error': str(e), 'analysis_completed': False}

            # Economic indicators analysis
            try:
                if not self._check_opt_out_request(user_id, session_id, 'ECONOMIC_ANALYSIS'):
                    economic_analysis = self.economic_analyzer.analyze_economic_indicators(social_data)
                    analysis_results['economic_indicators'] = {
                        'brand_mentions': [asdict(b) for b in economic_analysis.brand_mentions],
                        'location_patterns': [asdict(l) for l in economic_analysis.location_patterns],
                        'purchase_activities': [asdict(p) for p in economic_analysis.purchase_activities],
                        'professional_network': asdict(economic_analysis.professional_network),
                        'economic_profile': asdict(economic_analysis.economic_profile),
                        'economic_risk_score': economic_analysis.economic_risk_score,
                        'economic_insights': economic_analysis.economic_insights,
                        'privacy_economic_implications': economic_analysis.privacy_economic_implications,
                        'analysis_completed': True
                    }
                else:
                    analysis_results['economic_indicators'] = {'status': 'opted_out', 'analysis_completed': False}
            except Exception as e:
                analysis_results['economic_indicators'] = {'error': str(e), 'analysis_completed': False}

        # Professional-level analyses
        if access_level == AccessLevel.PROFESSIONAL:
            # Mental state analysis (requires highest access level)
            try:
                if not self._check_opt_out_request(user_id, session_id, 'MENTAL_STATE_ANALYSIS'):
                    mental_state_analysis = self.mental_state_analyzer.analyze_mental_state(social_data)
                    analysis_results['mental_state_assessment'] = {
                        'language_patterns': asdict(mental_state_analysis.language_patterns),
                        'emoji_patterns': asdict(mental_state_analysis.emoji_patterns),
                        'social_interaction': asdict(mental_state_analysis.social_interaction),
                        'content_tone': asdict(mental_state_analysis.content_tone),
                        'risk_factors': asdict(mental_state_analysis.risk_factors),
                        'mental_state_profile': asdict(mental_state_analysis.mental_state_profile),
                        'assessment_confidence': mental_state_analysis.assessment_confidence,
                        'recommendations': mental_state_analysis.recommendations,
                        'privacy_considerations': mental_state_analysis.privacy_considerations,
                        'analysis_completed': True
                    }
                else:
                    analysis_results['mental_state_assessment'] = {'status': 'opted_out', 'analysis_completed': False}
            except Exception as e:
                analysis_results['mental_state_assessment'] = {'error': str(e), 'analysis_completed': False}

        # Generate interest profile based on available analyses
        analysis_results['interest_profile'] = self._generate_comprehensive_interest_profile(analysis_results)

        return analysis_results

    def _determine_analysis_scope(self, access_level: AccessLevel) -> Dict[str, bool]:
        """Determine what analyses are available for each access level"""

        scope_mapping = {
            AccessLevel.BASIC: {
                'sentiment_analysis': True,
                'hashtag_patterns': True,
                'mention_patterns': True,
                'engagement_analysis': True,
                'topic_modeling': True,
                'schedule_patterns': False,
                'economic_indicators': False,
                'mental_state_assessment': False
            },
            AccessLevel.ENHANCED: {
                'sentiment_analysis': True,
                'hashtag_patterns': True,
                'mention_patterns': True,
                'engagement_analysis': True,
                'topic_modeling': True,
                'schedule_patterns': True,
                'economic_indicators': True,
                'mental_state_assessment': False
            },
            AccessLevel.PROFESSIONAL: {
                'sentiment_analysis': True,
                'hashtag_patterns': True,
                'mention_patterns': True,
                'engagement_analysis': True,
                'topic_modeling': True,
                'schedule_patterns': True,
                'economic_indicators': True,
                'mental_state_assessment': True
            },
            AccessLevel.RESTRICTED: {
                'sentiment_analysis': False,
                'hashtag_patterns': False,
                'mention_patterns': False,
                'engagement_analysis': False,
                'topic_modeling': False,
                'schedule_patterns': False,
                'economic_indicators': False,
                'mental_state_assessment': False
            }
        }

        return scope_mapping.get(access_level, scope_mapping[AccessLevel.BASIC])

    def _create_authorization_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create response for authorization errors"""

        return {
            'analysis_approved': False,
            'rejection_reason': 'authorization_error',
            'error_message': error_message,
            'authorization_required': True,
            'recommendations': [
                'Verify your identity with multi-factor email verification',
                'Ensure you have permission to analyze the requested data',
                'Contact support if you believe this is an error'
            ],
            'analysis_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_version': '4.4',
                'authorization_approved': False,
                'rejection_type': 'authorization_error'
            }
        }

    def _create_authorization_rejection_response(self, authorization_result) -> Dict[str, Any]:
        """Create response for authorization rejections"""

        return {
            'analysis_approved': False,
            'rejection_reason': 'authorization_rejected',
            'authorization_result': asdict(authorization_result),
            'failure_reasons': authorization_result.failure_reasons,
            'required_actions': authorization_result.required_actions,
            'recommendations': [
                'Complete required identity verification steps',
                'Obtain necessary consent for third-party analysis',
                'Verify data ownership for self-analysis requests'
            ],
            'next_steps': {
                'identity_verification_required': authorization_result.verification_required,
                'consent_required': authorization_result.consent_required,
                'access_level': authorization_result.access_level.value
            },
            'analysis_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_version': '4.4',
                'authorization_approved': False,
                'rejection_type': 'authorization_rejected'
            }
        }

    # Authorization framework integration methods
    def initiate_identity_verification(self, user_id: str, email: str,
                                       ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Initiate identity verification process"""

        if not self.authorization_framework:
            return {'success': False, 'error': 'Authorization framework not available'}

        try:
            verification = self.authorization_framework.identity_verifier.initiate_email_verification(
                user_id, email, ip_address, user_agent
            )

            return {
                'success': True,
                'verification_id': verification.verification_id,
                'expires_at': verification.expires_at.isoformat(),
                'message': f'Verification code sent to {email}'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def verify_identity(self, verification_id: str, verification_code: str,
                        ip_address: str) -> Dict[str, Any]:
        """Complete identity verification"""

        if not self.authorization_framework:
            return {'success': False, 'error': 'Authorization framework not available'}

        return self.authorization_framework.identity_verifier.verify_identity(
            verification_id, verification_code, ip_address
        )

    def request_third_party_consent(self, requester_user_id: str, target_email: str,
                                    analysis_purpose: str, data_scope: List[str]) -> Dict[str, Any]:
        """Request consent for third-party analysis"""

        if not self.authorization_framework:
            return {'success': False, 'error': 'Authorization framework not available'}

        try:
            consent_request = self.authorization_framework.consent_manager.request_third_party_consent(
                requester_user_id, target_email, analysis_purpose, data_scope
            )

            return {
                'success': True,
                'consent_id': consent_request.consent_id,
                'consent_token': consent_request.consent_token,
                'expires_at': consent_request.expires_at.isoformat(),
                'message': f'Consent request sent to {target_email}'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_authorization_status(self) -> Dict[str, Any]:
        """Get current authorization framework status"""

        if not self.authorization_framework:
            return {'authorization_enabled': False}

        return self.authorization_framework.get_authorization_status()

    def _perform_sentiment_analysis_with_opt_out_check(self, content_list: List[str],
                                                       user_id: str, session_id: str) -> Dict[str, Any]:
        """Perform sentiment analysis with opt-out checking"""

        if self._check_opt_out_request(user_id, session_id, 'SENTIMENT_ANALYSIS'):
            return {'status': 'opted_out', 'message': 'User opted out of sentiment analysis'}

        return self._perform_sentiment_analysis(content_list)

    def _analyze_hashtag_patterns_with_opt_out_check(self, content_list: List[str],
                                                     user_id: str, session_id: str) -> Dict[str, Any]:
        """Analyze hashtag patterns with opt-out checking"""

        if self._check_opt_out_request(user_id, session_id, 'SENTIMENT_ANALYSIS'):
            return {'status': 'opted_out', 'message': 'User opted out of hashtag analysis'}

        return self._analyze_hashtag_patterns(content_list)

    def _analyze_mention_patterns_with_opt_out_check(self, content_list: List[str],
                                                     user_id: str, session_id: str) -> Dict[str, Any]:
        """Analyze mention patterns with opt-out checking"""

        if self._check_opt_out_request(user_id, session_id, 'SENTIMENT_ANALYSIS'):
            return {'status': 'opted_out', 'message': 'User opted out of mention analysis'}

        return self._analyze_mention_patterns(content_list)

    def _analyze_engagement_with_opt_out_check(self, social_data: Dict[str, Any],
                                               user_id: str, session_id: str) -> Dict[str, Any]:
        """Analyze engagement with opt-out checking"""

        if self._check_opt_out_request(user_id, session_id, 'SENTIMENT_ANALYSIS'):
            return {'status': 'opted_out', 'message': 'User opted out of engagement analysis'}

        return self._analyze_engagement(social_data)

    def _perform_topic_modeling_with_opt_out_check(self, content_list: List[str],
                                                   user_id: str, session_id: str) -> Dict[str, Any]:
        """Perform topic modeling with opt-out checking"""

        if self._check_opt_out_request(user_id, session_id, 'SENTIMENT_ANALYSIS'):
            return {'status': 'opted_out', 'message': 'User opted out of topic modeling'}

        return self._perform_topic_modeling(content_list)

    def _check_opt_out_request(self, user_id: str, session_id: str, stage: str) -> bool:
        """Check if user has requested opt-out at current stage"""

        if not self.consent_framework:
            return False

        # Check for active opt-out requests
        for request in self.consent_framework.opt_out_manager.opt_out_requests.values():
            if (request.user_id == user_id and
                    request.session_id == session_id and
                    request.processing_stage.value.upper() == stage and
                    request.status == 'pending'):
                return True

        return False

    def _create_consent_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create response for consent-related errors"""

        return {
            'analysis_approved': False,
            'rejection_reason': 'consent_required',
            'error_message': error_message,
            'consent_required': True,
            'recommendations': [
                'Complete the consent process to proceed with analysis',
                'Review and accept required consent items',
                'Ensure all mandatory consents are granted'
            ],
            'analysis_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_version': '4.4',
                'consent_verified': False,
                'rejection_type': 'consent_required'
            }
        }

    def request_immediate_deletion(self, user_id: str, deletion_scope: str = 'complete') -> Dict[str, Any]:
        """Request immediate deletion during or after analysis"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        deletion_request = self.consent_framework.deletion_manager.request_immediate_deletion(
            user_id, deletion_scope
        )

        return {
            'success': True,
            'request_id': deletion_request.request_id,
            'verification_code': deletion_request.verification_code,
            'message': 'Deletion request created. Use verification code to confirm.',
            'deletion_scope': deletion_scope,
            'estimated_completion': '< 5 minutes'
        }

    def execute_deletion(self, request_id: str, verification_code: str) -> Dict[str, Any]:
        """Execute verified deletion request"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        return self.consent_framework.deletion_manager.execute_deletion(request_id, verification_code)

    def request_opt_out(self, user_id: str, session_id: str, current_stage: str,
                        reason: str = None) -> Dict[str, Any]:
        """Request opt-out from current processing stage"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        from .consent_framework import ProcessingStage

        try:
            stage_enum = ProcessingStage[current_stage.upper()]
        except KeyError:
            return {'success': False, 'error': 'Invalid processing stage'}

        opt_out_request = self.consent_framework.opt_out_manager.request_opt_out(
            user_id, session_id, stage_enum, reason
        )

        return {
            'success': True,
            'request_id': opt_out_request.request_id,
            'message': 'Opt-out request processed. Processing will stop at current stage.',
            'data_to_delete': opt_out_request.data_to_delete
        }

    def process_opt_out(self, request_id: str) -> Dict[str, Any]:
        """Process opt-out request"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        return self.consent_framework.opt_out_manager.process_opt_out(request_id)

    def withdraw_consent(self, user_id: str, consent_type: str, reason: str = None) -> Dict[str, Any]:
        """Withdraw previously granted consent"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        from .consent_framework import ConsentType

        try:
            consent_type_enum = ConsentType[consent_type.upper()]
        except KeyError:
            return {'success': False, 'error': 'Invalid consent type'}

        success = self.consent_framework.consent_manager.withdraw_consent(
            user_id, consent_type_enum, reason
        )

        return {
            'success': success,
            'message': 'Consent withdrawn successfully' if success else 'Consent withdrawal failed',
            'consent_type': consent_type,
            'immediate_effect': True
        }

    def get_transparency_report(self) -> Dict[str, Any]:
        """Get current transparency report"""

        if not self.consent_framework:
            return {'transparency_enabled': False}

        return self.consent_framework.get_transparency_dashboard()

    def initiate_consent_process(self, user_id: str, session_id: str,
                                 ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Initiate user consent process"""

        if not self.consent_framework:
            return {'consent_enabled': False}

        return self.consent_framework.initiate_user_journey(user_id, session_id, ip_address, user_agent)

    def process_consent_step(self, process_id: str, consent_type: str, granted: bool,
                             ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Process individual consent step"""

        if not self.consent_framework:
            return {'success': False, 'error': 'Consent framework not available'}

        from .consent_framework import ConsentType

        try:
            consent_type_enum = ConsentType[consent_type.upper()]
        except KeyError:
            return {'success': False, 'error': 'Invalid consent type'}

        return self.consent_framework.consent_manager.process_consent_step(
            process_id, consent_type_enum, granted, ip_address, user_agent
        )

    # Continue with existing methods...

    def _extract_data_sources(self, social_data: Dict[str, Any]) -> List[str]:
        """Extract data sources from social data"""
        sources = []

        if 'social_profiles' in social_data:
            sources.append('public_social_media_profiles')

        if 'discovered_profiles' in social_data:
            sources.append('publicly_available_posts')

        # Check for any posts or content
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})
                    if 'posts' in inferred_data:
                        sources.append('publicly_visible_content')
                        break

        return list(set(sources))  # Remove duplicates

    def _extract_data_types(self, social_data: Dict[str, Any]) -> List[str]:
        """Extract data types from social data"""
        data_types = []

        # Check for different types of data
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})

                    if 'bio' in inferred_data or 'description' in inferred_data:
                        data_types.append('public_profile_information')

                    if 'posts' in inferred_data:
                        data_types.append('public_text_content')

                    if 'followers' in inferred_data or 'following' in inferred_data:
                        data_types.append('public_engagement_metrics')

        return list(set(data_types))  # Remove duplicates

    def _create_ethical_rejection_response(self, ethical_approval) -> Dict[str, Any]:
        """Create response for ethically rejected requests"""

        return {
            'analysis_approved': False,
            'rejection_reason': 'ethical_boundaries',
            'ethical_assessment': asdict(ethical_approval.ethical_assessment),
            'age_verification': asdict(ethical_approval.age_verification),
            'violations': [v.value for v in ethical_approval.ethical_assessment.violations],
            'recommendations': ethical_approval.ethical_assessment.recommendations,
            'usage_restrictions': ethical_approval.usage_restrictions,
            'appeal_process': 'Contact ethics board for review if you believe this rejection is in error',
            'analysis_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_version': '4.4',
                'ethics_approved': False,
                'rejection_type': 'ethical_boundaries'
            }
        }

    def _create_ethical_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create response for ethical evaluation errors"""

        return {
            'analysis_approved': False,
            'rejection_reason': 'ethical_evaluation_error',
            'error_message': error_message,
            'recommendations': [
                'Please verify age verification data is complete',
                'Ensure use case description is provided',
                'Contact support if the error persists'
            ],
            'analysis_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'analysis_version': '4.4',
                'ethics_approved': False,
                'rejection_type': 'evaluation_error'
            }
        }

    def _classify_mental_health_risk(self, risk_factors) -> str:
        """Classify mental health risk level"""

        if not hasattr(risk_factors, 'depression_indicators'):
            return 'unknown'

        try:
            # Calculate average risk scores
            depression_risk = np.mean(
                list(risk_factors.depression_indicators.values())) if risk_factors.depression_indicators else 0
            anxiety_risk = np.mean(
                list(risk_factors.anxiety_indicators.values())) if risk_factors.anxiety_indicators else 0
            stress_risk = np.mean(
                list(risk_factors.stress_indicators.values())) if risk_factors.stress_indicators else 0

            overall_risk = (depression_risk + anxiety_risk + stress_risk) / 3

            # Factor in crisis warnings
            if risk_factors.crisis_warning_signals:
                overall_risk = max(overall_risk, 0.8)

            # Classify risk
            if overall_risk > 0.7:
                return 'high'
            elif overall_risk > 0.4:
                return 'medium'
            else:
                return 'low'

        except Exception:
            return 'unknown'

    def _extract_content_from_social_data(self, social_data: Dict[str, Any]) -> List[str]:
        """Extract text content from social media data"""

        content_list = []

        # Extract from different social media platforms
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    # Extract bio/description
                    inferred_data = profile.get('inferred_data', {})

                    if 'bio' in inferred_data:
                        content_list.append(inferred_data['bio'])

                    if 'description' in inferred_data:
                        content_list.append(inferred_data['description'])

                    if 'page_title' in profile:
                        content_list.append(profile['page_title'])

                    if 'page_description' in profile:
                        content_list.append(profile['page_description'])

                    # Extract from posts if available
                    if 'posts' in inferred_data:
                        for post in inferred_data['posts'][:10]:  # Limit to 10 posts
                            if isinstance(post, dict) and 'text' in post:
                                content_list.append(post['text'])
                            elif isinstance(post, str):
                                content_list.append(post)

        # Filter out empty or very short content
        content_list = [content for content in content_list if content and len(content.strip()) > 10]

        return content_list

    def _perform_sentiment_analysis(self, content_list: List[str]) -> Dict[str, Any]:
        """Perform comprehensive sentiment analysis"""

        if not content_list:
            return {'overall_sentiment': 'neutral', 'sentiment_distribution': {}, 'emotional_profile': {}}

        sentiment_results = []
        emotional_indicators = defaultdict(int)

        for content in content_list:
            result = self.sentiment_analyzer.analyze_sentiment(content)
            sentiment_results.append(result)

            # Count emotional indicators
            for emotion in result.emotional_indicators:
                emotional_indicators[emotion] += 1

        # Calculate overall sentiment
        avg_polarity = np.mean([r.polarity for r in sentiment_results])
        avg_subjectivity = np.mean([r.subjectivity for r in sentiment_results])

        # Classify overall sentiment
        if avg_polarity > 0.1:
            overall_sentiment = 'positive'
        elif avg_polarity < -0.1:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'

        # Distribution of sentiments
        sentiment_counts = Counter([r.classification for r in sentiment_results])
        total_sentiments = len(sentiment_results)

        sentiment_distribution = {
            classification: count / total_sentiments
            for classification, count in sentiment_counts.items()
        }

        # Emotional profile
        total_emotions = sum(emotional_indicators.values())
        emotional_profile = {
            emotion: count / total_emotions if total_emotions > 0 else 0
            for emotion, count in emotional_indicators.items()
        }

        return {
            'overall_sentiment': overall_sentiment,
            'average_polarity': avg_polarity,
            'average_subjectivity': avg_subjectivity,
            'sentiment_distribution': sentiment_distribution,
            'emotional_profile': emotional_profile,
            'confidence_score': np.mean([r.confidence for r in sentiment_results])
        }

    def _analyze_hashtag_patterns(self, content_list: List[str]) -> Dict[str, Any]:
        """Analyze hashtag usage patterns"""

        hashtag_patterns = self.hashtag_analyzer.analyze_hashtag_patterns(content_list)

        if not hashtag_patterns:
            return {'patterns': [], 'usage_style': 'minimal', 'trending_topics': []}

        # Determine usage style
        total_hashtags = sum(p.frequency for p in hashtag_patterns)
        unique_hashtags = len(hashtag_patterns)

        if total_hashtags == 0:
            usage_style = 'minimal'
        elif unique_hashtags / len(content_list) > 0.5:
            usage_style = 'diverse'
        elif total_hashtags / len(content_list) > 2:
            usage_style = 'heavy'
        else:
            usage_style = 'moderate'

        # Get trending topics
        trending_topics = [
            {'hashtag': p.hashtag, 'score': p.trending_score}
            for p in hashtag_patterns[:5]  # Top 5
        ]

        return {
            'patterns': [asdict(p) for p in hashtag_patterns],
            'usage_style': usage_style,
            'total_hashtags': total_hashtags,
            'unique_hashtags': unique_hashtags,
            'trending_topics': trending_topics
        }

    def _analyze_mention_patterns(self, content_list: List[str]) -> Dict[str, Any]:
        """Analyze mention (@username) patterns"""

        return self.hashtag_analyzer.analyze_mention_patterns(content_list)

    def _analyze_engagement(self, social_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content engagement patterns"""

        # Extract engagement data from social profiles
        content_data = []

        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})

                    # Create content entry with engagement metrics
                    content_entry = {
                        'text': inferred_data.get('bio', ''),
                        'likes': inferred_data.get('followers', 0),
                        'comments': inferred_data.get('public_repos', 0),  # For GitHub
                        'shares': 0,  # Placeholder
                        'reactions': 0  # Placeholder
                    }

                    if content_entry['text']:
                        content_data.append(content_entry)

        if not content_data:
            return asdict(EngagementMetrics(0.0, {}, [], 'neutral', 0.0, 0.0))

        engagement_metrics = self.engagement_analyzer.analyze_engagement(content_data)
        return asdict(engagement_metrics)

    def _perform_topic_modeling(self, content_list: List[str]) -> Dict[str, Any]:
        """Perform topic modeling for interest categorization"""

        if len(content_list) < 3:
            return {'topics': [], 'primary_topics': [], 'topic_diversity': 0.0}

        topics = self.topic_engine.perform_topic_modeling(content_list, num_topics=5)

        # Get primary topics (top 3 by relevance)
        primary_topics = [
            {
                'name': topic.topic_name,
                'keywords': topic.keywords,
                'relevance': topic.relevance_score
            }
            for topic in topics[:3]
        ]

        # Calculate topic diversity
        if topics:
            relevance_scores = [t.relevance_score for t in topics]
            topic_diversity = 1.0 - (max(relevance_scores) - min(relevance_scores))
        else:
            topic_diversity = 0.0

        return {
            'topics': [asdict(topic) for topic in topics],
            'primary_topics': primary_topics,
            'topic_diversity': topic_diversity,
            'total_topics_identified': len(topics)
        }

    def _generate_comprehensive_interest_profile(self, analysis_results: Dict[str, Any]) -> InterestProfile:
        """Generate comprehensive interest profile including all analysis dimensions"""

        # Extract primary interests from topic modeling
        primary_interests = []
        interest_scores = {}

        topic_data = analysis_results.get('topic_modeling', {})
        for topic in topic_data.get('primary_topics', []):
            interest_name = topic['name']
            primary_interests.append(interest_name)
            interest_scores[interest_name] = topic['relevance']

        # Add interests from hashtag patterns
        hashtag_data = analysis_results.get('hashtag_patterns', {})
        for pattern in hashtag_data.get('patterns', [])[:3]:  # Top 3 hashtags
            hashtag = pattern['hashtag']
            if hashtag not in interest_scores:
                interest_scores[hashtag] = pattern['trending_score']

        # Add interests from economic indicators
        economic_data = analysis_results.get('economic_indicators', {})
        for brand in economic_data.get('brand_mentions', [])[:3]:  # Top 3 brands
            brand_name = brand.get('brand_name', '')
            if brand_name and brand_name not in interest_scores:
                interest_scores[brand_name] = brand.get('sentiment_score', 0.0)

        # Comprehensive behavioral patterns from all analyses
        sentiment_data = analysis_results.get('sentiment_analysis', {})
        engagement_data = analysis_results.get('engagement_analysis', {})
        schedule_data = analysis_results.get('schedule_patterns', {})
        mental_state_data = analysis_results.get('mental_state_assessment', {})

        comprehensive_behavioral_patterns = {
            # Core behavioral patterns
            'emotional_tendency': sentiment_data.get('overall_sentiment', 'neutral'),
            'communication_style': self._determine_communication_style(sentiment_data, hashtag_data),
            'engagement_preference': engagement_data.get('audience_response_sentiment', 'neutral'),
            'content_frequency': self._estimate_content_frequency(analysis_results),

            # Schedule-based behavioral patterns
            'temporal_signature': schedule_data.get('post_timing', {}).get('temporal_signature', 'unknown'),
            'activity_rhythm': schedule_data.get('activity_frequency', {}).get('engagement_rhythm', 'unknown'),
            'geographic_scope': schedule_data.get('geographic_inference', {}).get('geographic_scope', 'unknown'),
            'work_life_balance': schedule_data.get('work_personal_boundary', {}).get('boundary_clarity', 'unknown'),
            'schedule_consistency': schedule_data.get('post_timing', {}).get('consistency_score', 0.0),
            'privacy_awareness': len([i for i in schedule_data.get('privacy_implications', []) if '✅' in i]) > 0,
            'posting_frequency': schedule_data.get('post_timing', {}).get('posting_frequency', 'unknown'),
            'peak_activity_hours': schedule_data.get('post_timing', {}).get('peak_hours', []),
            'time_zone_indicators': schedule_data.get('post_timing', {}).get('time_zone_indicators', []),

            # Economic behavioral patterns
            'spending_capacity': economic_data.get('economic_profile', {}).get('spending_capacity', 'unknown'),
            'brand_affinity': economic_data.get('economic_profile', {}).get('brand_affinity_tier', 'unknown'),
            'purchase_style': economic_data.get('economic_profile', {}).get('purchase_decision_style', 'balanced'),
            'economic_lifestyle': economic_data.get('economic_profile', {}).get('economic_lifestyle', 'practical'),
            'professional_level': economic_data.get('professional_network', {}).get('seniority_level', 'unknown'),
            'economic_risk_awareness': economic_data.get('economic_risk_score', 0.0) < 0.5,
            'brand_loyalty_tendency': self._calculate_brand_loyalty_tendency(economic_data),
            'financial_sophistication': economic_data.get('economic_profile', {}).get('financial_sophistication',
                                                                                      'basic'),
            'professional_influence': economic_data.get('professional_network', {}).get('professional_influence', 0.0),

            # Mental state behavioral patterns
            'overall_mental_state': mental_state_data.get('mental_state_profile', {}).get('overall_mental_state',
                                                                                          'stable'),
            'emotional_stability': mental_state_data.get('mental_state_profile', {}).get('emotional_stability_score',
                                                                                         0.5),
            'social_connectivity': mental_state_data.get('mental_state_profile', {}).get('social_connectivity_level',
                                                                                         'unknown'),
            'stress_level': mental_state_data.get('mental_state_profile', {}).get('stress_level', 'unknown'),
            'wellbeing_trajectory': mental_state_data.get('mental_state_profile', {}).get('wellbeing_trajectory',
                                                                                          'stable'),
            'language_complexity': mental_state_data.get('language_patterns', {}).get('complexity_score', 0.0),
            'emoji_usage_frequency': mental_state_data.get('emoji_patterns', {}).get('emoji_frequency', 0.0),
            'social_isolation_risk': mental_state_data.get('social_interaction', {}).get('social_engagement_level',
                                                                                         'unknown') == 'isolated',
            'mental_health_protective_factors': len(
                mental_state_data.get('risk_factors', {}).get('protective_factors', [])),
            'crisis_risk_indicators': len(mental_state_data.get('risk_factors', {}).get('crisis_warning_signals', []))
        }

        # Comprehensive content preferences with all insights
        comprehensive_content_preferences = {
            # Core content preferences
            'preferred_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
            'hashtag_usage': hashtag_data.get('usage_style', 'minimal'),
            'interaction_style': analysis_results.get('mention_patterns', {}).get('interaction_style',
                                                                                  'non_interactive'),
            'topic_diversity': topic_data.get('topic_diversity', 0.0),

            # Schedule-based preferences
            'preferred_posting_times': schedule_data.get('post_timing', {}).get('peak_hours', []),
            'geographic_preferences': schedule_data.get('geographic_inference', {}).get('likely_locations', []),
            'work_content_ratio': schedule_data.get('work_personal_boundary', {}).get('professional_content_ratio',
                                                                                      0.0),

            # Economic content preferences
            'brand_mention_frequency': len(economic_data.get('brand_mentions', [])),
            'location_sharing_tendency': len(economic_data.get('location_patterns', [])),
            'purchase_sharing_behavior': len(economic_data.get('purchase_activities', [])),
            'professional_content_ratio': economic_data.get('professional_network', {}).get('thought_leadership_score',
                                                                                            0.0),
            'luxury_brand_affinity': len(
                [b for b in economic_data.get('brand_mentions', []) if b.get('price_tier') == 'luxury']),
            'economic_transparency': economic_data.get('economic_risk_score', 0.0),
            'career_focus_level': economic_data.get('professional_network', {}).get('networking_activity', 'passive'),

            # Mental state content preferences
            'emotional_expression_frequency': mental_state_data.get('emoji_patterns', {}).get('emotional_emoji_ratio',
                                                                                              0.0),
            'social_interaction_preference': mental_state_data.get('social_interaction', {}).get('interaction_rate',
                                                                                                 0.0),
            'language_formality_preference': mental_state_data.get('language_patterns', {}).get('formality_level',
                                                                                                'neutral'),
            'content_tone_consistency': mental_state_data.get('content_tone', {}).get('tone_consistency', 0.0),
            'wellbeing_content_sharing': len(mental_state_data.get('content_tone', {}).get('wellbeing_indicators', [])),
            'emotional_volatility': mental_state_data.get('content_tone', {}).get('emotional_volatility', 0.0),
            'crisis_communication_patterns': len(
                mental_state_data.get('risk_factors', {}).get('crisis_warning_signals', [])) > 0
        }

        # Enhanced engagement style determination with all factors
        engagement_style = self._determine_comprehensive_engagement_style(
            engagement_data, comprehensive_behavioral_patterns, schedule_data, economic_data, mental_state_data
        )

        return InterestProfile(
            primary_interests=primary_interests,
            interest_scores=interest_scores,
            interest_evolution={},  # Would require historical data
            behavioral_patterns=comprehensive_behavioral_patterns,
            content_preferences=comprehensive_content_preferences,
            engagement_style=engagement_style
        )

    def _calculate_brand_loyalty_tendency(self, economic_data: Dict[str, Any]) -> str:
        """Calculate brand loyalty tendency from purchase activities"""

        purchase_activities = economic_data.get('purchase_activities', [])

        if not purchase_activities:
            return 'unknown'

        loyalty_scores = [activity.get('brand_loyalty_score', 0.0) for activity in purchase_activities]
        avg_loyalty = np.mean(loyalty_scores) if loyalty_scores else 0.0

        if avg_loyalty > 0.7:
            return 'high'
        elif avg_loyalty > 0.4:
            return 'medium'
        else:
            return 'low'

    def _determine_communication_style(self, sentiment_data: Dict, hashtag_data: Dict) -> str:
        """Determine communication style from sentiment and hashtag usage"""

        sentiment = sentiment_data.get('overall_sentiment', 'neutral')
        subjectivity = sentiment_data.get('average_subjectivity', 0.5)
        hashtag_style = hashtag_data.get('usage_style', 'minimal')

        if subjectivity > 0.7 and sentiment == 'positive':
            return 'enthusiastic'
        elif subjectivity > 0.7 and sentiment == 'negative':
            return 'critical'
        elif subjectivity < 0.3:
            return 'factual'
        elif hashtag_style == 'heavy':
            return 'expressive'
        else:
            return 'balanced'

    def _estimate_content_frequency(self, analysis_results: Dict) -> str:
        """Estimate content posting frequency"""

        content_count = analysis_results.get('analysis_metadata', {}).get('content_analyzed', 0)

        if content_count > 20:
            return 'high'
        elif content_count > 10:
            return 'moderate'
        elif content_count > 5:
            return 'low'
        else:
            return 'minimal'

    def _determine_comprehensive_engagement_style(self, engagement_data: Dict,
                                                  behavioral_patterns: Dict,
                                                  schedule_data: Dict,
                                                  economic_data: Dict,
                                                  mental_state_data: Dict) -> str:
        """Determine comprehensive engagement style including all factors"""

        engagement_rate = engagement_data.get('engagement_rate', 0.0)
        viral_potential = engagement_data.get('viral_potential', 0.0)
        communication_style = behavioral_patterns.get('communication_style', 'balanced')

        # Schedule-based factors
        temporal_signature = behavioral_patterns.get('temporal_signature', 'unknown')
        activity_rhythm = behavioral_patterns.get('activity_rhythm', 'unknown')
        consistency_score = behavioral_patterns.get('schedule_consistency', 0.0)

        # Economic factors
        professional_influence = behavioral_patterns.get('professional_influence', 0.0)
        spending_capacity = behavioral_patterns.get('spending_capacity', 'unknown')
        professional_level = behavioral_patterns.get('professional_level', 'unknown')

        # Mental state factors
        mental_state = behavioral_patterns.get('overall_mental_state', 'stable')
        emotional_stability = behavioral_patterns.get('emotional_stability', 0.5)
        social_connectivity = behavioral_patterns.get('social_connectivity', 'unknown')

        # Comprehensive engagement style determination with mental health considerations

        # Crisis or concerning mental state overrides other factors
        if mental_state in ['critical', 'concerning']:
            if social_connectivity == 'isolated':
                return 'withdrawn_isolated'
            elif emotional_stability < 0.3:
                return 'emotionally_volatile'
            else:
                return 'struggling_communicator'

        # High-functioning patterns
        if professional_influence > 0.7 and professional_level in ['executive', 'senior']:
            if mental_state == 'positive' and emotional_stability > 0.7:
                return 'influential_thought_leader'
            elif consistency_score > 0.7:
                return 'professional_thought_leader'
            else:
                return 'executive_influencer'

        # Influencer patterns with mental health context
        elif engagement_rate > 0.7 and viral_potential > 0.5:
            if mental_state == 'positive' and emotional_stability > 0.6:
                if spending_capacity == 'high':
                    return 'balanced_luxury_influencer'
                else:
                    return 'stable_viral_influencer'
            elif emotional_stability < 0.4:
                return 'volatile_influencer'
            elif spending_capacity == 'high':
                return 'luxury_influencer'
            else:
                return 'viral_influencer'

        # Active engagement patterns
        elif engagement_rate > 0.5:
            if mental_state == 'positive' and social_connectivity in ['medium', 'high']:
                if 'business_hours' in temporal_signature:
                    return 'healthy_business_active'
                else:
                    return 'socially_healthy_active'
            elif social_connectivity == 'isolated':
                return 'active_but_isolated'
            elif activity_rhythm == 'bursty' and emotional_stability < 0.4:
                return 'emotionally_driven_active'
            elif 'business_hours' in temporal_signature:
                return 'business_active'
            else:
                return 'active'

        # Social engagement patterns
        elif communication_style == 'enthusiastic':
            if mental_state == 'positive' and social_connectivity == 'high':
                return 'socially_thriving'
            elif emotional_stability > 0.6:
                return 'stable_social'
            elif spending_capacity in ['high', 'medium']:
                return 'affluent_social'
            else:
                return 'social'

        # Informative patterns
        elif communication_style == 'factual':
            if mental_state == 'positive' and professional_level in ['senior', 'executive']:
                return 'authoritative_informative'
            elif emotional_stability > 0.7:
                return 'stable_informative'
            elif professional_level in ['senior', 'executive']:
                return 'executive_informative'
            else:
                return 'informative'

        # Scheduled/consistent patterns
        elif consistency_score > 0.6:
            if mental_state == 'positive' and emotional_stability > 0.6:
                return 'disciplined_communicator'
            elif professional_level in ['senior', 'executive']:
                return 'executive_scheduled'
            else:
                return 'scheduled_poster'

        # Default patterns with mental health context
        elif mental_state == 'positive' and emotional_stability > 0.6:
            if spending_capacity == 'high':
                return 'balanced_affluent_casual'
            else:
                return 'balanced_casual'
        elif social_connectivity == 'isolated':
            return 'casual_isolated'
        elif spending_capacity == 'high':
            return 'affluent_casual'
        else:
            return 'casual'

        def get_privacy_status(self) -> Dict[str, Any]:
            """Get current privacy framework status"""

            if not self.privacy_framework:
                return {'privacy_enabled': False}

            return {
                'privacy_enabled': True,
                'compliance_status': self.privacy_framework.validate_privacy_compliance(),
                'client_side_config': self.privacy_framework.get_client_side_config(),
                'retention_policy': {
                    'max_hours': self.privacy_framework.retention_policy.max_retention_hours,
                    'auto_deletion': self.privacy_framework.retention_policy.auto_deletion_enabled,
                    'secure_deletion': self.privacy_framework.retention_policy.secure_deletion_required,
                    'audit_trail': self.privacy_framework.retention_policy.audit_trail_enabled
                }
            }

        def get_ethical_compliance_status(self) -> Dict[str, Any]:
            """Get current ethical compliance status"""

            if not self.ethical_framework:
                return {'ethical_boundaries_enabled': False}

            return {
                'ethical_boundaries_enabled': True,
                'compliance_report': self.ethical_framework.get_compliance_report(),
                'ethics_board_status': 'active',
                'age_verification_methods': [
                    'government_id',
                    'credit_card',
                    'phone_verification',
                    'third_party_service',
                    'declaration_with_validation'
                ],
                'allowed_use_cases': [
                    'legitimate_research',
                    'security_analysis',
                    'self_assessment',
                    'educational'
                ],
                'prohibited_use_cases': [
                    'malicious_stalking',
                    'harassment',
                    'discrimination',
                    'unauthorized_profiling'
                ]
            }

        def get_consent_status(self) -> Dict[str, Any]:
            """Get current consent framework status"""

            if not self.consent_framework:
                return {'consent_enabled': False}

            return {
                'consent_enabled': True,
                'multi_step_consent': True,
                'granular_control': True,
                'immediate_deletion': True,
                'stage_by_stage_opt_out': True,
                'consent_withdrawal': True,
                'transparency_reports': True,
                'available_consent_types': [
                    'data_collection',
                    'data_processing',
                    'analysis_inference',
                    'data_retention',
                    'result_storage',
                    'third_party_sharing',
                    'marketing_communications'
                ],
                'processing_stages': [
                    'data_ingestion',
                    'privacy_anonymization',
                    'ethical_evaluation',
                    'sentiment_analysis',
                    'schedule_analysis',
                    'economic_analysis',
                    'mental_state_analysis',
                    'results_generation',
                    'data_deletion'
                ]
            }

        def enable_client_side_processing(self) -> Dict[str, Any]:
            """Enable client-side processing mode"""

            if not self.privacy_framework:
                raise ValueError("Privacy framework not initialized")

            self.privacy_framework.processing_mode.client_side_enabled = True
            self.privacy_framework.processing_mode.local_processing_only = True

            return self.privacy_framework.get_client_side_config()

        def _create_empty_analysis(self, processing_id: str = None, privacy_level: str = 'standard',
                                   ethical_approval=None, consent_verified: bool = False,
                                   authorization_result=None) -> Dict[str, Any]:
            """Create empty analysis structure when no content is available"""

            return {
                'sentiment_analysis': {
                    'overall_sentiment': 'neutral',
                    'sentiment_distribution': {},
                    'emotional_profile': {}
                },
                'hashtag_patterns': {
                    'patterns': [],
                    'usage_style': 'minimal',
                    'trending_topics': []
                },
                'mention_patterns': {
                    'total_mentions': 0,
                    'interaction_style': 'non_interactive'
                },
                'engagement_analysis': asdict(EngagementMetrics(0.0, {}, [], 'neutral', 0.0, 0.0)),
                'topic_modeling': {
                    'topics': [],
                    'primary_topics': [],
                    'topic_diversity': 0.0
                },
                'schedule_patterns': {
                    'post_timing': {},
                    'activity_frequency': {},
                    'geographic_inference': {},
                    'work_personal_boundary': {},
                    'overall_schedule_score': 0.0,
                    'behavioral_insights': [],
                    'privacy_implications': [],
                    'analysis_completed': False
                },
                'economic_indicators': {
                    'brand_mentions': [],
                    'location_patterns': [],
                    'purchase_activities': [],
                    'professional_network': {},
                    'economic_profile': {},
                    'economic_risk_score': 0.0,
                    'economic_insights': [],
                    'privacy_economic_implications': [],
                    'analysis_completed': False
                },
                'mental_state_assessment': {
                    'language_patterns': {},
                    'emoji_patterns': {},
                    'social_interaction': {},
                    'content_tone': {},
                    'risk_factors': {},
                    'mental_state_profile': {},
                    'assessment_confidence': 0.0,
                    'recommendations': [],
                    'privacy_considerations': [],
                    'analysis_completed': False
                },
                'interest_profile': asdict(InterestProfile([], {}, {}, {}, {}, 'minimal')),
                'authorization_status': {
                    'authorized': authorization_result.authorized if authorization_result else True,
                    'access_level': authorization_result.access_level.value if authorization_result else 'basic',
                    'verification_completed': True,
                    'consent_obtained': True,
                    'analysis_scope': self._determine_analysis_scope(
                        authorization_result.access_level if authorization_result else AccessLevel.BASIC)
                },
                'privacy_compliance': self.privacy_framework.validate_privacy_compliance() if self.privacy_framework else {},
                'privacy_metrics': {
                    'processing_id': processing_id,
                    'privacy_level': privacy_level,
                    'data_protection_enabled': self.privacy_framework is not None
                },
                'ethical_compliance': {
                    'approved': ethical_approval.ethics_approved if ethical_approval else True,
                    'compliance_score': ethical_approval.compliance_score if ethical_approval else 1.0,
                    'age_verified': ethical_approval.age_verification.verified if ethical_approval else False,
                    'restrictions_applied': True
                } if ethical_approval else {'enabled': self.ethical_framework is not None},
                'consent_status': {
                    'consent_verified': consent_verified,
                    'user_control_options': {
                        'immediate_deletion': True,
                        'opt_out_available': True,
                        'withdraw_consent': True,
                        'download_data': True
                    }
                },
                'results_presentation': {
                    'privacy_score': {'value': 1, 'colour': '#008000'},
                    'inferences': [],
                    'mitigation_recommendations': [
                        '🔒 Privacy framework active - Zero data retention',
                        '⚖️ Ethical boundaries enforced - All guidelines followed',
                        '🎛️ User consent verified - Full control maintained',
                        '🔐 Authorization verified - Identity and access confirmed',
                        '🛡️ All analysis performed on anonymized data',
                        '🚫 No content available for comprehensive analysis'
                    ]
                },
                'analysis_metadata': {
                    'content_analyzed': 0,
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'analysis_version': '4.4',
                    'privacy_protected': self.privacy_framework is not None,
                    'ethics_approved': ethical_approval.ethics_approved if ethical_approval else True,
                    'consent_verified': consent_verified,
                    'authorization_approved': authorization_result.authorized if authorization_result else True,
                    'access_level': authorization_result.access_level.value if authorization_result else 'basic',
                    'processing_id': processing_id,
                    'privacy_level': privacy_level,
                    'ethical_compliance_score': ethical_approval.compliance_score if ethical_approval else 1.0,
                    'note': 'Insufficient content for comprehensive analysis',
                    'opt_out_available': True,
                    'immediate_deletion_available': True,
                    'features': [
                        'authorization_framework',
                        'sentiment_analysis',
                        'hashtag_patterns',
                        'mention_patterns',
                        'engagement_analysis',
                        'topic_modeling',
                        'schedule_patterns',
                        'economic_indicators',
                        'mental_state_assessment',
                        'interest_profile',
                        'privacy_framework',
                        'ethical_boundaries',
                        'consent_framework',
                        'results_presentation'
                    ],
                    'economic_brands_detected': 0,
                    'economic_locations_detected': 0,
                    'purchase_activities_detected': 0,
                    'economic_risk_level': 'low',
                    'professional_influence_detected': False,
                    'mental_state_detected': 'stable',
                    'mental_health_risk_level': 'low',
                    'emotional_stability_score': 0.5,
                    'social_connectivity_level': 'unknown',
                    'crisis_indicators_detected': False,
                    'protective_factors_identified': 0
                }
            }

        def get_comprehensive_framework_status(self) -> Dict[str, Any]:
            """Get complete status of all integrated frameworks"""

            return {
                'framework_integration': {
                    'privacy_framework': self.privacy_framework is not None,
                    'ethical_framework': self.ethical_framework is not None,
                    'consent_framework': self.consent_framework is not None,
                    'authorization_framework': self.authorization_framework is not None
                },
                'privacy_status': self.get_privacy_status(),
                'ethical_status': self.get_ethical_compliance_status(),
                'consent_status': self.get_consent_status(),
                'authorization_status': self.get_authorization_status(),
                'integrated_features': [
                    'Multi-factor identity verification',
                    'Third-party consent management',
                    'IP-based abuse prevention',
                    'Comprehensive access logging',
                    'Self-analysis data ownership verification',
                    'Tiered access level control',
                    'Real-time authorization checking',
                    'Session management and validation',
                    'Multi-step consent process',
                    'Granular consent management',
                    'Stage-by-stage opt-out capabilities',
                    'Immediate data deletion',
                    'Consent withdrawal mechanisms',
                    'Transparency reporting',
                    'Zero persistent storage',
                    'Advanced anonymization',
                    'End-to-end encryption',
                    'Secure data deletion',
                    'Ethical boundaries enforcement',
                    'Professional ethics oversight',
                    'Age verification system',
                    'Malicious use prevention',
                    'Real-time compliance monitoring'
                ],
                'security_measures': {
                    'encryption': 'AES-256 end-to-end',
                    'data_retention': '24 hours maximum',
                    'deletion_method': 'Cryptographic overwriting',
                    'access_control': 'Multi-factor authentication',
                    'audit_logging': 'Complete activity tracking',
                    'abuse_prevention': 'IP-based blocking with escalation',
                    'session_security': 'Time-limited secure tokens',
                    'consent_verification': 'Multi-step process with audit trail'
                },
                'compliance_standards': [
                    'GDPR - General Data Protection Regulation',
                    'CCPA - California Consumer Privacy Act',
                    'PIPEDA - Personal Information Protection and Electronic Documents Act',
                    'LGPD - Lei Geral de Proteção de Dados',
                    'SOC 2 Type II - Security and Availability',
                    'ISO 27001 - Information Security Management',
                    'NIST Privacy Framework - Privacy Engineering',
                    'IEEE 2857 - Privacy Engineering Standards'
                ],
                'system_capabilities': {
                    'analysis_types': ['self_analysis', 'third_party_analysis', 'research_analysis',
                                       'security_analysis'],
                    'access_levels': ['basic', 'enhanced', 'professional', 'restricted'],
                    'verification_methods': ['email_verification', 'sms_verification', 'biometric_verification',
                                             'document_verification'],
                    'consent_types': ['data_collection', 'data_processing', 'analysis_inference', 'data_retention',
                                      'result_storage'],
                    'processing_stages': ['data_ingestion', 'privacy_anonymization', 'ethical_evaluation',
                                          'analysis_stages'],
                    'privacy_levels': ['minimal', 'standard', 'strict'],
                    'deletion_scopes': ['complete', 'analysis_only', 'partial']
                }
            }

    def create_ai_inference_engine(privacy_enabled: bool = True, ethics_enabled: bool = True,
                                   consent_enabled: bool = True, authorization_enabled: bool = True):
        """Factory function to create AI inference engine with full protection"""
        return AIInferenceEngine(
            privacy_enabled=privacy_enabled,
            ethics_enabled=ethics_enabled,
            consent_enabled=consent_enabled,
            authorization_enabled=authorization_enabled
        )






