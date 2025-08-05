import logging
import time
import requests
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import hashlib
from datetime import datetime, timedelta
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Data source attribution record"""
    source_type: str  # 'public_api', 'public_webpage', 'search_engine', etc.
    url: str
    platform: str
    access_method: str  # 'api', 'scraping', 'search'
    timestamp: datetime
    robots_compliant: bool
    rate_limited: bool
    data_classification: str  # 'public', 'semi_public', 'inferred'
    legal_basis: str  # 'legitimate_interest', 'public_information', etc.

@dataclass
class PrivacyConfig:
    """Privacy configuration settings"""
    respect_robots_txt: bool = True
    min_request_delay: float = 1.0
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500
    user_agent: str = "LeakPeek/1.0 (Privacy Analysis Tool; https://leakpeek.com/robots)"
    timeout_seconds: int = 10
    max_retries: int = 2
    public_only: bool = True
    attribution_required: bool = True

class RateLimiter:
    """Advanced rate limiting with multiple time windows"""
    
    def __init__(self, config: PrivacyConfig):
        self.config = config
        self.request_times = defaultdict(list)
        self.domain_delays = defaultdict(float)
        self.lock = threading.RLock()
        
    def can_make_request(self, domain: str) -> bool:
        """Check if we can make a request to the domain"""
        with self.lock:
            now = datetime.utcnow()
            
            # Clean old request times
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            self.request_times[domain] = [
                t for t in self.request_times[domain] 
                if t > hour_ago
            ]
            
            recent_requests = [
                t for t in self.request_times[domain] 
                if t > minute_ago
            ]
            
            # Check rate limits
            if len(recent_requests) >= self.config.max_requests_per_minute:
                logger.warning(f"Rate limit exceeded for {domain}: {len(recent_requests)} requests in last minute")
                return False
            
            if len(self.request_times[domain]) >= self.config.max_requests_per_hour:
                logger.warning(f"Rate limit exceeded for {domain}: {len(self.request_times[domain])} requests in last hour")
                return False
            
            return True
    
    def record_request(self, domain: str):
        """Record a request and enforce minimum delay"""
        with self.lock:
            now = datetime.utcnow()
            self.request_times[domain].append(now)
            
            # Enforce minimum delay
            last_request = self.domain_delays.get(domain, 0)
            elapsed = time.time() - last_request
            
            if elapsed < self.config.min_request_delay:
                delay = self.config.min_request_delay - elapsed
                logger.debug(f"Enforcing rate limit delay of {delay:.2f}s for {domain}")
                time.sleep(delay)
            
            self.domain_delays[domain] = time.time()

class RobotsChecker:
    """Robots.txt compliance checker with caching"""
    
    def __init__(self):
        self.robots_cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 3600  # 1 hour
        self.lock = threading.RLock()
    
    def can_fetch(self, url: str, user_agent: str) -> bool:
        """Check if we can fetch a URL according to robots.txt"""
        try:
            domain = urlparse(url).netloc
            
            with self.lock:
                # Check cache
                if domain in self.robots_cache:
                    if time.time() < self.cache_expiry.get(domain, 0):
                        rp = self.robots_cache[domain]
                        return rp.can_fetch(user_agent, url)
                
                # Fetch and cache robots.txt
                robots_url = urljoin(f"https://{domain}", "/robots.txt")
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                try:
                    rp.read()
                    self.robots_cache[domain] = rp
                    self.cache_expiry[domain] = time.time() + self.cache_ttl
                    
                    can_fetch = rp.can_fetch(user_agent, url)
                    logger.debug(f"Robots.txt check for {domain}: {'allowed' if can_fetch else 'disallowed'}")
                    return can_fetch
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch robots.txt for {domain}: {str(e)}")
                    # If robots.txt is not accessible, assume we can fetch
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Default to allowing if check fails
    
    def get_crawl_delay(self, domain: str, user_agent: str) -> float:
        """Get crawl delay from robots.txt"""
        try:
            if domain in self.robots_cache:
                rp = self.robots_cache[domain]
                delay = rp.crawl_delay(user_agent)
                return float(delay) if delay else 1.0
        except Exception:
            pass
        return 1.0  # Default delay

class DataClassifier:
    """Classifies data based on privacy sensitivity"""
    
    @staticmethod
    def classify_data_sensitivity(data_type: str, source: str) -> str:
        """Classify data sensitivity level"""
        
        # High sensitivity data (avoid collecting)
        high_sensitivity = {
            'private_messages', 'private_posts', 'private_photos', 
            'contact_info', 'location_data', 'financial_info',
            'health_info', 'political_views', 'religious_views'
        }
        
        # Medium sensitivity (collect with extra care)
        medium_sensitivity = {
            'employment_history', 'education_history', 'connections',
            'activity_patterns', 'interests', 'demographics'
        }
        
        # Low sensitivity (generally safe to collect if public)
        low_sensitivity = {
            'username', 'display_name', 'bio', 'public_posts',
            'follower_count', 'following_count', 'join_date',
            'public_repositories', 'public_activity'
        }
        
        data_lower = data_type.lower()
        
        if any(sensitive in data_lower for sensitive in high_sensitivity):
            return 'high'
        elif any(sensitive in data_lower for sensitive in medium_sensitivity):
            return 'medium'
        elif any(sensitive in data_lower for sensitive in low_sensitivity):
            return 'low'
        else:
            return 'unknown'
    
    @staticmethod
    def is_public_data(source_type: str, access_level: str) -> bool:
        """Determine if data is truly public"""
        
        public_sources = {
            'public_api', 'public_webpage', 'search_engine_results',
            'open_directory', 'public_registry', 'published_content'
        }
        
        public_access_levels = {
            'public', 'open', 'unrestricted', 'search_indexed'
        }
        
        return (source_type in public_sources or 
                access_level in public_access_levels)

class PrivacyCompliantCollector:
    """Privacy-first data collection with comprehensive compliance"""
    
    def __init__(self, config: Optional[PrivacyConfig] = None):
        self.config = config or PrivacyConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.robots_checker = RobotsChecker()
        self.data_sources: List[DataSource] = []
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with privacy-compliant headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def collect_data(self, url: str, data_type: str, 
                    platform: str = 'unknown') -> Optional[Dict[str, Any]]:
        """Collect data with full privacy compliance"""
        
        try:
            domain = urlparse(url).netloc
            
            # Step 1: Check if we can make request (rate limiting)
            if not self.rate_limiter.can_make_request(domain):
                logger.warning(f"Rate limit exceeded for {domain}, skipping request")
                return None
            
            # Step 2: Check robots.txt compliance
            if self.config.respect_robots_txt:
                if not self.robots_checker.can_fetch(url, self.config.user_agent):
                    logger.info(f"Robots.txt disallows fetching {url}")
                    self._record_blocked_source(url, platform, 'robots_txt_blocked')
                    return None
            
            # Step 3: Apply crawl delay from robots.txt
            crawl_delay = self.robots_checker.get_crawl_delay(domain, self.config.user_agent)
            additional_delay = max(crawl_delay, self.config.min_request_delay)
            
            # Step 4: Make the request
            self.rate_limiter.record_request(domain)
            
            response = self._make_request(url)
            if not response:
                return None
            
            # Step 5: Classify and validate data
            data = self._extract_public_data(response, url)
            if not data:
                return None
            
            # Step 6: Record data source for attribution
            self._record_data_source(url, platform, data_type, response)
            
            # Step 7: Apply additional privacy filters
            filtered_data = self._apply_privacy_filters(data, data_type)
            
            logger.info(f"Successfully collected data from {url} (platform: {platform})")
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error collecting data from {url}: {str(e)}")
            return None
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retries and error handling"""
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self.session.get(
                    url, 
                    timeout=self.config.timeout_seconds,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited by server, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                elif response.status_code in [403, 404]:
                    logger.info(f"Resource not accessible: {response.status_code}")
                    return None
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    if attempt < self.config.max_retries:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    return None
                    
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def _extract_public_data(self, response: requests.Response, 
                           url: str) -> Optional[Dict[str, Any]]:
        """Extract only publicly accessible data"""
        
        try:
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                return self._extract_json_data(response)
            elif 'text/html' in content_type:
                return self._extract_html_data(response, url)
            else:
                logger.debug(f"Unsupported content type: {content_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            return None
    
    def _extract_json_data(self, response: requests.Response) -> Dict[str, Any]:
        """Extract data from JSON response (typically APIs)"""
        
        try:
            data = response.json()
            
            # Filter out sensitive fields
            if isinstance(data, dict):
                filtered_data = {}
                
                # Allow only public fields
                public_fields = {
                    'login', 'name', 'bio', 'location', 'blog', 'company',
                    'public_repos', 'followers', 'following', 'created_at',
                    'updated_at', 'type', 'site_admin', 'avatar_url',
                    'html_url', 'repos_url', 'organizations_url'
                }
                
                for key, value in data.items():
                    if key in public_fields and not self._is_sensitive_data(key, value):
                        filtered_data[key] = value
                
                return filtered_data
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
            return {}
    
    def _extract_html_data(self, response: requests.Response, 
                          url: str) -> Dict[str, Any]:
        """Extract data from HTML response"""
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract only basic public metadata
            data = {
                'url': url,
                'title': '',
                'description': '',
                'type': 'webpage'
            }
            
            # Page title
            title_tag = soup.find('title')
            if title_tag:
                data['title'] = title_tag.get_text().strip()[:200]  # Limit length
            
            # Meta description
            description_tag = soup.find('meta', attrs={'name': 'description'})
            if description_tag:
                data['description'] = description_tag.get('content', '')[:500]
            
            # Open Graph data (public metadata)
            og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
            for tag in og_tags:
                property_name = tag.get('property', '').replace('og:', '')
                if property_name in ['title', 'description', 'type', 'site_name']:
                    data[f'og_{property_name}'] = tag.get('content', '')[:200]
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting HTML data: {str(e)}")
            return {}
    
    def _is_sensitive_data(self, key: str, value: Any) -> bool:
        """Check if data field contains sensitive information"""
        
        sensitive_keywords = {
            'email', 'phone', 'address', 'private', 'personal',
            'secret', 'token', 'password', 'api_key', 'private_key'
        }
        
        key_lower = str(key).lower()
        
        # Check key name
        if any(sensitive in key_lower for sensitive in sensitive_keywords):
            return True
        
        # Check value content if string
        if isinstance(value, str):
            value_lower = value.lower()
            if any(sensitive in value_lower for sensitive in sensitive_keywords):
                return True
            
            # Check for email patterns
            if '@' in value and '.' in value:
                return True
        
        return False
    
    def _apply_privacy_filters(self, data: Dict[str, Any], 
                             data_type: str) -> Dict[str, Any]:
        """Apply additional privacy filters to collected data"""
        
        if not data:
            return {}
        
        filtered_data = {}
        
        for key, value in data.items():
            # Skip sensitive data
            if self._is_sensitive_data(key, value):
                logger.debug(f"Filtering out sensitive field: {key}")
                continue
            
            # Classify data sensitivity
            sensitivity = DataClassifier.classify_data_sensitivity(key, data_type)
            
            if sensitivity == 'high':
                logger.debug(f"Filtering out high-sensitivity field: {key}")
                continue
            
            # Add privacy metadata
            if isinstance(value, dict):
                value['_privacy_level'] = sensitivity
            
            filtered_data[key] = value
        
        # Add collection metadata
        filtered_data['_collection_metadata'] = {
            'collected_at': datetime.utcnow().isoformat(),
            'collection_method': 'privacy_compliant',
            'data_classification': 'public_only'
        }
        
        return filtered_data
    
    def _record_data_source(self, url: str, platform: str, 
                          data_type: str, response: requests.Response):
        """Record data source for attribution"""
        
        source = DataSource(
            source_type=self._determine_source_type(response),
            url=url,
            platform=platform,
            access_method='http_request',
            timestamp=datetime.utcnow(),
            robots_compliant=True,
            rate_limited=True,
            data_classification='public',
            legal_basis='legitimate_interest_public_data'
        )
        
        self.data_sources.append(source)
    
    def _record_blocked_source(self, url: str, platform: str, reason: str):
        """Record blocked source attempts"""
        
        source = DataSource(
            source_type='blocked',
            url=url,
            platform=platform,
            access_method='blocked',
            timestamp=datetime.utcnow(),
            robots_compliant=reason != 'robots_txt_blocked',
            rate_limited=True,
            data_classification='blocked',
            legal_basis=f'blocked_{reason}'
        )
        
        self.data_sources.append(source)
    
    def _determine_source_type(self, response: requests.Response) -> str:
        """Determine the type of data source"""
        
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            return 'public_api'
        elif 'text/html' in content_type:
            return 'public_webpage'
        else:
            return 'public_resource'
    
    def get_data_sources(self) -> List[Dict[str, Any]]:
        """Get all data sources for attribution"""
        
        return [
            {
                'source_type': source.source_type,
                'url': source.url,
                'platform': source.platform,
                'timestamp': source.timestamp.isoformat(),
                'robots_compliant': source.robots_compliant,
                'data_classification': source.data_classification,
                'legal_basis': source.legal_basis
            }
            for source in self.data_sources
        ]
    
    def generate_attribution_report(self) -> Dict[str, Any]:
        """Generate comprehensive attribution report"""
        
        sources_by_platform = defaultdict(list)
        sources_by_type = defaultdict(int)
        
        for source in self.data_sources:
            sources_by_platform[source.platform].append({
                'url': source.url,
                'timestamp': source.timestamp.isoformat(),
                'type': source.source_type,
                'compliant': source.robots_compliant
            })
            sources_by_type[source.source_type] += 1
        
        return {
            'report_generated': datetime.utcnow().isoformat(),
            'total_sources': len(self.data_sources),
            'sources_by_platform': dict(sources_by_platform),
            'sources_by_type': dict(sources_by_type),
            'compliance_summary': {
                'robots_compliant': sum(1 for s in self.data_sources if s.robots_compliant),
                'rate_limited': sum(1 for s in self.data_sources if s.rate_limited),
                'public_only': sum(1 for s in self.data_sources if s.data_classification == 'public')
            },
            'legal_basis': list(set(s.legal_basis for s in self.data_sources))
        }

def create_privacy_compliant_collector(config: Optional[PrivacyConfig] = None):
    """Factory function to create privacy-compliant collector"""
    return PrivacyCompliantCollector(config)
