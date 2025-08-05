import requests
import logging
import re
import time
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class SocialProfile:
    platform: str
    url: str
    username: str
    confidence_score: float
    discovery_method: str
    profile_data: Dict
    verification_status: str

class SocialMediaDiscovery:
    """Advanced social media profile discovery engine"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Platform URL patterns for discovery
        self.platform_patterns = {
            'twitter': [
                'https://twitter.com/{username}',
                'https://x.com/{username}'
            ],
            'linkedin': [
                'https://linkedin.com/in/{username}',
                'https://www.linkedin.com/in/{username}'
            ],
            'github': [
                'https://github.com/{username}'
            ],
            'instagram': [
                'https://instagram.com/{username}',
                'https://www.instagram.com/{username}'
            ],
            'facebook': [
                'https://facebook.com/{username}',
                'https://www.facebook.com/{username}'
            ],
            'youtube': [
                'https://youtube.com/@{username}',
                'https://www.youtube.com/c/{username}',
                'https://www.youtube.com/user/{username}'
            ],
            'reddit': [
                'https://reddit.com/user/{username}',
                'https://www.reddit.com/u/{username}'
            ],
            'tiktok': [
                'https://tiktok.com/@{username}',
                'https://www.tiktok.com/@{username}'
            ],
            'pinterest': [
                'https://pinterest.com/{username}',
                'https://www.pinterest.com/{username}'
            ],
            'medium': [
                'https://medium.com/@{username}',
                'https://{username}.medium.com'
            ]
        }
        
        # Common username variations
        self.username_transformations = [
            lambda x: x,  # Original
            lambda x: x.lower(),
            lambda x: x.replace(' ', ''),
            lambda x: x.replace(' ', '_'),
            lambda x: x.replace(' ', '-'),
            lambda x: x.replace(' ', '.'),
            lambda x: ''.join([part[0] for part in x.split()]),  # Initials
            lambda x: x.split()[0],  # First name only
        ]
        
        self.rate_limit_delay = 0.5  # Seconds between requests
    
    def discover_profiles(self, name_variants: List[str], email: str) -> List[SocialProfile]:
        """
        Discover social media profiles using name variants and email
        """
        
        discovered_profiles = []
        usernames_to_try = self._generate_username_candidates(name_variants, email)
        
        logger.info(f"Generated {len(usernames_to_try)} username candidates for discovery")
        
        # Try each username on each platform
        for username in usernames_to_try:
            for platform, url_patterns in self.platform_patterns.items():
                for url_pattern in url_patterns:
                    try:
                        profile = self._check_profile_exists(
                            platform, url_pattern, username, name_variants
                        )
                        
                        if profile:
                            discovered_profiles.append(profile)
                            logger.info(f"Discovered {platform} profile: {profile.url}")
                        
                        time.sleep(self.rate_limit_delay)
                        
                    except Exception as e:
                        logger.warning(f"Error checking {platform} for {username}: {str(e)}")
                        continue
        
        # Remove duplicates and sort by confidence
        unique_profiles = self._deduplicate_profiles(discovered_profiles)
        unique_profiles.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return unique_profiles
    
    def _generate_username_candidates(self, name_variants: List[str], email: str) -> Set[str]:
        """Generate potential usernames from name variants and email"""
        
        candidates = set()
        
        # Add email username part
        if '@' in email:
            email_username = email.split('@')[0]
            candidates.add(email_username)
        
        # Generate variations from name variants
        for name_variant in name_variants:
            for transform in self.username_transformations:
                try:
                    transformed = transform(name_variant)
                    if transformed and len(transformed) >= 2:
                        candidates.add(transformed)
                        
                        # Add common number suffixes
                        for i in range(10):
                            candidates.add(f"{transformed}{i}")
                        
                        # Add year suffixes (common birth years)
                        for year in range(1980, 2005):
                            candidates.add(f"{transformed}{year}")
                            
                except Exception:
                    continue
        
        # Filter out too short or invalid usernames
        valid_candidates = {
            candidate for candidate in candidates 
            if len(candidate) >= 2 and len(candidate) <= 30 and
            re.match(r'^[a-zA-Z0-9._-]+$', candidate)
        }
        
        return valid_candidates
    
    def _check_profile_exists(self, platform: str, url_pattern: str, 
                            username: str, name_variants: List[str]) -> Optional[SocialProfile]:
        """Check if a profile exists on a platform"""
        
        try:
            url = url_pattern.format(username=username)
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            # Platform-specific existence checks
            exists, profile_data = self._platform_specific_check(platform, response, url)
            
            if exists:
                # Calculate confidence based on name matching and profile data
                confidence = self._calculate_profile_confidence(
                    platform, profile_data, username, name_variants
                )
                
                return SocialProfile(
                    platform=platform,
                    url=url,
                    username=username,
                    confidence_score=confidence,
                    discovery_method='automated_discovery',
                    profile_data=profile_data,
                    verification_status='unverified'
                )
            
        except Exception as e:
            logger.debug(f"Error checking {url}: {str(e)}")
        
        return None
    
    def _platform_specific_check(self, platform: str, response: requests.Response, 
                                url: str) -> Tuple[bool, Dict]:
        """Platform-specific logic to determine if profile exists"""
        
        profile_data = {'status_code': response.status_code, 'url': url}
        
        if response.status_code != 200:
            return False, profile_data
        
        content = response.text.lower()
        
        # Platform-specific indicators
        if platform == 'github':
            # GitHub specific checks
            if 'page not found' in content or '404' in content:
                return False, profile_data
            if 'repositories' in content or 'commits' in content:
                profile_data['has_activity'] = True
                return True, profile_data
        
        elif platform == 'twitter':
            # Twitter/X specific checks
            if 'this account doesn\'t exist' in content:
                return False, profile_data
            if 'suspended' in content:
                profile_data['status'] = 'suspended'
                return False, profile_data
            if 'tweets' in content or 'following' in content:
                return True, profile_data
        
        elif platform == 'linkedin':
            # LinkedIn specific checks
            if 'page not found' in content or 'member not found' in content:
                return False, profile_data
            if response.url != url:  # Redirect to login indicates private profile
                profile_data['status'] = 'private'
            return True, profile_data
        
        elif platform == 'instagram':
            # Instagram specific checks
            if 'page not found' in content or 'user not found' in content:
                return False, profile_data
            if 'posts' in content or 'followers' in content:
                return True, profile_data
        
        # Generic check for other platforms
        if any(indicator in content for indicator in ['profile', 'user', 'posts', 'followers']):
            return True, profile_data
        
        return False, profile_data
    
    def _calculate_profile_confidence(self, platform: str, profile_data: Dict, 
                                    username: str, name_variants: List[str]) -> float:
        """Calculate confidence score for discovered profile"""
        
        confidence = 50.0  # Base confidence
        
        # Platform reliability scoring
        platform_scores = {
            'github': 90,
            'linkedin': 85,
            'twitter': 75,
            'instagram': 70,
            'facebook': 65,
            'youtube': 80,
            'reddit': 60,
            'medium': 75
        }
        
        base_score = platform_scores.get(platform, 50)
        confidence = (confidence + base_score) / 2
        
        # Username matching with name variants
        username_lower = username.lower()
        max_name_match = 0.0
        
        for variant in name_variants:
            variant_lower = variant.lower()
            
            # Exact match
            if variant_lower == username_lower:
                max_name_match = 100.0
                break
            
            # Partial matches
            if variant_lower in username_lower:
                max_name_match = max(max_name_match, 80.0)
            
            # Check individual name parts
            variant_parts = variant_lower.split()
            for part in variant_parts:
                if part in username_lower and len(part) > 2:
                    max_name_match = max(max_name_match, 60.0)
        
        # Combine confidence scores
        final_confidence = (confidence * 0.6) + (max_name_match * 0.4)
        
        # Boost for profile activity indicators
        if profile_data.get('has_activity'):
            final_confidence += 10
        
        # Penalty for private/suspended profiles
        if profile_data.get('status') in ['private', 'suspended']:
            final_confidence -= 20
        
        return min(100.0, max(0.0, final_confidence))
    
    def _deduplicate_profiles(self, profiles: List[SocialProfile]) -> List[SocialProfile]:
        """Remove duplicate profiles based on URL similarity"""
        
        unique_profiles = []
        seen_urls = set()
        
        for profile in profiles:
            # Normalize URL for comparison
            normalized_url = profile.url.lower().rstrip('/')
            
            if normalized_url not in seen_urls:
                unique_profiles.append(profile)
                seen_urls.add(normalized_url)
        
        return unique_profiles

def create_social_discovery_engine():
    """Factory function to create social media discovery engine"""
    return SocialMediaDiscovery()
