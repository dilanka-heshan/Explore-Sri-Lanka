-- Minimal schema update for user authentication
-- Run this in your Supabase SQL Editor FIRST

-- Add the essential missing columns to user_profiles table
DO $$ 
BEGIN
    -- Add password_hash column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='password_hash') THEN
        ALTER TABLE user_profiles ADD COLUMN password_hash VARCHAR(255);
    END IF;
    
    -- Add bio column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='bio') THEN
        ALTER TABLE user_profiles ADD COLUMN bio TEXT;
    END IF;
    
    -- Add phone column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='phone') THEN
        ALTER TABLE user_profiles ADD COLUMN phone VARCHAR(50);
    END IF;
    
    -- Add date_of_birth column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='date_of_birth') THEN
        ALTER TABLE user_profiles ADD COLUMN date_of_birth DATE;
    END IF;
    
    -- Add nationality column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='nationality') THEN
        ALTER TABLE user_profiles ADD COLUMN nationality VARCHAR(100);
    END IF;
    
    -- Add location column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='location') THEN
        ALTER TABLE user_profiles ADD COLUMN location VARCHAR(255);
    END IF;
    
    -- Add role column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='role') THEN
        ALTER TABLE user_profiles ADD COLUMN role VARCHAR(20) DEFAULT 'user';
    END IF;
    
    -- Add email_verified column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='email_verified') THEN
        ALTER TABLE user_profiles ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Add is_active column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='is_active') THEN
        ALTER TABLE user_profiles ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
    
    -- Add last_login column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='user_profiles' AND column_name='last_login') THEN
        ALTER TABLE user_profiles ADD COLUMN last_login TIMESTAMP WITH TIME ZONE;
    END IF;
    
    RAISE NOTICE 'Essential columns added to user_profiles table';
END $$;

-- Make sure email is NOT NULL and unique
ALTER TABLE user_profiles ALTER COLUMN email SET NOT NULL;

-- Add unique constraint on email if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_profiles_email_key') THEN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_email_key UNIQUE (email);
    END IF;
END $$;

-- Add role constraint if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_profiles_role_check') THEN
        ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_role_check 
        CHECK (role IN ('user', 'admin', 'moderator'));
    END IF;
END $$;

SELECT 'Minimal user_profiles schema update completed!' as status;
