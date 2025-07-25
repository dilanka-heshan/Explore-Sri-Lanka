"""
Sample Sri Lankan Attractions Dataset
This file contains sample attraction data for testing the upload functionality
"""

SAMPLE_ATTRACTIONS = [
    {
        "name": "Sigiriya Rock Fortress",
        "description": "Ancient rock fortress and UNESCO World Heritage site featuring stunning frescoes, water gardens, and panoramic views from the top.",
        "category": "historical",
        "latitude": 7.9570,
        "longitude": 80.7603,
        "rating": 4.6,
        "review_count": 15420,
        "tags": ["unesco", "historical", "climbing", "ancient", "fortress", "frescoes", "photography"],
        "entry_fee_lkr": 5000.0,
        "opening_hours": {
            "monday": "7:00-17:30",
            "tuesday": "7:00-17:30", 
            "wednesday": "7:00-17:30",
            "thursday": "7:00-17:30",
            "friday": "7:00-17:30",
            "saturday": "7:00-17:30",
            "sunday": "7:00-17:30"
        },
        "visit_duration_hours": 3.0,
        "difficulty_level": "moderate",
        "best_season": "dry_season",
        "facilities": ["parking", "restaurant", "souvenir_shop", "restrooms", "guide_service"],
        "contact_info": {"phone": "+94 66 228 6571", "website": "sigiriya.lk"},
        "images": ["sigiriya1.jpg", "sigiriya2.jpg"],
        "popularity_score": 0.95,
        "accessibility_features": ["wheelchair_access_to_base"],
        "recommended_for": ["couple", "family", "group"],
        "suitable_for_budget": ["mid_range", "luxury"]
    },
    {
        "name": "Temple of the Sacred Tooth Relic (Sri Dalada Maligawa)",
        "description": "Sacred Buddhist temple housing the tooth relic of Buddha, featuring traditional Kandy architecture and daily ceremonial rituals.",
        "category": "cultural",
        "latitude": 7.2955,
        "longitude": 80.6415,
        "rating": 4.5,
        "review_count": 12890,
        "tags": ["buddhist", "temple", "sacred", "cultural", "kandy", "rituals", "architecture"],
        "entry_fee_lkr": 1500.0,
        "opening_hours": {
            "monday": "5:30-20:00",
            "tuesday": "5:30-20:00",
            "wednesday": "5:30-20:00", 
            "thursday": "5:30-20:00",
            "friday": "5:30-20:00",
            "saturday": "5:30-20:00",
            "sunday": "5:30-20:00"
        },
        "visit_duration_hours": 1.5,
        "difficulty_level": "easy",
        "best_season": "year_round",
        "facilities": ["parking", "security", "guide_service", "photography_area"],
        "contact_info": {"phone": "+94 81 234 4226"},
        "images": ["dalada_maligawa1.jpg"],
        "popularity_score": 0.92,
        "accessibility_features": ["wheelchair_accessible"],
        "recommended_for": ["solo", "couple", "family"],
        "suitable_for_budget": ["budget", "mid_range", "luxury"]
    },
    {
        "name": "Ella Rock Hiking Trail",
        "description": "Scenic hiking trail through tea plantations and forests leading to breathtaking panoramic views of Ella Gap and surrounding mountains.",
        "category": "adventure",
        "latitude": 6.8667,
        "longitude": 81.0500,
        "rating": 4.7,
        "review_count": 8945,
        "tags": ["hiking", "adventure", "mountains", "tea_plantations", "nature", "panoramic_views", "trekking"],
        "entry_fee_lkr": 0.0,
        "opening_hours": {
            "monday": "6:00-18:00",
            "tuesday": "6:00-18:00",
            "wednesday": "6:00-18:00",
            "thursday": "6:00-18:00", 
            "friday": "6:00-18:00",
            "saturday": "6:00-18:00",
            "sunday": "6:00-18:00"
        },
        "visit_duration_hours": 4.5,
        "difficulty_level": "challenging",
        "best_season": "dry_season",
        "facilities": ["trail_markers", "basic_restrooms"],
        "contact_info": {},
        "images": ["ella_rock1.jpg", "ella_rock2.jpg"],
        "popularity_score": 0.88,
        "accessibility_features": [],
        "recommended_for": ["solo", "couple", "group"],
        "suitable_for_budget": ["budget", "mid_range"]
    },
    {
        "name": "Yala National Park",
        "description": "Premier wildlife sanctuary famous for leopard sightings, elephants, and diverse bird species across varied ecosystems.",
        "category": "wildlife", 
        "latitude": 6.3725,
        "longitude": 81.5119,
        "rating": 4.4,
        "review_count": 11250,
        "tags": ["safari", "wildlife", "leopards", "elephants", "birds", "nature", "photography"],
        "entry_fee_lkr": 3500.0,
        "opening_hours": {
            "monday": "6:00-18:30",
            "tuesday": "closed", 
            "wednesday": "6:00-18:30",
            "thursday": "6:00-18:30",
            "friday": "6:00-18:30",
            "saturday": "6:00-18:30",
            "sunday": "6:00-18:30"
        },
        "visit_duration_hours": 6.0,
        "difficulty_level": "easy",
        "best_season": "dry_season",
        "facilities": ["safari_vehicles", "guide_service", "visitor_center", "restrooms"],
        "contact_info": {"phone": "+94 47 203 9449", "website": "yalasrilanka.lk"},
        "images": ["yala1.jpg", "yala2.jpg", "yala3.jpg"],
        "popularity_score": 0.91,
        "accessibility_features": ["vehicle_accessible"],
        "recommended_for": ["couple", "family", "group"],
        "suitable_for_budget": ["mid_range", "luxury"]
    },
    {
        "name": "Galle Fort",
        "description": "17th-century Dutch colonial fort with cobblestone streets, ramparts, museums, boutique shops, and stunning ocean views.",
        "category": "historical",
        "latitude": 6.0267,
        "longitude": 80.2170,
        "rating": 4.5,
        "review_count": 9876,
        "tags": ["dutch_colonial", "fort", "unesco", "ocean_views", "museums", "shopping", "architecture"],
        "entry_fee_lkr": 0.0,
        "opening_hours": {
            "monday": "24_hours",
            "tuesday": "24_hours",
            "wednesday": "24_hours",
            "thursday": "24_hours",
            "friday": "24_hours", 
            "saturday": "24_hours",
            "sunday": "24_hours"
        },
        "visit_duration_hours": 3.5,
        "difficulty_level": "easy",
        "best_season": "year_round",
        "facilities": ["parking", "restaurants", "shops", "museums", "restrooms"],
        "contact_info": {"website": "gallefort.gov.lk"},
        "images": ["galle_fort1.jpg", "galle_fort2.jpg"],
        "popularity_score": 0.89,
        "accessibility_features": ["wheelchair_partial"],
        "recommended_for": ["solo", "couple", "family"],
        "suitable_for_budget": ["budget", "mid_range", "luxury"]
    },
    {
        "name": "Mirissa Beach",
        "description": "Pristine crescent-shaped beach famous for whale watching, surfing, and beautiful sunsets with palm-lined shores.",
        "category": "beach",
        "latitude": 5.9487,
        "longitude": 80.4563,
        "rating": 4.3,
        "review_count": 7654,
        "tags": ["beach", "whale_watching", "surfing", "sunset", "swimming", "relaxation", "seafood"],
        "entry_fee_lkr": 0.0,
        "opening_hours": {
            "monday": "24_hours",
            "tuesday": "24_hours",
            "wednesday": "24_hours",
            "thursday": "24_hours",
            "friday": "24_hours",
            "saturday": "24_hours", 
            "sunday": "24_hours"
        },
        "visit_duration_hours": 4.0,
        "difficulty_level": "easy",
        "best_season": "dry_season",
        "facilities": ["restaurants", "beach_bars", "water_sports", "parking"],
        "contact_info": {},
        "images": ["mirissa1.jpg", "mirissa2.jpg"],
        "popularity_score": 0.85,
        "accessibility_features": ["beach_wheelchair"],
        "recommended_for": ["couple", "family", "group"],
        "suitable_for_budget": ["budget", "mid_range"]
    },
    {
        "name": "Dambulla Cave Temple",
        "description": "Ancient Buddhist cave temple complex with over 150 Buddha statues and intricate ceiling paintings dating back to 1st century BC.",
        "category": "cultural",
        "latitude": 7.8567,
        "longitude": 80.6482,
        "rating": 4.4,
        "review_count": 6789,
        "tags": ["buddhist", "caves", "ancient", "paintings", "statues", "unesco", "spiritual"],
        "entry_fee_lkr": 1500.0,
        "opening_hours": {
            "monday": "7:00-19:00",
            "tuesday": "7:00-19:00",
            "wednesday": "7:00-19:00",
            "thursday": "7:00-19:00",
            "friday": "7:00-19:00",
            "saturday": "7:00-19:00",
            "sunday": "7:00-19:00"
        },
        "visit_duration_hours": 2.0,
        "difficulty_level": "moderate",
        "best_season": "year_round",
        "facilities": ["parking", "guide_service", "museum", "souvenir_shop"],
        "contact_info": {"phone": "+94 66 228 4873"},
        "images": ["dambulla1.jpg", "dambulla2.jpg"],
        "popularity_score": 0.87,
        "accessibility_features": ["partial_wheelchair_access"],
        "recommended_for": ["solo", "couple", "family"],
        "suitable_for_budget": ["budget", "mid_range", "luxury"]
    },
    {
        "name": "Horton Plains National Park",
        "description": "High-altitude plateau featuring World's End cliff, Baker's Falls, unique montane ecosystem, and endemic wildlife.",
        "category": "nature",
        "latitude": 6.8061,
        "longitude": 80.7950,
        "rating": 4.6,
        "review_count": 5432,
        "tags": ["national_park", "worlds_end", "cliff", "waterfall", "hiking", "endemic_species", "plateau"],
        "entry_fee_lkr": 3000.0,
        "opening_hours": {
            "monday": "6:30-18:30",
            "tuesday": "6:30-18:30",
            "wednesday": "6:30-18:30",
            "thursday": "6:30-18:30",
            "friday": "6:30-18:30",
            "saturday": "6:30-18:30",
            "sunday": "6:30-18:30"
        },
        "visit_duration_hours": 5.0,
        "difficulty_level": "moderate",
        "best_season": "dry_season",
        "facilities": ["visitor_center", "guided_trails", "restrooms", "parking"],
        "contact_info": {"phone": "+94 52 222 8049"},
        "images": ["horton_plains1.jpg", "horton_plains2.jpg"],
        "popularity_score": 0.83,
        "accessibility_features": [],
        "recommended_for": ["solo", "couple", "group"],
        "suitable_for_budget": ["mid_range", "luxury"]
    },
    {
        "name": "Nuwara Eliya Tea Plantations",
        "description": "Scenic hill country tea estates with guided factory tours, tea tasting experiences, and stunning mountain vistas.",
        "category": "nature",
        "latitude": 6.9497,
        "longitude": 80.7891,
        "rating": 4.2,
        "review_count": 4567,
        "tags": ["tea_plantations", "factory_tours", "mountains", "scenic", "tasting", "hill_country"],
        "entry_fee_lkr": 500.0,
        "opening_hours": {
            "monday": "8:00-17:00",
            "tuesday": "8:00-17:00",
            "wednesday": "8:00-17:00",
            "thursday": "8:00-17:00",
            "friday": "8:00-17:00",
            "saturday": "8:00-17:00",
            "sunday": "closed"
        },
        "visit_duration_hours": 2.5,
        "difficulty_level": "easy",
        "best_season": "year_round",
        "facilities": ["factory_tours", "tea_shop", "cafe", "parking"],
        "contact_info": {"phone": "+94 52 223 4681"},
        "images": ["tea_plantation1.jpg", "tea_plantation2.jpg"],
        "popularity_score": 0.78,
        "accessibility_features": ["wheelchair_accessible"],
        "recommended_for": ["couple", "family", "group"],
        "suitable_for_budget": ["budget", "mid_range", "luxury"]
    },
    {
        "name": "Nine Arch Bridge",
        "description": "Iconic railway bridge built entirely of stone, brick and cement without steel, surrounded by lush green tea fields.",
        "category": "photography",
        "latitude": 6.8832,
        "longitude": 81.0587,
        "rating": 4.5,
        "review_count": 8901,
        "tags": ["railway", "bridge", "architecture", "photography", "train", "scenic", "ella"],
        "entry_fee_lkr": 0.0,
        "opening_hours": {
            "monday": "24_hours",
            "tuesday": "24_hours", 
            "wednesday": "24_hours",
            "thursday": "24_hours",
            "friday": "24_hours",
            "saturday": "24_hours",
            "sunday": "24_hours"
        },
        "visit_duration_hours": 1.5,
        "difficulty_level": "easy",
        "best_season": "year_round",
        "facilities": ["viewpoints", "walking_paths"],
        "contact_info": {},
        "images": ["nine_arch1.jpg", "nine_arch2.jpg"],
        "popularity_score": 0.86,
        "accessibility_features": ["walking_required"],
        "recommended_for": ["solo", "couple", "family"],
        "suitable_for_budget": ["budget", "mid_range", "luxury"]
    }
]

# Function to get the sample dataset
def get_sample_dataset():
    """Return the sample attractions dataset"""
    return SAMPLE_ATTRACTIONS

# Function to create a JSON file with the dataset
def create_sample_json_file(filename="sample_attractions.json"):
    """Create a JSON file with the sample dataset"""
    import json
    with open(filename, 'w') as f:
        json.dump(SAMPLE_ATTRACTIONS, f, indent=2)
    return filename

# Function to create a CSV file with the dataset
def create_sample_csv_file(filename="sample_attractions.csv"):
    """Create a CSV file with the sample dataset"""
    import pandas as pd
    
    # Flatten the data for CSV format
    flattened_data = []
    for attraction in SAMPLE_ATTRACTIONS:
        flat_attr = attraction.copy()
        
        # Convert complex fields to strings
        flat_attr['tags'] = ','.join(attraction['tags'])
        flat_attr['facilities'] = ','.join(attraction['facilities'])
        flat_attr['recommended_for'] = ','.join(attraction['recommended_for'])
        flat_attr['suitable_for_budget'] = ','.join(attraction['suitable_for_budget'])
        flat_attr['accessibility_features'] = ','.join(attraction['accessibility_features'])
        flat_attr['images'] = ','.join(attraction['images'])
        
        # Convert opening hours to string representation
        flat_attr['opening_hours'] = str(attraction['opening_hours'])
        flat_attr['contact_info'] = str(attraction['contact_info'])
        
        flattened_data.append(flat_attr)
    
    df = pd.DataFrame(flattened_data)
    df.to_csv(filename, index=False)
    return filename

if __name__ == "__main__":
    # Create sample files for testing
    json_file = create_sample_json_file()
    print(f"Created sample JSON file: {json_file}")
    
    try:
        csv_file = create_sample_csv_file()
        print(f"Created sample CSV file: {csv_file}")
    except ImportError:
        print("pandas not available, skipping CSV file creation")
