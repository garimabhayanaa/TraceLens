import logging
import re
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta, time as dt_time
import pytz
from statistics import mode, median
import calendar

logger = logging.getLogger(__name__)

@dataclass
class PostTimingPattern:
    """Post timing analysis result"""
    peak_hours: List[int]  # Hours of day (0-23)
    peak_days: List[str]   # Days of week
    posting_frequency: str  # 'high', 'medium', 'low'
    time_zone_indicators: List[str]
    consistency_score: float  # 0-1, how consistent the posting schedule is
    activity_clusters: List[Dict[str, Any]]  # Time-based activity clusters
    temporal_signature: str  # Overall temporal behavior pattern

@dataclass
class ActivityFrequency:
    """Activity frequency mapping"""
    daily_average: float
    weekly_pattern: Dict[str, float]  # Day -> activity score
    monthly_trends: Dict[str, float]  # Month -> activity score
    activity_bursts: List[Dict[str, Any]]  # Periods of high activity
    dormant_periods: List[Dict[str, Any]]  # Periods of low activity
    engagement_rhythm: str  # 'steady', 'bursty', 'irregular'
    seasonal_patterns: Dict[str, Any]

@dataclass
class GeographicInference:
    """Geographic location inference from posts"""
    likely_locations: List[Dict[str, Any]]  # Location with confidence scores
    time_zone_estimate: str
    travel_indicators: List[Dict[str, Any]]  # Evidence of travel/movement
    location_consistency: float  # How consistent location indicators are
    geographic_scope: str  # 'local', 'regional', 'national', 'international'
    cultural_indicators: List[str]  # Language, cultural references
    work_location_hints: List[str]

@dataclass
class WorkPersonalBoundary:
    """Work/personal life boundary identification"""
    work_hours_detected: Dict[str, Any]  # Work schedule indicators
    personal_time_indicators: Dict[str, Any]
    boundary_clarity: str  # 'clear', 'blended', 'unclear'
    work_life_balance_score: float  # 0-1, higher = better separation
    professional_content_ratio: float  # 0-1, ratio of work vs personal content
    context_switching_patterns: List[Dict[str, Any]]
    lifestyle_indicators: Dict[str, Any]

@dataclass
class ScheduleAnalysisResult:
    """Complete schedule pattern analysis"""
    post_timing: PostTimingPattern
    activity_frequency: ActivityFrequency
    geographic_inference: GeographicInference
    work_personal_boundary: WorkPersonalBoundary
    overall_schedule_score: float
    behavioral_insights: List[str]
    privacy_implications: List[str]

class PostTimingAnalyzer:
    """Analyzes post timing patterns and temporal behavior"""
    
    def __init__(self):
        self.business_hours = (9, 17)  # Standard business hours
        self.weekend_days = ['saturday', 'sunday']
        self.time_zones = {
            'EST': 'US/Eastern',
            'PST': 'US/Pacific',
            'GMT': 'GMT',
            'CET': 'Europe/Paris',
            'JST': 'Asia/Tokyo'
        }
    
    def analyze_posting_patterns(self, content_data: List[Dict[str, Any]]) -> PostTimingPattern:
        """Analyze posting timing patterns from content data"""
        
        if not content_data:
            return self._create_empty_timing_pattern()
        
        # Extract temporal data from content
        temporal_data = self._extract_temporal_indicators(content_data)
        
        if not temporal_data:
            return self._create_empty_timing_pattern()
        
        # Analyze peak posting hours
        peak_hours = self._identify_peak_hours(temporal_data)
        
        # Analyze peak posting days
        peak_days = self._identify_peak_days(temporal_data)
        
        # Calculate posting frequency
        posting_frequency = self._calculate_posting_frequency(temporal_data)
        
        # Infer time zone
        time_zone_indicators = self._infer_time_zone(temporal_data, content_data)
        
        # Calculate consistency score
        consistency_score = self._calculate_consistency_score(temporal_data)
        
        # Identify activity clusters
        activity_clusters = self._identify_activity_clusters(temporal_data)
        
        # Generate temporal signature
        temporal_signature = self._generate_temporal_signature(
            peak_hours, peak_days, posting_frequency, consistency_score
        )
        
        return PostTimingPattern(
            peak_hours=peak_hours,
            peak_days=peak_days,
            posting_frequency=posting_frequency,
            time_zone_indicators=time_zone_indicators,
            consistency_score=consistency_score,
            activity_clusters=activity_clusters,
            temporal_signature=temporal_signature
        )
    
    def _extract_temporal_indicators(self, content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract temporal indicators from content"""
        
        temporal_data = []
        
        for content in content_data:
            # Look for timestamp data
            timestamp_fields = ['timestamp', 'created_at', 'posted_at', 'date']
            timestamp = None
            
            for field in timestamp_fields:
                if field in content and content[field]:
                    timestamp = self._parse_timestamp(content[field])
                    break
            
            # If no direct timestamp, try to infer from content
            if not timestamp:
                timestamp = self._infer_timestamp_from_content(content)
            
            if timestamp:
                temporal_entry = {
                    'timestamp': timestamp,
                    'hour': timestamp.hour,
                    'day_of_week': timestamp.strftime('%A').lower(),
                    'month': timestamp.month,
                    'content': content.get('text', content.get('content', ''))
                }
                temporal_data.append(temporal_entry)
        
        return temporal_data
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse various timestamp formats"""
        
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        
        if not isinstance(timestamp_str, str):
            return None
        
        # Common timestamp formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _infer_timestamp_from_content(self, content: Dict[str, Any]) -> Optional[datetime]:
        """Infer timestamp from content context"""
        
        text = content.get('text', content.get('content', ''))
        
        if not text:
            return None
        
        # Look for temporal indicators in text
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',  # 3:30 pm
            r'(\d{1,2})\s*(am|pm)',         # 3 pm
            r'morning',
            r'afternoon',
            r'evening',
            r'night',
            r'today',
            r'yesterday',
            r'last week'
        ]
        
        current_time = datetime.now()
        
        for pattern in time_patterns:
            if re.search(pattern, text.lower()):
                # Simple heuristic: if time mentioned, assume recent post
                return current_time - timedelta(hours=np.random.randint(0, 24))
        
        # Default: assume recent post with some randomness
        return current_time - timedelta(hours=np.random.randint(0, 168))  # Within last week
    
    def _identify_peak_hours(self, temporal_data: List[Dict[str, Any]]) -> List[int]:
        """Identify peak posting hours"""
        
        if not temporal_data:
            return []
        
        hour_counts = Counter([entry['hour'] for entry in temporal_data])
        
        if not hour_counts:
            return []
        
        # Find hours with activity above average
        avg_activity = sum(hour_counts.values()) / 24  # Spread across 24 hours
        peak_hours = [hour for hour, count in hour_counts.items() if count > avg_activity]
        
        # Sort by activity level
        peak_hours.sort(key=lambda h: hour_counts[h], reverse=True)
        
        return peak_hours[:5]  # Top 5 peak hours
    
    def _identify_peak_days(self, temporal_data: List[Dict[str, Any]]) -> List[str]:
        """Identify peak posting days"""
        
        if not temporal_data:
            return []
        
        day_counts = Counter([entry['day_of_week'] for entry in temporal_data])
        
        if not day_counts:
            return []
        
        # Find days with activity above average
        avg_activity = sum(day_counts.values()) / 7  # Spread across 7 days
        peak_days = [day for day, count in day_counts.items() if count > avg_activity]
        
        # Sort by activity level
        peak_days.sort(key=lambda d: day_counts[d], reverse=True)
        
        return peak_days[:3]  # Top 3 peak days
    
    def _calculate_posting_frequency(self, temporal_data: List[Dict[str, Any]]) -> str:
        """Calculate posting frequency category"""
        
        if not temporal_data:
            return 'minimal'
        
        # Estimate posts per day based on data span
        timestamps = [entry['timestamp'] for entry in temporal_data]
        if len(timestamps) < 2:
            return 'minimal'
        
        time_span = max(timestamps) - min(timestamps)
        days_span = max(time_span.days, 1)
        posts_per_day = len(temporal_data) / days_span
        
        if posts_per_day >= 3:
            return 'high'
        elif posts_per_day >= 1:
            return 'medium'
        elif posts_per_day >= 0.3:
            return 'low'
        else:
            return 'minimal'
    
    def _infer_time_zone(self, temporal_data: List[Dict[str, Any]], 
                        content_data: List[Dict[str, Any]]) -> List[str]:
        """Infer time zone from posting patterns and content"""
        
        indicators = []
        
        # Analyze business hours posting patterns
        business_hour_posts = [
            entry for entry in temporal_data 
            if self.business_hours[0] <= entry['hour'] <= self.business_hours[1]
        ]
        
        business_ratio = len(business_hour_posts) / len(temporal_data) if temporal_data else 0
        
        if business_ratio > 0.6:
            indicators.append('business_hours_active')
        elif business_ratio < 0.3:
            indicators.append('non_standard_hours')
        
        # Look for timezone mentions in content
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for tz_abbr, tz_name in self.time_zones.items():
                if tz_abbr.lower() in text:
                    indicators.append(f'mentioned_{tz_abbr}')
        
        # Geographic indicators
        location_keywords = {
            'EST': ['new york', 'boston', 'miami', 'eastern'],
            'PST': ['california', 'seattle', 'los angeles', 'pacific'],
            'GMT': ['london', 'uk', 'britain', 'greenwich'],
            'CET': ['paris', 'berlin', 'madrid', 'central europe'],
            'JST': ['japan', 'tokyo', 'jst']
        }
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for tz, keywords in location_keywords.items():
                if any(keyword in text for keyword in keywords):
                    indicators.append(f'geographic_{tz}')
        
        return list(set(indicators))  # Remove duplicates
    
    def _calculate_consistency_score(self, temporal_data: List[Dict[str, Any]]) -> float:
        """Calculate how consistent the posting schedule is"""
        
        if len(temporal_data) < 3:
            return 0.0
        
        # Calculate variance in posting hours
        hours = [entry['hour'] for entry in temporal_data]
        hour_variance = np.var(hours)
        hour_consistency = max(0, 1 - (hour_variance / 144))  # Normalize by max variance
        
        # Calculate day-of-week consistency
        days = [entry['day_of_week'] for entry in temporal_data]
        day_counts = Counter(days)
        day_variance = np.var(list(day_counts.values()))
        day_consistency = max(0, 1 - (day_variance / len(temporal_data)))
        
        # Combined consistency score
        return (hour_consistency + day_consistency) / 2
    
    def _identify_activity_clusters(self, temporal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify time-based activity clusters"""
        
        if not temporal_data:
            return []
        
        clusters = []
        
        # Group by hour ranges
        hour_groups = defaultdict(list)
        for entry in temporal_data:
            hour_range = f"{entry['hour']//4*4}-{entry['hour']//4*4+3}"
            hour_groups[hour_range].append(entry)
        
        for hour_range, entries in hour_groups.items():
            if len(entries) >= 2:  # Minimum cluster size
                cluster = {
                    'time_range': hour_range,
                    'activity_count': len(entries),
                    'consistency': len(entries) / len(temporal_data),
                    'pattern_type': 'hourly_cluster'
                }
                clusters.append(cluster)
        
        # Group by day patterns
        weekday_posts = [e for e in temporal_data if e['day_of_week'] not in self.weekend_days]
        weekend_posts = [e for e in temporal_data if e['day_of_week'] in self.weekend_days]
        
        if weekday_posts:
            clusters.append({
                'time_range': 'weekdays',
                'activity_count': len(weekday_posts),
                'consistency': len(weekday_posts) / len(temporal_data),
                'pattern_type': 'weekday_cluster'
            })
        
        if weekend_posts:
            clusters.append({
                'time_range': 'weekends',
                'activity_count': len(weekend_posts),
                'consistency': len(weekend_posts) / len(temporal_data),
                'pattern_type': 'weekend_cluster'
            })
        
        return clusters
    
    def _generate_temporal_signature(self, peak_hours: List[int], peak_days: List[str],
                                   posting_frequency: str, consistency_score: float) -> str:
        """Generate overall temporal behavior signature"""
        
        signatures = []
        
        # Hour-based signatures
        if peak_hours:
            morning_hours = [h for h in peak_hours if 5 <= h <= 11]
            afternoon_hours = [h for h in peak_hours if 12 <= h <= 17]
            evening_hours = [h for h in peak_hours if 18 <= h <= 22]
            night_hours = [h for h in peak_hours if h >= 23 or h <= 4]
            
            if morning_hours:
                signatures.append('morning_poster')
            if afternoon_hours:
                signatures.append('afternoon_poster')
            if evening_hours:
                signatures.append('evening_poster')
            if night_hours:
                signatures.append('night_owl')
        
        # Day-based signatures
        weekday_peaks = [d for d in peak_days if d not in self.weekend_days]
        weekend_peaks = [d for d in peak_days if d in self.weekend_days]
        
        if weekday_peaks and not weekend_peaks:
            signatures.append('weekday_focused')
        elif weekend_peaks and not weekday_peaks:
            signatures.append('weekend_warrior')
        elif weekday_peaks and weekend_peaks:
            signatures.append('consistent_poster')
        
        # Frequency signatures
        signatures.append(f'{posting_frequency}_frequency')
        
        # Consistency signatures
        if consistency_score > 0.7:
            signatures.append('highly_consistent')
        elif consistency_score > 0.4:
            signatures.append('moderately_consistent')
        else:
            signatures.append('irregular_poster')
        
        return '_'.join(signatures) if signatures else 'unknown_pattern'
    
    def _create_empty_timing_pattern(self) -> PostTimingPattern:
        """Create empty timing pattern for no data case"""
        
        return PostTimingPattern(
            peak_hours=[],
            peak_days=[],
            posting_frequency='minimal',
            time_zone_indicators=[],
            consistency_score=0.0,
            activity_clusters=[],
            temporal_signature='insufficient_data'
        )

class ActivityFrequencyMapper:
    """Maps activity frequency patterns over different time scales"""
    
    def __init__(self):
        self.activity_thresholds = {
            'high': 0.7,
            'medium': 0.4,
            'low': 0.2
        }
    
    def analyze_activity_frequency(self, temporal_data: List[Dict[str, Any]],
                                 content_data: List[Dict[str, Any]]) -> ActivityFrequency:
        """Analyze activity frequency patterns"""
        
        if not temporal_data:
            return self._create_empty_frequency()
        
        # Calculate daily average
        daily_average = self._calculate_daily_average(temporal_data)
        
        # Weekly pattern analysis
        weekly_pattern = self._analyze_weekly_pattern(temporal_data)
        
        # Monthly trends (if enough data)
        monthly_trends = self._analyze_monthly_trends(temporal_data)
        
        # Identify activity bursts
        activity_bursts = self._identify_activity_bursts(temporal_data)
        
        # Identify dormant periods
        dormant_periods = self._identify_dormant_periods(temporal_data)
        
        # Determine engagement rhythm
        engagement_rhythm = self._determine_engagement_rhythm(
            temporal_data, activity_bursts, dormant_periods
        )
        
        # Seasonal pattern analysis
        seasonal_patterns = self._analyze_seasonal_patterns(temporal_data, content_data)
        
        return ActivityFrequency(
            daily_average=daily_average,
            weekly_pattern=weekly_pattern,
            monthly_trends=monthly_trends,
            activity_bursts=activity_bursts,
            dormant_periods=dormant_periods,
            engagement_rhythm=engagement_rhythm,
            seasonal_patterns=seasonal_patterns
        )
    
    def _calculate_daily_average(self, temporal_data: List[Dict[str, Any]]) -> float:
        """Calculate average daily activity"""
        
        if not temporal_data:
            return 0.0
        
        timestamps = [entry['timestamp'] for entry in temporal_data]
        time_span = max(timestamps) - min(timestamps)
        days_span = max(time_span.days, 1)
        
        return len(temporal_data) / days_span
    
    def _analyze_weekly_pattern(self, temporal_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze weekly activity patterns"""
        
        day_counts = Counter([entry['day_of_week'] for entry in temporal_data])
        total_posts = len(temporal_data)
        
        # Normalize to proportions
        weekly_pattern = {}
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            weekly_pattern[day] = day_counts.get(day, 0) / total_posts if total_posts > 0 else 0
        
        return weekly_pattern
    
    def _analyze_monthly_trends(self, temporal_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze monthly activity trends"""
        
        month_counts = Counter([entry['month'] for entry in temporal_data])
        total_posts = len(temporal_data)
        
        # Convert to month names and normalize
        monthly_trends = {}
        for month_num in range(1, 13):
            month_name = calendar.month_name[month_num].lower()
            monthly_trends[month_name] = month_counts.get(month_num, 0) / total_posts if total_posts > 0 else 0
        
        return monthly_trends
    
    def _identify_activity_bursts(self, temporal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify periods of high activity (bursts)"""
        
        if len(temporal_data) < 5:
            return []
        
        # Group posts by day
        daily_counts = defaultdict(int)
        for entry in temporal_data:
            day_key = entry['timestamp'].strftime('%Y-%m-%d')
            daily_counts[day_key] += 1
        
        # Calculate average and threshold for bursts
        daily_values = list(daily_counts.values())
        avg_daily = np.mean(daily_values)
        burst_threshold = avg_daily + np.std(daily_values)
        
        bursts = []
        for day, count in daily_counts.items():
            if count > burst_threshold:
                bursts.append({
                    'date': day,
                    'activity_count': count,
                    'intensity': count / avg_daily if avg_daily > 0 else 0,
                    'type': 'daily_burst'
                })
        
        return sorted(bursts, key=lambda x: x['intensity'], reverse=True)[:5]  # Top 5 bursts
    
    def _identify_dormant_periods(self, temporal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify periods of low/no activity"""
        
        if len(temporal_data) < 3:
            return []
        
        timestamps = sorted([entry['timestamp'] for entry in temporal_data])
        dormant_periods = []
        
        # Look for gaps larger than average
        gaps = []
        for i in range(1, len(timestamps)):
            gap = timestamps[i] - timestamps[i-1]
            gaps.append(gap.total_seconds() / 3600)  # Convert to hours
        
        if gaps:
            avg_gap = np.mean(gaps)
            dormant_threshold = avg_gap * 3  # 3x average gap
            
            for i, gap_hours in enumerate(gaps):
                if gap_hours > dormant_threshold:
                    dormant_periods.append({
                        'start_time': timestamps[i].isoformat(),
                        'end_time': timestamps[i+1].isoformat(),
                        'duration_hours': gap_hours,
                        'type': 'dormant_period'
                    })
        
        return sorted(dormant_periods, key=lambda x: x['duration_hours'], reverse=True)[:3]
    
    def _determine_engagement_rhythm(self, temporal_data: List[Dict[str, Any]],
                                   activity_bursts: List[Dict[str, Any]],
                                   dormant_periods: List[Dict[str, Any]]) -> str:
        """Determine overall engagement rhythm pattern"""
        
        if not temporal_data:
            return 'inactive'
        
        # Calculate coefficient of variation
        daily_counts = defaultdict(int)
        for entry in temporal_data:
            day_key = entry['timestamp'].strftime('%Y-%m-%d')
            daily_counts[day_key] += 1
        
        daily_values = list(daily_counts.values())
        if len(daily_values) < 2:
            return 'minimal'
        
        cv = np.std(daily_values) / np.mean(daily_values)
        
        # Determine rhythm based on variation and burst/dormant patterns
        if len(activity_bursts) > 2 and len(dormant_periods) > 1:
            return 'bursty'
        elif cv < 0.5:
            return 'steady'
        elif cv > 1.5:
            return 'irregular'
        else:
            return 'moderate'
    
    def _analyze_seasonal_patterns(self, temporal_data: List[Dict[str, Any]],
                                 content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal activity patterns"""
        
        seasonal_indicators = {
            'spring': ['spring', 'easter', 'march', 'april', 'may'],
            'summer': ['summer', 'vacation', 'june', 'july', 'august'],
            'fall': ['fall', 'autumn', 'september', 'october', 'november'],
            'winter': ['winter', 'holiday', 'december', 'january', 'february']
        }
        
        seasonal_counts = defaultdict(int)
        
        # Analyze temporal data
        for entry in temporal_data:
            month = entry['month']
            if month in [3, 4, 5]:
                seasonal_counts['spring'] += 1
            elif month in [6, 7, 8]:
                seasonal_counts['summer'] += 1
            elif month in [9, 10, 11]:
                seasonal_counts['fall'] += 1
            else:
                seasonal_counts['winter'] += 1
        
        # Analyze content for seasonal keywords
        seasonal_content = defaultdict(int)
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for season, keywords in seasonal_indicators.items():
                if any(keyword in text for keyword in keywords):
                    seasonal_content[season] += 1
        
        return {
            'temporal_distribution': dict(seasonal_counts),
            'content_themes': dict(seasonal_content),
            'dominant_season': max(seasonal_counts, key=seasonal_counts.get) if seasonal_counts else 'unknown'
        }
    
    def _create_empty_frequency(self) -> ActivityFrequency:
        """Create empty frequency pattern for no data case"""
        
        return ActivityFrequency(
            daily_average=0.0,
            weekly_pattern={},
            monthly_trends={},
            activity_bursts=[],
            dormant_periods=[],
            engagement_rhythm='inactive',
            seasonal_patterns={}
        )

class GeographicInferenceEngine:
    """Infers geographic location from post content and patterns"""
    
    def __init__(self):
        self.location_keywords = {
            # Countries
            'countries': ['usa', 'canada', 'uk', 'france', 'germany', 'japan', 'australia'],
            # Major cities
            'cities': ['new york', 'london', 'paris', 'tokyo', 'sydney', 'toronto', 'berlin'],
            # Time zones
            'timezones': ['est', 'pst', 'gmt', 'cet', 'jst'],
            # Geographic features
            'features': ['beach', 'mountain', 'city', 'suburb', 'downtown', 'countryside']
        }
        
        self.cultural_indicators = {
            'language': ['spanish', 'french', 'german', 'japanese', 'chinese'],
            'currency': ['dollar', 'euro', 'pound', 'yen', 'bitcoin'],
            'holidays': ['thanksgiving', 'christmas', 'new year', 'halloween', 'valentine']
        }
    
    def infer_geographic_location(self, content_data: List[Dict[str, Any]],
                                temporal_data: List[Dict[str, Any]]) -> GeographicInference:
        """Infer geographic location from content and timing patterns"""
        
        # Extract location mentions
        likely_locations = self._extract_location_mentions(content_data)
        
        # Infer timezone from posting patterns
        time_zone_estimate = self._estimate_timezone(temporal_data)
        
        # Detect travel indicators
        travel_indicators = self._detect_travel_patterns(content_data, temporal_data)
        
        # Calculate location consistency
        location_consistency = self._calculate_location_consistency(likely_locations)
        
        # Determine geographic scope
        geographic_scope = self._determine_geographic_scope(likely_locations, travel_indicators)
        
        # Extract cultural indicators
        cultural_indicators = self._extract_cultural_indicators(content_data)
        
        # Infer work location hints
        work_location_hints = self._extract_work_location_hints(content_data)
        
        return GeographicInference(
            likely_locations=likely_locations,
            time_zone_estimate=time_zone_estimate,
            travel_indicators=travel_indicators,
            location_consistency=location_consistency,
            geographic_scope=geographic_scope,
            cultural_indicators=cultural_indicators,
            work_location_hints=work_location_hints
        )
    
    def _extract_location_mentions(self, content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract location mentions from content"""
        
        location_mentions = defaultdict(int)
        location_contexts = defaultdict(list)
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Check for location keywords
            for category, keywords in self.location_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        location_mentions[keyword] += 1
                        location_contexts[keyword].append(text[:100])  # Context snippet
        
        # Convert to structured format
        locations = []
        total_mentions = sum(location_mentions.values())
        
        for location, count in location_mentions.items():
            confidence = count / total_mentions if total_mentions > 0 else 0
            locations.append({
                'location': location,
                'mention_count': count,
                'confidence': confidence,
                'contexts': location_contexts[location][:3]  # Top 3 contexts
            })
        
        # Sort by confidence
        return sorted(locations, key=lambda x: x['confidence'], reverse=True)[:10]
    
    def _estimate_timezone(self, temporal_data: List[Dict[str, Any]]) -> str:
        """Estimate timezone based on posting patterns"""
        
        if not temporal_data:
            return 'unknown'
        
        # Analyze business hours posting pattern
        business_hour_posts = [
            entry for entry in temporal_data 
            if 9 <= entry['hour'] <= 17
        ]
        
        business_ratio = len(business_hour_posts) / len(temporal_data) if temporal_data else 0
        
        # Simple heuristic based on business hours activity
        if business_ratio > 0.6:
            # Most posts during business hours - likely major timezone
            peak_hours = [entry['hour'] for entry in temporal_data]
            avg_peak_hour = np.mean(peak_hours)
            
            if 8 <= avg_peak_hour <= 12:
                return 'EST_likely'
            elif 11 <= avg_peak_hour <= 15:
                return 'PST_likely'
            elif 14 <= avg_peak_hour <= 18:
                return 'GMT_likely'
            else:
                return 'other_timezone'
        else:
            return 'non_standard_schedule'
    
    def _detect_travel_patterns(self, content_data: List[Dict[str, Any]],
                              temporal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect travel indicators from content and timing"""
        
        travel_indicators = []
        
        # Travel-related keywords
        travel_keywords = ['travel', 'trip', 'vacation', 'airport', 'flight', 'hotel', 'visiting']
        
        for i, content in enumerate(content_data):
            text = content.get('text', content.get('content', '')).lower()
            
            # Check for travel keywords
            travel_mentions = [keyword for keyword in travel_keywords if keyword in text]
            
            if travel_mentions:
                # Try to get corresponding timestamp
                timestamp = None
                if i < len(temporal_data):
                    timestamp = temporal_data[i]['timestamp'].isoformat()
                
                travel_indicators.append({
                    'type': 'travel_mention',
                    'keywords': travel_mentions,
                    'content': text[:150],
                    'timestamp': timestamp,
                    'confidence': len(travel_mentions) / len(travel_keywords)
                })
        
        # Detect timezone inconsistencies (might indicate travel)
        if len(temporal_data) > 5:
            hour_variance = np.var([entry['hour'] for entry in temporal_data])
            if hour_variance > 50:  # High variance in posting hours
                travel_indicators.append({
                    'type': 'timezone_inconsistency',
                    'variance': hour_variance,
                    'confidence': min(hour_variance / 100, 1.0)
                })
        
        return travel_indicators
    
    def _calculate_location_consistency(self, likely_locations: List[Dict[str, Any]]) -> float:
        """Calculate how consistent location indicators are"""
        
        if not likely_locations:
            return 0.0
        
        # If one location dominates, consistency is high
        top_confidence = likely_locations[0]['confidence'] if likely_locations else 0
        
        # Check for conflicting high-confidence locations
        high_confidence_locations = [loc for loc in likely_locations if loc['confidence'] > 0.3]
        
        if len(high_confidence_locations) <= 1:
            return min(top_confidence * 2, 1.0)  # Boost for single dominant location
        else:
            # Penalize for multiple competing locations
            return top_confidence / len(high_confidence_locations)
    
    def _determine_geographic_scope(self, likely_locations: List[Dict[str, Any]],
                                  travel_indicators: List[Dict[str, Any]]) -> str:
        """Determine overall geographic scope of activity"""
        
        if not likely_locations:
            return 'unknown'
        
        # Count location types
        country_mentions = sum(1 for loc in likely_locations if loc['location'] in self.location_keywords['countries'])
        city_mentions = sum(1 for loc in likely_locations if loc['location'] in self.location_keywords['cities'])
        
        # Factor in travel indicators
        travel_score = len(travel_indicators)
        
        if travel_score >= 3:
            return 'international'
        elif country_mentions >= 2:
            return 'national'
        elif city_mentions >= 2:
            return 'regional'
        elif likely_locations:
            return 'local'
        else:
            return 'unknown'
    
    def _extract_cultural_indicators(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Extract cultural indicators from content"""
        
        cultural_mentions = []
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for category, indicators in self.cultural_indicators.items():
                for indicator in indicators:
                    if indicator in text:
                        cultural_mentions.append(f"{category}_{indicator}")
        
        return list(set(cultural_mentions))  # Remove duplicates
    
    def _extract_work_location_hints(self, content_data: List[Dict[str, Any]]) -> List[str]:
        """Extract work location hints from content"""
        
        work_keywords = ['office', 'workplace', 'company', 'commute', 'downtown', 'business district']
        work_hints = []
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for keyword in work_keywords:
                if keyword in text:
                    work_hints.append(keyword)
        
        return list(set(work_hints))

class WorkPersonalBoundaryAnalyzer:
    """Analyzes work-personal life boundaries from social media patterns"""
    
    def __init__(self):
        self.work_keywords = [
            'meeting', 'project', 'deadline', 'client', 'office', 'work', 'colleague',
            'manager', 'team', 'presentation', 'conference', 'business', 'professional'
        ]
        
        self.personal_keywords = [
            'family', 'friends', 'weekend', 'vacation', 'hobby', 'personal', 'fun',
            'relax', 'home', 'dinner', 'party', 'movie', 'game', 'sport'
        ]
        
        self.business_hours = (9, 17)
        self.weekend_days = ['saturday', 'sunday']
    
    def analyze_work_personal_boundaries(self, content_data: List[Dict[str, Any]],
                                       temporal_data: List[Dict[str, Any]]) -> WorkPersonalBoundary:
        """Analyze work-personal life boundaries"""
        
        # Detect work hours patterns
        work_hours_detected = self._detect_work_hours(temporal_data, content_data)
        
        # Identify personal time indicators
        personal_time_indicators = self._identify_personal_time(temporal_data, content_data)
        
        # Assess boundary clarity
        boundary_clarity = self._assess_boundary_clarity(work_hours_detected, personal_time_indicators)
        
        # Calculate work-life balance score
        balance_score = self._calculate_balance_score(
            work_hours_detected, personal_time_indicators, temporal_data
        )
        
        # Calculate professional content ratio
        professional_ratio = self._calculate_professional_content_ratio(content_data)
        
        # Identify context switching patterns
        context_switching = self._identify_context_switching_patterns(content_data, temporal_data)
        
        # Extract lifestyle indicators
        lifestyle_indicators = self._extract_lifestyle_indicators(content_data)
        
        return WorkPersonalBoundary(
            work_hours_detected=work_hours_detected,
            personal_time_indicators=personal_time_indicators,
            boundary_clarity=boundary_clarity,
            work_life_balance_score=balance_score,
            professional_content_ratio=professional_ratio,
            context_switching_patterns=context_switching,
            lifestyle_indicators=lifestyle_indicators
        )
    
    def _detect_work_hours(self, temporal_data: List[Dict[str, Any]], 
                          content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect work hours from posting patterns and content"""
        
        # Analyze posting during business hours
        business_hour_posts = [
            entry for entry in temporal_data 
            if (self.business_hours[0] <= entry['hour'] <= self.business_hours[1] and 
                entry['day_of_week'] not in self.weekend_days)
        ]
        
        business_ratio = len(business_hour_posts) / len(temporal_data) if temporal_data else 0
        
        # Analyze work-related content timing
        work_content_hours = []
        for i, content in enumerate(content_data):
            text = content.get('text', content.get('content', '')).lower()
            
            if any(keyword in text for keyword in self.work_keywords):
                if i < len(temporal_data):
                    work_content_hours.append(temporal_data[i]['hour'])
        
        # Determine likely work schedule
        if work_content_hours:
            avg_work_hour = np.mean(work_content_hours)
            work_hour_range = (min(work_content_hours), max(work_content_hours))
        else:
            avg_work_hour = None
            work_hour_range = None
        
        return {
            'business_hours_activity_ratio': business_ratio,
            'work_content_hours': work_content_hours,
            'average_work_hour': avg_work_hour,
            'work_hour_range': work_hour_range,
            'likely_schedule': self._classify_work_schedule(business_ratio, work_content_hours)
        }
    
    def _identify_personal_time(self, temporal_data: List[Dict[str, Any]], 
                              content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify personal time indicators"""
        
        # Weekend activity
        weekend_posts = [
            entry for entry in temporal_data 
            if entry['day_of_week'] in self.weekend_days
        ]
        
        weekend_ratio = len(weekend_posts) / len(temporal_data) if temporal_data else 0
        
        # Evening/night activity
        evening_posts = [
            entry for entry in temporal_data 
            if entry['hour'] >= 18 or entry['hour'] <= 6
        ]
        
        evening_ratio = len(evening_posts) / len(temporal_data) if temporal_data else 0
        
        # Personal content timing
        personal_content_hours = []
        for i, content in enumerate(content_data):
            text = content.get('text', content.get('content', '')).lower()
            
            if any(keyword in text for keyword in self.personal_keywords):
                if i < len(temporal_data):
                    personal_content_hours.append(temporal_data[i]['hour'])
        
        return {
            'weekend_activity_ratio': weekend_ratio,
            'evening_activity_ratio': evening_ratio,
            'personal_content_hours': personal_content_hours,
            'personal_time_patterns': self._analyze_personal_time_patterns(personal_content_hours)
        }
    
    def _assess_boundary_clarity(self, work_hours: Dict[str, Any], 
                               personal_time: Dict[str, Any]) -> str:
        """Assess how clear the work-personal boundaries are"""
        
        business_ratio = work_hours.get('business_hours_activity_ratio', 0)
        weekend_ratio = personal_time.get('weekend_activity_ratio', 0)
        
        # Clear boundaries: mostly business hours for work, weekends for personal
        if business_ratio > 0.7 and weekend_ratio > 0.3:
            return 'clear'
        # Blended: mixed timing for both work and personal content
        elif 0.3 < business_ratio < 0.7:
            return 'blended'
        # Unclear: insufficient data or no clear pattern
        else:
            return 'unclear'
    
    def _calculate_balance_score(self, work_hours: Dict[str, Any], 
                               personal_time: Dict[str, Any],
                               temporal_data: List[Dict[str, Any]]) -> float:
        """Calculate work-life balance score"""
        
        if not temporal_data:
            return 0.5  # Neutral score for no data
        
        # Factor 1: Weekend personal time (positive for balance)
        weekend_score = personal_time.get('weekend_activity_ratio', 0)
        
        # Factor 2: Evening personal time (positive for balance)
        evening_score = personal_time.get('evening_activity_ratio', 0)
        
        # Factor 3: Not working all the time (positive for balance)
        business_ratio = work_hours.get('business_hours_activity_ratio', 0)
        work_boundary_score = 1 - min(business_ratio, 1.0)
        
        # Combine factors
        balance_score = (weekend_score + evening_score + work_boundary_score) / 3
        
        return min(balance_score, 1.0)
    
    def _calculate_professional_content_ratio(self, content_data: List[Dict[str, Any]]) -> float:
        """Calculate ratio of professional vs personal content"""
        
        if not content_data:
            return 0.0
        
        work_content_count = 0
        personal_content_count = 0
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            has_work_keywords = any(keyword in text for keyword in self.work_keywords)
            has_personal_keywords = any(keyword in text for keyword in self.personal_keywords)
            
            if has_work_keywords:
                work_content_count += 1
            if has_personal_keywords:
                personal_content_count += 1
        
        total_classified = work_content_count + personal_content_count
        
        if total_classified == 0:
            return 0.5  # Neutral if no clear indicators
        
        return work_content_count / total_classified
    
    def _identify_context_switching_patterns(self, content_data: List[Dict[str, Any]], 
                                           temporal_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns of switching between work and personal contexts"""
        
        if len(content_data) < 3:
            return []
        
        context_sequence = []
        
        # Classify each piece of content
        for i, content in enumerate(content_data):
            text = content.get('text', content.get('content', '')).lower()
            
            has_work = any(keyword in text for keyword in self.work_keywords)
            has_personal = any(keyword in text for keyword in self.personal_keywords)
            
            timestamp = temporal_data[i]['timestamp'] if i < len(temporal_data) else None
            
            if has_work and not has_personal:
                context = 'work'
            elif has_personal and not has_work:
                context = 'personal'
            else:
                context = 'neutral'
            
            context_sequence.append({
                'context': context,
                'timestamp': timestamp,
                'index': i
            })
        
        # Identify switching patterns
        switches = []
        for i in range(1, len(context_sequence)):
            prev_context = context_sequence[i-1]['context']
            curr_context = context_sequence[i]['context']
            
            if (prev_context != curr_context and 
                prev_context != 'neutral' and curr_context != 'neutral'):
                switches.append({
                    'from_context': prev_context,
                    'to_context': curr_context,
                    'timestamp': context_sequence[i]['timestamp'],
                    'switch_type': f"{prev_context}_to_{curr_context}"
                })
        
        return switches
    
    def _extract_lifestyle_indicators(self, content_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract lifestyle indicators from content"""
        
        lifestyle_categories = {
            'fitness': ['gym', 'workout', 'exercise', 'running', 'yoga'],
            'social': ['friends', 'party', 'dinner', 'drinks', 'social'],
            'family': ['family', 'kids', 'spouse', 'parents', 'home'],
            'hobbies': ['hobby', 'reading', 'music', 'art', 'photography'],
            'travel': ['travel', 'vacation', 'trip', 'explore', 'adventure'],
            'tech': ['technology', 'coding', 'programming', 'tech', 'digital']
        }
        
        lifestyle_scores = defaultdict(int)
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for category, keywords in lifestyle_categories.items():
                if any(keyword in text for keyword in keywords):
                    lifestyle_scores[category] += 1
        
        # Normalize scores
        total_content = len(content_data)
        normalized_scores = {
            category: count / total_content 
            for category, count in lifestyle_scores.items()
        }
        
        # Identify dominant lifestyle themes
        dominant_themes = sorted(
            normalized_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        return {
            'category_scores': normalized_scores,
            'dominant_themes': [theme[0] for theme in dominant_themes],
            'lifestyle_diversity': len([score for score in normalized_scores.values() if score > 0])
        }
    
    def _classify_work_schedule(self, business_ratio: float, work_hours: List[int]) -> str:
        """Classify the likely work schedule type"""
        
        if not work_hours or business_ratio < 0.2:
            return 'flexible_or_unemployed'
        elif business_ratio > 0.8:
            return 'traditional_business_hours'
        elif business_ratio > 0.5:
            return 'mostly_business_hours'
        else:
            return 'irregular_schedule'
    
    def _analyze_personal_time_patterns(self, personal_hours: List[int]) -> Dict[str, Any]:
        """Analyze personal time patterns"""
        
        if not personal_hours:
            return {'pattern': 'no_clear_pattern'}
        
        # Categorize personal time
        morning_personal = len([h for h in personal_hours if 6 <= h <= 11])
        evening_personal = len([h for h in personal_hours if 18 <= h <= 23])
        night_personal = len([h for h in personal_hours if h >= 24 or h <= 5])
        
        total_personal = len(personal_hours)
        
        patterns = {
            'morning_ratio': morning_personal / total_personal,
            'evening_ratio': evening_personal / total_personal,
            'night_ratio': night_personal / total_personal,
            'dominant_personal_time': None
        }
        
        # Determine dominant personal time
        if patterns['evening_ratio'] > 0.5:
            patterns['dominant_personal_time'] = 'evening'
        elif patterns['morning_ratio'] > 0.4:
            patterns['dominant_personal_time'] = 'morning'
        elif patterns['night_ratio'] > 0.3:
            patterns['dominant_personal_time'] = 'night'
        else:
            patterns['dominant_personal_time'] = 'mixed'
        
        return patterns

class SchedulePatternDetector:
    """Main schedule pattern detection engine"""
    
    def __init__(self):
        self.timing_analyzer = PostTimingAnalyzer()
        self.frequency_mapper = ActivityFrequencyMapper()
        self.geographic_engine = GeographicInferenceEngine()
        self.boundary_analyzer = WorkPersonalBoundaryAnalyzer()
    
    def analyze_schedule_patterns(self, social_data: Dict[str, Any]) -> ScheduleAnalysisResult:
        """Comprehensive schedule pattern analysis"""
        
        logger.info("Starting comprehensive schedule pattern detection")
        
        # Extract content and temporal data
        content_data = self._extract_content_data(social_data)
        temporal_data = self._extract_temporal_data(social_data, content_data)
        
        # Perform all schedule analyses
        post_timing = self.timing_analyzer.analyze_posting_patterns(temporal_data)
        activity_frequency = self.frequency_mapper.analyze_activity_frequency(temporal_data, content_data)
        geographic_inference = self.geographic_engine.infer_geographic_location(content_data, temporal_data)
        work_personal_boundary = self.boundary_analyzer.analyze_work_personal_boundaries(content_data, temporal_data)
        
        # Calculate overall schedule score
        overall_score = self._calculate_overall_schedule_score(
            post_timing, activity_frequency, geographic_inference, work_personal_boundary
        )
        
        # Generate behavioral insights
        behavioral_insights = self._generate_behavioral_insights(
            post_timing, activity_frequency, geographic_inference, work_personal_boundary
        )
        
        # Assess privacy implications
        privacy_implications = self._assess_privacy_implications(
            post_timing, activity_frequency, geographic_inference, work_personal_boundary
        )
        
        logger.info(f"Schedule pattern analysis completed: Overall score {overall_score:.2f}")
        
        return ScheduleAnalysisResult(
            post_timing=post_timing,
            activity_frequency=activity_frequency,
            geographic_inference=geographic_inference,
            work_personal_boundary=work_personal_boundary,
            overall_schedule_score=overall_score,
            behavioral_insights=behavioral_insights,
            privacy_implications=privacy_implications
        )
    
    def _extract_content_data(self, social_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content data from social profiles"""
        
        content_list = []
        
        # Extract from social profiles and discovered profiles
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    inferred_data = profile.get('inferred_data', {})
                    
                    # Add profile bio/description
                    if 'bio' in inferred_data:
                        content_list.append({
                            'text': inferred_data['bio'],
                            'source': 'bio',
                            'platform': profile.get('platform')
                        })
                    
                    if 'page_description' in inferred_data:
                        content_list.append({
                            'text': inferred_data['page_description'],
                            'source': 'description',
                            'platform': profile.get('platform')
                        })
                    
                    # Add any posts if available
                    if 'posts' in inferred_data:
                        for post in inferred_data['posts'][:20]:  # Limit posts
                            if isinstance(post, dict):
                                content_list.append({
                                    'text': post.get('text', ''),
                                    'timestamp': post.get('timestamp'),
                                    'source': 'post',
                                    'platform': profile.get('platform')
                                })
                            elif isinstance(post, str):
                                content_list.append({
                                    'text': post,
                                    'source': 'post',
                                    'platform': profile.get('platform')
                                })
        
        return content_list
    
    def _extract_temporal_data(self, social_data: Dict[str, Any], 
                             content_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract temporal data from social profiles and content"""
        
        temporal_list = []
        
        # Try to extract timestamps from content
        for content in content_data:
            if 'timestamp' in content and content['timestamp']:
                timestamp = self._parse_timestamp(content['timestamp'])
                if timestamp:
                    temporal_list.append({
                        'timestamp': timestamp,
                        'hour': timestamp.hour,
                        'day_of_week': timestamp.strftime('%A').lower(),
                        'month': timestamp.month,
                        'content': content.get('text', '')
                    })
        
        # If no timestamps, generate synthetic data based on profile creation dates
        if not temporal_list:
            for platform_data in ['social_profiles', 'discovered_profiles']:
                if platform_data in social_data:
                    for profile in social_data[platform_data]:
                        inferred_data = profile.get('inferred_data', {})
                        
                        # Check for account creation date
                        if 'created_at' in inferred_data:
                            timestamp = self._parse_timestamp(inferred_data['created_at'])
                            if timestamp:
                                # Generate some synthetic recent activity
                                for i in range(5):
                                    recent_time = timestamp + timedelta(
                                        days=np.random.randint(0, 365),
                                        hours=np.random.randint(0, 24)
                                    )
                                    temporal_list.append({
                                        'timestamp': recent_time,
                                        'hour': recent_time.hour,
                                        'day_of_week': recent_time.strftime('%A').lower(),
                                        'month': recent_time.month,
                                        'content': f"synthetic_activity_{i}"
                                    })
        
        return temporal_list
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string into datetime object"""
        
        if isinstance(timestamp_str, datetime):
            return timestamp_str
        
        if not isinstance(timestamp_str, str):
            return None
        
        # Common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _calculate_overall_schedule_score(self, post_timing: PostTimingPattern,
                                        activity_frequency: ActivityFrequency,
                                        geographic_inference: GeographicInference,
                                        work_personal_boundary: WorkPersonalBoundary) -> float:
        """Calculate overall schedule pattern score"""
        
        # Component scores
        timing_score = post_timing.consistency_score
        frequency_score = min(activity_frequency.daily_average / 5, 1.0)  # Normalize to daily posts
        location_score = geographic_inference.location_consistency
        boundary_score = work_personal_boundary.work_life_balance_score
        
        # Weighted average
        weights = [0.3, 0.25, 0.2, 0.25]  # timing, frequency, location, boundary
        scores = [timing_score, frequency_score, location_score, boundary_score]
        
        return sum(w * s for w, s in zip(weights, scores))
    
    def _generate_behavioral_insights(self, post_timing: PostTimingPattern,
                                    activity_frequency: ActivityFrequency,
                                    geographic_inference: GeographicInference,
                                    work_personal_boundary: WorkPersonalBoundary) -> List[str]:
        """Generate behavioral insights from schedule patterns"""
        
        insights = []
        
        # Timing insights
        if post_timing.temporal_signature:
            insights.append(f"Temporal behavior: {post_timing.temporal_signature}")
        
        if post_timing.peak_hours:
            peak_hour_str = ", ".join(f"{h}:00" for h in post_timing.peak_hours[:3])
            insights.append(f"Most active during: {peak_hour_str}")
        
        # Activity insights
        if activity_frequency.engagement_rhythm:
            insights.append(f"Engagement pattern: {activity_frequency.engagement_rhythm}")
        
        if activity_frequency.daily_average > 2:
            insights.append("High daily activity - frequent social media user")
        elif activity_frequency.daily_average < 0.5:
            insights.append("Low daily activity - occasional social media user")
        
        # Geographic insights
        if geographic_inference.geographic_scope:
            insights.append(f"Geographic scope: {geographic_inference.geographic_scope}")
        
        if geographic_inference.travel_indicators:
            insights.append(f"Travel activity detected: {len(geographic_inference.travel_indicators)} indicators")
        
        # Work-life insights
        if work_personal_boundary.boundary_clarity:
            insights.append(f"Work-life boundaries: {work_personal_boundary.boundary_clarity}")
        
        if work_personal_boundary.work_life_balance_score > 0.7:
            insights.append("Good work-life balance indicated")
        elif work_personal_boundary.work_life_balance_score < 0.3:
            insights.append("Potential work-life balance concerns")
        
        return insights
    
    def _assess_privacy_implications(self, post_timing: PostTimingPattern,
                                   activity_frequency: ActivityFrequency,
                                   geographic_inference: GeographicInference,
                                   work_personal_boundary: WorkPersonalBoundary) -> List[str]:
        """Assess privacy implications of detected patterns"""
        
        implications = []
        
        # Timing privacy risks
        if post_timing.consistency_score > 0.8:
            implications.append("⚠️ Highly predictable posting schedule may reveal daily routine")
        
        if post_timing.peak_hours and len(post_timing.peak_hours) <= 2:
            implications.append("⚠️ Narrow peak activity windows may indicate work/sleep schedule")
        
        # Location privacy risks
        if geographic_inference.location_consistency > 0.7:
            implications.append("⚠️ Consistent location indicators may reveal residence/work location")
        
        if geographic_inference.travel_indicators:
            implications.append("⚠️ Travel patterns may be trackable from posting history")
        
        # Work-life privacy risks
        if work_personal_boundary.boundary_clarity == 'clear':
            implications.append("⚠️ Clear work schedule patterns may reveal employment information")
        
        if work_personal_boundary.professional_content_ratio > 0.7:
            implications.append("⚠️ High professional content ratio may reveal career details")
        
        # Activity privacy risks
        if activity_frequency.engagement_rhythm == 'bursty':
            implications.append("⚠️ Burst activity patterns may correlate with life events")
        
        if len(implications) == 0:
            implications.append("✅ No significant privacy risks detected from schedule patterns")
        
        return implications

def create_schedule_pattern_detector():
    """Factory function to create schedule pattern detector"""
    return SchedulePatternDetector()
