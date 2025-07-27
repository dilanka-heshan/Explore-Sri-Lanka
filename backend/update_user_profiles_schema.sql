-- Update user_profiles table to add missing columns for authentication
-- Run this in your Supabase SQL Editor

-- Add missing columns to user_profiles table
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS nationality VARCHAR(100),
ADD COLUMN IF NOT EXISTS location VARCHAR(255),
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user',
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Add constraints for role if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_profiles_role_check') THEN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_role_check 
        CHECK (role IN ('user', 'admin', 'moderator'));
    END IF;
END $$;

-- Make email NOT NULL if not already
ALTER TABLE user_profiles ALTER COLUMN email SET NOT NULL;

-- Add unique constraint on email if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_profiles_email_key') THEN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_email_key UNIQUE (email);
    END IF;
END $$;

-- Create missing auth-related tables if they don't exist

-- User saved destinations
CREATE TABLE IF NOT EXISTS user_saved_destinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    destination_id INTEGER REFERENCES destinations(id) ON DELETE CASCADE,
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, destination_id)
);

-- User saved itineraries
CREATE TABLE IF NOT EXISTS user_saved_itineraries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    itinerary_id INTEGER REFERENCES itineraries(id) ON DELETE CASCADE,
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, itinerary_id)
);

-- Email verification tokens
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Password reset tokens
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_saved_destinations_user ON user_saved_destinations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_saved_destinations_destination ON user_saved_destinations(destination_id);
CREATE INDEX IF NOT EXISTS idx_user_saved_itineraries_user ON user_saved_itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user ON email_verification_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user ON password_reset_tokens(user_id);

-- Update RLS policies for new tables
ALTER TABLE user_saved_destinations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_saved_itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_verification_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- RLS policies for user saved destinations
DROP POLICY IF EXISTS "Users can manage own saved destinations" ON user_saved_destinations;
CREATE POLICY "Users can manage own saved destinations" ON user_saved_destinations FOR ALL USING (auth.uid() = user_id);

-- RLS policies for user saved itineraries
DROP POLICY IF EXISTS "Users can manage own saved itineraries" ON user_saved_itineraries;
CREATE POLICY "Users can manage own saved itineraries" ON user_saved_itineraries FOR ALL USING (auth.uid() = user_id);

-- RLS policies for email verification tokens
DROP POLICY IF EXISTS "Users can manage own email tokens" ON email_verification_tokens;
CREATE POLICY "Users can manage own email tokens" ON email_verification_tokens FOR ALL USING (auth.uid() = user_id);

-- RLS policies for password reset tokens
DROP POLICY IF EXISTS "Users can manage own password tokens" ON password_reset_tokens;
CREATE POLICY "Users can manage own password tokens" ON password_reset_tokens FOR ALL USING (auth.uid() = user_id);

-- Add missing triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add trigger to user_profiles if not exists
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

SELECT 'User profiles schema updated successfully!' as status;
