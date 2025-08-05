import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import numpy as np
from textblob import TextBlob
import json
from urllib.parse import urlparse
import time
from collections import Counter
from .data_collector import DataCollectionEngine
from .ml_inference import MLInferencePipeline

class DigitalFootprintAnalyzer:
    def __init__(self):
        self.data_collector = DataCollectionEngine()
        self.ml_pipeline = MLInferencePipeline()
        self.interest_keywords = {
            'technology': ['tech', 'programming', 'coding', 'software', 'AI', 'machine learning', 'developer', 'github',
                          'python', 'javascript', 'react', 'nodejs', 'api', 'database', 'cloud', 'cybersecurity'],
            'fitness': ['gym', 'workout', 'fitness', 'health', 'exercise', 'running', 'yoga', 'crossfit', 'marathon',
                       'cycling', 'wellness', 'nutrition', 'training', 'cardio'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure', 'wanderlust', 'backpacking', 'tourism',
                      'flight', 'hotel', 'destination', 'journey', 'abroad', 'visa'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef', 'foodie', 'dining', 'culinary',
                    'baking', 'ingredients', 'meal', 'taste', 'flavor'],
            'music': ['music', 'concert', 'band', 'song', 'album', 'playlist', 'musician', 'guitar', 'piano',
                     'singing', 'instrument', 'melody', 'rhythm', 'artist'],
            'sports': ['sports', 'game', 'team', 'match', 'championship', 'athlete', 'football', 'basketball', 'soccer',
                      'tennis', 'baseball', 'hockey', 'olympics', 'competition'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'sales', 'finance', 'investment', 'MBA',
                        'corporate', 'strategy', 'leadership', 'management', 'revenue'],
            'education': ['education', 'learning', 'student', 'university', 'college', 'course', 'degree', 'academic',
                         'research', 'study', 'knowledge', 'teaching', 'scholarship'],
            'art': ['art', 'design', 'creative', 'painting', 'drawing', 'photography', 'graphic', 'artist', 'gallery',
                   'exhibition', 'visual', 'aesthetic', 'illustration', 'sculpture']
        }
        
        self.economic_indicators = {
            'luxury_brands': ['apple', 'tesla', 'gucci', 'louis vuitton', 'rolex', 'bmw', 'mercedes', 'prada',
                             'chanel', 'versace', 'cartier', 'hermes', 'lamborghini', 'ferrari'],
            'budget_indicators': ['sale', 'discount', 'coupon', 'cheap', 'budget', 'affordable', 'deal', 'clearance',
                                 'thrift', 'secondhand', 'bargain', 'markdown'],
            'investment_terms': ['stock', 'crypto', 'bitcoin', 'investment', 'portfolio', 'trading', 'market',
                                'finance', 'dividend', 'bond', 'asset', 'equity', 'roi']
        }
        
        self.schedule_patterns = {
            'morning': ['morning', 'am', 'breakfast', 'coffee', 'commute', 'sunrise', 'early'],
            'afternoon': ['afternoon', 'lunch', 'pm', 'work', 'meeting', 'office'],
            'evening': ['evening', 'dinner', 'night', 'late', 'sunset', 'after work'],
            'weekend': ['weekend', 'saturday', 'sunday', 'free time', 'relax', 'leisure']
        }

    def analyze_public_profiles(self, name, email, social_links):
        """Main analysis function using ML Inference Pipeline"""
        
        # Collect raw data
        collected_data = self.data_collector.collect_public_data(name, email, social_links)
        collection_summary = self.data_collector.get_collection_summary(collected_data)
        
        # Prepare text data for ML analysis
        text_data = []
        text_data.append(f"{name} {email}")  # Basic info
        
        for profile in collected_data['social_profiles']:
            if 'page_title' in profile:
                text_data.append(profile['page_title'])
            if 'description' in profile:
                text_data.append(profile['description'])
        
        # Run ML inference pipeline
        ml_results = self.ml_pipeline.analyze_text_patterns(text_data)
        
        results = {
            'privacy_score': 8.0,  # Start with high privacy score
            'interests': [],
            'schedule_patterns': {},
            'economic_indicators': {},
            'mental_state': {},
            'data_sources': [],
            'recommendations': [],
            'confidence_levels': {},
            'collection_summary': collection_summary,
            'ml_analysis': ml_results  # Include raw ML results
        }
        
        # Process ML results into standard format
        self._process_ml_results(results, ml_results)
        
        # Process name analysis
        name_data = collected_data['name_analysis']
        if name_data['professional_indicators']:
            results['interests'].extend(['professional development', 'business'])
            results['data_sources'].append('Name Pattern Analysis')
        if name_data['potential_patterns']:
            results['interests'].extend(['technology'])
        
        # Process email analysis
        email_data = collected_data['email_analysis']
        results['data_sources'].append('Email Domain Analysis')
        
        if email_data['domain_type'] == 'privacy_focused':
            results['privacy_score'] += 0.5
            results['interests'].append('privacy/security')
            results['economic_indicators']['privacy_conscious'] = 'high'
        elif email_data['domain_type'] == 'corporate':
            results['economic_indicators']['employment_status'] = 'likely employed'
            results['economic_indicators']['email_service'] = 'corporate/custom domain'
        elif email_data['domain_type'] == 'educational':
            results['interests'].append('education')
            results['economic_indicators']['academic_affiliation'] = 'confirmed'
        else:
            results['economic_indicators']['email_service'] = 'free provider'
        
        # Process social profile data
        for profile in collected_data['social_profiles']:
            results['data_sources'].append(f"{profile['platform'].title()} Profile Analysis")
            
            # Apply privacy score impact
            results['privacy_score'] += profile.get('privacy_score_impact', 0)
            
            # Extract platform-specific insights
            if profile['platform'] == 'linkedin':
                results['interests'].extend(['professional development', 'business', 'networking'])
                results['economic_indicators'].update({
                    'employment_status': 'likely employed',
                    'professional_network': 'active',
                    'industry_engagement': 'business professional'
                })
                results['schedule_patterns'].update({
                    'active_hours': 'business hours',
                    'platform_usage': 'professional focused'
                })
                results['mental_state'].update({
                    'communication_style': 'professional',
                    'networking_activity': 'active'
                })
                
            elif profile['platform'] == 'github':
                results['interests'].extend(['programming', 'technology', 'open source'])
                results['economic_indicators']['technical_skills'] = 'demonstrated'
                
                # Use actual GitHub data if available
                if 'public_repos' in profile.get('inferred_data', {}):
                    repos = profile['inferred_data']['public_repos']
                    if repos > 20:
                        results['economic_indicators']['project_experience'] = 'extensive'
                        results['schedule_patterns']['coding_activity'] = 'highly active'
                    elif repos > 5:
                        results['economic_indicators']['project_experience'] = 'moderate'
                        results['schedule_patterns']['coding_activity'] = 'regular'
                        
                    if profile['inferred_data'].get('followers', 0) > 50:
                        results['mental_state']['technical_reputation'] = 'established'
                
                results['schedule_patterns'].update({
                    'active_hours': 'flexible (developer schedule)',
                    'work_pattern': 'project-based'
                })
                results['mental_state'].update({
                    'problem_solving': 'systematic',
                    'learning_approach': 'hands-on'
                })
                
            elif profile['platform'] == 'twitter' or profile['platform'] == 'x':  # Updated for X
                results['interests'].extend(['current events', 'social media'])
                results['mental_state'].update({
                    'social_engagement': 'active',
                    'communication_style': 'informal',
                    'opinion_sharing': 'public'
                })
                results['schedule_patterns'].update({
                    'active_hours': 'evenings and weekends',
                    'platform_usage': 'social commentary'
                })
                results['economic_indicators']['social_media_engagement'] = 'active'
                
            elif profile['platform'] == 'instagram':
                results['interests'].extend(['photography', 'lifestyle', 'visual arts'])
                results['mental_state'].update({
                    'social_engagement': 'high',
                    'self_expression': 'visual',
                    'lifestyle_sharing': 'active'
                })
                results['schedule_patterns'].update({
                    'content_creation': 'regular',
                    'visual_sharing': 'active'
                })
                results['economic_indicators']['lifestyle_exposure'] = 'high'
                
            elif profile['platform'] == 'facebook':
                results['interests'].extend(['social networking', 'personal connections'])
                results['mental_state'].update({
                    'family_connections': 'active',
                    'personal_sharing': 'likely high'
                })
                results['economic_indicators']['personal_network'] = 'extensive'
        
        # Process web presence data
        for presence in collected_data['web_presence']:
            results['data_sources'].append('Web Presence Analysis')
            results['economic_indicators']['digital_footprint'] = 'expanded'
        
        # Apply additional analysis based on collected data patterns
        self._apply_pattern_analysis(results, collected_data)
        
        # Ensure privacy score stays within bounds
        results['privacy_score'] = max(1.0, min(10.0, results['privacy_score']))
        
        # Remove duplicate interests
        results['interests'] = list(set(results['interests']))
        
        # Generate confidence levels
        results['confidence_levels'] = self._calculate_confidence_levels(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _process_ml_results(self, results, ml_results):
        """Process ML inference results into standard format"""
        
        # Process sentiment and emotion analysis
        sentiment = ml_results.get('sentiment_analysis', {})
        emotion = ml_results.get('emotion_analysis', {})
        
        if sentiment:
            results['mental_state'].update({
                'sentiment': sentiment.get('overall_sentiment', 'neutral'),
                'sentiment_confidence': sentiment.get('confidence', 0.5)
            })
        
        if emotion:
            results['mental_state'].update({
                'primary_emotion': emotion.get('primary_emotion', 'neutral'),
                'emotion_confidence': emotion.get('confidence', 0.5)
            })
        
        # Process interests from ML
        interest_data = ml_results.get('interest_inference', {})
        if interest_data and 'interests' in interest_data:
            for interest in interest_data['interests']:
                if isinstance(interest, dict) and 'category' in interest:
                    results['interests'].append(interest['category'])
                elif isinstance(interest, str):
                    results['interests'].append(interest)
        
        # Process personality traits
        personality = ml_results.get('personality_traits', {}).get('traits', {})
        for trait, info in personality.items():
            if isinstance(info, dict) and info.get('score', 0) > 0.5:
                results['mental_state'][f'personality_{trait}'] = f"score: {info['score']:.2f}"
        
        # Process behavioral patterns
        behavioral = ml_results.get('behavioral_patterns', {}).get('patterns', {})
        if isinstance(behavioral, dict):
            for key, value in behavioral.items():
                if isinstance(value, dict):
                    results['schedule_patterns'][key] = str(value)
                else:
                    results['schedule_patterns'][key] = str(value)
        
        # Process economic indicators from ML
        economic = ml_results.get('economic_indicators', {}).get('indicators', {})
        for indicator, info in economic.items():
            if isinstance(info, dict) and info.get('score', 0) > 0.3:
                results['economic_indicators'][indicator] = f"confidence: {info['score']:.2f}"
        
        # Process schedule patterns from ML
        schedule = ml_results.get('schedule_patterns', {}).get('patterns', {})
        for pattern, info in schedule.items():
            if isinstance(info, dict) and info.get('score', 0) > 0.3:
                results['schedule_patterns'][pattern] = f"detected: {info['score']:.2f}"
        
        # Process communication style
        comm_style = ml_results.get('communication_style', {})
        if comm_style and 'style' in comm_style:
            results['mental_state']['communication_style'] = comm_style['style']
        
        # Process social patterns
        social = ml_results.get('social_patterns', {})
        if social and 'orientation' in social:
            results['mental_state']['social_orientation'] = social['orientation']
        
        # Update data sources
        results['data_sources'].append('ML Pattern Analysis')
    
    def _apply_pattern_analysis(self, results, collected_data):
        """Apply cross-platform pattern analysis"""
        
        # Analyze consistency across platforms
        platforms = [profile['platform'] for profile in collected_data['social_profiles']]
        
        if len(platforms) > 3:
            results['economic_indicators']['platform_diversity'] = 'high'
            results['privacy_score'] -= 0.5  # More platforms = more exposure
        
        # Analyze name consistency
        name_data = collected_data['name_analysis']
        if name_data.get('name_complexity', {}).get('has_special_chars', False):
            results['mental_state']['username_creativity'] = 'high'
        
        # Cross-reference email and social patterns
        email_data = collected_data['email_analysis']
        if email_data['domain_type'] == 'corporate' and 'linkedin' in platforms:
            results['economic_indicators']['professional_consistency'] = 'high'
            results['confidence_levels'] = results.get('confidence_levels', {})
            results['confidence_levels']['employment_status'] = 85
    
    def _calculate_privacy_score(self, results):
        """Calculate privacy risk score (1-10, higher = more private)"""
        score = 10.0  # Start with maximum privacy
        
        # Reduce score based on data exposure
        if len(results['interests']) > 5:
            score -= 1.5  # Many interests revealed
        elif len(results['interests']) > 2:
            score -= 0.5
        
        if len(results['schedule_patterns']) > 3:
            score -= 2.0  # Detailed schedule patterns detectable
        elif len(results['schedule_patterns']) > 0:
            score -= 1.0
        
        if len(results['economic_indicators']) > 3:
            score -= 2.5  # Economic status highly inferable
        elif len(results['economic_indicators']) > 0:
            score -= 1.0
        
        if len(results['data_sources']) > 3:
            score -= 1.5  # Multiple data sources increase correlation risk
        elif len(results['data_sources']) > 1:
            score -= 0.5
        
        # Bonus points for privacy-conscious behavior
        if any('privacy' in str(value).lower() for value in results['economic_indicators'].values()):
            score += 0.5
        
        return max(1.0, min(10.0, score))  # Keep score between 1-10
    
    def _calculate_confidence_levels(self, results):
        """Calculate confidence levels for different analysis categories"""
        confidence = {}
        
        # Interest detection confidence
        if len(results['interests']) > 0:
            confidence['interests'] = min(90, len(results['interests']) * 15 + len(results['data_sources']) * 10)
        else:
            confidence['interests'] = 20
        
        # Schedule pattern confidence
        if len(results['schedule_patterns']) > 0:
            confidence['schedule_patterns'] = min(85, len(results['schedule_patterns']) * 20 + 30)
        else:
            confidence['schedule_patterns'] = 15
        
        # Economic indicator confidence
        if len(results['economic_indicators']) > 0:
            confidence['economic_indicators'] = min(80, len(results['economic_indicators']) * 15 + 25)
        else:
            confidence['economic_indicators'] = 10
        
        # Mental state confidence
        if len(results['mental_state']) > 0:
            confidence['mental_state'] = min(75, len(results['mental_state']) * 18 + 20)
        else:
            confidence['mental_state'] = 10
        
        # Overall confidence based on data sources and collection success
        if 'collection_summary' in results:
            success_rate = results['collection_summary'].get('success_rate', 0)
            confidence['overall'] = min(85, (sum(confidence.values()) / len(confidence)) * (0.5 + success_rate * 0.5))
        else:
            confidence['overall'] = sum(confidence.values()) / len(confidence) if confidence else 20
        
        # Include ML confidence if available
        if 'ml_analysis' in results and 'confidence_scores' in results['ml_analysis']:
            ml_confidence = results['ml_analysis']['confidence_scores'].get('overall', 0.5)
            confidence['ml_analysis'] = int(ml_confidence * 100)
        
        return confidence
    
    def _generate_recommendations(self, results):
        """Generate privacy improvement recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if results['privacy_score'] < 4:
            recommendations.append(
                "🚨 CRITICAL: Your privacy score is very low. Immediate action required to protect your digital footprint.")
        elif results['privacy_score'] < 6:
            recommendations.append(
                "⚠️ WARNING: Your privacy score indicates significant risks. Review your online presence carefully.")
        elif results['privacy_score'] < 8:
            recommendations.append("📋 Your privacy could be improved. Consider implementing the recommendations below.")
        else:
            recommendations.append("✅ Good privacy practices detected, but there's always room for improvement.")
        
        # Interest-based recommendations
        if len(results['interests']) > 5:
            recommendations.append(
                "🎯 Many personal interests are publicly visible. Consider limiting personal details in your profiles and posts.")
        
        # Schedule pattern recommendations
        if len(results['schedule_patterns']) > 2:
            recommendations.append(
                "⏰ Your activity patterns are highly predictable. Vary your posting times and online activity for better privacy.")
        
        # Economic indicator recommendations
        if len(results['economic_indicators']) > 3:
            recommendations.append(
                "💰 Significant economic information can be inferred about you. Be cautious about sharing lifestyle and purchase information.")
        
        # Data source recommendations
        if len(results['data_sources']) > 3:
            recommendations.append(
                "🔗 Information from multiple platforms can be easily correlated. Consider using different usernames and limiting cross-platform connections.")
        
        # ML-based recommendations
        if 'ml_analysis' in results:
            ml_results = results['ml_analysis']
            
            # Sentiment-based recommendations
            sentiment = ml_results.get('sentiment_analysis', {}).get('overall_sentiment', '')
            if sentiment == 'negative':
                recommendations.append(
                    "😟 Your online content shows negative sentiment patterns. Consider reviewing your public posts for emotional tone.")
            
            # Communication style recommendations
            comm_style = ml_results.get('communication_style', {}).get('style', '')
            if comm_style == 'informal':
                recommendations.append(
                    "💬 Your communication style is very informal. Consider more professional language for work-related platforms.")
        
        # Platform-specific recommendations
        data_sources_str = ' '.join(results['data_sources']).lower()
        if 'github' in data_sources_str:
            recommendations.append(
                "👩‍💻 Your GitHub activity reveals technical skills and work patterns. Consider making some repositories private.")
        
        if 'linkedin' in data_sources_str:
            recommendations.append(
                "💼 Your LinkedIn profile shows professional information. Review visibility settings for connections and activity.")
        
        if 'twitter' in data_sources_str or 'x' in data_sources_str:
            recommendations.append(
                "🐦 Your X/Twitter activity shows opinions and interests. Consider making your account private or limiting personal tweets.")
        
        if 'instagram' in data_sources_str:
            recommendations.append(
                "📸 Your Instagram reveals lifestyle and location patterns. Disable location services and review story visibility.")
        
        # General recommendations (always include)
        general_recommendations = [
            "🔒 Regularly review and update privacy settings on all your social media platforms",
            "👤 Use different profile pictures and usernames across platforms to prevent easy correlation",
            "📱 Be mindful of the information you share publicly - even seemingly innocent details can reveal patterns",
            "🛡️ Consider using privacy-focused alternatives for email and social media",
            "📋 Regularly audit your online presence by searching for your name and email address",
            "⚡ Enable two-factor authentication on all your accounts for added security",
            "🌐 Use a VPN when browsing to mask your IP address and location",
            "🗑️ Regularly delete old posts and clean up your digital history"
        ]
        
        # Add 3-4 most relevant general recommendations
        recommendations.extend(general_recommendations[:4])
        
        return recommendations

def perform_analysis(name, email, social_links):
    """Entry point for analysis - called from Flask app"""
    analyzer = DigitalFootprintAnalyzer()
    return analyzer.analyze_public_profiles(name, email, social_links)

