import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import re
from difflib import SequenceMatcher
import json

logger = logging.getLogger(__name__)

@dataclass
class CorrelationResult:
    correlation_type: str
    platforms: List[str]
    confidence_score: float
    evidence: Dict[str, Any]
    privacy_impact: float

@dataclass
class ProfileCluster:
    profiles: List[Dict]
    correlation_strength: float
    common_attributes: Dict[str, Any]
    risk_assessment: str

class CrossPlatformCorrelator:
    """Advanced cross-platform correlation analysis"""
    
    def __init__(self):
        self.correlation_weights = {
            'username_similarity': 0.3,
            'name_matching': 0.25,
            'temporal_patterns': 0.15,
            'content_similarity': 0.15,
            'network_overlap': 0.10,
            'metadata_matching': 0.05
        }
        
        self.privacy_risk_multipliers = {
            'high_correlation': 2.5,
            'medium_correlation': 1.5,
            'low_correlation': 1.0
        }
    
    def correlate_profiles(self, social_profiles: List[Dict], 
                         name_variants: List[str], email: str) -> Dict[str, Any]:
        """
        Perform comprehensive cross-platform correlation analysis
        """
        
        if len(social_profiles) < 2:
            return {
                'correlations': [],
                'profile_clusters': [],
                'overall_correlation_score': 0.0,
                'privacy_risk_assessment': 'low',
                'recommendations': ['Insufficient profiles for correlation analysis']
            }
        
        logger.info(f"Starting cross-platform correlation for {len(social_profiles)} profiles")
        
        # Perform different types of correlation analysis
        correlations = []
        
        # Username similarity correlation
        username_correlations = self._analyze_username_correlations(social_profiles)
        correlations.extend(username_correlations)
        
        # Name matching correlation
        name_correlations = self._analyze_name_correlations(social_profiles, name_variants)
        correlations.extend(name_correlations)
        
        # Profile metadata correlation
        metadata_correlations = self._analyze_metadata_correlations(social_profiles)
        correlations.extend(metadata_correlations)
        
        # Temporal pattern correlation
        temporal_correlations = self._analyze_temporal_correlations(social_profiles)
        correlations.extend(temporal_correlations)
        
        # Create profile clusters based on correlations
        profile_clusters = self._create_profile_clusters(social_profiles, correlations)
        
        # Calculate overall correlation score
        overall_score = self._calculate_overall_correlation_score(correlations)
        
        # Assess privacy risk
        privacy_risk = self._assess_privacy_risk(overall_score, correlations, profile_clusters)
        
        # Generate recommendations
        recommendations = self._generate_correlation_recommendations(
            overall_score, correlations, profile_clusters
        )
        
        return {
            'correlations': [self._correlation_to_dict(c) for c in correlations],
            'profile_clusters': [self._cluster_to_dict(c) for c in profile_clusters],
            'overall_correlation_score': overall_score,
            'privacy_risk_assessment': privacy_risk,
            'correlation_strength': self._categorize_correlation_strength(overall_score),
            'recommendations': recommendations,
            'analysis_metadata': {
                'profiles_analyzed': len(social_profiles),
                'correlations_found': len(correlations),
                'clusters_identified': len(profile_clusters)
            }
        }
    
    def _analyze_username_correlations(self, profiles: List[Dict]) -> List[CorrelationResult]:
        """Analyze username similarities across platforms"""
        
        correlations = []
        
        for i, profile1 in enumerate(profiles):
            for j, profile2 in enumerate(profiles[i+1:], i+1):
                
                username1 = self._extract_username(profile1.get('url', ''))
                username2 = self._extract_username(profile2.get('url', ''))
                
                if username1 and username2:
                    similarity = self._calculate_username_similarity(username1, username2)
                    
                    if similarity > 0.6:  # Threshold for significant similarity
                        correlation = CorrelationResult(
                            correlation_type='username_similarity',
                            platforms=[profile1.get('platform'), profile2.get('platform')],
                            confidence_score=similarity * 100,
                            evidence={
                                'username1': username1,
                                'username2': username2,
                                'similarity_score': similarity,
                                'comparison_method': 'string_similarity'
                            },
                            privacy_impact=3.0 * similarity  # Higher similarity = higher privacy impact
                        )
                        correlations.append(correlation)
        
        return correlations
    
    def _analyze_name_correlations(self, profiles: List[Dict], 
                                 name_variants: List[str]) -> List[CorrelationResult]:
        """Analyze name matching across profiles"""
        
        correlations = []
        
        for profile in profiles:
            name_matches = []
            
            # Check profile URL for name matches
            profile_url = profile.get('url', '').lower()
            
            for variant in name_variants:
                variant_lower = variant.lower()
                
                # Check for exact matches
                if variant_lower in profile_url:
                    name_matches.append({
                        'variant': variant,
                        'match_type': 'exact',
                        'confidence': 0.9
                    })
                
                # Check for partial matches
                elif any(part in profile_url for part in variant_lower.split() if len(part) > 2):
                    name_matches.append({
                        'variant': variant,
                        'match_type': 'partial',
                        'confidence': 0.6
                    })
            
            if name_matches:
                # Calculate overall name match confidence
                avg_confidence = sum(match['confidence'] for match in name_matches) / len(name_matches)
                
                correlation = CorrelationResult(
                    correlation_type='name_matching',
                    platforms=[profile.get('platform')],
                    confidence_score=avg_confidence * 100,
                    evidence={
                        'matches_found': name_matches,
                        'profile_url': profile.get('url'),
                        'match_count': len(name_matches)
                    },
                    privacy_impact=2.5 * avg_confidence
                )
                correlations.append(correlation)
        
        return correlations
    
    def _analyze_metadata_correlations(self, profiles: List[Dict]) -> List[CorrelationResult]:
        """Analyze metadata correlations between profiles"""
        
        correlations = []
        
        for i, profile1 in enumerate(profiles):
            for j, profile2 in enumerate(profiles[i+1:], i+1):
                
                metadata_matches = self._compare_profile_metadata(profile1, profile2)
                
                if metadata_matches['match_score'] > 0.4:
                    correlation = CorrelationResult(
                        correlation_type='metadata_matching',
                        platforms=[profile1.get('platform'), profile2.get('platform')],
                        confidence_score=metadata_matches['match_score'] * 100,
                        evidence=metadata_matches,
                        privacy_impact=2.0 * metadata_matches['match_score']
                    )
                    correlations.append(correlation)
        
        return correlations
    
    def _analyze_temporal_correlations(self, profiles: List[Dict]) -> List[CorrelationResult]:
        """Analyze temporal patterns across profiles"""
        
        correlations = []
        
        # Look for profiles created around the same time
        profile_timestamps = []
        
        for profile in profiles:
            # Extract timestamp information if available
            inferred_data = profile.get('inferred_data', {})
            created_date = inferred_data.get('account_created')
            
            if created_date:
                profile_timestamps.append({
                    'platform': profile.get('platform'),
                    'created_date': created_date,
                    'profile': profile
                })
        
        # Compare creation times
        if len(profile_timestamps) >= 2:
            temporal_clusters = self._find_temporal_clusters(profile_timestamps)
            
            for cluster in temporal_clusters:
                if len(cluster) >= 2:
                    correlation = CorrelationResult(
                        correlation_type='temporal_patterns',
                        platforms=[p['platform'] for p in cluster],
                        confidence_score=70.0,  # Moderate confidence for temporal correlation
                        evidence={
                            'cluster_size': len(cluster),
                            'creation_dates': [p['created_date'] for p in cluster],
                            'time_window': 'Similar creation timeframe'
                        },
                        privacy_impact=1.5
                    )
                    correlations.append(correlation)
        
        return correlations
    
    def _create_profile_clusters(self, profiles: List[Dict], 
                               correlations: List[CorrelationResult]) -> List[ProfileCluster]:
        """Create clusters of related profiles based on correlations"""
        
        # Build correlation graph
        correlation_graph = defaultdict(set)
        
        for correlation in correlations:
            platforms = correlation.platforms
            if len(platforms) == 2:
                platform1, platform2 = platforms
                correlation_graph[platform1].add(platform2)
                correlation_graph[platform2].add(platform1)
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        platform_to_profile = {p.get('platform'): p for p in profiles}
        
        for platform in correlation_graph:
            if platform not in visited:
                cluster_platforms = set()
                self._dfs_cluster(platform, correlation_graph, visited, cluster_platforms)
                
                if len(cluster_platforms) >= 2:
                    cluster_profiles = [
                        platform_to_profile[p] for p in cluster_platforms 
                        if p in platform_to_profile
                    ]
                    
                    # Calculate cluster strength
                    cluster_strength = self._calculate_cluster_strength(
                        cluster_platforms, correlations
                    )
                    
                    # Analyze common attributes
                    common_attributes = self._analyze_common_attributes(cluster_profiles)
                    
                    # Assess risk
                    risk_assessment = self._assess_cluster_risk(cluster_strength, len(cluster_profiles))
                    
                    cluster = ProfileCluster(
                        profiles=cluster_profiles,
                        correlation_strength=cluster_strength,
                        common_attributes=common_attributes,
                        risk_assessment=risk_assessment
                    )
                    
                    clusters.append(cluster)
        
        return clusters
    
    def _calculate_username_similarity(self, username1: str, username2: str) -> float:
        """Calculate similarity between two usernames"""
        
        # Normalize usernames
        u1 = username1.lower().strip()
        u2 = username2.lower().strip()
        
        # Exact match
        if u1 == u2:
            return 1.0
        
        # Use sequence matcher for similarity
        similarity = SequenceMatcher(None, u1, u2).ratio()
        
        # Boost similarity for common transformations
        if u1.replace('_', '') == u2.replace('_', ''):
            similarity = max(similarity, 0.9)
        
        if u1.replace('.', '') == u2.replace('.', ''):
            similarity = max(similarity, 0.9)
        
        # Check for number variations
        u1_no_nums = re.sub(r'\d+', '', u1)
        u2_no_nums = re.sub(r'\d+', '', u2)
        
        if u1_no_nums == u2_no_nums and u1_no_nums:
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def _extract_username(self, url: str) -> Optional[str]:
        """Extract username from social media URL"""
        
        if not url:
            return None
        
        # Common patterns for username extraction
        patterns = [
            r'/([^/]+)/?$',  # Last path component
            r'/@([^/]+)',    # @username pattern
            r'/user/([^/]+)', # /user/username pattern
            r'/u/([^/]+)',   # /u/username pattern
            r'/in/([^/]+)',  # LinkedIn /in/username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                username = match.group(1)
                # Validate username
                if re.match(r'^[a-zA-Z0-9._-]+$', username) and len(username) <= 50:
                    return username
        
        return None
    
    def _compare_profile_metadata(self, profile1: Dict, profile2: Dict) -> Dict[str, Any]:
        """Compare metadata between two profiles"""
        
        matches = {
            'match_score': 0.0,
            'matched_attributes': [],
            'total_comparisons': 0
        }
        
        # Compare inferred data
        data1 = profile1.get('inferred_data', {})
        data2 = profile2.get('inferred_data', {})
        
        comparable_fields = [
            'employment_status', 'communication_style', 'technical_expertise',
            'content_type', 'social_network_type'
        ]
        
        matched_count = 0
        total_comparisons = 0
        
        for field in comparable_fields:
            if field in data1 and field in data2:
                total_comparisons += 1
                if data1[field] == data2[field]:
                    matched_count += 1
                    matches['matched_attributes'].append({
                        'field': field,
                        'value': data1[field]
                    })
        
        if total_comparisons > 0:
            matches['match_score'] = matched_count / total_comparisons
            matches['total_comparisons'] = total_comparisons
        
        return matches
    
    def _find_temporal_clusters(self, profile_timestamps: List[Dict]) -> List[List[Dict]]:
        """Find clusters of profiles created around the same time"""
        
        # This is a simplified implementation
        # In practice, you'd parse actual dates and use more sophisticated clustering
        
        clusters = []
        
        # Group by year (simplified)
        year_groups = defaultdict(list)
        
        for profile_data in profile_timestamps:
            created_date = profile_data['created_date']
            
            # Extract year if possible
            year_match = re.search(r'(\d{4})', str(created_date))
            if year_match:
                year = year_match.group(1)
                year_groups[year].append(profile_data)
        
        # Return groups with multiple profiles
        for year, profiles in year_groups.items():
            if len(profiles) >= 2:
                clusters.append(profiles)
        
        return clusters
    
    def _dfs_cluster(self, platform: str, graph: defaultdict, 
                    visited: set, cluster: set):
        """Depth-first search to find connected components"""
        visited.add(platform)
        cluster.add(platform)
        
        for neighbor in graph[platform]:
            if neighbor not in visited:
                self._dfs_cluster(neighbor, graph, visited, cluster)
    
    def _calculate_cluster_strength(self, platforms: Set[str], 
                                  correlations: List[CorrelationResult]) -> float:
        """Calculate the strength of a profile cluster"""
        
        relevant_correlations = [
            c for c in correlations 
            if all(p in platforms for p in c.platforms)
        ]
        
        if not relevant_correlations:
            return 0.0
        
        # Weight correlations by type and confidence
        total_weight = 0.0
        weighted_score = 0.0
        
        for correlation in relevant_correlations:
            weight = self.correlation_weights.get(correlation.correlation_type, 0.1)
            total_weight += weight
            weighted_score += correlation.confidence_score * weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _analyze_common_attributes(self, profiles: List[Dict]) -> Dict[str, Any]:
        """Analyze common attributes across clustered profiles"""
        
        common_attrs = {
            'platforms': [p.get('platform') for p in profiles],
            'data_types': list(set(p.get('data_type') for p in profiles)),
            'common_indicators': {},
            'shared_patterns': []
        }
        
        # Find common indicators
        all_indicators = defaultdict(int)
        
        for profile in profiles:
            indicators = profile.get('indicators', {})
            for key, value in indicators.items():
                if value:  # Only count True values
                    all_indicators[key] += 1
        
        # Keep indicators present in multiple profiles
        profile_count = len(profiles)
        for indicator, count in all_indicators.items():
            if count >= 2 or count / profile_count >= 0.5:
                common_attrs['common_indicators'][indicator] = {
                    'count': count,
                    'percentage': (count / profile_count) * 100
                }
        
        return common_attrs
    
    def _assess_cluster_risk(self, strength: float, profile_count: int) -> str:
        """Assess privacy risk of a profile cluster"""
        
        if strength > 80 and profile_count >= 4:
            return 'high'
        elif strength > 60 and profile_count >= 3:
            return 'medium'
        elif strength > 40:
            return 'low'
        else:
            return 'minimal'
    
    def _calculate_overall_correlation_score(self, correlations: List[CorrelationResult]) -> float:
        """Calculate overall correlation score"""
        
        if not correlations:
            return 0.0
        
        # Weight correlations by type and aggregate
        total_weight = 0.0
        weighted_score = 0.0
        
        for correlation in correlations:
            weight = self.correlation_weights.get(correlation.correlation_type, 0.1)
            total_weight += weight
            weighted_score += (correlation.confidence_score / 100.0) * weight
        
        return (weighted_score / total_weight * 100) if total_weight > 0 else 0.0
    
    def _assess_privacy_risk(self, overall_score: float, 
                           correlations: List[CorrelationResult],
                           clusters: List[ProfileCluster]) -> str:
        """Assess overall privacy risk from correlations"""
        
        # Base risk from correlation score
        if overall_score > 80:
            base_risk = 'high'
        elif overall_score > 60:
            base_risk = 'medium'
        elif overall_score > 30:
            base_risk = 'low'
        else:
            base_risk = 'minimal'
        
        # Adjust for high-impact correlations
        high_impact_correlations = [c for c in correlations if c.privacy_impact > 3.0]
        if len(high_impact_correlations) >= 3:
            if base_risk == 'medium':
                base_risk = 'high'
            elif base_risk == 'low':
                base_risk = 'medium'
        
        # Adjust for large clusters
        large_clusters = [c for c in clusters if len(c.profiles) >= 4]
        if large_clusters:
            if base_risk == 'medium':
                base_risk = 'high'
            elif base_risk == 'low':
                base_risk = 'medium'
        
        return base_risk
    
    def _categorize_correlation_strength(self, score: float) -> str:
        """Categorize correlation strength"""
        
        if score > 80:
            return 'very_high'
        elif score > 60:
            return 'high'
        elif score > 40:
            return 'medium'
        elif score > 20:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_correlation_recommendations(self, overall_score: float,
                                            correlations: List[CorrelationResult],
                                            clusters: List[ProfileCluster]) -> List[str]:
        """Generate recommendations based on correlation analysis"""
        
        recommendations = []
        
        # Overall score recommendations
        if overall_score > 70:
            recommendations.append(
                "🔴 HIGH CORRELATION DETECTED: Your profiles are highly correlated across platforms. "
                "Consider using different usernames and limiting shared information."
            )
        elif overall_score > 50:
            recommendations.append(
                "⚠️ MEDIUM CORRELATION: Some patterns link your profiles. "
                "Review username choices and profile information consistency."
            )
        
        # Username correlation recommendations
        username_correlations = [c for c in correlations if c.correlation_type == 'username_similarity']
        if len(username_correlations) >= 2:
            recommendations.append(
                "👤 Use different usernames across platforms to reduce cross-platform linking."
            )
        
        # Name matching recommendations
        name_correlations = [c for c in correlations if c.correlation_type == 'name_matching']
        if len(name_correlations) >= 3:
            recommendations.append(
                "📝 Your real name appears in multiple profile URLs. "
                "Consider using pseudonyms or handles instead."
            )
        
        # Cluster-specific recommendations
        high_risk_clusters = [c for c in clusters if c.risk_assessment == 'high']
        if high_risk_clusters:
            cluster = high_risk_clusters[0]
            platforms = [p.get('platform') for p in cluster.profiles]
            recommendations.append(
                f"🔗 HIGHLY CORRELATED CLUSTER: Profiles on {', '.join(platforms)} "
                f"are strongly linked. Consider compartmentalizing your online presence."
            )
        
        # General recommendations
        if overall_score > 30:
            recommendations.extend([
                "🛡️ Use different profile pictures across platforms",
                "📱 Avoid cross-posting identical content",
                "⚡ Stagger account creation times for future profiles",
                "🌐 Consider using different email addresses for different platforms"
            ])
        
        return recommendations
    
    def _correlation_to_dict(self, correlation: CorrelationResult) -> Dict[str, Any]:
        """Convert CorrelationResult to dictionary"""
        return {
            'correlation_type': correlation.correlation_type,
            'platforms': correlation.platforms,
            'confidence_score': correlation.confidence_score,
            'evidence': correlation.evidence,
            'privacy_impact': correlation.privacy_impact
        }
    
    def _cluster_to_dict(self, cluster: ProfileCluster) -> Dict[str, Any]:
        """Convert ProfileCluster to dictionary"""
        return {
            'profile_count': len(cluster.profiles),
            'platforms': [p.get('platform') for p in cluster.profiles],
            'correlation_strength': cluster.correlation_strength,
            'common_attributes': cluster.common_attributes,
            'risk_assessment': cluster.risk_assessment
        }

def create_cross_platform_correlator():
    """Factory function to create cross-platform correlator"""
    return CrossPlatformCorrelator()
