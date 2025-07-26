-- Enhanced Travel Plans Database Schema
-- This creates comprehensive tables for storing user travel plans with PDF generation support

-- Main travel plans table
CREATE TABLE IF NOT EXISTS user_travel_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Plan metadata
    title VARCHAR(200) NOT NULL,
    description TEXT,
    destination_summary TEXT NOT NULL,
    trip_duration_days INTEGER NOT NULL CHECK (trip_duration_days > 0),
    budget_level VARCHAR(20) NOT NULL CHECK (budget_level IN ('budget', 'mid_range', 'luxury')),
    trip_type VARCHAR(20) NOT NULL CHECK (trip_type IN ('solo', 'couple', 'family', 'group')),
    
    -- Original planning request
    original_query TEXT NOT NULL,
    interests TEXT[] DEFAULT '{}',
    
    -- Generated travel plan (stored as JSONB for efficient querying)
    travel_plan_data JSONB NOT NULL,
    
    -- Enhancement flags
    has_places_enhancement BOOLEAN DEFAULT FALSE,
    has_ai_enhancement BOOLEAN DEFAULT FALSE,
    clustering_method VARCHAR(50),
    
    -- Trip status and privacy
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'cancelled', 'archived')),
    privacy VARCHAR(20) DEFAULT 'private' CHECK (privacy IN ('private', 'public', 'shared')),
    
    -- User interaction
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_notes TEXT,
    favorite BOOLEAN DEFAULT FALSE,
    
    -- Trip dates
    planned_start_date TIMESTAMP WITH TIME ZONE,
    actual_start_date TIMESTAMP WITH TIME ZONE,
    actual_end_date TIMESTAMP WITH TIME ZONE,
    
    -- Sharing and collaboration
    shared_with UUID[] DEFAULT '{}',
    collaboration_enabled BOOLEAN DEFAULT FALSE,
    
    -- Analytics
    times_viewed INTEGER DEFAULT 0,
    times_downloaded INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    
    -- PDF generation
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_file_path TEXT,
    pdf_generated_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Cost tracking (stored as JSONB)
    estimated_cost JSONB,
    actual_cost JSONB,
    
    -- Modifications history (stored as JSONB array)
    modifications JSONB DEFAULT '[]'::jsonb
);

-- Travel plan sharing table
CREATE TABLE IF NOT EXISTS travel_plan_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    travel_plan_id UUID NOT NULL REFERENCES user_travel_plans(id) ON DELETE CASCADE,
    shared_by_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    shared_with_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    can_edit BOOLEAN DEFAULT FALSE,
    shared_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE,
    message TEXT,
    
    UNIQUE(travel_plan_id, shared_with_user_id)
);

-- Travel plan modifications log
CREATE TABLE IF NOT EXISTS travel_plan_modifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    travel_plan_id UUID NOT NULL REFERENCES user_travel_plans(id) ON DELETE CASCADE,
    modified_by_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    modification_type VARCHAR(50) NOT NULL, -- 'created', 'updated', 'status_changed', 'shared', etc.
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PDF generation log
CREATE TABLE IF NOT EXISTS travel_plan_pdfs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    travel_plan_id UUID NOT NULL REFERENCES user_travel_plans(id) ON DELETE CASCADE,
    generated_by_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    generation_time_seconds FLOAT,
    include_maps BOOLEAN DEFAULT TRUE,
    include_photos BOOLEAN DEFAULT TRUE,
    include_weather BOOLEAN DEFAULT TRUE,
    custom_title TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    downloaded_count INTEGER DEFAULT 0,
    last_downloaded TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_user_id ON user_travel_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_status ON user_travel_plans(status);
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_created_at ON user_travel_plans(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_planned_start_date ON user_travel_plans(planned_start_date);
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_favorite ON user_travel_plans(favorite) WHERE favorite = TRUE;
CREATE INDEX IF NOT EXISTS idx_user_travel_plans_search ON user_travel_plans USING gin((title || ' ' || destination_summary || ' ' || original_query));

CREATE INDEX IF NOT EXISTS idx_travel_plan_shares_shared_with ON travel_plan_shares(shared_with_user_id);
CREATE INDEX IF NOT EXISTS idx_travel_plan_shares_travel_plan ON travel_plan_shares(travel_plan_id);

CREATE INDEX IF NOT EXISTS idx_travel_plan_modifications_plan ON travel_plan_modifications(travel_plan_id);
CREATE INDEX IF NOT EXISTS idx_travel_plan_modifications_created_at ON travel_plan_modifications(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_travel_plan_pdfs_plan ON travel_plan_pdfs(travel_plan_id);
CREATE INDEX IF NOT EXISTS idx_travel_plan_pdfs_generated_at ON travel_plan_pdfs(generated_at DESC);

-- Create updated_at trigger for user_travel_plans
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_travel_plans_updated_at 
    BEFORE UPDATE ON user_travel_plans 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Views for common queries
-- User travel plan summary view
CREATE OR REPLACE VIEW user_travel_plan_summary AS
SELECT 
    utp.id,
    utp.user_id,
    utp.title,
    utp.destination_summary,
    utp.trip_duration_days,
    utp.budget_level,
    utp.trip_type,
    utp.status,
    utp.favorite,
    utp.user_rating,
    utp.planned_start_date,
    utp.created_at,
    utp.updated_at,
    utp.times_viewed,
    utp.pdf_generated,
    COUNT(tps.id) as share_count,
    COUNT(tpm.id) as modification_count
FROM user_travel_plans utp
LEFT JOIN travel_plan_shares tps ON utp.id = tps.travel_plan_id
LEFT JOIN travel_plan_modifications tpm ON utp.id = tpm.travel_plan_id
GROUP BY utp.id;

-- User travel stats view
CREATE OR REPLACE VIEW user_travel_stats AS
SELECT 
    user_id,
    COUNT(*) as total_plans,
    COUNT(*) FILTER (WHERE status = 'draft') as draft_plans,
    COUNT(*) FILTER (WHERE status = 'active') as active_plans,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_plans,
    COUNT(*) FILTER (WHERE favorite = TRUE) as favorite_plans,
    SUM(trip_duration_days) as total_trip_days,
    AVG(user_rating) as average_rating,
    COUNT(*) FILTER (WHERE pdf_generated = TRUE) as plans_with_pdf,
    MAX(created_at) as last_plan_created,
    MIN(created_at) as first_plan_created
FROM user_travel_plans
GROUP BY user_id;

-- Shared plans view (for users to see plans shared with them)
CREATE OR REPLACE VIEW shared_travel_plans_view AS
SELECT 
    tps.id as share_id,
    tps.travel_plan_id,
    tps.shared_by_user_id,
    tps.shared_with_user_id,
    tps.can_edit,
    tps.shared_at,
    tps.last_accessed,
    tps.message,
    utp.title,
    utp.destination_summary,
    utp.trip_duration_days,
    utp.budget_level,
    utp.trip_type,
    utp.status,
    utp.planned_start_date,
    sb.email as shared_by_email,
    sb.raw_user_meta_data->>'full_name' as shared_by_name
FROM travel_plan_shares tps
JOIN user_travel_plans utp ON tps.travel_plan_id = utp.id
JOIN auth.users sb ON tps.shared_by_user_id = sb.id;

-- RLS (Row Level Security) Policies
ALTER TABLE user_travel_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plan_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plan_modifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE travel_plan_pdfs ENABLE ROW LEVEL SECURITY;

-- Policies for user_travel_plans
CREATE POLICY "Users can view their own travel plans" ON user_travel_plans
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view shared travel plans" ON user_travel_plans
    FOR SELECT USING (
        auth.uid() = ANY(shared_with) OR 
        privacy = 'public' OR
        EXISTS (
            SELECT 1 FROM travel_plan_shares 
            WHERE travel_plan_id = id AND shared_with_user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own travel plans" ON user_travel_plans
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own travel plans" ON user_travel_plans
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Shared users can update travel plans if allowed" ON user_travel_plans
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM travel_plan_shares 
            WHERE travel_plan_id = id 
            AND shared_with_user_id = auth.uid() 
            AND can_edit = TRUE
        )
    );

CREATE POLICY "Users can delete their own travel plans" ON user_travel_plans
    FOR DELETE USING (auth.uid() = user_id);

-- Policies for travel_plan_shares
CREATE POLICY "Users can view shares they created or received" ON travel_plan_shares
    FOR SELECT USING (
        auth.uid() = shared_by_user_id OR 
        auth.uid() = shared_with_user_id
    );

CREATE POLICY "Users can create shares for their own travel plans" ON travel_plan_shares
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_travel_plans 
            WHERE id = travel_plan_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete shares they created" ON travel_plan_shares
    FOR DELETE USING (auth.uid() = shared_by_user_id);

-- Policies for travel_plan_modifications
CREATE POLICY "Users can view modifications for accessible travel plans" ON travel_plan_modifications
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_travel_plans utp
            WHERE utp.id = travel_plan_id 
            AND (
                utp.user_id = auth.uid() OR
                auth.uid() = ANY(utp.shared_with) OR
                EXISTS (
                    SELECT 1 FROM travel_plan_shares tps
                    WHERE tps.travel_plan_id = utp.id AND tps.shared_with_user_id = auth.uid()
                )
            )
        )
    );

CREATE POLICY "Users can insert modifications for accessible travel plans" ON travel_plan_modifications
    FOR INSERT WITH CHECK (
        auth.uid() = modified_by_user_id AND
        EXISTS (
            SELECT 1 FROM user_travel_plans utp
            WHERE utp.id = travel_plan_id 
            AND (
                utp.user_id = auth.uid() OR
                EXISTS (
                    SELECT 1 FROM travel_plan_shares tps
                    WHERE tps.travel_plan_id = utp.id 
                    AND tps.shared_with_user_id = auth.uid() 
                    AND tps.can_edit = TRUE
                )
            )
        )
    );

-- Policies for travel_plan_pdfs
CREATE POLICY "Users can view PDFs for accessible travel plans" ON travel_plan_pdfs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM user_travel_plans utp
            WHERE utp.id = travel_plan_id 
            AND (
                utp.user_id = auth.uid() OR
                auth.uid() = ANY(utp.shared_with) OR
                EXISTS (
                    SELECT 1 FROM travel_plan_shares tps
                    WHERE tps.travel_plan_id = utp.id AND tps.shared_with_user_id = auth.uid()
                )
            )
        )
    );

CREATE POLICY "Users can create PDFs for accessible travel plans" ON travel_plan_pdfs
    FOR INSERT WITH CHECK (
        auth.uid() = generated_by_user_id AND
        EXISTS (
            SELECT 1 FROM user_travel_plans utp
            WHERE utp.id = travel_plan_id 
            AND (
                utp.user_id = auth.uid() OR
                EXISTS (
                    SELECT 1 FROM travel_plan_shares tps
                    WHERE tps.travel_plan_id = utp.id AND tps.shared_with_user_id = auth.uid()
                )
            )
        )
    );

-- Comments for documentation
COMMENT ON TABLE user_travel_plans IS 'Main table storing user-generated travel plans with comprehensive metadata and plan data';
COMMENT ON TABLE travel_plan_shares IS 'Table managing sharing of travel plans between users with permission controls';
COMMENT ON TABLE travel_plan_modifications IS 'Audit log of all modifications made to travel plans';
COMMENT ON TABLE travel_plan_pdfs IS 'Log of PDF generation requests and file metadata';

COMMENT ON COLUMN user_travel_plans.travel_plan_data IS 'Complete travel plan stored as JSONB for efficient querying and flexibility';
COMMENT ON COLUMN user_travel_plans.modifications IS 'Array of modification history stored as JSONB';
COMMENT ON COLUMN user_travel_plans.estimated_cost IS 'Estimated costs breakdown stored as JSONB with currency and category details';
COMMENT ON COLUMN user_travel_plans.actual_cost IS 'Actual costs breakdown stored as JSONB for completed trips';
