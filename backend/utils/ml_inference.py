import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import re
from collections import Counter
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import logging

# For production, install these ML libraries:
# transformers, torch, scikit-learn, textblob

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Using fallback methods.")

logger = logging.getLogger(__name__)


class MLInferencePipeline:
    """
    Advanced AI Inference Pipeline using Machine Learning models for pattern analysis
    with lazy loading to improve startup performance
    """

    def __init__(self):
        # Initialize as None - models will be loaded only when first accessed
        self._sentiment_analyzer = None
        self._interest_classifier = None
        self._emotion_analyzer = None
        self.ml_models_loaded = False

        # Initialize pattern analyzers immediately (lightweight)
        self.initialize_pattern_analyzers()

        # Initialize fallback methods (lightweight)
        self._initialize_fallback_methods()

        logger.info("ML Inference Pipeline initialized with lazy loading")

    @property
    def sentiment_analyzer(self):
        """Lazy load sentiment analyzer"""
        if self._sentiment_analyzer is None and TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading sentiment analysis model...")
                self._sentiment_analyzer = pipeline(
                    'sentiment-analysis',
                    model='cardiffnlp/twitter-roberta-base-sentiment-latest'
                )
                logger.info("Sentiment analysis model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading sentiment model: {str(e)}")
                self._sentiment_analyzer = False  # Mark as failed
        return self._sentiment_analyzer

    @property
    def interest_classifier(self):
        """Lazy load interest classifier"""
        if self._interest_classifier is None and TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading interest classification model...")
                self._interest_classifier = pipeline(
                    'zero-shot-classification',
                    model='facebook/bart-large-mnli'
                )
                logger.info("Interest classification model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading interest classifier: {str(e)}")
                self._interest_classifier = False  # Mark as failed
        return self._interest_classifier

    @property
    def emotion_analyzer(self):
        """Lazy load emotion analyzer"""
        if self._emotion_analyzer is None and TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading emotion analysis model...")
                self._emotion_analyzer = pipeline(
                    'text-classification',
                    model='j-hartmann/emotion-english-distilroberta-base'
                )
                logger.info("Emotion analysis model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading emotion analyzer: {str(e)}")
                self._emotion_analyzer = False  # Mark as failed
        return self._emotion_analyzer

    def initialize_ml_models(self):
        """
        DEPRECATED: Models are now loaded lazily
        This method is kept for backward compatibility
        """
        logger.warning("initialize_ml_models() is deprecated. Models are now loaded lazily.")
        # Just check if transformers is available
        self.ml_models_loaded = TRANSFORMERS_AVAILABLE
        if self.ml_models_loaded:
            logger.info("ML models will be loaded on-demand")
        else:
            logger.info("Using fallback methods (transformers not available)")

    def _initialize_fallback_methods(self):
        """Initialize fallback methods when ML models aren't available"""
        self.sentiment_keywords = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'love', 'best', 'awesome', 'happy'],
            'negative': ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'sad', 'angry']
        }

        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'thrilled', 'delighted', 'cheerful'],
            'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'sadness': ['sad', 'depressed', 'disappointed', 'melancholy', 'gloomy']
        }

    def initialize_pattern_analyzers(self):
        """Initialize pattern analysis components"""
        # Interest categories for classification
        self.interest_categories = [
            'technology', 'fitness', 'travel', 'food', 'music', 'sports',
            'business', 'education', 'art', 'gaming', 'fashion', 'health',
            'finance', 'politics', 'science', 'entertainment'
        ]

        # Economic indicators patterns
        self.economic_patterns = {
            'high_income': ['luxury', 'premium', 'expensive', 'exclusive', 'high-end'],
            'budget_conscious': ['cheap', 'affordable', 'budget', 'discount', 'sale'],
            'investment_oriented': ['invest', 'portfolio', 'stocks', 'crypto', 'trading'],
            'career_focused': ['career', 'professional', 'promotion', 'networking', 'leadership']
        }

        # Schedule patterns
        self.time_patterns = {
            'early_bird': ['morning', 'early', '6am', '7am', 'sunrise', 'breakfast'],
            'night_owl': ['late', 'night', '11pm', '12am', 'midnight', 'evening'],
            'workday': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'work'],
            'weekend': ['saturday', 'sunday', 'weekend', 'leisure', 'relax']
        }

    def analyze_text_patterns(self, text_data: list) -> dict:
        """
        Main method to analyze patterns in collected text data using ML models
        """
        if not text_data:
            return self._empty_analysis_result()

        # Combine all text for analysis
        combined_text = ' '.join(text_data)

        analysis_results = {
            'sentiment_analysis': self._analyze_sentiment(combined_text),
            'emotion_analysis': self._analyze_emotions(combined_text),
            'interest_inference': self._infer_interests(combined_text),
            'personality_traits': self._infer_personality_traits(combined_text),
            'behavioral_patterns': self._analyze_behavioral_patterns(text_data),
            'economic_indicators': self._infer_economic_status(combined_text),
            'schedule_patterns': self._infer_schedule_patterns(combined_text),
            'communication_style': self._analyze_communication_style(combined_text),
            'social_patterns': self._analyze_social_patterns(combined_text)
        }

        # Calculate confidence scores
        analysis_results['confidence_scores'] = self._calculate_confidence_scores(analysis_results)

        return analysis_results

    def _analyze_sentiment(self, text: str) -> dict:
        """Analyze overall sentiment using ML models or fallback"""
        # Try to use ML model (will load lazily if needed)
        sentiment_model = self.sentiment_analyzer

        if sentiment_model and sentiment_model is not False:
            try:
                # Use transformer model for sentiment analysis
                result = sentiment_model(text[:512])
                sentiment_label = result[0]['label'].lower()
                confidence = result[0]['score']

                return {
                    'overall_sentiment': sentiment_label,
                    'confidence': confidence,
                    'method': 'transformer_model'
                }
            except Exception as e:
                logger.error(f"ML sentiment analysis failed: {str(e)}")

        # Fallback to rule-based sentiment analysis
        return self._fallback_sentiment_analysis(text)

    def _fallback_sentiment_analysis(self, text: str) -> dict:
        """Fallback sentiment analysis using TextBlob and keyword matching"""
        # Use TextBlob for basic sentiment
        blob = TextBlob(text.lower())
        polarity = blob.sentiment.polarity

        # Count positive and negative keywords
        positive_count = sum(1 for word in self.sentiment_keywords['positive'] if word in text.lower())
        negative_count = sum(1 for word in self.sentiment_keywords['negative'] if word in text.lower())

        if polarity > 0.1 or positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.8, 0.5 + abs(polarity))
        elif polarity < -0.1 or negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.8, 0.5 + abs(polarity))
        else:
            sentiment = 'neutral'
            confidence = 0.6

        return {
            'overall_sentiment': sentiment,
            'confidence': confidence,
            'method': 'textblob_keywords'
        }

    def _analyze_emotions(self, text: str) -> dict:
        """Analyze emotional patterns"""
        # Try to use ML model (will load lazily if needed)
        emotion_model = self.emotion_analyzer

        if emotion_model and emotion_model is not False:
            try:
                result = emotion_model(text[:512])
                emotion = result[0]['label'].lower()
                confidence = result[0]['score']

                return {
                    'primary_emotion': emotion,
                    'confidence': confidence,
                    'method': 'transformer_model'
                }
            except Exception as e:
                logger.error(f"ML emotion analysis failed: {str(e)}")

        # Fallback emotion detection
        emotions_detected = {}
        text_lower = text.lower()

        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                emotions_detected[emotion] = count

        if emotions_detected:
            primary_emotion = max(emotions_detected, key=emotions_detected.get)
            confidence = min(0.8, emotions_detected[primary_emotion] / 10)
        else:
            primary_emotion = 'neutral'
            confidence = 0.5

        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'detected_emotions': emotions_detected,
            'method': 'keyword_matching'
        }

    def _infer_interests(self, text: str) -> dict:
        """Infer user interests using classification models"""
        # Try to use ML model (will load lazily if needed)
        classifier = self.interest_classifier

        if classifier and classifier is not False:
            try:
                result = classifier(text[:512], self.interest_categories)
                interests = []

                for label, score in zip(result['labels'], result['scores']):
                    if score > 0.3:  # Threshold for relevance
                        interests.append({
                            'category': label,
                            'confidence': score
                        })

                return {
                    'interests': interests[:5],  # Top 5 interests
                    'method': 'zero_shot_classification'
                }
            except Exception as e:
                logger.error(f"ML interest classification failed: {str(e)}")

        # Fallback interest detection using keyword matching
        return self._fallback_interest_detection(text)

    def _fallback_interest_detection(self, text: str) -> dict:
        """Fallback interest detection using keyword matching"""
        interest_keywords = {
            'technology': ['tech', 'programming', 'coding', 'software', 'AI', 'computer'],
            'fitness': ['gym', 'workout', 'fitness', 'health', 'exercise', 'running'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine'],
            'music': ['music', 'concert', 'band', 'song', 'album'],
            'sports': ['sports', 'game', 'team', 'match', 'championship']
        }

        detected_interests = []
        text_lower = text.lower()

        for category, keywords in interest_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches >= 2:  # Require at least 2 keyword matches
                confidence = min(0.9, matches / len(keywords) + 0.3)
                detected_interests.append({
                    'category': category,
                    'confidence': confidence
                })

        # Sort by confidence
        detected_interests.sort(key=lambda x: x['confidence'], reverse=True)

        return {
            'interests': detected_interests[:5],
            'method': 'keyword_matching'
        }

    def _infer_personality_traits(self, text: str) -> dict:
        """Infer personality traits using text analysis"""
        personality_indicators = {
            'extroversion': ['social', 'party', 'people', 'friends', 'outgoing', 'energetic'],
            'openness': ['creative', 'art', 'novel', 'curious', 'explore', 'adventure'],
            'conscientiousness': ['organized', 'plan', 'schedule', 'responsible', 'detail'],
            'agreeableness': ['helpful', 'kind', 'cooperative', 'team', 'support'],
            'neuroticism': ['stress', 'worry', 'anxious', 'emotional', 'sensitive']
        }

        traits_detected = {}
        text_lower = text.lower()

        for trait, indicators in personality_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if matches > 0:
                # Normalize score based on text length and indicator presence
                score = min(1.0, matches / len(indicators) * 2)
                traits_detected[trait] = {
                    'score': score,
                    'confidence': min(0.8, score + 0.2)
                }

        return {
            'traits': traits_detected,
            'method': 'keyword_frequency_analysis'
        }

    def _analyze_behavioral_patterns(self, text_data: list) -> dict:
        """Analyze behavioral patterns from multiple text samples"""
        if len(text_data) < 2:
            return {'patterns': [], 'method': 'insufficient_data'}

        patterns = {
            'posting_frequency': self._analyze_posting_frequency(text_data),
            'content_consistency': self._analyze_content_consistency(text_data),
            'engagement_style': self._analyze_engagement_style(text_data)
        }

        return {
            'patterns': patterns,
            'method': 'temporal_analysis'
        }

    def _analyze_posting_frequency(self, text_data: list) -> dict:
        """Analyze posting frequency patterns"""
        total_posts = len(text_data)

        if total_posts < 5:
            frequency = 'low'
        elif total_posts < 20:
            frequency = 'moderate'
        else:
            frequency = 'high'

        return {
            'frequency_level': frequency,
            'total_posts_analyzed': total_posts
        }

    def _analyze_content_consistency(self, text_data: list) -> dict:
        """Analyze consistency in content themes"""
        if len(text_data) < 3:
            return {'consistency': 'unknown', 'reason': 'insufficient_data'}

        # Simple topic consistency using keyword overlap
        all_keywords = []
        for text in text_data:
            words = [word.lower() for word in text.split() if len(word) > 3]
            all_keywords.extend(words)

        keyword_frequency = Counter(all_keywords)
        common_keywords = [word for word, count in keyword_frequency.most_common(10) if count > 1]

        consistency_score = len(common_keywords) / max(len(set(all_keywords)), 1)

        if consistency_score > 0.3:
            consistency = 'high'
        elif consistency_score > 0.1:
            consistency = 'moderate'
        else:
            consistency = 'low'

        return {
            'consistency': consistency,
            'score': consistency_score,
            'common_themes': common_keywords[:5]
        }

    def _analyze_engagement_style(self, text_data: list) -> dict:
        """Analyze social engagement patterns"""
        engagement_indicators = {
            'questions': sum(1 for text in text_data if '?' in text),
            'exclamations': sum(1 for text in text_data if '!' in text),
            'mentions': sum(len(re.findall(r'@\w+', text)) for text in text_data),
            'hashtags': sum(len(re.findall(r'#\w+', text)) for text in text_data)
        }

        total_posts = len(text_data)
        engagement_score = sum(engagement_indicators.values()) / max(total_posts, 1)

        if engagement_score > 2:
            style = 'highly_interactive'
        elif engagement_score > 0.5:
            style = 'moderately_interactive'
        else:
            style = 'low_interaction'

        return {
            'style': style,
            'score': engagement_score,
            'indicators': engagement_indicators
        }

    def _infer_economic_status(self, text: str) -> dict:
        """Infer economic indicators from text"""
        economic_scores = {}
        text_lower = text.lower()

        for category, keywords in self.economic_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                economic_scores[category] = {
                    'score': min(1.0, matches / len(keywords) * 3),
                    'matches': matches
                }

        return {
            'indicators': economic_scores,
            'method': 'keyword_pattern_matching'
        }

    def _infer_schedule_patterns(self, text: str) -> dict:
        """Infer activity schedule patterns"""
        schedule_scores = {}
        text_lower = text.lower()

        for pattern, keywords in self.time_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > 0:
                schedule_scores[pattern] = {
                    'score': min(1.0, matches / len(keywords) * 2),
                    'matches': matches
                }

        return {
            'patterns': schedule_scores,
            'method': 'temporal_keyword_analysis'
        }

    def _analyze_communication_style(self, text: str) -> dict:
        """Analyze communication style patterns"""
        style_indicators = {
            'formality': self._assess_formality(text),
            'emoji_usage': len(re.findall(r'[😀-🙏]', text)),
            'abbreviation_usage': len(re.findall(r'\b[A-Z]{2,}\b', text)),
            'average_sentence_length': self._calculate_avg_sentence_length(text),
            'vocabulary_complexity': self._assess_vocabulary_complexity(text)
        }

        # Determine overall communication style
        if style_indicators['formality'] > 0.7:
            overall_style = 'formal'
        elif style_indicators['emoji_usage'] > 5 or style_indicators['abbreviation_usage'] > 3:
            overall_style = 'casual'
        else:
            overall_style = 'neutral'

        return {
            'style': overall_style,
            'indicators': style_indicators,
            'method': 'linguistic_analysis'
        }

    def _assess_formality(self, text: str) -> float:
        """Assess text formality level"""
        formal_indicators = ['therefore', 'however', 'furthermore', 'consequently', 'moreover']
        informal_indicators = ['gonna', 'wanna', 'yeah', 'ok', 'cool', 'awesome']

        formal_count = sum(1 for indicator in formal_indicators if indicator in text.lower())
        informal_count = sum(1 for indicator in informal_indicators if indicator in text.lower())

        if formal_count + informal_count == 0:
            return 0.5  # Neutral

        formality_score = formal_count / (formal_count + informal_count)
        return formality_score

    def _calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0

        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)

    def _assess_vocabulary_complexity(self, text: str) -> float:
        """Assess vocabulary complexity"""
        words = [word.lower() for word in re.findall(r'\b\w+\b', text)]

        if not words:
            return 0

        # Simple complexity assessment based on word length
        complex_words = [word for word in words if len(word) > 6]
        complexity_score = len(complex_words) / len(words)
        return complexity_score

    def _analyze_social_patterns(self, text: str) -> dict:
        """Analyze social interaction patterns"""
        social_indicators = {
            'community_references': len(re.findall(r'\b(we|us|our|community|team|group)\b', text.lower())),
            'individual_focus': len(re.findall(r'\b(I|me|my|myself)\b', text.lower())),
            'other_focus': len(re.findall(r'\b(you|your|they|them|others)\b', text.lower())),
            'collaborative_language': len(re.findall(r'\b(together|collaborate|share|help|support)\b', text.lower()))
        }

        total_indicators = sum(social_indicators.values())

        if total_indicators == 0:
            social_orientation = 'unknown'
        elif social_indicators['community_references'] + social_indicators['collaborative_language'] > \
                social_indicators['individual_focus']:
            social_orientation = 'community_oriented'
        elif social_indicators['individual_focus'] > social_indicators['other_focus'] + social_indicators[
            'community_references']:
            social_orientation = 'individual_focused'
        else:
            social_orientation = 'balanced'

        return {
            'orientation': social_orientation,
            'indicators': social_indicators,
            'method': 'pronoun_keyword_analysis'
        }

    def _calculate_confidence_scores(self, analysis_results: dict) -> dict:
        """Calculate confidence scores for different analysis components"""
        confidence_scores = {}

        for analysis_type, results in analysis_results.items():
            if analysis_type == 'confidence_scores':
                continue

            if isinstance(results, dict) and 'confidence' in results:
                confidence_scores[analysis_type] = results['confidence']
            elif isinstance(results, dict) and 'method' in results:
                # Assign confidence based on method used
                if results['method'] in ['transformer_model', 'zero_shot_classification']:
                    confidence_scores[analysis_type] = 0.85
                elif results['method'] in ['textblob_keywords', 'keyword_matching']:
                    confidence_scores[analysis_type] = 0.65
                else:
                    confidence_scores[analysis_type] = 0.50
            else:
                confidence_scores[analysis_type] = 0.60

        # Calculate overall confidence
        if confidence_scores:
            overall_confidence = sum(confidence_scores.values()) / len(confidence_scores)
            confidence_scores['overall'] = overall_confidence
        else:
            confidence_scores['overall'] = 0.50

        return confidence_scores

    def _empty_analysis_result(self) -> dict:
        """Return empty analysis result when no data is available"""
        return {
            'sentiment_analysis': {'overall_sentiment': 'neutral', 'confidence': 0.5},
            'emotion_analysis': {'primary_emotion': 'neutral', 'confidence': 0.5},
            'interest_inference': {'interests': [], 'method': 'no_data'},
            'personality_traits': {'traits': {}, 'method': 'no_data'},
            'behavioral_patterns': {'patterns': [], 'method': 'insufficient_data'},
            'economic_indicators': {'indicators': {}, 'method': 'no_data'},
            'schedule_patterns': {'patterns': {}, 'method': 'no_data'},
            'communication_style': {'style': 'unknown', 'method': 'no_data'},
            'social_patterns': {'orientation': 'unknown', 'method': 'no_data'},
            'confidence_scores': {'overall': 0.2}
        }

    def warmup_models(self):
        """
        Optional method to pre-load all models
        Call this if you want to load all models at once
        """
        logger.info("Warming up all ML models...")
        _ = self.sentiment_analyzer
        _ = self.interest_classifier
        _ = self.emotion_analyzer
        logger.info("All ML models warmed up")


def create_ml_inference_pipeline():
    """Factory function to create ML inference pipeline"""
    return MLInferencePipeline()

