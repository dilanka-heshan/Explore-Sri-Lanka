"""
Database setup script for Supabase
This script creates the necessary tables and initial data
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import supabase_manager, get_supabase_client, init_database
from models.orm.destination import Destination
from models.orm.gallery import Gallery
from models.orm.story import Story
from models.orm.subscriber import Subscriber

# SQL schema for Supabase
SCHEMA_SQL = """
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Destinations table
CREATE TABLE IF NOT EXISTS destinations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address TEXT,
    district VARCHAR(100),
    province VARCHAR(100),
    visit_time_minutes INTEGER DEFAULT 120,
    best_time_to_visit VARCHAR(255),
    accessibility_level VARCHAR(50),
    popularity_score FLOAT DEFAULT 0.0,
    user_rating FLOAT DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    entry_fee FLOAT DEFAULT 0.0,
    contact_info JSONB,
    facilities JSONB,
    image_urls JSONB,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Gallery table
CREATE TABLE IF NOT EXISTS gallery (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    alt_text VARCHAR(255),
    caption TEXT,
    file_name VARCHAR(255),
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    format VARCHAR(10),
    image_type VARCHAR(50),
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    photographer VARCHAR(255),
    license_type VARCHAR(100),
    source VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    is_approved BOOLEAN DEFAULT FALSE
);

-- Stories table
CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    excerpt TEXT,
    content TEXT NOT NULL,
    author_id INTEGER,
    author_name VARCHAR(255),
    author_email VARCHAR(255),
    category VARCHAR(100),
    tags JSONB,
    featured_destinations JSONB,
    meta_title VARCHAR(255),
    meta_description TEXT,
    featured_image_url VARCHAR(500),
    read_time_minutes INTEGER,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_featured BOOLEAN DEFAULT FALSE,
    is_trending BOOLEAN DEFAULT FALSE,
    allow_comments BOOLEAN DEFAULT TRUE
);

-- Subscribers table
CREATE TABLE IF NOT EXISTS subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    subscription_type VARCHAR(50) DEFAULT 'newsletter',
    frequency VARCHAR(20) DEFAULT 'weekly',
    interests JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255),
    subscription_source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE,
    unsubscribed_at TIMESTAMP WITH TIME ZONE,
    last_email_sent TIMESTAMP WITH TIME ZONE,
    user_agent VARCHAR(500),
    ip_address VARCHAR(45)
);

-- Users table for authentication (Supabase handles this automatically)
-- But we can create additional user profile data
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE,
    email VARCHAR(255),
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    preferences JSONB,
    travel_interests JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Itineraries table (for saved travel plans)
CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_days INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    itinerary_data JSONB NOT NULL,
    preferences JSONB,
    total_budget FLOAT,
    status VARCHAR(20) DEFAULT 'draft',
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_destinations_category ON destinations(category);
CREATE INDEX IF NOT EXISTS idx_destinations_district ON destinations(district);
CREATE INDEX IF NOT EXISTS idx_destinations_province ON destinations(province);
CREATE INDEX IF NOT EXISTS idx_destinations_location ON destinations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_gallery_destination ON gallery(destination_id);
CREATE INDEX IF NOT EXISTS idx_stories_category ON stories(category);
CREATE INDEX IF NOT EXISTS idx_stories_status ON stories(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_itineraries_user ON itineraries(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE destinations ENABLE ROW LEVEL SECURITY;
ALTER TABLE gallery ENABLE ROW LEVEL SECURITY;
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Public read access for destinations and gallery
CREATE POLICY "Public destinations read" ON destinations FOR SELECT USING (is_active = true);
CREATE POLICY "Public gallery read" ON gallery FOR SELECT USING (is_active = true AND is_approved = true);
CREATE POLICY "Public stories read" ON stories FOR SELECT USING (status = 'published');

-- User profiles are only accessible by the user themselves
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Itineraries are accessible by the user who created them
CREATE POLICY "Users can view own itineraries" ON itineraries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own itineraries" ON itineraries FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own itineraries" ON itineraries FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own itineraries" ON itineraries FOR DELETE USING (auth.uid() = user_id);

-- Public itineraries can be viewed by anyone
CREATE POLICY "Public itineraries read" ON itineraries FOR SELECT USING (is_public = true);
"""

# Sample data for testing
SAMPLE_DESTINATIONS = [
    {
        "name": "Sigiriya Rock Fortress",
        "description": "Ancient rock fortress and palace ruins, UNESCO World Heritage Site",
        "category": "Historical",
        "latitude": 7.9568,
        "longitude": 80.7595,
        "address": "Sigiriya, Matale District, Central Province",
        "district": "Matale",
        "province": "Central",
        "visit_time_minutes": 180,
        "best_time_to_visit": "Early morning (6:30 AM - 10:00 AM)",
        "accessibility_level": "Moderate",
        "popularity_score": 9.5,
        "user_rating": 4.7,
        "review_count": 2543,
        "entry_fee": 30.0,
        "contact_info": {"phone": "+94 66 2286741"},
        "facilities": ["parking", "restrooms", "guide_service", "museum"],
        "image_urls": [
            "https://example.com/sigiriya1.jpg",
            "https://example.com/sigiriya2.jpg"
        ],
        "tags": ["unesco", "ancient", "climbing", "views", "history"]
    },
    {
        "name": "Temple of the Sacred Tooth Relic",
        "description": "Sacred Buddhist temple housing the tooth relic of Buddha",
        "category": "Cultural",
        "latitude": 7.2906,
        "longitude": 80.6337,
        "address": "Sri Dalada Veediya, Kandy",
        "district": "Kandy",
        "province": "Central",
        "visit_time_minutes": 120,
        "best_time_to_visit": "Morning (6:00 AM - 11:00 AM) or Evening (6:00 PM - 8:00 PM)",
        "accessibility_level": "Easy",
        "popularity_score": 9.2,
        "user_rating": 4.6,
        "review_count": 1876,
        "entry_fee": 1.5,
        "contact_info": {"phone": "+94 81 2234226"},
        "facilities": ["parking", "restrooms", "gift_shop"],
        "image_urls": [
            "https://example.com/dalada1.jpg",
            "https://example.com/dalada2.jpg"
        ],
        "tags": ["buddhist", "temple", "sacred", "cultural", "kandy"]
    },
    {
        "name": "Mirissa Beach",
        "description": "Beautiful beach known for whale watching and surfing",
        "category": "Beach",
        "latitude": 5.9487,
        "longitude": 80.4585,
        "address": "Mirissa, Matara District",
        "district": "Matara",
        "province": "Southern",
        "visit_time_minutes": 240,
        "best_time_to_visit": "All day, best for whale watching: 6:00 AM - 12:00 PM",
        "accessibility_level": "Easy",
        "popularity_score": 8.8,
        "user_rating": 4.4,
        "review_count": 1234,
        "entry_fee": 0.0,
        "contact_info": {},
        "facilities": ["parking", "restaurants", "accommodation", "water_sports"],
        "image_urls": [
            "https://example.com/mirissa1.jpg",
            "https://example.com/mirissa2.jpg"
        ],
        "tags": ["beach", "whale_watching", "surfing", "swimming", "sunset"]
    }
]

async def setup_database():
    """Setup database tables and initial data"""
    print("Setting up database...")
    
    # Initialize database connection
    init_database()
    
    client = get_supabase_client()
    if not client:
        print("Error: Could not connect to Supabase")
        return False
    
    try:
        # Note: In Supabase, you would typically run the SQL schema directly in the Supabase dashboard
        # or using the Supabase CLI. This is just for reference.
        print("Database schema should be created in Supabase dashboard.")
        print("You can copy the SQL from the SCHEMA_SQL variable above.")
        
        # Insert sample destinations
        print("Inserting sample destinations...")
        for destination in SAMPLE_DESTINATIONS:
            try:
                result = supabase_manager.insert_data("destinations", destination)
                print(f"Inserted destination: {destination['name']}")
            except Exception as e:
                print(f"Error inserting {destination['name']}: {e}")
        
        print("Database setup completed!")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(setup_database())
