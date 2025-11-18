-- Add voice preferences to user settings
-- This allows users to choose their preferred TTS engine

CREATE TABLE IF NOT EXISTS user_voice_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    engine_preference VARCHAR(20) DEFAULT 'auto' CHECK (engine_preference IN ('auto', 'gtts', 'azure', 'coqui')),
    language_preference VARCHAR(10) DEFAULT 'auto',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_voice_prefs_user_id ON user_voice_preferences(user_id);

-- Function to auto-create default voice preferences for new users
CREATE OR REPLACE FUNCTION create_default_voice_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_voice_preferences (user_id, engine_preference, language_preference)
    VALUES (NEW.id, 'auto', 'auto');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create voice preferences on user signup
DROP TRIGGER IF EXISTS trigger_create_voice_preferences ON users;
CREATE TRIGGER trigger_create_voice_preferences
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_default_voice_preferences();

-- Add voice preferences for existing users
INSERT INTO user_voice_preferences (user_id, engine_preference, language_preference)
SELECT id, 'auto', 'auto'
FROM users
WHERE id NOT IN (SELECT user_id FROM user_voice_preferences);
