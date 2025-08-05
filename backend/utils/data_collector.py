import requests
import time
import json
from urllib.parse import urlparse, urljoin
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import logging
from .input_processor import create_input_processor
from .social_discovery import create_social_discovery_engine
from .public_records import create_public_records_scanner
from .cross_platform_correlation import create_cross_platform_correlator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectionEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 1  # seconds between requests
        self.input_processor = create_input_processor()  # Enhanced input processing
        self.social_discovery = create_social_discovery_engine()
        self.public_records_scanner = create_public_records_scanner()
        self.cross_platform_correlator = create_cross_platform_correlator()

    def collect_public_data(self, name: str, email: str, social_links: List[str]) -> Dict[str, Any]:
        """Main entry point for comprehensive data collection with all new features"""
        
        # Enhanced input validation and processing
        input_validation = self.input_processor.process_input(name, email)
        
        # Use validated/cleaned inputs for collection
        cleaned_name = input_validation['name_validation']['cleaned_name']
        name_variants = input_validation['name_validation']['variants']
        
        collected_data = {
            'input_validation': input_validation,  # Complete input validation results
            'name_analysis': self._enhance_name_analysis(input_validation['name_validation']),
            'email_analysis': self._enhance_email_analysis(input_validation['email_analysis']),
            'social_profiles': [],
            'discovered_profiles': [],  # NEW: Auto-discovered profiles
            'web_presence': [],
            'public_records': [],  # NEW: Public records
            'cross_platform_correlation': {},  # NEW: Correlation analysis
            'metadata': {
                'collection_timestamp': time.time(),
                'sources_attempted': len(social_links),
                'sources_successful': 0,
                'input_confidence': input_validation['overall_confidence']
            }
        }

        # Collect data from provided social media profiles
        for link in social_links:
            if link.strip():
                try:
                    profile_data = self._collect_social_profile_data(link.strip())
                    if profile_data:
                        # Enhance profile data with name matching
                        profile_data['name_match_score'] = self._calculate_name_match(
                            profile_data.get('url', ''), name_variants
                        )
                        collected_data['social_profiles'].append(profile_data)
                        collected_data['metadata']['sources_successful'] += 1
                    time.sleep(self.rate_limit_delay)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error collecting data from {link}: {str(e)}")
                    continue

        # AUTO-DISCOVER additional social media profiles
        try:
            logger.info("Starting social media profile discovery...")
            discovered_profiles = self.social_discovery.discover_profiles(name_variants, email)
            
            # Convert discovered profiles to standard format
            for discovered_profile in discovered_profiles:
                profile_dict = {
                    'platform': discovered_profile.platform,
                    'url': discovered_profile.url,
                    'username': discovered_profile.username,
                    'confidence_level': discovered_profile.confidence_score / 100,
                    'discovery_method': discovered_profile.discovery_method,
                    'data_type': 'discovered_profile',
                    'verification_status': discovered_profile.verification_status,
                    'privacy_score_impact': -1.0,  # Default impact
                    'inferred_data': discovered_profile.profile_data
                }
                collected_data['discovered_profiles'].append(profile_dict)
            
            logger.info(f"Discovered {len(discovered_profiles)} additional profiles")
            
        except Exception as e:
            logger.error(f"Profile discovery failed: {str(e)}")

        # SCAN PUBLIC RECORDS (limited, ethical scope)
        try:
            logger.info("Starting public records scan...")
            public_records = self.public_records_scanner.scan_public_records(
                cleaned_name, email
            )
            
            # Convert public records to standard format
            for record in public_records:
                record_dict = {
                    'record_type': record.record_type,
                    'source': record.source,
                    'data': record.data,
                    'confidence_score': record.confidence_score,
                    'verification_status': record.verification_status,
                    'privacy_impact': record.privacy_impact
                }
                collected_data['public_records'].append(record_dict)
            
            logger.info(f"Found {len(public_records)} public records")
            
        except Exception as e:
            logger.error(f"Public records scan failed: {str(e)}")

        # Search for additional web presence using cleaned name and validated email
        web_presence = self._search_web_presence(cleaned_name, email)
        collected_data['web_presence'] = web_presence

        # CROSS-PLATFORM CORRELATION ANALYSIS
        try:
            logger.info("Starting cross-platform correlation analysis...")
            
            # Combine all profiles for correlation analysis
            all_profiles = collected_data['social_profiles'] + collected_data['discovered_profiles']
            
            if len(all_profiles) >= 2:
                correlation_analysis = self.cross_platform_correlator.correlate_profiles(
                    all_profiles, name_variants, email
                )
                collected_data['cross_platform_correlation'] = correlation_analysis
                
                logger.info(f"Correlation analysis completed: "
                           f"Score {correlation_analysis['overall_correlation_score']:.1f}, "
                           f"Risk: {correlation_analysis['privacy_risk_assessment']}")
            else:
                collected_data['cross_platform_correlation'] = {
                    'correlations': [],
                    'overall_correlation_score': 0.0,
                    'privacy_risk_assessment': 'insufficient_data',
                    'recommendations': ['Need at least 2 profiles for correlation analysis']
                }
                
        except Exception as e:
            logger.error(f"Cross-platform correlation failed: {str(e)}")
            collected_data['cross_platform_correlation'] = {
                'error': str(e),
                'correlations': [],
                'overall_correlation_score': 0.0
            }

        return collected_data

    def _enhance_name_analysis(self, name_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance name analysis with additional insights from validation"""
        
        enhanced_analysis = {
            # Original validation results
            'is_valid': name_validation['is_valid'],
            'original_name': name_validation['original_name'],
            'cleaned_name': name_validation['cleaned_name'],
            'variants': name_validation['variants'],
            'confidence_score': name_validation['confidence_score'],
            'issues': name_validation['issues'],
            'name_type': name_validation['name_type'],
            
            # Enhanced analysis
            'full_name': name_validation['cleaned_name'],
            'name_parts': name_validation['cleaned_name'].split(),
            'potential_patterns': [],
            'cultural_indicators': [],
            'professional_indicators': []
        }
        
        name_lower = name_validation['cleaned_name'].lower()
        
        # Check for professional indicators in name
        professional_terms = ['dr', 'prof', 'ceo', 'cto', 'engineer', 'developer', 'manager']
        for term in professional_terms:
            if term in name_lower:
                enhanced_analysis['professional_indicators'].append(term)

        # Check for tech-related naming patterns
        tech_indicators = ['dev', 'code', 'tech', 'data', 'ai', 'ml']
        for indicator in tech_indicators:
            if indicator in name_lower:
                enhanced_analysis['potential_patterns'].append(f'tech_related_{indicator}')

        # Name length and complexity analysis
        enhanced_analysis['name_complexity'] = {
            'total_length': len(name_validation['cleaned_name']),
            'word_count': len(enhanced_analysis['name_parts']),
            'has_special_chars': bool(re.search(r'[^a-zA-Z\s]', name_validation['cleaned_name'])),
            'capitalization_pattern': self._analyze_capitalization(name_validation['cleaned_name'])
        }

        return enhanced_analysis

    def _enhance_email_analysis(self, email_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance email analysis with additional insights from validation"""
        
        enhanced_analysis = {
            # Original validation results
            'is_valid': email_validation['is_valid'],
            'email': email_validation['email'],
            'local_part': email_validation['local_part'],
            'domain': email_validation['domain'],
            'domain_type': email_validation['domain_type'],
            'provider': email_validation['provider'],
            'mx_exists': email_validation['mx_exists'],
            'is_disposable': email_validation['is_disposable'],
            'is_academic': email_validation['is_academic'],
            'is_government': email_validation['is_government'],
            'risk_score': email_validation['risk_score'],
            'country': email_validation['country'],
            'issues': email_validation['issues'],
            
            # Enhanced analysis for backward compatibility
            'privacy_indicators': [],
            'professional_indicators': [],
            'security_features': []
        }
        
        # Map new analysis to old format for compatibility
        if email_validation['domain_type'] == 'free':
            enhanced_analysis['domain_type'] = 'free_provider'
        elif email_validation['is_disposable']:
            enhanced_analysis['privacy_indicators'].append('privacy_conscious_email')
        elif email_validation['is_academic']:
            enhanced_analysis['domain_type'] = 'educational'
            enhanced_analysis['professional_indicators'].append('academic_affiliation')
        elif email_validation['domain_type'] == 'corporate':
            enhanced_analysis['professional_indicators'].append('corporate_email')
        else:
            enhanced_analysis['professional_indicators'].append('custom_domain_owner')

        # Analyze local part patterns
        if email_validation['local_part']:
            enhanced_analysis['local_part_analysis'] = self._analyze_email_local_part(
                email_validation['local_part']
            )

        return enhanced_analysis

    def _calculate_name_match(self, url: str, name_variants: List[str]) -> float:
        """Calculate how well a URL matches the name variants"""
        
        if not url or not name_variants:
            return 0.0
        
        url_lower = url.lower()
        max_score = 0.0
        
        for variant in name_variants:
            variant_lower = variant.lower()
            
            # Exact match
            if variant_lower in url_lower:
                max_score = max(max_score, 1.0)
            
            # Partial match
            variant_parts = variant_lower.split()
            for part in variant_parts:
                if part in url_lower and len(part) > 2:
                    max_score = max(max_score, 0.7)
        
        return max_score

    def _analyze_capitalization(self, name: str) -> str:
        """Analyze capitalization patterns in name"""
        if name.isupper():
            return 'all_uppercase'
        elif name.islower():
            return 'all_lowercase'
        elif name.istitle():
            return 'title_case'
        else:
            return 'mixed_case'

    def _analyze_email_local_part(self, local_part: str) -> Dict[str, Any]:
        """Analyze the local part of email for patterns"""
        analysis = {
            'length': len(local_part),
            'has_numbers': bool(re.search(r'\d', local_part)),
            'has_special_chars': bool(re.search(r'[^a-zA-Z0-9.]', local_part)),
            'pattern_indicators': []
        }

        # Check for common patterns
        if '.' in local_part:
            analysis['pattern_indicators'].append('contains_dots')
        if re.search(r'\d{2,}', local_part):
            analysis['pattern_indicators'].append('contains_year_like_numbers')
        if any(word in local_part.lower() for word in ['admin', 'info', 'contact', 'support']):
            analysis['pattern_indicators'].append('business_related')

        return analysis

    def _collect_social_profile_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Collect data from a social media profile URL"""
        try:
            domain = urlparse(url).netloc.lower()
            
            # Route to specific platform handlers
            if 'linkedin.com' in domain:
                return self._collect_linkedin_data(url)
            elif 'twitter.com' in domain or 'x.com' in domain:
                return self._collect_twitter_data(url)
            elif 'github.com' in domain:
                return self._collect_github_data(url)
            elif 'instagram.com' in domain:
                return self._collect_instagram_data(url)
            elif 'facebook.com' in domain:
                return self._collect_facebook_data(url)
            else:
                return self._collect_generic_profile_data(url)
                
        except Exception as e:
            logger.error(f"Error collecting social profile data from {url}: {str(e)}")
            return None

    def _collect_linkedin_data(self, url: str) -> Dict[str, Any]:
        """Collect LinkedIn profile data (public information only)"""
        # Note: LinkedIn has strict anti-scraping measures
        # This is a simplified implementation for educational purposes
        data = {
            'platform': 'linkedin',
            'url': url,
            'data_type': 'professional',
            'indicators': {
                'professional_network': True,
                'career_focused': True,
                'business_connections': True
            },
            'inferred_data': {
                'employment_status': 'likely_employed',
                'professional_activity': 'active',
                'industry_engagement': 'business_professional',
                'networking_behavior': 'professional_networking'
            },
            'privacy_score_impact': -1.5,  # LinkedIn presence reduces privacy score
            'confidence_level': 0.8
        }

        # In a real implementation, you would:
        # 1. Check if profile is public
        # 2. Extract visible information like job title, company, location
        # 3. Analyze connection count if visible
        # 4. Look for public posts or activity

        return data

    def _collect_twitter_data(self, url: str) -> Dict[str, Any]:
        """Collect Twitter/X profile data"""
        data = {
            'platform': 'twitter',
            'url': url,
            'data_type': 'social_media',
            'indicators': {
                'social_media_active': True,
                'public_opinions': True,
                'real_time_updates': True
            },
            'inferred_data': {
                'communication_style': 'public_social',
                'opinion_sharing': 'active',
                'current_events_engagement': 'likely',
                'social_network_size': 'unknown'
            },
            'privacy_score_impact': -2.0,
            'confidence_level': 0.7
        }

        try:
            # Basic public information extraction (respecting robots.txt)
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                # In a real implementation, you would parse public information
                # like bio, follower count (if visible), recent public tweets
                data['accessibility'] = 'public_profile_accessible'
            else:
                data['accessibility'] = 'profile_protected_or_unavailable'
                data['privacy_score_impact'] = -0.5  # Less impact if protected
        except Exception as e:
            logger.error(f"Error accessing Twitter profile: {str(e)}")
            data['accessibility'] = 'access_error'

        return data

    def _collect_github_data(self, url: str) -> Dict[str, Any]:
        """Collect GitHub profile data"""
        data = {
            'platform': 'github',
            'url': url,
            'data_type': 'professional_technical',
            'indicators': {
                'technical_skills': True,
                'open_source_contribution': True,
                'coding_activity': True
            },
            'inferred_data': {
                'technical_expertise': 'demonstrated',
                'programming_languages': 'multiple_likely',
                'project_complexity': 'unknown',
                'collaboration_style': 'open_source'
            },
            'privacy_score_impact': -1.0,
            'confidence_level': 0.9
        }

        try:
            # GitHub API for public information (no authentication needed for public data)
            username = url.split('/')[-1]
            api_url = f'https://api.github.com/users/{username}'
            
            response = self.session.get(api_url, timeout=10)
            if response.status_code == 200:
                github_data = response.json()
                data['inferred_data'].update({
                    'public_repos': github_data.get('public_repos', 0),
                    'followers': github_data.get('followers', 0),
                    'following': github_data.get('following', 0),
                    'account_created': github_data.get('created_at', 'unknown'),
                    'bio_provided': bool(github_data.get('bio')),
                    'location_provided': bool(github_data.get('location')),
                    'company_provided': bool(github_data.get('company'))
                })

                # Adjust privacy impact based on information available
                if github_data.get('bio') or github_data.get('location'):
                    data['privacy_score_impact'] = -1.5

        except Exception as e:
            logger.error(f"Error accessing GitHub API: {str(e)}")
            data['accessibility'] = 'api_access_error'

        return data

    def _collect_instagram_data(self, url: str) -> Dict[str, Any]:
        """Collect Instagram profile data"""
        data = {
            'platform': 'instagram',
            'url': url,
            'data_type': 'lifestyle_social',
            'indicators': {
                'visual_content_sharing': True,
                'lifestyle_exposure': True,
                'social_connections': True
            },
            'inferred_data': {
                'content_type': 'visual_lifestyle',
                'sharing_frequency': 'unknown',
                'privacy_consciousness': 'unknown'
            },
            'privacy_score_impact': -1.8,
            'confidence_level': 0.6
        }

        # Instagram has strong anti-scraping measures
        # This would typically require official API access
        data['collection_method'] = 'profile_existence_check'
        return data

    def _collect_facebook_data(self, url: str) -> Dict[str, Any]:
        """Collect Facebook profile data"""
        data = {
            'platform': 'facebook',
            'url': url,
            'data_type': 'personal_social',
            'indicators': {
                'personal_network': True,
                'life_events_sharing': True,
                'family_connections': True
            },
            'inferred_data': {
                'social_network_type': 'personal_family',
                'information_sharing': 'potentially_detailed'
            },
            'privacy_score_impact': -2.5,  # Facebook typically has more personal info
            'confidence_level': 0.5
        }

        # Facebook has very strict privacy controls and anti-scraping
        data['collection_method'] = 'profile_existence_check'
        return data

    def _collect_generic_profile_data(self, url: str) -> Dict[str, Any]:
        """Collect data from generic social media or professional profiles"""
        data = {
            'platform': 'unknown',
            'url': url,
            'data_type': 'generic_web_presence',
            'indicators': {
                'web_presence': True,
                'multi_platform_user': True
            },
            'inferred_data': {
                'digital_footprint': 'expanded',
                'platform_diversity': 'multi_platform'
            },
            'privacy_score_impact': -0.8,
            'confidence_level': 0.4
        }

        try:
            domain = urlparse(url).netloc
            data['domain'] = domain

            # Attempt basic information gathering
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for common profile indicators
                title = soup.find('title')
                if title:
                    data['page_title'] = title.get_text().strip()

                # Look for meta description
                description = soup.find('meta', attrs={'name': 'description'})
                if description:
                    data['description'] = description.get('content', '')

                data['accessibility'] = 'accessible'
            else:
                data['accessibility'] = 'not_accessible'

        except Exception as e:
            logger.error(f"Error collecting generic profile data: {str(e)}")
            data['accessibility'] = 'access_error'

        return data

    def _search_web_presence(self, name: str, email: str) -> List[Dict[str, Any]]:
        """Search for additional web presence indicators"""
        web_presence = []

        # Search for common patterns that might indicate web presence
        search_terms = [
            f'"{name}"',
            f'"{email.split("@")[0]}"',  # Username part of email
        ]

        # This is a placeholder for web presence detection
        # In a real implementation, you might use:
        # 1. Search engine APIs (Google Custom Search, Bing API)
        # 2. Social media search APIs
        # 3. People search engines APIs
        # 4. Professional network searches

        presence_indicators = {
            'search_visibility': 'unknown',
            'professional_listings': 'unknown',
            'social_media_mentions': 'unknown',
            'news_mentions': 'unknown'
        }

        web_presence.append({
            'type': 'web_search_analysis',
            'indicators': presence_indicators,
            'privacy_impact': 'requires_manual_search',
            'search_terms': search_terms
        })

        return web_presence

    def get_collection_summary(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of data collection results with enhanced metrics"""
        summary = {
            'total_sources_attempted': collected_data['metadata']['sources_attempted'],
            'successful_collections': collected_data['metadata']['sources_successful'],
            'discovered_profiles_count': len(collected_data.get('discovered_profiles', [])),
            'public_records_count': len(collected_data.get('public_records', [])),
            'correlation_score': collected_data.get('cross_platform_correlation', {}).get('overall_correlation_score', 0),
            'success_rate': 0,
            'platforms_identified': [],
            'data_types_collected': set(),
            'privacy_risk_score': 0,
            'collection_timestamp': collected_data['metadata']['collection_timestamp'],
            'input_validation_score': collected_data['metadata'].get('input_confidence', 0),
            'name_validation': collected_data.get('name_analysis', {}).get('is_valid', False),
            'email_validation': collected_data.get('email_analysis', {}).get('is_valid', False)
        }

        if summary['total_sources_attempted'] > 0:
            summary['success_rate'] = summary['successful_collections'] / summary['total_sources_attempted']

        # Analyze collected profiles (both provided and discovered)
        all_profiles = collected_data['social_profiles'] + collected_data.get('discovered_profiles', [])
        for profile in all_profiles:
            summary['platforms_identified'].append(profile['platform'])
            summary['data_types_collected'].add(profile['data_type'])
            summary['privacy_risk_score'] += abs(profile.get('privacy_score_impact', 0))

        summary['data_types_collected'] = list(summary['data_types_collected'])
        
        # Add correlation risk assessment
        correlation_data = collected_data.get('cross_platform_correlation', {})
        summary['privacy_risk_assessment'] = correlation_data.get('privacy_risk_assessment', 'unknown')
        summary['correlation_recommendations'] = correlation_data.get('recommendations', [])
        
        return summary
