-- Create user plans table
CREATE TABLE IF NOT EXISTS user_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    plan_type VARCHAR(20) DEFAULT 'free' CHECK (plan_type IN ('free', 'student', 'premium')),
    max_documents INTEGER DEFAULT 5,
    max_queries_per_day INTEGER DEFAULT 50,
    features JSONB DEFAULT '{"voice": true, "api_access": false}'::jsonb,
    active_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_plans_user_id ON user_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_user_plans_plan_type ON user_plans(plan_type);

-- Function to auto-create free plan for new users
CREATE OR REPLACE FUNCTION create_default_user_plan()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_plans (user_id, plan_type, max_documents, max_queries_per_day)
    VALUES (NEW.id, 'free', 5, 50);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create plan on user signup
DROP TRIGGER IF EXISTS trigger_create_user_plan ON users;
CREATE TRIGGER trigger_create_user_plan
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_default_user_plan();
