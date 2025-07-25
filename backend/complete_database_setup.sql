-- ============================================================================
-- COMPLETE DATABASE SETUP FOR EXPLORE SRI LANKA
-- Run this entire script in your Supabase SQL Editor
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. CREATE ENUM TYPES
-- ============================================================================

-- Drop existing types if they exist (for clean setup)
DROP TYPE IF EXISTS destination_category CASCADE;
DROP TYPE IF EXISTS region_type CASCADE;
DROP TYPE IF EXISTS difficulty_level CASCADE;
DROP TYPE IF EXISTS season_type CASCADE;
DROP TYPE IF EXISTS trip_type CASCADE;
DROP TYPE IF EXISTS booking_status CASCADE;
DROP TYPE IF EXISTS budget_level CASCADE;

-- Create enum types
CREATE TYPE destination_category AS ENUM ('cultural', 'historical', 'adventure', 'wildlife', 'beach', 'nature', 'photography');
CREATE TYPE region_type AS ENUM ('Central', 'Southern', 'Northern', 'Eastern', 'Western', 'North Central', 'North Western', 'Sabaragamuwa', 'Uva');
CREATE TYPE difficulty_level AS ENUM ('easy', 'moderate', 'challenging');
CREATE TYPE season_type AS ENUM ('year_round', 'dry_season', 'wet_season');
CREATE TYPE trip_type AS ENUM ('solo', 'couple', 'family', 'group', 'photography', 'adventure', 'cultural');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed');
CREATE TYPE budget_level AS ENUM ('budget', 'mid_range', 'luxury');

-- ============================================================================
-- 2. DROP EXISTING TABLES (for clean setup)
-- ============================================================================

DROP TABLE IF EXISTS itinerary_destinations CASCADE;
DROP TABLE IF EXISTS itineraries CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS gallery CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS destinations CASCADE;

-- ============================================================================
-- 3. CREATE MAIN TABLES
-- ============================================================================

-- Destinations table (unified structure matching sample data)
CREATE TABLE destinations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    slug VARCHAR(255) UNIQUE,
    description TEXT NOT NULL,
    long_description TEXT,
    category destination_category NOT NULL,
    
    -- Location data
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    district VARCHAR(100),
    province VARCHAR(100),
    region region_type,
    
    -- Rating and popularity
    rating DECIMAL(2,1) DEFAULT 0 CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER DEFAULT 0,
    popularity_score DECIMAL(3,2) DEFAULT 0 CHECK (popularity_score >= 0 AND popularity_score <= 1),
    
    -- Visit information
    visit_duration_hours DECIMAL(3,1) DEFAULT 2.0,
    difficulty_level difficulty_level DEFAULT 'easy',
    best_season season_type DEFAULT 'year_round',
    entry_fee_lkr DECIMAL(10, 2) DEFAULT 0,
    
    -- Structured data (JSONB for flexibility and performance)
    opening_hours JSONB DEFAULT '{}'::jsonb,
    facilities JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    images JSONB DEFAULT '[]'::jsonb,
    contact_info JSONB DEFAULT '{}'::jsonb,
    accessibility_features JSONB DEFAULT '[]'::jsonb,
    recommended_for JSONB DEFAULT '[]'::jsonb,
    suitable_for_budget JSONB DEFAULT '[]'::jsonb,
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Gallery table for destination images
CREATE TABLE gallery (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    alt_text VARCHAR(255),
    caption TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User profiles for personalization
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    
    -- Travel preferences
    travel_preferences JSONB DEFAULT '{}'::jsonb,
    interests JSONB DEFAULT '[]'::jsonb,
    budget_level budget_level DEFAULT 'mid_range',
    adventure_level INTEGER DEFAULT 3 CHECK (adventure_level >= 1 AND adventure_level <= 5),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews table
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    content TEXT,
    visit_date DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Itineraries table for saved travel plans
CREATE TABLE itineraries (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_days INTEGER NOT NULL CHECK (duration_days > 0),
    start_date DATE,
    
    -- Complete itinerary data as JSON
    itinerary_data JSONB NOT NULL,
    user_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- Budget and logistics
    total_budget DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'LKR',
    
    -- Status and visibility
    status VARCHAR(20) DEFAULT 'draft',
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Junction table for itinerary destinations
CREATE TABLE itinerary_destinations (
    id SERIAL PRIMARY KEY,
    itinerary_id INTEGER REFERENCES itineraries(id) ON DELETE CASCADE,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    day_number INTEGER NOT NULL,
    visit_order INTEGER NOT NULL,
    planned_duration_hours DECIMAL(3,1),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 4. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Destinations indexes
CREATE INDEX idx_destinations_category ON destinations(category);
CREATE INDEX idx_destinations_region ON destinations(region);
CREATE INDEX idx_destinations_location ON destinations(latitude, longitude);
CREATE INDEX idx_destinations_rating ON destinations(rating);
CREATE INDEX idx_destinations_popularity ON destinations(popularity_score);
CREATE INDEX idx_destinations_active ON destinations(is_active);
CREATE INDEX idx_destinations_tags ON destinations USING GIN(tags);
CREATE INDEX idx_destinations_facilities ON destinations USING GIN(facilities);

-- Gallery indexes
CREATE INDEX idx_gallery_destination ON gallery(destination_id);
CREATE INDEX idx_gallery_featured ON gallery(is_featured);

-- Reviews indexes
CREATE INDEX idx_reviews_destination ON reviews(destination_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- Itineraries indexes
CREATE INDEX idx_itineraries_user ON itineraries(user_id);
CREATE INDEX idx_itineraries_public ON itineraries(is_public);
CREATE INDEX idx_itineraries_duration ON itineraries(duration_days);

-- Itinerary destinations indexes
CREATE INDEX idx_itinerary_destinations_itinerary ON itinerary_destinations(itinerary_id);
CREATE INDEX idx_itinerary_destinations_day ON itinerary_destinations(day_number);

-- ============================================================================
-- 5. ENABLE ROW LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE destinations ENABLE ROW LEVEL SECURITY;
ALTER TABLE gallery ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE itinerary_destinations ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 6. CREATE RLS POLICIES
-- ============================================================================

-- Public read access to destinations and gallery
CREATE POLICY "Public destinations read" ON destinations FOR SELECT USING (is_active = true);
CREATE POLICY "Public gallery read" ON gallery FOR SELECT USING (true);

-- User profile policies
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Review policies
CREATE POLICY "Public reviews read" ON reviews FOR SELECT USING (true);
CREATE POLICY "Users can create reviews" ON reviews FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reviews" ON reviews FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reviews" ON reviews FOR DELETE USING (auth.uid() = user_id);

-- Itinerary policies
CREATE POLICY "Users can view own itineraries" ON itineraries FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own itineraries" ON itineraries FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own itineraries" ON itineraries FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own itineraries" ON itineraries FOR DELETE USING (auth.uid() = user_id);
CREATE POLICY "Public itineraries read" ON itineraries FOR SELECT USING (is_public = true);

-- Itinerary destinations inherit from itineraries
CREATE POLICY "Users can manage own itinerary destinations" ON itinerary_destinations FOR ALL USING (
    EXISTS (SELECT 1 FROM itineraries WHERE id = itinerary_id AND user_id = auth.uid())
);

-- ============================================================================
-- 7. CREATE HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_destinations_updated_at BEFORE UPDATE ON destinations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_itineraries_updated_at BEFORE UPDATE ON itineraries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. INSERT SAMPLE DATA
-- ============================================================================

-- Insert sample destinations
INSERT INTO destinations (
    name, slug, description, category, latitude, longitude, 
    rating, review_count, tags, entry_fee_lkr, opening_hours,
    visit_duration_hours, difficulty_level, best_season, facilities,
    contact_info, images, popularity_score, accessibility_features,
    recommended_for, suitable_for_budget, region, district, province,
    is_active, is_verified
) VALUES 

-- Sigiriya Rock Fortress
(
    'Sigiriya Rock Fortress',
    'sigiriya-rock-fortress',
    'Ancient rock fortress and UNESCO World Heritage site featuring stunning frescoes, water gardens, and panoramic views from the top.',
    'historical',
    7.9570, 80.7603,
    4.6, 15420,
    '["unesco", "historical", "climbing", "ancient", "fortress", "frescoes", "photography"]'::jsonb,
    5000.0,
    '{"monday": "7:00-17:30", "tuesday": "7:00-17:30", "wednesday": "7:00-17:30", "thursday": "7:00-17:30", "friday": "7:00-17:30", "saturday": "7:00-17:30", "sunday": "7:00-17:30"}'::jsonb,
    3.0, 'moderate', 'dry_season',
    '["parking", "restaurant", "souvenir_shop", "restrooms", "guide_service"]'::jsonb,
    '{"phone": "+94 66 228 6571", "website": "sigiriya.lk"}'::jsonb,
    '["sigiriya1.jpg", "sigiriya2.jpg"]'::jsonb,
    0.95,
    '["wheelchair_access_to_base"]'::jsonb,
    '["couple", "family", "group"]'::jsonb,
    '["mid_range", "luxury"]'::jsonb,
    'Central', 'Matale', 'Central',
    true, true
),

-- Temple of the Sacred Tooth Relic
(
    'Temple of the Sacred Tooth Relic (Sri Dalada Maligawa)',
    'temple-sacred-tooth-relic',
    'Sacred Buddhist temple housing the tooth relic of Buddha, featuring traditional Kandy architecture and daily ceremonial rituals.',
    'cultural',
    7.2955, 80.6415,
    4.5, 12890,
    '["buddhist", "temple", "sacred", "cultural", "kandy", "rituals", "architecture"]'::jsonb,
    1500.0,
    '{"monday": "5:30-20:00", "tuesday": "5:30-20:00", "wednesday": "5:30-20:00", "thursday": "5:30-20:00", "friday": "5:30-20:00", "saturday": "5:30-20:00", "sunday": "5:30-20:00"}'::jsonb,
    1.5, 'easy', 'year_round',
    '["parking", "security", "guide_service", "photography_area"]'::jsonb,
    '{"phone": "+94 81 234 4226"}'::jsonb,
    '["dalada_maligawa1.jpg"]'::jsonb,
    0.92,
    '["wheelchair_accessible"]'::jsonb,
    '["solo", "couple", "family"]'::jsonb,
    '["budget", "mid_range", "luxury"]'::jsonb,
    'Central', 'Kandy', 'Central',
    true, true
),

-- Ella Rock Hiking Trail
(
    'Ella Rock Hiking Trail',
    'ella-rock-hiking-trail',
    'Scenic hiking trail through tea plantations and forests leading to breathtaking panoramic views of Ella Gap and surrounding mountains.',
    'adventure',
    6.8667, 81.0500,
    4.7, 8945,
    '["hiking", "adventure", "mountains", "tea_plantations", "nature", "panoramic_views", "trekking"]'::jsonb,
    0.0,
    '{"monday": "6:00-18:00", "tuesday": "6:00-18:00", "wednesday": "6:00-18:00", "thursday": "6:00-18:00", "friday": "6:00-18:00", "saturday": "6:00-18:00", "sunday": "6:00-18:00"}'::jsonb,
    4.5, 'challenging', 'dry_season',
    '["trail_markers", "basic_restrooms"]'::jsonb,
    '{}'::jsonb,
    '["ella_rock1.jpg", "ella_rock2.jpg"]'::jsonb,
    0.88,
    '[]'::jsonb,
    '["solo", "couple", "group"]'::jsonb,
    '["budget", "mid_range"]'::jsonb,
    'Uva', 'Badulla', 'Uva',
    true, true
),

-- Yala National Park
(
    'Yala National Park',
    'yala-national-park',
    'Premier wildlife sanctuary famous for leopard sightings, elephants, and diverse bird species across varied ecosystems.',
    'wildlife',
    6.3725, 81.5119,
    4.4, 11250,
    '["safari", "wildlife", "leopards", "elephants", "birds", "nature", "photography"]'::jsonb,
    3500.0,
    '{"monday": "6:00-18:30", "tuesday": "closed", "wednesday": "6:00-18:30", "thursday": "6:00-18:30", "friday": "6:00-18:30", "saturday": "6:00-18:30", "sunday": "6:00-18:30"}'::jsonb,
    6.0, 'easy', 'dry_season',
    '["safari_vehicles", "guide_service", "visitor_center", "restrooms"]'::jsonb,
    '{"phone": "+94 47 203 9449", "website": "yalasrilanka.lk"}'::jsonb,
    '["yala1.jpg", "yala2.jpg", "yala3.jpg"]'::jsonb,
    0.91,
    '["vehicle_accessible"]'::jsonb,
    '["couple", "family", "group"]'::jsonb,
    '["mid_range", "luxury"]'::jsonb,
    'Southern', 'Hambantota', 'Southern',
    true, true
),

-- Galle Fort
(
    'Galle Fort',
    'galle-fort',
    '17th-century Dutch colonial fort with cobblestone streets, ramparts, museums, boutique shops, and stunning ocean views.',
    'historical',
    6.0267, 80.2170,
    4.5, 9876,
    '["dutch_colonial", "fort", "unesco", "ocean_views", "museums", "shopping", "architecture"]'::jsonb,
    0.0,
    '{"monday": "24_hours", "tuesday": "24_hours", "wednesday": "24_hours", "thursday": "24_hours", "friday": "24_hours", "saturday": "24_hours", "sunday": "24_hours"}'::jsonb,
    3.5, 'easy', 'year_round',
    '["parking", "restaurants", "shops", "museums", "restrooms"]'::jsonb,
    '{"website": "gallefort.gov.lk"}'::jsonb,
    '["galle_fort1.jpg", "galle_fort2.jpg"]'::jsonb,
    0.89,
    '["wheelchair_partial"]'::jsonb,
    '["solo", "couple", "family"]'::jsonb,
    '["budget", "mid_range", "luxury"]'::jsonb,
    'Southern', 'Galle', 'Southern',
    true, true
),

-- Mirissa Beach
(
    'Mirissa Beach',
    'mirissa-beach',
    'Pristine crescent-shaped beach famous for whale watching, surfing, and beautiful sunsets with palm-lined shores.',
    'beach',
    5.9487, 80.4563,
    4.3, 7654,
    '["beach", "whale_watching", "surfing", "sunset", "swimming", "relaxation", "seafood"]'::jsonb,
    0.0,
    '{"monday": "24_hours", "tuesday": "24_hours", "wednesday": "24_hours", "thursday": "24_hours", "friday": "24_hours", "saturday": "24_hours", "sunday": "24_hours"}'::jsonb,
    4.0, 'easy', 'dry_season',
    '["restaurants", "beach_bars", "water_sports", "parking"]'::jsonb,
    '{}'::jsonb,
    '["mirissa1.jpg", "mirissa2.jpg"]'::jsonb,
    0.85,
    '["beach_wheelchair"]'::jsonb,
    '["couple", "family", "group"]'::jsonb,
    '["budget", "mid_range"]'::jsonb,
    'Southern', 'Matara', 'Southern',
    true, true
),

-- Dambulla Cave Temple
(
    'Dambulla Cave Temple',
    'dambulla-cave-temple',
    'Ancient Buddhist cave temple complex with over 150 Buddha statues and intricate ceiling paintings dating back to 1st century BC.',
    'cultural',
    7.8567, 80.6482,
    4.4, 6789,
    '["buddhist", "caves", "ancient", "paintings", "statues", "unesco", "spiritual"]'::jsonb,
    1500.0,
    '{"monday": "7:00-19:00", "tuesday": "7:00-19:00", "wednesday": "7:00-19:00", "thursday": "7:00-19:00", "friday": "7:00-19:00", "saturday": "7:00-19:00", "sunday": "7:00-19:00"}'::jsonb,
    2.0, 'moderate', 'year_round',
    '["parking", "guide_service", "museum", "souvenir_shop"]'::jsonb,
    '{"phone": "+94 66 228 4873"}'::jsonb,
    '["dambulla1.jpg", "dambulla2.jpg"]'::jsonb,
    0.87,
    '["partial_wheelchair_access"]'::jsonb,
    '["solo", "couple", "family"]'::jsonb,
    '["budget", "mid_range", "luxury"]'::jsonb,
    'Central', 'Matale', 'Central',
    true, true
),

-- Horton Plains National Park
(
    'Horton Plains National Park',
    'horton-plains-national-park',
    'High-altitude plateau featuring World''s End cliff, Baker''s Falls, unique montane ecosystem, and endemic wildlife.',
    'nature',
    6.8061, 80.7950,
    4.6, 5432,
    '["national_park", "worlds_end", "cliff", "waterfall", "hiking", "endemic_species", "plateau"]'::jsonb,
    3000.0,
    '{"monday": "6:30-18:30", "tuesday": "6:30-18:30", "wednesday": "6:30-18:30", "thursday": "6:30-18:30", "friday": "6:30-18:30", "saturday": "6:30-18:30", "sunday": "6:30-18:30"}'::jsonb,
    5.0, 'moderate', 'dry_season',
    '["visitor_center", "guided_trails", "restrooms", "parking"]'::jsonb,
    '{"phone": "+94 52 222 8049"}'::jsonb,
    '["horton_plains1.jpg", "horton_plains2.jpg"]'::jsonb,
    0.83,
    '[]'::jsonb,
    '["solo", "couple", "group"]'::jsonb,
    '["mid_range", "luxury"]'::jsonb,
    'Central', 'Nuwara Eliya', 'Central',
    true, true
),

-- Nuwara Eliya Tea Plantations
(
    'Nuwara Eliya Tea Plantations',
    'nuwara-eliya-tea-plantations',
    'Scenic hill country tea estates with guided factory tours, tea tasting experiences, and stunning mountain vistas.',
    'nature',
    6.9497, 80.7891,
    4.2, 4567,
    '["tea_plantations", "factory_tours", "mountains", "scenic", "tasting", "hill_country"]'::jsonb,
    500.0,
    '{"monday": "8:00-17:00", "tuesday": "8:00-17:00", "wednesday": "8:00-17:00", "thursday": "8:00-17:00", "friday": "8:00-17:00", "saturday": "8:00-17:00", "sunday": "closed"}'::jsonb,
    2.5, 'easy', 'year_round',
    '["factory_tours", "tea_shop", "cafe", "parking"]'::jsonb,
    '{"phone": "+94 52 223 4681"}'::jsonb,
    '["tea_plantation1.jpg", "tea_plantation2.jpg"]'::jsonb,
    0.78,
    '["wheelchair_accessible"]'::jsonb,
    '["couple", "family", "group"]'::jsonb,
    '["budget", "mid_range", "luxury"]'::jsonb,
    'Central', 'Nuwara Eliya', 'Central',
    true, true
),

-- Nine Arch Bridge
(
    'Nine Arch Bridge',
    'nine-arch-bridge',
    'Iconic railway bridge built entirely of stone, brick and cement without steel, surrounded by lush green tea fields.',
    'photography',
    6.8832, 81.0587,
    4.5, 8901,
    '["railway", "bridge", "architecture", "photography", "train", "scenic", "ella"]'::jsonb,
    0.0,
    '{"monday": "24_hours", "tuesday": "24_hours", "wednesday": "24_hours", "thursday": "24_hours", "friday": "24_hours", "saturday": "24_hours", "sunday": "24_hours"}'::jsonb,
    1.5, 'easy', 'year_round',
    '["viewpoints", "walking_paths"]'::jsonb,
    '{}'::jsonb,
    '["nine_arch1.jpg", "nine_arch2.jpg"]'::jsonb,
    0.86,
    '["walking_required"]'::jsonb,
    '["solo", "couple", "family"]'::jsonb,
    '["budget", "mid_range", "luxury"]'::jsonb,
    'Uva', 'Badulla', 'Uva',
    true, true
);

-- ============================================================================
-- 9. INSERT SAMPLE GALLERY IMAGES
-- ============================================================================

INSERT INTO gallery (destination_id, image_url, alt_text, caption, is_featured, display_order) VALUES
(1, 'https://example.com/images/sigiriya_main.jpg', 'Sigiriya Rock Fortress view', 'Majestic view of Sigiriya Rock', true, 1),
(1, 'https://example.com/images/sigiriya_frescoes.jpg', 'Ancient frescoes at Sigiriya', 'Beautiful ancient frescoes', false, 2),
(2, 'https://example.com/images/tooth_temple_main.jpg', 'Temple of Tooth Relic', 'Sacred Buddhist temple in Kandy', true, 1),
(3, 'https://example.com/images/ella_rock_view.jpg', 'View from Ella Rock', 'Panoramic mountain views', true, 1),
(4, 'https://example.com/images/yala_leopard.jpg', 'Leopard in Yala', 'Magnificent leopard sighting', true, 1),
(5, 'https://example.com/images/galle_fort_walls.jpg', 'Galle Fort ramparts', 'Historic Dutch fort walls', true, 1);

-- ============================================================================
-- 10. INSERT SAMPLE USER PROFILES
-- ============================================================================

INSERT INTO user_profiles (id, email, full_name, interests, budget_level, adventure_level, travel_preferences) VALUES
(uuid_generate_v4(), 'demo@example.com', 'Demo User', 
 '["cultural", "nature", "photography"]'::jsonb, 'mid_range', 3,
 '{"preferred_duration": 7, "group_size": 2, "transportation": "private_car"}'::jsonb);

-- ============================================================================
-- 11. INSERT SAMPLE REVIEWS
-- ============================================================================

INSERT INTO reviews (destination_id, user_id, rating, title, content, visit_date) VALUES
(1, (SELECT id FROM user_profiles LIMIT 1), 5, 'Amazing historical site!', 'Sigiriya is absolutely breathtaking. The climb is challenging but the views are worth it.', '2024-12-15'),
(2, (SELECT id FROM user_profiles LIMIT 1), 4, 'Peaceful and spiritual', 'Beautiful temple with rich history. The evening ceremony is spectacular.', '2024-12-16'),
(4, (SELECT id FROM user_profiles LIMIT 1), 5, 'Best safari experience', 'Saw leopards, elephants, and countless birds. Guide was excellent!', '2024-12-17');

-- ============================================================================
-- 12. CREATE SAMPLE ITINERARY
-- ============================================================================

INSERT INTO itineraries (
    user_id, title, description, duration_days, start_date,
    itinerary_data, total_budget, is_public
) VALUES (
    (SELECT id FROM user_profiles LIMIT 1),
    'Classic Sri Lanka Adventure',
    'A 7-day journey through Sri Lanka''s cultural and natural highlights',
    7,
    '2025-02-01',
    '{
        "days": [
            {"day": 1, "destinations": [1], "activities": ["arrive", "visit_sigiriya"]},
            {"day": 2, "destinations": [2], "activities": ["temple_visit", "kandy_city"]},
            {"day": 3, "destinations": [3], "activities": ["ella_rock_hike"]},
            {"day": 4, "destinations": [4], "activities": ["yala_safari"]},
            {"day": 5, "destinations": [5], "activities": ["galle_fort_explore"]},
            {"day": 6, "destinations": [6], "activities": ["beach_relaxation"]},
            {"day": 7, "destinations": [], "activities": ["departure"]}
        ]
    }'::jsonb,
    75000.00,
    true
);

-- ============================================================================
-- 13. CREATE VIEWS FOR EASIER DATA ACCESS
-- ============================================================================

-- View for destinations with aggregated data
CREATE OR REPLACE VIEW destinations_summary AS
SELECT 
    d.*,
    COALESCE(r.avg_rating, d.rating) as calculated_rating,
    COALESCE(r.total_reviews, d.review_count) as total_reviews,
    g.featured_image
FROM destinations d
LEFT JOIN (
    SELECT 
        destination_id,
        AVG(rating::decimal) as avg_rating,
        COUNT(*) as total_reviews
    FROM reviews 
    GROUP BY destination_id
) r ON d.id = r.destination_id
LEFT JOIN (
    SELECT DISTINCT ON (destination_id)
        destination_id,
        image_url as featured_image
    FROM gallery 
    WHERE is_featured = true
    ORDER BY destination_id, display_order
) g ON d.id = g.destination_id
WHERE d.is_active = true;

-- ============================================================================
-- 14. VERIFICATION QUERIES
-- ============================================================================

-- Check if everything was created successfully
DO $$
BEGIN
    RAISE NOTICE 'Database setup completed successfully!';
    RAISE NOTICE 'Total destinations created: %', (SELECT COUNT(*) FROM destinations);
    RAISE NOTICE 'Total gallery images: %', (SELECT COUNT(*) FROM gallery);
    RAISE NOTICE 'Total user profiles: %', (SELECT COUNT(*) FROM user_profiles);
    RAISE NOTICE 'Total reviews: %', (SELECT COUNT(*) FROM reviews);
    RAISE NOTICE 'Total itineraries: %', (SELECT COUNT(*) FROM itineraries);
END $$;

-- Final verification select
SELECT 
    'Setup Complete' as status,
    COUNT(*) as destinations_count,
    COUNT(DISTINCT category) as categories_count,
    COUNT(DISTINCT region) as regions_count,
    AVG(rating) as average_rating
FROM destinations 
WHERE is_active = true;

-- ============================================================================
-- SETUP COMPLETE!
-- Your database is now ready with:
-- - 10 sample destinations across Sri Lanka
-- - Proper indexes for performance
-- - Row Level Security enabled
-- - Sample user profiles and reviews
-- - A sample itinerary
-- - Helper views for easier data access
-- ============================================================================
