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

class DigitalFootprintAnalyzer:
    def __init__(self):
        self.interest_keywords = {
            'technology': ['tech', 'programming', 'coding', 'software', 'AI', 'machine learning'],
            'fitness': ['gym', 'workout', 'fitness', 'health', 'exercise', 'running'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure', 'wanderlust'],
            'food': ['food', 'cooking', 'recipe', 'restaurant', 'cuisine', 'chef'],
            'music': ['music', 'concert', 'band', 'song', 'album', 'playlist'],
            'sports': ['sports', 'game', 'team', 'match', 'championship', 'athlete']
        }
    
    def analyze_public_profiles(self, name, email, social_links):
        """Main analysis function"""
        results = {
            'privacy_score': 7.5,  # Default score, will be calculated
            'interests': [],
            'schedule_patterns': {},
            'economic_indicators': {},
            'mental_state': {},
            'data_sources': [],
            'recommendations': []
        }
        
        # Analyze each social media link
        for link in social_links:
            try:
                profile_data = self._analyze_social_profile(link)
                if profile_data:
                    results = self._merge_analysis_results(results, profile_data)
            except Exception as e:
                print(f"Error analyzing {link}: {str(e)}")
                continue
        
        # Calculate overall privacy score
        results['privacy_score'] = self._calculate_privacy_score(results)
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_social_profile(self, url):
        """Analyze a single social media profile"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            # For demo purposes, we'll simulate analysis
            # In production, this would use official APIs where possible
            
            domain = urlparse(url).netloc.lower()
            
            if 'linkedin.com' in domain:
                return self._analyze_linkedin_profile(url, headers)
            elif 'twitter.com' in domain or 'x.com' in domain:
                return self._analyze_twitter_profile(url, headers)
            elif 'github.com' in domain:
                return self._analyze_github_profile(url, headers)
            else:
                return self._analyze_generic_profile(url, headers)
                
        except Exception as e:
            print(f"Profile analysis error: {str(e)}")
            return None
    
    def _analyze_linkedin_profile(self, url, headers):
        """Analyze LinkedIn profile (public info only)"""
        # Simulate LinkedIn analysis
        return {
            'interests': ['technology', 'professional development'],
            'economic_indicators': {
                'employment_status': 'employed',
                'industry': 'technology',
                'experience_level': 'mid-level'
            },
            'schedule_patterns': {
                'active_hours': 'business hours',
                'posting_frequency': 'weekly'
            },
            'data_source': 'LinkedIn Profile'
        }
    
    def _analyze_twitter_profile(self, url, headers):
        """Analyze Twitter/X profile"""
        # Simulate Twitter analysis
        return {
            'interests': ['current events', 'technology'],
            'mental_state': {
                'sentiment': 'neutral',
                'engagement_level': 'moderate'
            },
            'schedule_patterns': {
                'active_hours': 'evenings',
                'posting_frequency': 'daily'
            },
            'data_source': 'Twitter/X Profile'
        }
    
    def _analyze_github_profile(self, url, headers):
        """Analyze GitHub profile"""
        # Simulate GitHub analysis
        return {
            'interests': ['programming', 'open source', 'technology'],
            'schedule_patterns': {
                'active_hours': 'late night',
                'activity_level': 'high',
                'consistency': 'regular'
            },
            'economic_indicators': {
                'skill_level': 'advanced',
                'project_complexity': 'high'
            },
            'data_source': 'GitHub Profile'
        }
    
    def _analyze_generic_profile(self, url, headers):
        """Analyze generic social media profile"""
        # Basic web scraping for public information
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text().lower()
                
                # Extract interests based on keywords
                detected_interests = []
                for category, keywords in self.interest_keywords.items():
                    if any(keyword in text_content for keyword in keywords):
                        detected_interests.append(category)
                
                return {
                    'interests': detected_interests,
                    'data_source': f'Public Profile: {urlparse(url).netloc}'
                }
        except:
            pass
        
        return None
    
    def _merge_analysis_results(self, main_results, profile_data):
        """Merge results from multiple profiles"""
        if not profile_data:
            return main_results
        
        # Merge interests
        if 'interests' in profile_data:
            main_results['interests'].extend(profile_data['interests'])
            main_results['interests'] = list(set(main_results['interests']))  # Remove duplicates
        
        # Merge other data
        for key in ['schedule_patterns', 'economic_indicators', 'mental_state']:
            if key in profile_data:
                main_results[key].update(profile_data[key])
        
        # Add data source
        if 'data_source' in profile_data:
            main_results['data_sources'].append(profile_data['data_source'])
        
        return main_results
    
    def _calculate_privacy_score(self, results):
        """Calculate privacy risk score (1-10, higher = more private)"""
        score = 10.0  # Start with maximum privacy
        
        # Reduce score based on data exposure
        if len(results['interests']) > 3:
            score -= 1.0  # Many interests revealed
        
        if results['schedule_patterns']:
            score -= 1.5  # Schedule patterns detectable
        
        if results['economic_indicators']:
            score -= 2.0  # Economic status inferable
        
        if len(results['data_sources']) > 2:
            score -= 1.5  # Multiple data sources
        
        return max(1.0, score)  # Minimum score of 1
    
    def _generate_recommendations(self, results):
        """Generate privacy improvement recommendations"""
        recommendations = []
        
        if results['privacy_score'] < 5:
            recommendations.append("Your privacy score is low. Consider reviewing your social media privacy settings.")
        
        if len(results['interests']) > 5:
            recommendations.append("Many interests are publicly visible. Consider limiting personal details in profiles.")
        
        if results['schedule_patterns']:
            recommendations.append("Your activity patterns are detectable. Vary your posting times for better privacy.")
        
        if len(results['data_sources']) > 3:
            recommendations.append("Information from multiple platforms can be correlated. Review all your public profiles.")
        
        # Always include general recommendations
        recommendations.extend([
            "Regularly review and update your privacy settings on all platforms.",
            "Be mindful of the information you share publicly.",
            "Consider using privacy-focused alternatives to mainstream social media."
        ])
        
        return recommendations

def perform_analysis(name, email, social_links):
    """Entry point for analysis"""
    analyzer = DigitalFootprintAnalyzer()
    return analyzer.analyze_public_profiles(name, email, social_links)
