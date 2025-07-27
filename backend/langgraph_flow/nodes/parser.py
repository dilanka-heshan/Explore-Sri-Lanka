"""
Enhanced Parser Node for Travel Planning
Extracts user preferences, trip details, and interests from natural language input
"""

import re
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

def parse_user_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhanced parser that extracts detailed travel preferences from user input
    
    Args:
        state: Current planning state containing user_input
    
    Returns:
        Updated state with parsed user profile and trip details
    """
    
    user_input = state.get("user_input", "")
    
    try:
        # Parse basic trip details
        duration_days = extract_duration(user_input)
        start_date = extract_start_date(user_input)
        
        # Parse user interests and preferences
        interests = extract_interests(user_input)
        trip_type = extract_trip_type(user_input)
        budget_level = extract_budget_level(user_input)
        
        # Parse preferences and requirements
        age_group = extract_age_group(user_input)
        mobility_requirements = extract_mobility_requirements(user_input)
        preferred_pace = extract_pace_preference(user_input)
        
        # Parse preference levels (1-5 scale)
        cultural_interest = extract_interest_level(user_input, ["cultural", "culture", "heritage", "history", "temple"])
        adventure_level = extract_interest_level(user_input, ["adventure", "hiking", "climbing", "extreme", "thrill"])
        nature_appreciation = extract_interest_level(user_input, ["nature", "wildlife", "forest", "national park", "animals"])
        
        # Parse specific requirements
        excluded_attractions = extract_excluded_items(user_input)
        preferred_regions = extract_preferred_regions(user_input)
        special_requirements = extract_special_requirements(user_input)
        
        # Create user profile
        user_profile = {
            "interests": interests,
            "trip_type": trip_type,
            "budget_level": budget_level,
            "age_group": age_group,
            "mobility_requirements": mobility_requirements,
            "preferred_pace": preferred_pace,
            "cultural_interest_level": cultural_interest,
            "adventure_level": adventure_level,
            "nature_appreciation": nature_appreciation
        }
        
        # Update state
        state.update({
            "user_profile": user_profile,
            "duration_days": duration_days,
            "start_date": start_date,
            "parsed_interests": interests,
            "excluded_attractions": excluded_attractions,
            "preferred_regions": preferred_regions,
            "special_requirements": special_requirements,
            "reasoning_log": state.get("reasoning_log", []) + [
                f"Parsed user preferences: {len(interests)} interests, {duration_days} days, {trip_type} trip"
            ]
        })
        
        logger.info(f"Successfully parsed user input: {interests}, {duration_days} days, {trip_type}")
        return state
        
    except Exception as e:
        logger.error(f"Error parsing user input: {e}")
        # Return default values
        state.update({
            "user_profile": create_default_profile(),
            "duration_days": 3,
            "start_date": date.today() + timedelta(days=30),
            "parsed_interests": ["cultural", "nature"],
            "reasoning_log": state.get("reasoning_log", []) + [
                f"Used default preferences due to parsing error: {e}"
            ]
        })
        return state

def extract_duration(text: str) -> int:
    """Extract trip duration from text"""
    
    # Patterns for duration
    patterns = [
        r'(\d+)\s*days?',
        r'(\d+)\s*day\s*trip',
        r'for\s*(\d+)\s*days?',
        r'(\d+)\s*nights?',
        r'(\d+)\s*week',
        r'a\s*week',
        r'two\s*weeks?',
        r'three\s*weeks?'
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            if 'week' in pattern:
                if 'two' in match.group():
                    return 14
                elif 'three' in match.group():
                    return 21
                elif match.group(1):
                    return int(match.group(1)) * 7
                else:
                    return 7
            else:
                return int(match.group(1))
    
    # Default duration
    return 5

def extract_start_date(text: str) -> date:
    """Extract start date from text"""
    
    today = date.today()
    
    # Look for relative dates
    if re.search(r'next\s*week', text.lower()):
        return today + timedelta(days=7)
    elif re.search(r'next\s*month', text.lower()):
        return today + timedelta(days=30)
    elif re.search(r'december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov', text.lower()):
        # Try to parse specific months (simplified)
        month_mapping = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        for month_name, month_num in month_mapping.items():
            if month_name in text.lower():
                year = today.year if month_num >= today.month else today.year + 1
                return date(year, month_num, 1)
    
    # Default to 30 days from now
    return today + timedelta(days=30)

def extract_interests(text: str) -> List[str]:
    """Extract interests and activities from text"""
    
    interest_keywords = {
        'cultural': ['cultural', 'culture', 'heritage', 'traditional', 'temples', 'buddhist', 'hindu'],
        'nature': ['nature', 'natural', 'scenery', 'landscape', 'mountains', 'forests', 'waterfalls'],
        'adventure': ['adventure', 'hiking', 'climbing', 'trekking', 'extreme', 'adrenaline', 'zip'],
        'beach': ['beach', 'coast', 'ocean', 'sea', 'surfing', 'swimming', 'sunset'],
        'wildlife': ['wildlife', 'animals', 'safari', 'national park', 'elephants', 'leopards'],
        'historical': ['historical', 'history', 'ancient', 'ruins', 'archaeological', 'colonial'],
        'photography': ['photography', 'photos', 'instagram', 'scenic', 'photogenic'],
        'food': ['food', 'cuisine', 'culinary', 'local food', 'street food', 'restaurants'],
        'spiritual': ['spiritual', 'meditation', 'peaceful', 'religious', 'pilgrimage'],
        'shopping': ['shopping', 'markets', 'souvenirs', 'handicrafts', 'local products']
    }
    
    text_lower = text.lower()
    detected_interests = []
    
    for interest, keywords in interest_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if interest not in detected_interests:
                    detected_interests.append(interest)
                break
    
    # If no specific interests detected, provide defaults
    if not detected_interests:
        detected_interests = ['cultural', 'nature']
    
    return detected_interests

def extract_trip_type(text: str) -> str:
    """Extract trip type from text"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['solo', 'alone', 'myself', 'by myself']):
        return 'solo'
    elif any(word in text_lower for word in ['couple', 'partner', 'husband', 'wife', 'boyfriend', 'girlfriend']):
        return 'couple'
    elif any(word in text_lower for word in ['family', 'kids', 'children', 'parents']):
        return 'family'
    elif any(word in text_lower for word in ['group', 'friends', 'colleagues']):
        return 'group'
    
    return 'couple'  # default

def extract_budget_level(text: str) -> str:
    """Extract budget level from text"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['budget', 'cheap', 'affordable', 'low cost', 'backpack']):
        return 'budget'
    elif any(word in text_lower for word in ['luxury', 'premium', 'high-end', 'expensive', 'first class']):
        return 'luxury'
    elif any(word in text_lower for word in ['mid-range', 'moderate', 'comfortable']):
        return 'mid_range'
    
    return 'mid_range'  # default

def extract_age_group(text: str) -> str:
    """Extract age group from text"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['senior', 'elderly', 'retired', 'over 60']):
        return 'senior'
    elif any(word in text_lower for word in ['young', 'college', 'student', 'under 25']):
        return 'young_adult'
    elif any(word in text_lower for word in ['family', 'kids', 'children']):
        return 'family'
    
    return 'adult'  # default

def extract_mobility_requirements(text: str) -> str:
    """Extract mobility requirements from text"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['wheelchair', 'disabled', 'mobility issues', 'limited walking']):
        return 'limited_mobility'
    elif any(word in text_lower for word in ['fit', 'athletic', 'active', 'good shape']):
        return 'high_mobility'
    
    return 'normal'  # default

def extract_pace_preference(text: str) -> str:
    """Extract pace preference from text"""
    
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['relaxed', 'slow', 'leisure', 'peaceful', 'easy']):
        return 'slow'
    elif any(word in text_lower for word in ['fast', 'quick', 'packed', 'busy', 'active']):
        return 'fast'
    
    return 'moderate'  # default

def extract_interest_level(text: str, keywords: List[str]) -> int:
    """Extract interest level (1-5) for specific categories"""
    
    text_lower = text.lower()
    
    # Count mentions and look for intensity words
    keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
    
    if keyword_count == 0:
        return 3  # neutral
    
    # Look for intensity indicators
    if any(word in text_lower for word in ['love', 'passionate', 'obsessed', 'very interested']):
        return 5
    elif any(word in text_lower for word in ['really like', 'very much', 'especially']):
        return 4
    elif any(word in text_lower for word in ['interested', 'like', 'enjoy']):
        return 3
    elif any(word in text_lower for word in ['not very', 'not really', 'not interested']):
        return 2
    elif any(word in text_lower for word in ['hate', 'dislike', 'avoid']):
        return 1
    
    return min(3 + keyword_count, 5)  # Scale based on mentions

def extract_excluded_items(text: str) -> List[str]:
    """Extract items to exclude from the plan"""
    
    excluded = []
    text_lower = text.lower()
    
    # Look for exclusion patterns
    exclusion_patterns = [
        r'no\s+(\w+)',
        r'avoid\s+(\w+)',
        r'not\s+interested\s+in\s+(\w+)',
        r'skip\s+(\w+)'
    ]
    
    for pattern in exclusion_patterns:
        matches = re.findall(pattern, text_lower)
        excluded.extend(matches)
    
    return excluded

def extract_preferred_regions(text: str) -> List[str]:
    """Extract preferred regions/areas from text"""
    
    # Sri Lankan regions and popular areas
    regions = {
        'colombo': 'Western',
        'kandy': 'Central',
        'galle': 'Southern',
        'ella': 'Uva',
        'sigiriya': 'North Central',
        'anuradhapura': 'North Central',
        'polonnaruwa': 'North Central',
        'nuwara eliya': 'Central',
        'bentota': 'Southern',
        'mirissa': 'Southern',
        'yala': 'Southern',
        'arugam bay': 'Eastern'
    }
    
    text_lower = text.lower()
    preferred = []
    
    for location, region in regions.items():
        if location in text_lower:
            if region not in preferred:
                preferred.append(region)
    
    return preferred

def extract_special_requirements(text: str) -> str:
    """Extract special requirements from text"""
    
    requirements = []
    text_lower = text.lower()
    
    if 'vegetarian' in text_lower or 'vegan' in text_lower:
        requirements.append('vegetarian food')
    
    if 'halal' in text_lower:
        requirements.append('halal food')
    
    if 'english' in text_lower and 'guide' in text_lower:
        requirements.append('english speaking guide')
    
    if 'air condition' in text_lower or 'ac' in text_lower:
        requirements.append('air conditioned transport')
    
    return '; '.join(requirements) if requirements else ""

def create_default_profile() -> Dict[str, Any]:
    """Create default user profile when parsing fails"""
    
    return {
        "interests": ["cultural", "nature"],
        "trip_type": "couple",
        "budget_level": "mid_range",
        "age_group": "adult",
        "mobility_requirements": "normal",
        "preferred_pace": "moderate",
        "cultural_interest_level": 3,
        "adventure_level": 3,
        "nature_appreciation": 3
    }
