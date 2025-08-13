import re
import logging
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SocialMediaURLValidator:
    """Comprehensive social media URL validation"""

    def __init__(self):
        # Updated patterns for modern social media URLs
        self.platform_patterns = {
            'linkedin': [
                r'^https?://(www\.)?linkedin\.com/(in|pub)/[\w\-%.]+/?.*$',
                r'^https?://(www\.)?linkedin\.com/profile/view\?id=[\w\-%.]+.*$'
            ],
            'instagram': [
                r'^https?://(www\.)?instagram\.com/[\w\-.]+/?.*$',
                r'^https?://(www\.)?instagram\.com/p/[\w\-]+/?.*$',
                r'^https?://(www\.)?instagram\.com/reel/[\w\-]+/?.*$'
            ],
            'twitter': [
                r'^https?://(www\.)?(twitter\.com|x\.com)/[\w\-]+/?.*$',
                r'^https?://(www\.)?(twitter\.com|x\.com)/intent/user\?screen_name=[\w\-]+.*$'
            ],
            'facebook': [
                r'^https?://(www\.)?facebook\.com/[\w\-.]+/?.*$',
                r'^https?://(www\.)?facebook\.com/people/[\w\-%.]+/\d+/?.*$',
                r'^https?://(www\.)?facebook\.com/profile\.php\?id=\d+.*$'
            ],
            'github': [
                r'^https?://(www\.)?github\.com/[\w\-]+/?.*$'
            ],
            'youtube': [
                r'^https?://(www\.)?youtube\.com/(c/|channel/|user/|@)[\w\-]+/?.*$',
                r'^https?://(www\.)?youtube\.com/c/[\w\-]+/?.*$'
            ],
            'tiktok': [
                r'^https?://(www\.)?tiktok\.com/@[\w\-.]+/?.*$'
            ],
            'reddit': [
                r'^https?://(www\.)?reddit\.com/(u|user)/[\w\-]+/?.*$'
            ],
            'pinterest': [
                r'^https?://(www\.)?pinterest\.com/[\w\-]+/?.*$'
            ],
            'snapchat': [
                r'^https?://(www\.)?snapchat\.com/add/[\w\-]+/?.*$'
            ]
        }

        # Generic social media domains
        self.social_domains = {
            'linkedin.com', 'instagram.com', 'twitter.com', 'x.com',
            'facebook.com', 'github.com', 'youtube.com', 'tiktok.com',
            'reddit.com', 'pinterest.com', 'snapchat.com', 'discord.com',
            'medium.com', 'behance.net', 'dribbble.com', 'vimeo.com'
        }

    def validate_social_url(self, url: str) -> Dict[str, any]:
        """
        Validate social media URL and return detailed analysis
        """
        if not url or not isinstance(url, str):
            return {
                'is_valid': False,
                'error': 'URL is required and must be a string',
                'platform': None,
                'username': None
            }

        # Clean and normalize URL
        clean_url = self._clean_url(url)

        # Basic URL format validation
        if not self._is_valid_url_format(clean_url):
            return {
                'is_valid': False,
                'error': 'Invalid URL format. Please enter a valid URL starting with http:// or https://',
                'platform': None,
                'username': None
            }

        # Check if it's a social media domain
        domain = self._extract_domain(clean_url)
        if not self._is_social_media_domain(domain):
            return {
                'is_valid': False,
                'error': f'URL must be from a supported social media platform. Domain "{domain}" is not supported.',
                'platform': None,
                'username': None,
                'supported_platforms': list(self.platform_patterns.keys())
            }

        # Validate against platform patterns
        platform, is_valid = self._validate_platform_pattern(clean_url)

        if not is_valid:
            return {
                'is_valid': False,
                'error': f'Invalid URL format for {platform or "social media"} platform. Please check the URL structure.',
                'platform': platform,
                'username': None,
                'example_formats': self._get_example_formats(platform) if platform else []
            }

        # Extract username if possible
        username = self._extract_username(clean_url, platform)

        return {
            'is_valid': True,
            'platform': platform,
            'username': username,
            'cleaned_url': clean_url,
            'domain': domain
        }

    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL"""
        url = url.strip()

        # Add https if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Remove common tracking parameters
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid']
        parsed = urlparse(url)

        if parsed.query:
            query_params = parsed.query.split('&')
            clean_params = [param for param in query_params
                            if not any(param.startswith(f'{track}=') for track in tracking_params)]

            if clean_params:
                clean_query = '&'.join(clean_params)
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{clean_query}"
            else:
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        return url

    def _is_valid_url_format(self, url: str) -> bool:
        """Check if URL has valid format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''

    def _is_social_media_domain(self, domain: str) -> bool:
        """Check if domain is a social media platform"""
        return domain in self.social_domains

    def _validate_platform_pattern(self, url: str) -> Tuple[Optional[str], bool]:
        """Validate URL against platform-specific patterns"""
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return platform, True

        # Check if it's a recognized social domain but doesn't match patterns
        domain = self._extract_domain(url)
        if self._is_social_media_domain(domain):
            # Try to infer platform from domain
            platform = self._infer_platform_from_domain(domain)
            return platform, True  # Accept if it's a known social domain

        return None, False

    def _infer_platform_from_domain(self, domain: str) -> str:
        """Infer platform name from domain"""
        domain_to_platform = {
            'linkedin.com': 'linkedin',
            'instagram.com': 'instagram',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'facebook.com': 'facebook',
            'github.com': 'github',
            'youtube.com': 'youtube',
            'tiktok.com': 'tiktok',
            'reddit.com': 'reddit',
            'pinterest.com': 'pinterest',
            'snapchat.com': 'snapchat'
        }
        return domain_to_platform.get(domain, 'unknown')

    def _extract_username(self, url: str, platform: str) -> Optional[str]:
        """Extract username from social media URL"""
        try:
            parsed = urlparse(url)
            path_parts = [part for part in parsed.path.split('/') if part]

            if not path_parts:
                return None

            if platform == 'linkedin':
                # LinkedIn: /in/username or /pub/username
                if len(path_parts) >= 2 and path_parts[0] in ['in', 'pub']:
                    return path_parts[1]

            elif platform in ['instagram', 'github', 'pinterest']:
                # Direct username: /username
                if len(path_parts) >= 1:
                    return path_parts[0]

            elif platform in ['twitter']:
                # Twitter/X: /username
                if len(path_parts) >= 1:
                    return path_parts[0]

            elif platform == 'tiktok':
                # TikTok: /@username
                if len(path_parts) >= 1 and path_parts[0].startswith('@'):
                    return path_parts[0][1:]  # Remove @

            elif platform == 'youtube':
                # YouTube: /c/username, /channel/id, /user/username, /@username
                if len(path_parts) >= 2:
                    if path_parts[0] in ['c', 'user']:
                        return path_parts[1]
                    elif path_parts[0].startswith('@'):
                        return path_parts[0][1:]
                elif len(path_parts) >= 1 and path_parts[0].startswith('@'):
                    return path_parts[0][1:]

            elif platform == 'reddit':
                # Reddit: /u/username or /user/username
                if len(path_parts) >= 2 and path_parts[0] in ['u', 'user']:
                    return path_parts[1]

            # Generic fallback
            if len(path_parts) >= 1:
                return path_parts[0]

            return None
        except:
            return None

    def _get_example_formats(self, platform: str) -> List[str]:
        """Get example URL formats for a platform"""
        examples = {
            'linkedin': [
                'https://linkedin.com/in/username',
                'https://www.linkedin.com/in/username'
            ],
            'instagram': [
                'https://instagram.com/username',
                'https://www.instagram.com/username'
            ],
            'twitter': [
                'https://twitter.com/username',
                'https://x.com/username'
            ],
            'facebook': [
                'https://facebook.com/username',
                'https://www.facebook.com/username'
            ],
            'github': [
                'https://github.com/username'
            ],
            'youtube': [
                'https://youtube.com/@username',
                'https://www.youtube.com/c/username'
            ],
            'tiktok': [
                'https://tiktok.com/@username'
            ]
        }
        return examples.get(platform, [])


def create_url_validator():
    """Factory function to create URL validator"""
    return SocialMediaURLValidator()
