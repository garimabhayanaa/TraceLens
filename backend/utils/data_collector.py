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
from .privacy_compliance import (
    create_privacy_compliant_collector, 
    PrivacyConfig, 
    DataClassifier
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectionEngine:
    def __init__(self):
        # Privacy-first configuration
        privacy_config = PrivacyConfig(
            respect_robots_txt=True,
            min_request_delay=2.0,  # Increased for ethical scraping
            max_requests_per_minute=20,  # Conservative rate limiting
            max_requests_per_hour=300,
            user_agent="LeakPeek/1.0 (Privacy Analysis Tool; +https://leakpeek.com/privacy)",
            timeout_seconds=10,
            max_retries=1,
            public_only=True,
            attribution_required=True
        )
        
        # Initialize privacy-compliant collector
        self.privacy_collector = create_privacy_compliant_collector(privacy_config)
        
        # Create session with privacy-compliant headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': privacy_config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'DNT': '1',  # Do Not Track header
        })
        
        # Increased rate limiting for ethical collection
        self.rate_limit_delay = 2.0  # seconds between requests
        
        # Initialize other components
        self.input_processor = create_input_processor()  # Enhanced input processing
        self.social_discovery = create_social_discovery_engine()
        self.public_records_scanner = create_public_records_scanner()
        self.cross_platform_correlator = create_cross_platform_correlator()

    def collect_public_data(self, name: str, email: str, social_links: List[str]) -> Dict[str, Any]:
        """Main entry point for privacy-first comprehensive data collection"""
        
        logger.info("Starting privacy-compliant data collection with comprehensive features")
        
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
            'discovered_profiles': [],  # Auto-discovered profiles
            'web_presence': [],
            'public_records': [],  # Public records
            'cross_platform_correlation': {},  # Correlation analysis
            'data_sources_attribution': [],  # NEW: Data source attribution
            'privacy_compliance': {  # NEW: Privacy compliance report
                'collection_method': 'privacy_first',
                'robots_txt_respected': True,
                'rate_limited': True,
                'public_data_only': True,
                'ethical_guidelines_followed': True,
                'user_agent': self.session.headers['User-Agent']
            },
            'metadata': {
                'collection_timestamp': time.time(),
                'sources_attempted': len(social_links),
                'sources_successful': 0,
                'input_confidence': input_validation['overall_confidence']
            }
        }

        # Collect data from provided social media profiles with privacy compliance
        for link in social_links:
            if link.strip():
                try:
                    # Use privacy-compliant collection method
                    profile_data = self._collect_social_profile_data_private(link.strip())
                    if profile_data:
                        # Enhance profile data with name matching
                        profile_data['name_match_score'] = self._calculate_name_match(
                            profile_data.get('url', ''), name_variants
                        )
                        # Add data classification
                        profile_data['data_sensitivity'] = DataClassifier.classify_data_sensitivity(
                            profile_data.get('data_type', ''), 
                            profile_data.get('platform', '')
                        )
                        profile_data['collection_compliance'] = 'privacy_first'
                        collected_data['social_profiles'].append(profile_data)
                        collected_data['metadata']['sources_successful'] += 1
                    
                    # Respect enhanced rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error collecting data from {link}: {str(e)}")
                    continue

        # AUTO-DISCOVER additional social media profiles (privacy-compliant)
        try:
            logger.info("Starting privacy-compliant profile discovery...")
            discovered_profiles = self.social_discovery.discover_profiles(name_variants, email)
            
            # Convert discovered profiles to standard format with privacy checks
            for discovered_profile in discovered_profiles:
                # Verify public accessibility and robots.txt compliance
                if self._is_profile_publicly_accessible(discovered_profile.url):
                    profile_dict = {
                        'platform': discovered_profile.platform,
                        'url': discovered_profile.url,
                        'username': discovered_profile.username,
                        'confidence_level': discovered_profile.confidence_score / 100,
                        'discovery_method': discovered_profile.discovery_method,
                        'data_type': 'discovered_profile',
                        'verification_status': discovered_profile.verification_status,
                        'privacy_score_impact': -1.0,  # Default impact
                        'inferred_data': discovered_profile.profile_data,
                        'data_sensitivity': 'low',  # Discovered profiles are minimal data
                        'access_level': 'public',
                        'collection_compliance': 'privacy_first'
                    }
                    collected_data['discovered_profiles'].append(profile_dict)
                else:
                    logger.debug(f"Skipping non-public profile: {discovered_profile.url}")
            
            logger.info(f"Discovered {len(collected_data['discovered_profiles'])} public profiles")
            
        except Exception as e:
            logger.error(f"Profile discovery failed: {str(e)}")

        # SCAN PUBLIC RECORDS (ethical, limited scope)
        try:
            logger.info("Starting ethical public records scan...")
            public_records = self.public_records_scanner.scan_public_records(
                cleaned_name, email
            )
            
            # Convert public records to standard format with privacy filtering
            for record in public_records:
                # Only include records with acceptable privacy impact
                if record.privacy_impact <= 3.0:  # Filter high-impact records
                    record_dict = {
                        'record_type': record.record_type,
                        'source': record.source,
                        'data': record.data,
                        'confidence_score': record.confidence_score,
                        'verification_status': record.verification_status,
                        'privacy_impact': record.privacy_impact,
                        'data_sensitivity': 'medium' if record.privacy_impact > 2.0 else 'low',
                        'legal_basis': 'public_records',
                        'collection_compliance': 'ethical_public_only'
                    }
                    collected_data['public_records'].append(record_dict)
                else:
                    logger.info(f"Filtered high-impact record: {record.record_type} (impact: {record.privacy_impact})")
            
            logger.info(f"Found {len(collected_data['public_records'])} ethical public records")
            
        except Exception as e:
            logger.error(f"Public records scan failed: {str(e)}")

        # Search for additional web presence using privacy-compliant methods
        web_presence = self._search_web_presence_private(cleaned_name, email)
        collected_data['web_presence'] = web_presence

        # CROSS-PLATFORM CORRELATION ANALYSIS
        try:
            logger.info("Starting privacy-aware correlation analysis...")
            
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

        # Generate comprehensive data source attribution
        collected_data['data_sources_attribution'] = self._generate_attribution_report()
        
        # Update privacy compliance report with final statistics
        collected_data['privacy_compliance'].update({
            'total_requests_made': len(collected_data['data_sources_attribution']),
            'robots_txt_violations': 0,  # We respect all robots.txt
            'rate_limit_violations': 0,  # We implement conservative rate limiting
            'private_data_collected': False,  # We only collect public data
            'attribution_complete': True
        })

        logger.info("Privacy-compliant comprehensive data collection completed")
        return collected_data

    def _collect_social_profile_data_private(self, url: str) -> Optional[Dict[str, Any]]:
        """Collect social profile data with full privacy compliance"""
        
        try:
            domain = urlparse(url).netloc.lower()
            
            # First, use privacy-compliant collector for basic data
            raw_data = self.privacy_collector.collect_data(
                url, 
                data_type='social_profile',
                platform=self._extract_platform_name(domain)
            )
            
            if not raw_data:
                logger.debug(f"Privacy collector returned no data for {url}")
                return None
            
            # Route to specific platform handlers for enhanced processing
            if 'linkedin.com' in domain:
                return self._enhance_linkedin_data_private(raw_data, url)
            elif 'twitter.com' in domain or 'x.com' in domain:
                return self._enhance_twitter_data_private(raw_data, url)
            elif 'github.com' in domain:
                return self._enhance_github_data_private(raw_data, url)
            elif 'instagram.com' in domain:
                return self._enhance_instagram_data_private(raw_data, url)
            elif 'facebook.com' in domain:
                return self._enhance_facebook_data_private(raw_data, url)
            else:
                return self._enhance_generic_data_private(raw_data, url)
                
        except Exception as e:
            logger.error(f"Error collecting private social profile data from {url}: {str(e)}")
            return None

    def _enhance_linkedin_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance LinkedIn data with privacy compliance"""
        
        data = {
            'platform': 'linkedin',
            'url': url,
            'data_type': 'professional',
            'access_level': 'public',
            'data_source': 'linkedin_public',
            'collection_method': 'privacy_compliant',
            'robots_compliant': True,
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
            'privacy_score_impact': -1.5,
            'confidence_level': 0.8,
            'raw_data_classification': 'public_profile_metadata'
        }

        # Only include truly public information
        if 'title' in raw_data:
            data['inferred_data']['page_title'] = raw_data['title'][:100]  # Limit length
        
        return data

    def _enhance_twitter_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance Twitter data with privacy compliance"""
        
        data = {
            'platform': 'twitter',
            'url': url,
            'data_type': 'social_media',
            'access_level': 'public',
            'data_source': 'twitter_public',
            'collection_method': 'privacy_compliant',
            'robots_compliant': True,
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
            'confidence_level': 0.7,
            'accessibility': 'public_profile_accessible'
        }

        # Only include public metadata
        if 'title' in raw_data:
            data['inferred_data']['page_title'] = raw_data['title'][:100]
        if 'description' in raw_data:
            data['inferred_data']['page_description'] = raw_data['description'][:200]

        return data

    def _enhance_github_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance GitHub data with privacy compliance"""
        
        data = {
            'platform': 'github',
            'url': url,
            'data_type': 'professional_technical',
            'access_level': 'public',
            'data_source': 'github_api_public',
            'collection_method': 'privacy_compliant',
            'robots_compliant': True,
            'indicators': {
                'technical_skills': True,
                'open_source_contribution': True,
                'coding_activity': True
            },
            'inferred_data': {
                'technical_expertise': 'demonstrated',
                'programming_languages': 'multiple_likely',
                'collaboration_style': 'open_source'
            },
            'privacy_score_impact': -1.0,
            'confidence_level': 0.9
        }

        # Only include public API fields that are definitely public
        public_fields = {
            'login', 'name', 'public_repos', 'followers', 'following', 'created_at'
        }

        for field in public_fields:
            if field in raw_data:
                data['inferred_data'][field] = raw_data[field]

        # Assess privacy impact
        if raw_data.get('bio') or raw_data.get('location'):
            data['privacy_score_impact'] = -1.5
            data['inferred_data']['has_detailed_profile'] = True

        return data

    def _enhance_instagram_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance Instagram data with privacy compliance"""
        
        return {
            'platform': 'instagram',
            'url': url,
            'data_type': 'lifestyle_social',
            'access_level': 'public',
            'data_source': 'instagram_public_metadata',
            'collection_method': 'privacy_compliant_minimal',
            'robots_compliant': True,
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
            'confidence_level': 0.6,
            'collection_method': 'profile_existence_check',
            'note': 'Minimal data collection due to platform restrictions'
        }

    def _enhance_facebook_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance Facebook data with privacy compliance"""
        
        return {
            'platform': 'facebook',
            'url': url,
            'data_type': 'personal_social',
            'access_level': 'minimal_public',
            'data_source': 'facebook_public_metadata',
            'collection_method': 'privacy_compliant_minimal',
            'robots_compliant': True,
            'indicators': {
                'personal_network': True,
                'life_events_sharing': True,
                'family_connections': True
            },
            'inferred_data': {
                'social_network_type': 'personal_family',
                'information_sharing': 'potentially_detailed'
            },
            'privacy_score_impact': -2.5,
            'confidence_level': 0.5,
            'collection_method': 'profile_existence_check',
            'note': 'Minimal data collection due to strict privacy controls'
        }

    def _enhance_generic_data_private(self, raw_data: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance generic profile data with privacy compliance"""
        
        data = {
            'platform': 'unknown',
            'url': url,
            'data_type': 'generic_web_presence',
            'access_level': 'public',
            'data_source': 'generic_webpage',
            'collection_method': 'privacy_compliant',
            'robots_compliant': True,
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

        # Include only safe public metadata
        if 'title' in raw_data:
            data['inferred_data']['page_title'] = raw_data['title'][:100]
        if 'description' in raw_data:
            data['inferred_data']['page_description'] = raw_data['description'][:200]

        return data

    def _is_profile_publicly_accessible(self, url: str) -> bool:
        """Check if a profile is publicly accessible with robots.txt compliance"""
        
        try:
            # Check robots.txt compliance first
            if not self.privacy_collector.robots_checker.can_fetch(
                url, self.session.headers['User-Agent']
            ):
                logger.debug(f"Robots.txt disallows access to {url}")
                return False
            
            # Check if profile exists and is public
            response = self.privacy_collector._make_request(url)
            if response and response.status_code == 200:
                content = response.text.lower()
                
                # Check for indicators that profile requires authentication
                private_indicators = [
                    'login required', 'sign in', 'authenticate', 
                    'private profile', 'account suspended', 'page not found'
                ]
                
                if any(indicator in content for indicator in private_indicators):
                    return False
                
                return True
                
            return False
            
        except Exception:
            return False

    def _search_web_presence_private(self, name: str, email: str) -> List[Dict[str, Any]]:
        """Search for web presence with full privacy compliance"""
        
        web_presence = []

        search_terms = [
            f'"{name}"',
            f'"{email.split("@")[0]}"',  # Username part of email
        ]

        # Privacy-compliant web presence detection
        presence_indicators = {
            'search_visibility': 'requires_search_engine_api',
            'professional_listings': 'requires_manual_verification',
            'social_media_mentions': 'detected_through_correlation',
            'news_mentions': 'requires_news_api'
        }

        web_presence.append({
            'type': 'privacy_compliant_web_analysis',
            'indicators': presence_indicators,
            'privacy_impact': 'minimal',
            'search_terms': search_terms,
            'collection_method': 'correlation_based',
            'data_source': 'internal_correlation_analysis',
            'attribution': 'Based on correlation of discovered profiles, no external search performed',
            'ethical_note': 'No direct web searching performed to respect privacy',
            'robots_compliant': True
        })

        return web_presence

    def _generate_attribution_report(self) -> List[Dict[str, Any]]:
        """Generate comprehensive data source attribution report"""
        
        # Get attribution from privacy collector
        privacy_sources = self.privacy_collector.get_data_sources()
        
        # Add our own attribution for internal processes
        internal_sources = [
            {
                'source_type': 'input_validation',
                'platform': 'internal',
                'timestamp': time.time(),
                'robots_compliant': True,
                'data_classification': 'processed',
                'legal_basis': 'legitimate_interest'
            },
            {
                'source_type': 'correlation_analysis',
                'platform': 'internal',
                'timestamp': time.time(),
                'robots_compliant': True,
                'data_classification': 'derived',
                'legal_basis': 'legitimate_interest'
            }
        ]
        
        return privacy_sources + internal_sources

    def _extract_platform_name(self, domain: str) -> str:
        """Extract platform name from domain"""
        
        platform_map = {
            'linkedin.com': 'linkedin',
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'github.com': 'github',
            'instagram.com': 'instagram',
            'facebook.com': 'facebook',
            'youtube.com': 'youtube',
            'reddit.com': 'reddit',
            'tiktok.com': 'tiktok'
        }
        
        for platform_domain, platform_name in platform_map.items():
            if platform_domain in domain:
                return platform_name
        
        return 'unknown'

    # Enhanced analysis methods (keeping existing functionality)
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

    def get_collection_summary(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced collection summary with privacy compliance metrics"""
        
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
            'email_validation': collected_data.get('email_analysis', {}).get('is_valid', False),
            
            # Privacy compliance metrics
            'privacy_compliance': {
                'robots_txt_respected': collected_data['privacy_compliance']['robots_txt_respected'],
                'rate_limited': collected_data['privacy_compliance']['rate_limited'],
                'public_data_only': collected_data['privacy_compliance']['public_data_only'],
                'ethical_guidelines_followed': collected_data['privacy_compliance']['ethical_guidelines_followed'],
                'data_sources_attributed': len(collected_data.get('data_sources_attribution', [])),
                'collection_method': collected_data['privacy_compliance']['collection_method']
            },
            
            # Attribution summary
            'attribution_summary': {
                'total_sources': len(collected_data.get('data_sources_attribution', [])),
                'source_types': list(set(
                    source.get('source_type', 'unknown') 
                    for source in collected_data.get('data_sources_attribution', [])
                )),
                'platforms_accessed': list(set(
                    source.get('platform', 'unknown') 
                    for source in collected_data.get('data_sources_attribution', [])
                ))
            }
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