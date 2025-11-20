-- Site Feedback Table
-- Stores comprehensive user feedback about the entire application

CREATE TABLE IF NOT EXISTS site_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Overall satisfaction (1-5 stars)
    overall_rating INTEGER NOT NULL CHECK (overall_rating >= 1 AND overall_rating <= 5),

    -- Category-specific ratings
    ease_of_use_rating INTEGER CHECK (ease_of_use_rating >= 1 AND ease_of_use_rating <= 5),
    features_rating INTEGER CHECK (features_rating >= 1 AND features_rating <= 5),
    performance_rating INTEGER CHECK (performance_rating >= 1 AND performance_rating <= 5),

    -- Feedback type
    feedback_type VARCHAR(50) NOT NULL, -- 'bug', 'feature_request', 'improvement', 'praise', 'other'

    -- User feedback
    feedback_title VARCHAR(200),
    feedback_message TEXT NOT NULL,

    -- What user likes most
    likes TEXT,

    -- What user wants improved
    improvements TEXT,

    -- Would recommend? (NPS score)
    would_recommend BOOLEAN,
    nps_score INTEGER CHECK (nps_score >= 0 AND nps_score <= 10),

    -- Contact preferences
    can_contact BOOLEAN DEFAULT false,
    contact_email VARCHAR(255),

    -- Device/Browser info (auto-captured)
    user_agent TEXT,
    screen_resolution VARCHAR(50),
    browser_info JSONB,

    -- Current page when feedback submitted
    page_url TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Status tracking (for admin review)
    status VARCHAR(20) DEFAULT 'new', -- 'new', 'reviewed', 'in_progress', 'resolved'
    admin_notes TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_site_feedback_user_id ON site_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_site_feedback_created_at ON site_feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_site_feedback_type ON site_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_site_feedback_status ON site_feedback(status);
CREATE INDEX IF NOT EXISTS idx_site_feedback_rating ON site_feedback(overall_rating);

-- Enable RLS (Row Level Security)
ALTER TABLE site_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can view their own feedback
CREATE POLICY "Users can view own feedback"
    ON site_feedback FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own feedback
CREATE POLICY "Users can insert own feedback"
    ON site_feedback FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own feedback (within 24 hours)
CREATE POLICY "Users can update own feedback within 24h"
    ON site_feedback FOR UPDATE
    USING (
        auth.uid() = user_id
        AND created_at > NOW() - INTERVAL '24 hours'
    );

-- Comment for documentation
COMMENT ON TABLE site_feedback IS 'Stores user feedback about the entire application experience';
COMMENT ON COLUMN site_feedback.overall_rating IS 'Overall satisfaction rating (1-5 stars)';
COMMENT ON COLUMN site_feedback.feedback_type IS 'Category of feedback: bug, feature_request, improvement, praise, other';
COMMENT ON COLUMN site_feedback.nps_score IS 'Net Promoter Score (0-10): How likely to recommend to others';
COMMENT ON COLUMN site_feedback.status IS 'Admin tracking: new, reviewed, in_progress, resolved';
