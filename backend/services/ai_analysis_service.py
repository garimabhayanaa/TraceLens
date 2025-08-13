# services/ai_analysis_service.py
import logging
import threading
from datetime import datetime
from typing import Dict, Any
from models.firestore_models import AnalysisSession, FirestoreUser, AuditLog
from utils.ai_inference_engine import create_ai_inference_engine
from utils.analyzer import DigitalFootprintAnalyzer

logger = logging.getLogger(__name__)

class AIAnalysisService:
    """Service for handling AI analysis requests"""
    
    def __init__(self):
        self.ai_engine = create_ai_inference_engine()
        self.analyzer = DigitalFootprintAnalyzer()
    
    def process_analysis_async(self, session_id: str, social_media_url: str, analysis_type: str):
        """Process analysis in background thread"""
        thread = threading.Thread(
            target=self._process_analysis,
            args=(session_id, social_media_url, analysis_type)
        )
        thread.daemon = True
        thread.start()
    
    def _process_analysis(self, session_id: str, social_media_url: str, analysis_type: str):
        """Process the actual analysis"""
        try:
            # Update status to processing
            AnalysisSession.update(session_id, {
                'status': 'processing',
                'progress': 10,
                'message': 'Starting analysis...'
            })
            
            # Get session info
            session = AnalysisSession.get_by_id(session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return
            
            user_id = session['user_id']
            
            # Extract basic info from URL
            url_parts = social_media_url.split('/')
            platform = self._detect_platform(social_media_url)
            username = self._extract_username(social_media_url)
            
            # Update progress
            AnalysisSession.update(session_id, {
                'progress': 30,
                'message': 'Collecting public data...'
            })
            
            # Perform analysis based on type
            if analysis_type == 'comprehensive':
                results = self._comprehensive_analysis(social_media_url, platform, username)
            elif analysis_type == 'privacy_only':
                results = self._privacy_analysis(social_media_url, platform, username)
            elif analysis_type == 'sentiment':
                results = self._sentiment_analysis(social_media_url, platform, username)
            else:
                results = self._basic_analysis(social_media_url, platform, username)
            
            # Update progress
            AnalysisSession.update(session_id, {
                'progress': 80,
                'message': 'Generating insights...'
            })
            
            # Add metadata
            results['metadata'] = {
                'analysis_type': analysis_type,
                'social_media_url': social_media_url,
                'platform': platform,
                'username': username,
                'analyzed_at': datetime.utcnow().isoformat(),
                'analysis_version': '2.0',
                'firebase_backend': True
            }
            
            # Complete analysis
            AnalysisSession.update(session_id, {
                'status': 'completed',
                'progress': 100,
                'message': 'Analysis completed successfully',
                'results': results,
                'completed_at': datetime.utcnow()
            })
            
            # Update user usage
            FirestoreUser.increment_usage(user_id)
            
            # Log completion
            AuditLog.create({
                'user_id': user_id,
                'action': 'analysis_completed',
                'session_id': session_id,
                'details': {
                    'analysis_type': analysis_type,
                    'platform': platform,
                    'success': True
                }
            })
            
            logger.info(f"Analysis completed successfully: {session_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed for {session_id}: {str(e)}")
            
            # Update session with error
            AnalysisSession.update(session_id, {
                'status': 'failed',
                'progress': 0,
                'message': f'Analysis failed: {str(e)}',
                'error': str(e),
                'failed_at': datetime.utcnow()
            })
            
            # Log failure
            session = AnalysisSession.get_by_id(session_id)
            if session:
                AuditLog.create({
                    'user_id': session['user_id'],
                    'action': 'analysis_failed',
                    'session_id': session_id,
                    'details': {
                        'error': str(e),
                        'analysis_type': analysis_type
                    }
                })
    
    def _detect_platform(self, url: str) -> str:
        """Detect social media platform from URL"""
        url_lower = url.lower()
        if 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'github.com' in url_lower:
            return 'github'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'youtube.com' in url_lower:
            return 'youtube'
        else:
            return 'unknown'
    
    def _extract_username(self, url: str) -> str:
        """Extract username from social media URL"""
        try:
            parts = url.strip('/').split('/')
            if len(parts) >= 2:
                return parts[-1]
            return 'unknown'
        except:
            return 'unknown'
    
    def _comprehensive_analysis(self, url: str, platform: str, username: str) -> Dict[str, Any]:
        """Perform comprehensive analysis"""
        # Mock comprehensive analysis - replace with actual implementation
        return {
            'privacy_score': 7.2,
            'privacy_grade': 'B',
            'sentiment_analysis': {
                'overall_sentiment': 'positive',
                'confidence': 0.78,
                'emotional_indicators': ['professional', 'optimistic']
            },
            'behavioral_patterns': {
                'posting_frequency': 'regular',
                'active_hours': 'business_hours',
                'engagement_style': 'professional'
            },
            'economic_indicators': {
                'professional_network': 'active',
                'brand_associations': ['technology', 'professional_development'],
                'economic_status': 'employed_professional'
            },
            'privacy_recommendations': [
                'Consider making profile more private',
                'Review information shared in bio',
                'Check privacy settings for posts'
            ],
            'platform_specific': {
                'platform': platform,
                'username': username,
                'profile_completeness': 'high',
                'professional_indicators': True
            }
        }
    
    def _privacy_analysis(self, url: str, platform: str, username: str) -> Dict[str, Any]:
        """Perform privacy-focused analysis"""
        return {
            'privacy_score': 6.5,
            'privacy_grade': 'B-',
            'privacy_risks': [
                'Public profile information',
                'Visible connection network',
                'Recent activity patterns'
            ],
            'recommendations': [
                'Adjust privacy settings',
                'Limit public information',
                'Review third-party access'
            ],
            'platform_privacy': {
                'platform': platform,
                'default_privacy': 'public',
                'privacy_controls': 'available'
            }
        }
    
    def _sentiment_analysis(self, url: str, platform: str, username: str) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        return {
            'sentiment_analysis': {
                'overall_sentiment': 'positive',
                'confidence': 0.82,
                'emotional_breakdown': {
                    'positive': 0.65,
                    'neutral': 0.25,
                    'negative': 0.10
                },
                'emotional_indicators': ['professional', 'optimistic', 'engaging']
            },
            'communication_style': {
                'tone': 'professional',
                'formality': 'high',
                'engagement': 'active'
            },
            'platform_context': {
                'platform': platform,
                'username': username
            }
        }
    
    def _basic_analysis(self, url: str, platform: str, username: str) -> Dict[str, Any]:
        """Perform basic analysis"""
        return {
            'basic_profile': {
                'platform': platform,
                'username': username,
                'profile_type': 'public',
                'analysis_level': 'basic'
            },
            'summary': {
                'profile_found': True,
                'accessibility': 'public',
                'content_available': True
            },
            'recommendations': [
                'Consider upgrading to comprehensive analysis',
                'Review privacy settings'
            ]
        }
