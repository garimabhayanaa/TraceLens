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

class DigitalFootprintAnalyzer:
    def __init__(self):
        self.interest_keywords = {
            'technology': ['tech', 'programming', 'coding', 'software', 'AI', 'machine learning', 'developer', 'github',
                           'python', 'javascript', 'react', 'nodejs'],
            'fitness': ['gym', 'workout', 'fitness', 'health', 'exercise', 'running', 'yoga', 'crossfit', 'marathon',
                        'cycling'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure', 'wanderlust', 'backpacking', 'tourism',
                       'flight', 'hotel'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef', 'foodie', 'dining', 'culinary',
                     'baking'],
            'music': ['music', 'concert', 'band', 'song', 'album', 'playlist', 'musician', 'guitar', 'piano',
                      'singing'],
            'sports': ['sports', 'game', 'team', 'match', 'championship', 'athlete', 'football', 'basketball', 'soccer',
                       'tennis'],
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'sales', 'finance', 'investment', 'MBA',
                         'corporate'],
            'education': ['education', 'learning', 'student', 'university', 'college', 'course', 'degree', 'academic',
                          'research'],
            'art': ['art', 'design', 'creative', 'painting', 'drawing', 'photography', 'graphic', 'artist', 'gallery',
                    'exhibition']
        }

        self.economic_indicators = {
            'luxury_brands': ['apple', 'tesla', 'gucci', 'louis vuitton', 'rolex', 'bmw', 'mercedes', 'prada',
                              'chanel'],
            'budget_indicators': ['sale', 'discount', 'coupon', 'cheap', 'budget', 'affordable', 'deal', 'clearance'],
            'investment_terms': ['stock', 'crypto', 'bitcoin', 'investment', 'portfolio', 'trading', 'market',
                                 'finance']
        }

        self.schedule_patterns = {
            'morning': ['morning', 'am', 'breakfast', 'coffee', 'commute'],
            'afternoon': ['afternoon', 'lunch', 'pm', 'work'],
            'evening': ['evening', 'dinner', 'night', 'late'],
            'weekend': ['weekend', 'saturday', 'sunday', 'free time', 'relax']
        }

    def analyze_public_profiles(self, name, email, social_links):
        """Main analysis function"""
        results = {
            'privacy_score': 8.0,  # Start with high privacy score
            'interests': [],
            'schedule_patterns': {},
            'economic_indicators': {},
            'mental_state': {},
            'data_sources': [],
            'recommendations': [],
            'confidence_levels': {}
        }

        # Analyze name patterns
        name_insights = self._analyze_name_patterns(name)
        results = self._merge_results(results, name_insights)

        # Analyze email domain
        email_insights = self._analyze_email_domain(email)
        results = self._merge_results(results, email_insights)

        # Analyze each social media link
        for link in social_links:
            if link.strip():
                try:
                    profile_data = self._analyze_social_profile(link.strip())
                    if profile_data:
                        results = self._merge_results(results, profile_data)
                except Exception as e:
                    print(f"Error analyzing {link}: {str(e)}")
                    continue

        # Calculate overall privacy score
        results['privacy_score'] = self._calculate_privacy_score(results)

        # Generate confidence levels
        results['confidence_levels'] = self._calculate_confidence_levels(results)

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _analyze_name_patterns(self, name):
        """Analyze patterns in the provided name"""
        insights = {
            'data_sources': ['Name Pattern Analysis'],
            'interests': [],
            'economic_indicators': {}
        }

        # Basic name analysis (very general patterns)
        name_lower = name.lower()

        # Check for common tech-related naming patterns
        if any(tech_word in name_lower for tech_word in ['dev', 'code', 'tech', 'data']):
            insights['interests'].append('technology')

        return insights

    def _analyze_email_domain(self, email):
        """Analyze the email domain for insights"""
        insights = {
            'data_sources': ['Email Domain Analysis'],
            'economic_indicators': {},
            'interests': []
        }

        domain = email.split('@')[1].lower() if '@' in email else ''

        # Analyze domain patterns
        if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
            insights['economic_indicators']['email_service'] = 'free provider'
        elif domain in ['protonmail.com', 'tutanota.com']:
            insights['interests'].append('privacy/security')
            insights['economic_indicators']['privacy_conscious'] = 'high'
        else:
            # Could be corporate email
            insights['economic_indicators']['email_service'] = 'corporate/custom domain'

        return insights

    def _analyze_social_profile(self, url):
        """Analyze a single social media profile"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            domain = urlparse(url).netloc.lower()

            if 'linkedin.com' in domain:
                return self._analyze_linkedin_profile(url, headers)
            elif 'twitter.com' in domain or 'x.com' in domain:
                return self._analyze_twitter_profile(url, headers)
            elif 'github.com' in domain:
                return self._analyze_github_profile(url, headers)
            elif 'instagram.com' in domain:
                return self._analyze_instagram_profile(url, headers)
            else:
                return self._analyze_generic_profile(url, headers)

        except Exception as e:
            print(f"Profile analysis error for {url}: {str(e)}")
            return None

    def _analyze_linkedin_profile(self, url, headers):
        """Simulate LinkedIn profile analysis"""
        # In a real implementation, this would use LinkedIn's API or carefully scrape public info
        return {
            'interests': ['professional development', 'business', 'networking'],
            'economic_indicators': {
                'employment_status': 'likely employed',
                'industry': 'business/professional',
                'experience_level': 'mid to senior level',
                'professional_network': 'active'
            },
            'schedule_patterns': {
                'active_hours': 'business hours',
                'posting_frequency': 'weekly',
                'platform_usage': 'professional focused'
            },
            'mental_state': {
                'communication_style': 'professional',
                'networking_activity': 'active'
            },
            'data_source': 'LinkedIn Profile Analysis'
        }

    def _analyze_twitter_profile(self, url, headers):
        """Simulate Twitter/X profile analysis"""
        return {
            'interests': ['current events', 'social media', 'news'],
            'mental_state': {
                'sentiment': 'mixed (typical social media)',
                'engagement_level': 'moderate to high',
                'communication_style': 'informal'
            },
            'schedule_patterns': {
                'active_hours': 'evenings and weekends',
                'posting_frequency': 'daily to weekly',
                'platform_usage': 'social commentary'
            },
            'economic_indicators': {
                'social_media_engagement': 'active',
                'brand_interactions': 'consumer level'
            },
            'data_source': 'Twitter/X Profile Analysis'
        }

    def _analyze_github_profile(self, url, headers):
        """Simulate GitHub profile analysis"""
        return {
            'interests': ['programming', 'open source', 'technology', 'software development'],
            'schedule_patterns': {
                'active_hours': 'flexible (developer schedule)',
                'activity_level': 'high',
                'consistency': 'regular commits',
                'work_pattern': 'project-based'
            },
            'economic_indicators': {
                'skill_level': 'intermediate to advanced',
                'project_complexity': 'varies',
                'employment_indicator': 'tech industry likely',
                'open_source_contribution': 'active'
            },
            'mental_state': {
                'problem_solving': 'systematic',
                'learning_approach': 'hands-on',
                'collaboration': 'open source community'
            },
            'data_source': 'GitHub Profile Analysis'
        }

    def _analyze_instagram_profile(self, url, headers):
        """Simulate Instagram profile analysis"""
        return {
            'interests': ['photography', 'lifestyle', 'social sharing'],
            'schedule_patterns': {
                'active_hours': 'evenings and weekends',
                'posting_frequency': 'several times per week',
                'content_type': 'visual/lifestyle'
            },
            'economic_indicators': {
                'lifestyle_level': 'social media active',
                'brand_engagement': 'consumer',
                'visual_content_creation': 'regular'
            },
            'mental_state': {
                'social_engagement': 'high',
                'self_expression': 'visual',
                'community_connection': 'social network focused'
            },
            'data_source': 'Instagram Profile Analysis'
        }

    def _analyze_generic_profile(self, url, headers):
        """Analyze generic social media profile or website"""
        try:
            # Basic web scraping for demonstration (be respectful of robots.txt in production)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text().lower()

                # Extract interests based on keywords
                detected_interests = []
                for category, keywords in self.interest_keywords.items():
                    matches = sum(1 for keyword in keywords if keyword in text_content)
                    if matches >= 2:  # Require at least 2 keyword matches
                        detected_interests.append(category)

                return {
                    'interests': detected_interests,
                    'data_source': f'Public Profile: {urlparse(url).netloc}',
                    'economic_indicators': {
                        'web_presence': 'active',
                        'platform_diversity': 'multi-platform user'
                    }
                }
        except Exception as e:
            print(f"Generic profile analysis failed: {str(e)}")

        return {
            'data_source': f'Profile Link: {urlparse(url).netloc}',
            'economic_indicators': {
                'web_presence': 'confirmed',
                'platform_usage': 'social media active'
            }
        }

    def _merge_results(self, main_results, new_data):
        """Merge results from multiple analysis sources"""
        if not new_data:
            return main_results

        # Merge interests
        if 'interests' in new_data:
            main_results['interests'].extend(new_data['interests'])
            main_results['interests'] = list(set(main_results['interests']))  # Remove duplicates

        # Merge other data categories
        for key in ['schedule_patterns', 'economic_indicators', 'mental_state']:
            if key in new_data:
                main_results[key].update(new_data[key])

        # Add data source
        if 'data_source' in new_data:
            main_results['data_sources'].append(new_data['data_source'])

        return main_results

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

        # Overall confidence
        confidence['overall'] = sum(confidence.values()) / len(confidence) if confidence else 20

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

        # General recommendations (always include)
        general_recommendations = [
            "🔒 Regularly review and update privacy settings on all your social media platforms",
            "👤 Use different profile pictures and usernames across platforms to prevent easy correlation",
            "📱 Be mindful of the information you share publicly - even seemingly innocent details can reveal patterns",
            "🛡️ Consider using privacy-focused alternatives for email and social media",
            "📋 Regularly audit your online presence by searching for your name and email address",
            "⚡ Enable two-factor authentication on all your accounts for added security"
        ]

        recommendations.extend(general_recommendations)

        return recommendations


def perform_analysis(name, email, social_links):
    """Entry point for analysis - called from Flask app"""
    analyzer = DigitalFootprintAnalyzer()
    return analyzer.analyze_public_profiles(name, email, social_links)

