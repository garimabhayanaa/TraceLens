import logging
import re
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

@dataclass
class BrandMention:
    """Brand mention analysis result"""
    brand_name: str
    mention_count: int
    sentiment_score: float
    mention_contexts: List[str]
    category: str
    price_tier: str  # 'luxury', 'premium', 'mid-range', 'budget'
    purchase_intent_score: float
    advocacy_level: str  # 'detractor', 'neutral', 'promoter'

@dataclass
class LocationPattern:
    """Location check-in pattern analysis"""
    location_name: str
    location_type: str  # 'restaurant', 'retail', 'travel', 'workplace', etc.
    frequency: int
    economic_tier: str  # 'luxury', 'upscale', 'mainstream', 'budget'
    spending_indicators: List[str]
    geographic_scope: str  # 'local', 'regional', 'national', 'international'
    social_context: str  # 'business', 'leisure', 'family', 'solo'

@dataclass
class PurchaseActivity:
    """Purchase-related social activity analysis"""
    product_category: str
    purchase_frequency: str  # 'frequent', 'occasional', 'rare'
    spending_level: str  # 'high', 'medium', 'low'
    purchase_triggers: List[str]  # 'impulse', 'research', 'recommendation', etc.
    brand_loyalty_score: float
    price_sensitivity: str  # 'high', 'medium', 'low'
    shopping_behavior: str  # 'early_adopter', 'mainstream', 'bargain_hunter'

@dataclass
class ProfessionalNetwork:
    """Professional network analysis"""
    industry_connections: Dict[str, int]
    seniority_level: str  # 'entry', 'mid', 'senior', 'executive'
    networking_activity: str  # 'active', 'moderate', 'passive'
    professional_influence: float  # 0-1 score
    career_trajectory: str  # 'ascending', 'stable', 'transitioning'
    industry_engagement: Dict[str, float]
    thought_leadership_score: float

@dataclass
class EconomicProfile:
    """Comprehensive economic profile"""
    estimated_income_bracket: str
    spending_capacity: str
    economic_lifestyle: str
    brand_affinity_tier: str
    purchase_decision_style: str
    economic_mobility_indicators: List[str]
    financial_sophistication: str
    economic_priorities: Dict[str, float]

@dataclass
class EconomicIndicatorsResult:
    """Complete economic indicators analysis"""
    brand_mentions: List[BrandMention]
    location_patterns: List[LocationPattern]
    purchase_activities: List[PurchaseActivity]
    professional_network: ProfessionalNetwork
    economic_profile: EconomicProfile
    economic_risk_score: float
    economic_insights: List[str]
    privacy_economic_implications: List[str]

class BrandMentionAnalyzer:
    """Analyzes brand mentions and brand sentiment"""
    
    def __init__(self):
        self.brand_database = {
            # Luxury brands
            'luxury': {
                'fashion': ['louis vuitton', 'gucci', 'prada', 'hermès', 'chanel', 'dior'],
                'automotive': ['ferrari', 'lamborghini', 'rolls royce', 'bentley', 'maserati'],
                'technology': ['vertu', 'goldvish', 'tag heuer', 'rolex', 'patek philippe'],
                'hospitality': ['four seasons', 'ritz carlton', 'mandarin oriental', 'bulgari hotels']
            },
            # Premium brands
            'premium': {
                'fashion': ['michael kors', 'coach', 'kate spade', 'tory burch', 'hugo boss'],
                'automotive': ['bmw', 'mercedes', 'audi', 'lexus', 'tesla'],
                'technology': ['apple', 'dyson', 'bang olufsen', 'bose'],
                'hospitality': ['marriott', 'hyatt', 'westin', 'sheraton']
            },
            # Mid-range brands
            'mid-range': {
                'fashion': ['zara', 'h&m', 'uniqlo', 'gap', 'banana republic'],
                'automotive': ['honda', 'toyota', 'volkswagen', 'mazda', 'subaru'],
                'technology': ['samsung', 'lg', 'sony', 'microsoft', 'dell'],
                'hospitality': ['holiday inn', 'best western', 'hilton garden inn']
            },
            # Budget brands
            'budget': {
                'fashion': ['walmart', 'target', 'old navy', 'forever 21'],
                'automotive': ['kia', 'hyundai', 'nissan', 'chevrolet'],
                'technology': ['xiaomi', 'huawei', 'asus', 'acer'],
                'hospitality': ['motel 6', 'super 8', 'days inn']
            }
        }
        
        self.purchase_intent_keywords = [
            'bought', 'purchased', 'ordered', 'shopping for', 'looking to buy',
            'considering', 'comparing', 'want to get', 'need to buy', 'investing in'
        ]
        
        self.advocacy_keywords = {
            'positive': ['love', 'amazing', 'recommend', 'excellent', 'fantastic', 'perfect'],
            'negative': ['hate', 'terrible', 'awful', 'disappointed', 'waste', 'regret'],
            'neutral': ['okay', 'decent', 'average', 'fine', 'acceptable']
        }
    
    def analyze_brand_mentions(self, content_data: List[Dict[str, Any]]) -> List[BrandMention]:
        """Analyze brand mentions across content"""
        
        if not content_data:
            return []
        
        brand_mentions_data = defaultdict(lambda: {
            'count': 0,
            'contexts': [],
            'sentiments': [],
            'purchase_intents': [],
            'advocacy_indicators': []
        })
        
        # Extract brand mentions from content
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Check for each brand
            for price_tier, categories in self.brand_database.items():
                for category, brands in categories.items():
                    for brand in brands:
                        if brand in text:
                            key = (brand, category, price_tier)
                            brand_mentions_data[key]['count'] += 1
                            brand_mentions_data[key]['contexts'].append(text[:150])
                            
                            # Analyze sentiment around brand mention
                            sentiment = self._analyze_brand_sentiment(text, brand)
                            brand_mentions_data[key]['sentiments'].append(sentiment)
                            
                            # Check for purchase intent
                            purchase_intent = self._detect_purchase_intent(text, brand)
                            brand_mentions_data[key]['purchase_intents'].append(purchase_intent)
                            
                            # Check for advocacy indicators
                            advocacy = self._detect_advocacy_level(text, brand)
                            brand_mentions_data[key]['advocacy_indicators'].append(advocacy)
        
        # Create brand mention objects
        brand_mentions = []
        for (brand_name, category, price_tier), data in brand_mentions_data.items():
            if data['count'] >= 1:  # Include all mentions
                avg_sentiment = np.mean(data['sentiments']) if data['sentiments'] else 0.0
                avg_purchase_intent = np.mean(data['purchase_intents']) if data['purchase_intents'] else 0.0
                
                # Determine advocacy level
                advocacy_scores = [score for score in data['advocacy_indicators'] if score != 0]
                if advocacy_scores:
                    avg_advocacy = np.mean(advocacy_scores)
                    if avg_advocacy > 0.3:
                        advocacy_level = 'promoter'
                    elif avg_advocacy < -0.3:
                        advocacy_level = 'detractor'
                    else:
                        advocacy_level = 'neutral'
                else:
                    advocacy_level = 'neutral'
                
                brand_mention = BrandMention(
                    brand_name=brand_name,
                    mention_count=data['count'],
                    sentiment_score=avg_sentiment,
                    mention_contexts=data['contexts'][:3],  # Top 3 contexts
                    category=category,
                    price_tier=price_tier,
                    purchase_intent_score=avg_purchase_intent,
                    advocacy_level=advocacy_level
                )
                
                brand_mentions.append(brand_mention)
        
        # Sort by mention count and sentiment
        brand_mentions.sort(key=lambda x: (x.mention_count, x.sentiment_score), reverse=True)
        
        return brand_mentions
    
    def _analyze_brand_sentiment(self, text: str, brand: str) -> float:
        """Analyze sentiment around brand mention"""
        
        # Find brand position and analyze surrounding context
        brand_pos = text.find(brand)
        if brand_pos == -1:
            return 0.0
        
        # Get context around brand mention
        start = max(0, brand_pos - 50)
        end = min(len(text), brand_pos + len(brand) + 50)
        context = text[start:end]
        
        # Simple sentiment analysis based on keywords
        positive_score = sum(1 for word in self.advocacy_keywords['positive'] if word in context)
        negative_score = sum(1 for word in self.advocacy_keywords['negative'] if word in context)
        
        if positive_score + negative_score == 0:
            return 0.0
        
        return (positive_score - negative_score) / (positive_score + negative_score)
    
    def _detect_purchase_intent(self, text: str, brand: str) -> float:
        """Detect purchase intent for a brand"""
        
        intent_score = 0.0
        text_lower = text.lower()
        
        for keyword in self.purchase_intent_keywords:
            if keyword in text_lower:
                # Check if keyword is near the brand mention
                brand_pos = text_lower.find(brand)
                keyword_pos = text_lower.find(keyword)
                
                if brand_pos != -1 and keyword_pos != -1:
                    distance = abs(brand_pos - keyword_pos)
                    if distance <= 100:  # Within 100 characters
                        intent_score += 1.0 - (distance / 100)  # Closer = higher score
        
        return min(intent_score, 1.0)
    
    def _detect_advocacy_level(self, text: str, brand: str) -> float:
        """Detect advocacy level for a brand"""
        
        brand_pos = text.find(brand)
        if brand_pos == -1:
            return 0.0
        
        # Get context around brand
        start = max(0, brand_pos - 30)
        end = min(len(text), brand_pos + len(brand) + 30)
        context = text[start:end]
        
        advocacy_score = 0.0
        
        # Check for positive advocacy
        for word in self.advocacy_keywords['positive']:
            if word in context:
                advocacy_score += 0.3
        
        # Check for negative advocacy
        for word in self.advocacy_keywords['negative']:
            if word in context:
                advocacy_score -= 0.3
        
        return max(-1.0, min(1.0, advocacy_score))

class LocationPatternAnalyzer:
    """Analyzes location check-in patterns and economic implications"""
    
    def __init__(self):
        self.location_types = {
            'luxury': {
                'restaurants': ['michelin', 'fine dining', 'tasting menu', 'sommelier'],
                'retail': ['boutique', 'flagship store', 'luxury mall', 'rodeo drive'],
                'travel': ['five star', 'resort', 'spa', 'private jet', 'first class'],
                'entertainment': ['vip', 'premium box', 'private club', 'exclusive']
            },
            'upscale': {
                'restaurants': ['steakhouse', 'wine bar', 'gastropub', 'craft cocktails'],
                'retail': ['department store', 'designer outlet', 'specialty store'],
                'travel': ['business class', 'boutique hotel', 'premium resort'],
                'entertainment': ['theater', 'concert hall', 'art gallery', 'wine tasting']
            },
            'mainstream': {
                'restaurants': ['chain restaurant', 'casual dining', 'sports bar'],
                'retail': ['shopping center', 'mall', 'big box store'],
                'travel': ['economy class', 'hotel', 'vacation rental'],
                'entertainment': ['movie theater', 'amusement park', 'sports event']
            },
            'budget': {
                'restaurants': ['fast food', 'food court', 'buffet', 'drive through'],
                'retail': ['discount store', 'outlet mall', 'thrift store'],
                'travel': ['budget airline', 'motel', 'hostel', 'camping'],
                'entertainment': ['free event', 'public park', 'community center']
            }
        }
        
        self.spending_keywords = [
            'expensive', 'cheap', 'affordable', 'pricey', 'worth it',
            'overpriced', 'bargain', 'deal', 'splurge', 'invest'
        ]
    
    def analyze_location_patterns(self, content_data: List[Dict[str, Any]]) -> List[LocationPattern]:
        """Analyze location patterns from content"""
        
        if not content_data:
            return []
        
        location_data = defaultdict(lambda: {
            'frequency': 0,
            'contexts': [],
            'spending_indicators': [],
            'social_contexts': []
        })
        
        # Extract location mentions
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Look for location indicators
            locations = self._extract_location_mentions(text)
            
            for location_info in locations:
                location_name = location_info['name']
                location_type = location_info['type']
                economic_tier = location_info['tier']
                
                key = (location_name, location_type, economic_tier)
                location_data[key]['frequency'] += 1
                location_data[key]['contexts'].append(text[:100])
                
                # Analyze spending indicators
                spending_indicators = self._extract_spending_indicators(text)
                location_data[key]['spending_indicators'].extend(spending_indicators)
                
                # Analyze social context
                social_context = self._determine_social_context(text)
                location_data[key]['social_contexts'].append(social_context)
        
        # Create location pattern objects
        location_patterns = []
        for (location_name, location_type, economic_tier), data in location_data.items():
            if data['frequency'] >= 1:
                # Determine geographic scope
                geographic_scope = self._determine_geographic_scope(location_name, data['contexts'])
                
                # Determine predominant social context
                social_contexts = [ctx for ctx in data['social_contexts'] if ctx != 'unknown']
                predominant_social_context = max(set(social_contexts), key=social_contexts.count) if social_contexts else 'unknown'
                
                location_pattern = LocationPattern(
                    location_name=location_name,
                    location_type=location_type,
                    frequency=data['frequency'],
                    economic_tier=economic_tier,
                    spending_indicators=list(set(data['spending_indicators'])),
                    geographic_scope=geographic_scope,
                    social_context=predominant_social_context
                )
                
                location_patterns.append(location_pattern)
        
        # Sort by frequency
        location_patterns.sort(key=lambda x: x.frequency, reverse=True)
        
        return location_patterns
    
    def _extract_location_mentions(self, text: str) -> List[Dict[str, str]]:
        """Extract location mentions from text"""
        
        locations = []
        
        # Check against location type keywords
        for tier, categories in self.location_types.items():
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in text:
                        locations.append({
                            'name': keyword,
                            'type': category,
                            'tier': tier
                        })
        
        # Look for specific location names (simplified)
        location_patterns = [
            r'\b\w+\s+(restaurant|bar|hotel|store|mall|club)\b',
            r'\bat\s+(\w+(?:\s+\w+)?)\b',
            r'\bvisiting\s+(\w+(?:\s+\w+)?)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    location_name = match[0] if match[0] else match[1]
                else:
                    location_name = match
                
                if len(location_name) > 2:  # Filter out short matches
                    locations.append({
                        'name': location_name,
                        'type': 'general',
                        'tier': 'mainstream'  # Default tier
                    })
        
        return locations
    
    def _extract_spending_indicators(self, text: str) -> List[str]:
        """Extract spending indicators from text"""
        
        indicators = []
        
        for keyword in self.spending_keywords:
            if keyword in text:
                indicators.append(keyword)
        
        # Look for price mentions
        price_patterns = [
            r'\$\d+',
            r'\d+\s*dollars?',
            r'\d+\s*bucks?',
            r'cost\s+\$?\d+',
            r'paid\s+\$?\d+'
        ]
        
        for pattern in price_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                indicators.append('price_mention')
        
        return indicators
    
    def _determine_social_context(self, text: str) -> str:
        """Determine social context of location visit"""
        
        business_keywords = ['meeting', 'client', 'work', 'business', 'conference']
        family_keywords = ['family', 'kids', 'children', 'parents', 'relatives']
        social_keywords = ['friends', 'party', 'celebration', 'group', 'together']
        solo_keywords = ['alone', 'myself', 'solo', 'by myself']
        
        if any(keyword in text for keyword in business_keywords):
            return 'business'
        elif any(keyword in text for keyword in family_keywords):
            return 'family'
        elif any(keyword in text for keyword in social_keywords):
            return 'leisure'
        elif any(keyword in text for keyword in solo_keywords):
            return 'solo'
        else:
            return 'unknown'
    
    def _determine_geographic_scope(self, location_name: str, contexts: List[str]) -> str:
        """Determine geographic scope of location activity"""
        
        international_indicators = ['international', 'abroad', 'overseas', 'foreign']
        national_indicators = ['across the country', 'nationwide', 'different state']
        regional_indicators = ['region', 'area', 'nearby cities']
        
        combined_text = ' '.join(contexts).lower()
        
        if any(indicator in combined_text for indicator in international_indicators):
            return 'international'
        elif any(indicator in combined_text for indicator in national_indicators):
            return 'national'
        elif any(indicator in combined_text for indicator in regional_indicators):
            return 'regional'
        else:
            return 'local'

class PurchaseActivityAnalyzer:
    """Analyzes purchase-related social media activity"""
    
    def __init__(self):
        self.product_categories = {
            'technology': ['phone', 'laptop', 'tablet', 'gadget', 'electronics', 'software'],
            'fashion': ['clothes', 'shoes', 'bag', 'dress', 'shirt', 'jacket', 'accessories'],
            'automotive': ['car', 'vehicle', 'truck', 'motorcycle', 'auto'],
            'home': ['furniture', 'appliance', 'decor', 'kitchen', 'bedroom', 'house'],
            'beauty': ['makeup', 'skincare', 'cosmetics', 'beauty', 'fragrance'],
            'food': ['restaurant', 'food', 'dining', 'grocery', 'meal'],
            'travel': ['flight', 'hotel', 'vacation', 'trip', 'travel', 'booking'],
            'entertainment': ['movie', 'game', 'book', 'music', 'concert', 'show']
        }
        
        self.purchase_indicators = {
            'immediate': ['bought', 'purchased', 'ordered', 'just got'],
            'intent': ['want to buy', 'planning to get', 'looking for', 'need to purchase'],
            'research': ['comparing', 'reviews', 'researching', 'considering'],
            'recommendation': ['recommend', 'suggest', 'should buy', 'worth getting']
        }
        
        self.price_sensitivity_indicators = {
            'high': ['cheap', 'discount', 'sale', 'deal', 'bargain', 'affordable'],
            'low': ['expensive', 'premium', 'luxury', 'splurge', 'invest', 'worth it'],
            'medium': ['reasonable', 'fair price', 'good value', 'moderate']
        }
    
    def analyze_purchase_activities(self, content_data: List[Dict[str, Any]]) -> List[PurchaseActivity]:
        """Analyze purchase-related activities"""
        
        if not content_data:
            return []
        
        category_activities = defaultdict(lambda: {
            'purchase_mentions': [],
            'purchase_types': [],
            'price_sensitivity_indicators': [],
            'brand_mentions': [],
            'frequency_indicators': []
        })
        
        # Analyze each piece of content
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            # Check for product categories
            for category, keywords in self.product_categories.items():
                if any(keyword in text for keyword in keywords):
                    
                    # Analyze purchase indicators
                    purchase_type = self._detect_purchase_type(text)
                    if purchase_type:
                        category_activities[category]['purchase_types'].append(purchase_type)
                        category_activities[category]['purchase_mentions'].append(text[:100])
                    
                    # Analyze price sensitivity
                    price_sensitivity = self._detect_price_sensitivity(text)
                    if price_sensitivity:
                        category_activities[category]['price_sensitivity_indicators'].append(price_sensitivity)
                    
                    # Check for brand mentions
                    brands = self._extract_brands_from_text(text, category)
                    category_activities[category]['brand_mentions'].extend(brands)
                    
                    # Frequency indicators
                    frequency_indicator = self._detect_frequency_indicator(text)
                    if frequency_indicator:
                        category_activities[category]['frequency_indicators'].append(frequency_indicator)
        
        # Create purchase activity objects
        purchase_activities = []
        for category, data in category_activities.items():
            if data['purchase_mentions']:
                # Calculate metrics
                purchase_frequency = self._calculate_purchase_frequency(data['frequency_indicators'])
                spending_level = self._calculate_spending_level(data['price_sensitivity_indicators'])
                purchase_triggers = self._identify_purchase_triggers(data['purchase_types'])
                brand_loyalty_score = self._calculate_brand_loyalty(data['brand_mentions'])
                price_sensitivity = self._determine_price_sensitivity(data['price_sensitivity_indicators'])
                shopping_behavior = self._determine_shopping_behavior(data)
                
                purchase_activity = PurchaseActivity(
                    product_category=category,
                    purchase_frequency=purchase_frequency,
                    spending_level=spending_level,
                    purchase_triggers=purchase_triggers,
                    brand_loyalty_score=brand_loyalty_score,
                    price_sensitivity=price_sensitivity,
                    shopping_behavior=shopping_behavior
                )
                
                purchase_activities.append(purchase_activity)
        
        return purchase_activities
    
    def _detect_purchase_type(self, text: str) -> Optional[str]:
        """Detect type of purchase activity"""
        
        for purchase_type, keywords in self.purchase_indicators.items():
            if any(keyword in text for keyword in keywords):
                return purchase_type
        
        return None
    
    def _detect_price_sensitivity(self, text: str) -> Optional[str]:
        """Detect price sensitivity from text"""
        
        for sensitivity_level, keywords in self.price_sensitivity_indicators.items():
            if any(keyword in text for keyword in keywords):
                return sensitivity_level
        
        return None
    
    def _extract_brands_from_text(self, text: str, category: str) -> List[str]:
        """Extract brand mentions from text for a specific category"""
        
        # This would ideally use the brand database from BrandMentionAnalyzer
        # For now, return a simplified approach
        brand_indicators = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', text)
        return brand_indicators[:3]  # Return top 3 potential brands
    
    def _detect_frequency_indicator(self, text: str) -> Optional[str]:
        """Detect purchase frequency indicators"""
        
        frequency_keywords = {
            'frequent': ['always', 'frequently', 'often', 'regularly', 'every week'],
            'occasional': ['sometimes', 'occasionally', 'once in a while', 'monthly'],
            'rare': ['rarely', 'seldom', 'hardly ever', 'once a year']
        }
        
        for frequency, keywords in frequency_keywords.items():
            if any(keyword in text for keyword in keywords):
                return frequency
        
        return None
    
    def _calculate_purchase_frequency(self, indicators: List[str]) -> str:
        """Calculate overall purchase frequency"""
        
        if not indicators:
            return 'occasional'
        
        frequency_counts = Counter(indicators)
        return frequency_counts.most_common(1)[0][0] if frequency_counts else 'occasional'
    
    def _calculate_spending_level(self, price_indicators: List[str]) -> str:
        """Calculate spending level from price sensitivity indicators"""
        
        if not price_indicators:
            return 'medium'
        
        high_spender_count = price_indicators.count('low')  # Low price sensitivity = high spending
        budget_count = price_indicators.count('high')      # High price sensitivity = low spending
        medium_count = price_indicators.count('medium')
        
        if high_spender_count > budget_count and high_spender_count > medium_count:
            return 'high'
        elif budget_count > high_spender_count and budget_count > medium_count:
            return 'low'
        else:
            return 'medium'
    
    def _identify_purchase_triggers(self, purchase_types: List[str]) -> List[str]:
        """Identify common purchase triggers"""
        
        trigger_counts = Counter(purchase_types)
        return [trigger for trigger, count in trigger_counts.most_common(3)]
    
    def _calculate_brand_loyalty(self, brand_mentions: List[str]) -> float:
        """Calculate brand loyalty score"""
        
        if not brand_mentions:
            return 0.0
        
        brand_counts = Counter(brand_mentions)
        total_mentions = len(brand_mentions)
        unique_brands = len(brand_counts)
        
        if unique_brands == 0:
            return 0.0
        
        # High loyalty = few brands mentioned frequently
        max_brand_frequency = max(brand_counts.values())
        loyalty_score = max_brand_frequency / total_mentions
        
        return loyalty_score
    
    def _determine_price_sensitivity(self, indicators: List[str]) -> str:
        """Determine overall price sensitivity"""
        
        if not indicators:
            return 'medium'
        
        sensitivity_counts = Counter(indicators)
        return sensitivity_counts.most_common(1)[0][0] if sensitivity_counts else 'medium'
    
    def _determine_shopping_behavior(self, data: Dict[str, List[str]]) -> str:
        """Determine shopping behavior pattern"""
        
        purchase_types = data['purchase_types']
        
        if 'immediate' in purchase_types and purchase_types.count('immediate') > len(purchase_types) * 0.6:
            return 'impulse_buyer'
        elif 'research' in purchase_types and purchase_types.count('research') > len(purchase_types) * 0.4:
            return 'research_driven'
        elif 'recommendation' in purchase_types:
            return 'socially_influenced'
        elif any('high' in indicator for indicator in data['price_sensitivity_indicators']):
            return 'bargain_hunter'
        else:
            return 'mainstream_shopper'

class ProfessionalNetworkAnalyzer:
    """Analyzes professional network and career indicators"""
    
    def __init__(self):
        self.industry_keywords = {
            'technology': ['software', 'tech', 'programming', 'coding', 'development', 'ai', 'machine learning'],
            'finance': ['banking', 'finance', 'investment', 'trading', 'accounting', 'wealth management'],
            'healthcare': ['medical', 'healthcare', 'doctor', 'nurse', 'pharmaceutical', 'biotech'],
            'education': ['education', 'teaching', 'academic', 'university', 'research', 'professor'],
            'marketing': ['marketing', 'advertising', 'branding', 'social media', 'pr', 'communications'],
            'consulting': ['consulting', 'strategy', 'management', 'advisory', 'transformation'],
            'legal': ['legal', 'law', 'attorney', 'lawyer', 'compliance', 'regulatory'],
            'retail': ['retail', 'sales', 'customer service', 'merchandising', 'e-commerce'],
            'manufacturing': ['manufacturing', 'production', 'supply chain', 'operations', 'logistics'],
            'real_estate': ['real estate', 'property', 'commercial', 'residential', 'development']
        }
        
        self.seniority_indicators = {
            'executive': ['ceo', 'cto', 'cfo', 'president', 'vp', 'vice president', 'executive', 'chief'],
            'senior': ['senior', 'principal', 'lead', 'manager', 'director', 'head of'],
            'mid': ['specialist', 'analyst', 'coordinator', 'associate', 'consultant'],
            'entry': ['intern', 'junior', 'assistant', 'trainee', 'entry level']
        }
        
        self.networking_indicators = [
            'conference', 'networking', 'industry event', 'professional development',
            'thought leadership', 'speaking', 'panel', 'keynote', 'webinar'
        ]
    
    def analyze_professional_network(self, content_data: List[Dict[str, Any]], 
                                   social_data: Dict[str, Any]) -> ProfessionalNetwork:
        """Analyze professional network characteristics"""
        
        if not content_data:
            return self._create_empty_professional_network()
        
        # Analyze industry connections
        industry_connections = self._analyze_industry_connections(content_data)
        
        # Determine seniority level
        seniority_level = self._determine_seniority_level(content_data, social_data)
        
        # Analyze networking activity
        networking_activity = self._analyze_networking_activity(content_data)
        
        # Calculate professional influence
        professional_influence = self._calculate_professional_influence(content_data, social_data)
        
        # Determine career trajectory
        career_trajectory = self._determine_career_trajectory(content_data)
        
        # Analyze industry engagement
        industry_engagement = self._analyze_industry_engagement(content_data)
        
        # Calculate thought leadership score
        thought_leadership_score = self._calculate_thought_leadership_score(content_data)
        
        return ProfessionalNetwork(
            industry_connections=industry_connections,
            seniority_level=seniority_level,
            networking_activity=networking_activity,
            professional_influence=professional_influence,
            career_trajectory=career_trajectory,
            industry_engagement=industry_engagement,
            thought_leadership_score=thought_leadership_score
        )
    
    def _analyze_industry_connections(self, content_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze industry connections from content"""
        
        industry_mentions = defaultdict(int)
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for industry, keywords in self.industry_keywords.items():
                if any(keyword in text for keyword in keywords):
                    industry_mentions[industry] += 1
        
        return dict(industry_mentions)
    
    def _determine_seniority_level(self, content_data: List[Dict[str, Any]], 
                                 social_data: Dict[str, Any]) -> str:
        """Determine professional seniority level"""
        
        seniority_indicators_found = []
        
        # Check content for seniority indicators
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for level, indicators in self.seniority_indicators.items():
                if any(indicator in text for indicator in indicators):
                    seniority_indicators_found.append(level)
        
        # Check social profiles for title information
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    bio = profile.get('inferred_data', {}).get('bio', '').lower()
                    page_title = profile.get('page_title', '').lower()
                    
                    for level, indicators in self.seniority_indicators.items():
                        if any(indicator in bio or indicator in page_title for indicator in indicators):
                            seniority_indicators_found.append(level)
        
        if not seniority_indicators_found:
            return 'unknown'
        
        # Return most senior level found
        level_hierarchy = ['executive', 'senior', 'mid', 'entry']
        for level in level_hierarchy:
            if level in seniority_indicators_found:
                return level
        
        return 'mid'  # Default
    
    def _analyze_networking_activity(self, content_data: List[Dict[str, Any]]) -> str:
        """Analyze networking activity level"""
        
        networking_mentions = 0
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            if any(indicator in text for indicator in self.networking_indicators):
                networking_mentions += 1
        
        total_content = len(content_data)
        networking_ratio = networking_mentions / total_content if total_content > 0 else 0
        
        if networking_ratio > 0.3:
            return 'active'
        elif networking_ratio > 0.1:
            return 'moderate'
        else:
            return 'passive'
    
    def _calculate_professional_influence(self, content_data: List[Dict[str, Any]], 
                                        social_data: Dict[str, Any]) -> float:
        """Calculate professional influence score"""
        
        influence_score = 0.0
        
        # Factor 1: Follower count (if available)
        total_followers = 0
        for platform_data in ['social_profiles', 'discovered_profiles']:
            if platform_data in social_data:
                for profile in social_data[platform_data]:
                    followers = profile.get('inferred_data', {}).get('followers', 0)
                    if isinstance(followers, int):
                        total_followers += followers
        
        # Normalize follower count (log scale)
        if total_followers > 0:
            influence_score += min(np.log10(total_followers) / 6, 0.4)  # Max 0.4 from followers
        
        # Factor 2: Professional content quality
        professional_content_count = 0
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            professional_keywords = ['industry', 'business', 'strategy', 'insights', 'analysis']
            if any(keyword in text for keyword in professional_keywords):
                professional_content_count += 1
        
        if content_data:
            professional_ratio = professional_content_count / len(content_data)
            influence_score += professional_ratio * 0.3  # Max 0.3 from content quality
        
        # Factor 3: Networking activity
        networking_mentions = sum(1 for content in content_data 
                                if any(indicator in content.get('text', '').lower() 
                                     for indicator in self.networking_indicators))
        
        if content_data:
            networking_ratio = networking_mentions / len(content_data)
            influence_score += networking_ratio * 0.3  # Max 0.3 from networking
        
        return min(influence_score, 1.0)
    
    def _determine_career_trajectory(self, content_data: List[Dict[str, Any]]) -> str:
        """Determine career trajectory from content"""
        
        career_keywords = {
            'ascending': ['promotion', 'new role', 'career growth', 'advancement', 'excited to announce'],
            'transitioning': ['career change', 'new industry', 'pivot', 'transition', 'exploring'],
            'stable': ['years with', 'continuing', 'established', 'experienced in']
        }
        
        trajectory_indicators = []
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            for trajectory, keywords in career_keywords.items():
                if any(keyword in text for keyword in keywords):
                    trajectory_indicators.append(trajectory)
        
        if not trajectory_indicators:
            return 'stable'
        
        # Return most common trajectory
        trajectory_counts = Counter(trajectory_indicators)
        return trajectory_counts.most_common(1)[0][0]
    
    def _analyze_industry_engagement(self, content_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze engagement level with different industries"""
        
        industry_engagement = {}
        
        for industry, keywords in self.industry_keywords.items():
            engagement_score = 0.0
            mentions = 0
            
            for content in content_data:
                text = content.get('text', content.get('content', '')).lower()
                
                if any(keyword in text for keyword in keywords):
                    mentions += 1
                    # Higher score for longer, more detailed content
                    content_length = len(text.split())
                    engagement_score += min(content_length / 100, 1.0)
            
            if mentions > 0:
                industry_engagement[industry] = engagement_score / mentions
        
        return industry_engagement
    
    def _calculate_thought_leadership_score(self, content_data: List[Dict[str, Any]]) -> float:
        """Calculate thought leadership score"""
        
        thought_leadership_indicators = [
            'opinion', 'insights', 'analysis', 'perspective', 'thoughts on',
            'future of', 'trends', 'predictions', 'industry outlook'
        ]
        
        leadership_content = 0
        
        for content in content_data:
            text = content.get('text', content.get('content', '')).lower()
            
            if any(indicator in text for indicator in thought_leadership_indicators):
                leadership_content += 1
        
        if not content_data:
            return 0.0
        
        return leadership_content / len(content_data)
    
    def _create_empty_professional_network(self) -> ProfessionalNetwork:
        """Create empty professional network for no data case"""
        
        return ProfessionalNetwork(
            industry_connections={},
            seniority_level='unknown',
            networking_activity='passive',
            professional_influence=0.0,
            career_trajectory='stable',
            industry_engagement={},
            thought_leadership_score=0.0
        )

class EconomicIndicatorsAnalyzer:
    """Main economic indicators analyzer combining all components"""
    
    def __init__(self):
        self.brand_analyzer = BrandMentionAnalyzer()
        self.location_analyzer = LocationPatternAnalyzer()
        self.purchase_analyzer = PurchaseActivityAnalyzer()
        self.professional_analyzer = ProfessionalNetworkAnalyzer()
    
    def analyze_economic_indicators(self, social_data: Dict[str, Any]) -> EconomicIndicatorsResult:
        """Comprehensive economic indicators analysis"""
        
        logger.info("Starting comprehensive economic indicators analysis")
        
        # Extract content data
        content_data = self._extract_content_data(social_data)
        
        if not content_data:
            return self._create_empty_economic_analysis()
        
        # Perform all analyses
        brand_mentions = self.brand_analyzer.analyze_brand_mentions(content_data)
        location_patterns = self.location_analyzer.analyze_location_patterns(content_data)
        purchase_activities = self.purchase_analyzer.analyze_purchase_activities(content_data)
        professional_network = self.professional_analyzer.analyze_professional_network(content_data, social_data)
        
        # Generate comprehensive economic profile
        economic_profile = self._generate_economic_profile(
            brand_mentions, location_patterns, purchase_activities, professional_network
        )
        
        # Calculate economic risk score
        economic_risk_score = self._calculate_economic_risk_score(
            brand_mentions, location_patterns, purchase_activities
        )
        
        # Generate economic insights
        economic_insights = self._generate_economic_insights(
            brand_mentions, location_patterns, purchase_activities, professional_network, economic_profile
        )
        
        # Assess privacy implications
        privacy_implications = self._assess_privacy_economic_implications(
            brand_mentions, location_patterns, purchase_activities, professional_network
        )
        
        logger.info(f"Economic indicators analysis completed: "
                   f"Brands: {len(brand_mentions)}, "
                   f"Locations: {len(location_patterns)}, "
                   f"Purchases: {len(purchase_activities)}")
        
        return EconomicIndicatorsResult(
            brand_mentions=brand_mentions,
            location_patterns=location_patterns,
            purchase_activities=purchase_activities,
            professional_network=professional_network,
            economic_profile=economic_profile,
            economic_risk_score=economic_risk_score,
            economic_insights=economic_insights,
            privacy_economic_implications=privacy_implications
        )
    
    def _extract_content_data(self, social_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract content data from social profiles"""
        
        content_list = []
        
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
                    
                    # Add posts if available
                    if 'posts' in inferred_data:
                        for post in inferred_data['posts'][:15]:  # Limit posts
                            if isinstance(post, dict):
                                content_list.append({
                                    'text': post.get('text', ''),
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
    
    def _generate_economic_profile(self, brand_mentions: List[BrandMention],
                                 location_patterns: List[LocationPattern],
                                 purchase_activities: List[PurchaseActivity],
                                 professional_network: ProfessionalNetwork) -> EconomicProfile:
        """Generate comprehensive economic profile"""
        
        # Estimate income bracket
        estimated_income_bracket = self._estimate_income_bracket(
            brand_mentions, location_patterns, professional_network
        )
        
        # Determine spending capacity
        spending_capacity = self._determine_spending_capacity(
            brand_mentions, location_patterns, purchase_activities
        )
        
        # Classify economic lifestyle
        economic_lifestyle = self._classify_economic_lifestyle(
            brand_mentions, location_patterns, purchase_activities
        )
        
        # Determine brand affinity tier
        brand_affinity_tier = self._determine_brand_affinity_tier(brand_mentions)
        
        # Classify purchase decision style
        purchase_decision_style = self._classify_purchase_decision_style(purchase_activities)
        
        # Identify economic mobility indicators
        economic_mobility_indicators = self._identify_economic_mobility_indicators(
            professional_network, purchase_activities
        )
        
        # Assess financial sophistication
        financial_sophistication = self._assess_financial_sophistication(
            professional_network, brand_mentions, purchase_activities
        )
        
        # Determine economic priorities
        economic_priorities = self._determine_economic_priorities(
            purchase_activities, brand_mentions, location_patterns
        )
        
        return EconomicProfile(
            estimated_income_bracket=estimated_income_bracket,
            spending_capacity=spending_capacity,
            economic_lifestyle=economic_lifestyle,
            brand_affinity_tier=brand_affinity_tier,
            purchase_decision_style=purchase_decision_style,
            economic_mobility_indicators=economic_mobility_indicators,
            financial_sophistication=financial_sophistication,
            economic_priorities=economic_priorities
        )
    
    def _estimate_income_bracket(self, brand_mentions: List[BrandMention],
                               location_patterns: List[LocationPattern],
                               professional_network: ProfessionalNetwork) -> str:
        """Estimate income bracket based on various indicators"""
        
        income_score = 0.0
        
        # Brand mentions influence
        luxury_brand_count = sum(1 for brand in brand_mentions if brand.price_tier == 'luxury')
        premium_brand_count = sum(1 for brand in brand_mentions if brand.price_tier == 'premium')
        
        if luxury_brand_count > 0:
            income_score += 0.4
        elif premium_brand_count > 0:
            income_score += 0.2
        
        # Location patterns influence
        luxury_location_count = sum(1 for loc in location_patterns if loc.economic_tier == 'luxury')
        upscale_location_count = sum(1 for loc in location_patterns if loc.economic_tier == 'upscale')
        
        if luxury_location_count > 0:
            income_score += 0.3
        elif upscale_location_count > 0:
            income_score += 0.15
        
        # Professional network influence
        if professional_network.seniority_level == 'executive':
            income_score += 0.3
        elif professional_network.seniority_level == 'senior':
            income_score += 0.2
        elif professional_network.seniority_level == 'mid':
            income_score += 0.1
        
        # Classify income bracket
        if income_score > 0.7:
            return 'high_income'
        elif income_score > 0.4:
            return 'upper_middle_income'
        elif income_score > 0.2:
            return 'middle_income'
        else:
            return 'moderate_income'
    
    def _determine_spending_capacity(self, brand_mentions: List[BrandMention],
                                   location_patterns: List[LocationPattern],
                                   purchase_activities: List[PurchaseActivity]) -> str:
        """Determine spending capacity"""
        
        high_spending_indicators = 0
        total_indicators = 0
        
        # Check brand tier distribution
        for brand in brand_mentions:
            total_indicators += 1
            if brand.price_tier in ['luxury', 'premium']:
                high_spending_indicators += 1
        
        # Check location tier distribution
        for location in location_patterns:
            total_indicators += 1
            if location.economic_tier in ['luxury', 'upscale']:
                high_spending_indicators += 1
        
        # Check purchase activity spending levels
        for activity in purchase_activities:
            total_indicators += 1
            if activity.spending_level == 'high':
                high_spending_indicators += 1
        
        if total_indicators == 0:
            return 'unknown'
        
        spending_ratio = high_spending_indicators / total_indicators
        
        if spending_ratio > 0.6:
            return 'high'
        elif spending_ratio > 0.3:
            return 'medium'
        else:
            return 'conservative'
    
    def _classify_economic_lifestyle(self, brand_mentions: List[BrandMention],
                                   location_patterns: List[LocationPattern],
                                   purchase_activities: List[PurchaseActivity]) -> str:
        """Classify economic lifestyle"""
        
        lifestyle_indicators = {
            'luxury': 0,
            'aspirational': 0,
            'practical': 0,
            'budget_conscious': 0
        }
        
        # Analyze brand preferences
        for brand in brand_mentions:
            if brand.price_tier == 'luxury':
                lifestyle_indicators['luxury'] += 1
            elif brand.price_tier == 'premium':
                lifestyle_indicators['aspirational'] += 1
            elif brand.price_tier == 'mid-range':
                lifestyle_indicators['practical'] += 1
            else:
                lifestyle_indicators['budget_conscious'] += 1
        
        # Analyze location patterns
        for location in location_patterns:
            if location.economic_tier == 'luxury':
                lifestyle_indicators['luxury'] += 1
            elif location.economic_tier == 'upscale':
                lifestyle_indicators['aspirational'] += 1
            elif location.economic_tier == 'mainstream':
                lifestyle_indicators['practical'] += 1
            else:
                lifestyle_indicators['budget_conscious'] += 1
        
        # Return dominant lifestyle
        if not lifestyle_indicators or all(v == 0 for v in lifestyle_indicators.values()):
            return 'practical'
        
        return max(lifestyle_indicators, key=lifestyle_indicators.get)
    
    def _determine_brand_affinity_tier(self, brand_mentions: List[BrandMention]) -> str:
        """Determine brand affinity tier"""
        
        if not brand_mentions:
            return 'unknown'
        
        tier_counts = Counter([brand.price_tier for brand in brand_mentions])
        dominant_tier = tier_counts.most_common(1)[0][0]
        
        return dominant_tier
    
    def _classify_purchase_decision_style(self, purchase_activities: List[PurchaseActivity]) -> str:
        """Classify purchase decision style"""
        
        if not purchase_activities:
            return 'unknown'
        
        # Analyze purchase triggers across all activities
        all_triggers = []
        for activity in purchase_activities:
            all_triggers.extend(activity.purchase_triggers)
        
        if not all_triggers:
            return 'balanced'
        
        trigger_counts = Counter(all_triggers)
        dominant_trigger = trigger_counts.most_common(1)[0][0]
        
        style_mapping = {
            'immediate': 'impulsive',
            'research': 'analytical',
            'recommendation': 'social_influenced',
            'intent': 'planned'
        }
        
        return style_mapping.get(dominant_trigger, 'balanced')
    
    def _identify_economic_mobility_indicators(self, professional_network: ProfessionalNetwork,
                                             purchase_activities: List[PurchaseActivity]) -> List[str]:
        """Identify economic mobility indicators"""
        
        indicators = []
        
        # Career trajectory indicators
        if professional_network.career_trajectory == 'ascending':
            indicators.append('career_advancement')
        
        # Professional influence indicators
        if professional_network.professional_influence > 0.6:
            indicators.append('professional_influence')
        
        # Industry engagement indicators
        if professional_network.industry_engagement:
            avg_engagement = np.mean(list(professional_network.industry_engagement.values()))
            if avg_engagement > 0.5:
                indicators.append('industry_engagement')
        
        # Purchase behavior indicators
        for activity in purchase_activities:
            if activity.spending_level == 'high' and activity.purchase_frequency != 'rare':
                indicators.append('increasing_spending_power')
                break
        
        return indicators
    
    def _assess_financial_sophistication(self, professional_network: ProfessionalNetwork,
                                       brand_mentions: List[BrandMention],
                                       purchase_activities: List[PurchaseActivity]) -> str:
        """Assess financial sophistication level"""
        
        sophistication_score = 0.0
        
        # Professional indicators
        if 'finance' in professional_network.industry_connections:
            sophistication_score += 0.3
        
        if professional_network.seniority_level in ['executive', 'senior']:
            sophistication_score += 0.2
        
        # Brand choice indicators (luxury brands often indicate financial sophistication)
        luxury_brand_count = sum(1 for brand in brand_mentions if brand.price_tier == 'luxury')
        if luxury_brand_count > 0:
            sophistication_score += 0.2
        
        # Purchase behavior indicators
        for activity in purchase_activities:
            if activity.shopping_behavior == 'research_driven':
                sophistication_score += 0.1
                break
        
        # Thought leadership indicators
        if professional_network.thought_leadership_score > 0.3:
            sophistication_score += 0.2
        
        # Classify sophistication level
        if sophistication_score > 0.6:
            return 'high'
        elif sophistication_score > 0.3:
            return 'medium'
        else:
            return 'basic'
    
    def _determine_economic_priorities(self, purchase_activities: List[PurchaseActivity],
                                     brand_mentions: List[BrandMention],
                                     location_patterns: List[LocationPattern]) -> Dict[str, float]:
        """Determine economic priorities"""
        
        priorities = defaultdict(float)
        
        # Analyze purchase categories
        for activity in purchase_activities:
            category = activity.product_category
            if activity.spending_level == 'high':
                priorities[category] += 0.3
            elif activity.spending_level == 'medium':
                priorities[category] += 0.2
            else:
                priorities[category] += 0.1
        
        # Analyze brand categories
        for brand in brand_mentions:
            category = brand.category
            if brand.price_tier == 'luxury':
                priorities[category] += 0.25
            elif brand.price_tier == 'premium':
                priorities[category] += 0.15
            else:
                priorities[category] += 0.05
        
        # Analyze location types
        for location in location_patterns:
            location_type = location.location_type
            if location.economic_tier in ['luxury', 'upscale']:
                priorities[location_type] += 0.2
            else:
                priorities[location_type] += 0.1
        
        return dict(priorities)
    
    def _calculate_economic_risk_score(self, brand_mentions: List[BrandMention],
                                     location_patterns: List[LocationPattern],
                                     purchase_activities: List[PurchaseActivity]) -> float:
        """Calculate economic privacy risk score"""
        
        risk_score = 0.0
        
        # High-end brand mentions increase risk
        luxury_brands = [b for b in brand_mentions if b.price_tier == 'luxury']
        risk_score += len(luxury_brands) * 0.1
        
        # Specific location mentions increase risk
        specific_locations = [l for l in location_patterns if l.geographic_scope in ['local', 'regional']]
        risk_score += len(specific_locations) * 0.05
        
        # Purchase pattern visibility increases risk
        detailed_purchases = [p for p in purchase_activities if p.purchase_frequency in ['frequent', 'occasional']]
        risk_score += len(detailed_purchases) * 0.08
        
        return min(risk_score, 1.0)
    
    def _generate_economic_insights(self, brand_mentions: List[BrandMention],
                                  location_patterns: List[LocationPattern],
                                  purchase_activities: List[PurchaseActivity],
                                  professional_network: ProfessionalNetwork,
                                  economic_profile: EconomicProfile) -> List[str]:
        """Generate economic insights"""
        
        insights = []
        
        # Brand insights
        if brand_mentions:
            dominant_tier = economic_profile.brand_affinity_tier
            insights.append(f"Primary brand preference: {dominant_tier.replace('_', ' ')} tier")
            
            luxury_count = sum(1 for b in brand_mentions if b.price_tier == 'luxury')
            if luxury_count > 0:
                insights.append(f"Shows affinity for luxury brands ({luxury_count} mentions)")
        
        # Location insights
        if location_patterns:
            upscale_locations = [l for l in location_patterns if l.economic_tier in ['luxury', 'upscale']]
            if upscale_locations:
                insights.append(f"Frequents upscale establishments ({len(upscale_locations)} detected)")
        
        # Professional insights
        if professional_network.seniority_level != 'unknown':
            insights.append(f"Professional level: {professional_network.seniority_level}")
        
        if professional_network.professional_influence > 0.5:
            insights.append("Demonstrates professional influence and thought leadership")
        
        # Economic profile insights
        insights.append(f"Estimated economic lifestyle: {economic_profile.economic_lifestyle}")
        insights.append(f"Purchase decision style: {economic_profile.purchase_decision_style}")
        
        # Spending insights
        if purchase_activities:
            high_spenders = [p for p in purchase_activities if p.spending_level == 'high']
            if high_spenders:
                categories = [p.product_category for p in high_spenders]
                insights.append(f"High spending detected in: {', '.join(set(categories))}")
        
        return insights
    
    def _assess_privacy_economic_implications(self, brand_mentions: List[BrandMention],
                                            location_patterns: List[LocationPattern],
                                            purchase_activities: List[PurchaseActivity],
                                            professional_network: ProfessionalNetwork) -> List[str]:
        """Assess privacy implications of economic data"""
        
        implications = []
        
        # Brand mention risks
        luxury_brands = [b for b in brand_mentions if b.price_tier == 'luxury']
        if luxury_brands:
            implications.append("⚠️ Luxury brand mentions may reveal high disposable income")
        
        # Location pattern risks
        specific_locations = [l for l in location_patterns if l.frequency > 1]
        if specific_locations:
            implications.append("⚠️ Regular location patterns may reveal lifestyle and spending habits")
        
        # Purchase activity risks
        detailed_purchases = [p for p in purchase_activities if p.purchase_frequency != 'rare']
        if detailed_purchases:
            implications.append("⚠️ Purchase patterns may be used for targeted advertising and profiling")
        
        # Professional network risks
        if professional_network.seniority_level in ['executive', 'senior']:
            implications.append("⚠️ Senior professional status may attract financial solicitation")
        
        if professional_network.professional_influence > 0.6:
            implications.append("⚠️ High professional influence may lead to business targeting")
        
        # Cross-category risks
        if brand_mentions and location_patterns and purchase_activities:
            implications.append("⚠️ Combined economic indicators create detailed financial profile")
        
        if not implications:
            implications.append("✅ Limited economic data exposure detected")
        
        return implications
    
    def _create_empty_economic_analysis(self) -> EconomicIndicatorsResult:
        """Create empty economic analysis for no data case"""
        
        return EconomicIndicatorsResult(
            brand_mentions=[],
            location_patterns=[],
            purchase_activities=[],
            professional_network=ProfessionalNetwork({}, 'unknown', 'passive', 0.0, 'stable', {}, 0.0),
            economic_profile=EconomicProfile(
                'unknown', 'unknown', 'practical', 'unknown', 'balanced', [], 'basic', {}
            ),
            economic_risk_score=0.0,
            economic_insights=['Insufficient economic data for analysis'],
            privacy_economic_implications=['✅ No significant economic data exposure detected']
        )

def create_economic_indicators_analyzer():
    """Factory function to create economic indicators analyzer"""
    return EconomicIndicatorsAnalyzer()
