-- Add admin role to users table
-- This allows certain users to access the admin dashboard

-- Add is_admin column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='is_admin') THEN
        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Add admin_notes column for internal notes
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='users' AND column_name='admin_notes') THEN
        ALTER TABLE users ADD COLUMN admin_notes TEXT;
    END IF;
END $$;

-- Create index for faster admin queries
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin) WHERE is_admin = true;

-- ⚠️ DO NOT COMMIT YOUR EMAIL TO GIT! ⚠️
-- To grant admin access to yourself:
-- 1. Sign up normally at your app
-- 2. Go to Supabase Dashboard → Table Editor → users
-- 3. Find your user row
-- 4. Set is_admin = true for your account
-- OR run this SQL in Supabase SQL Editor (NEVER commit this to Git):
-- UPDATE users SET is_admin = true WHERE email = 'your-email-here@example.com';

COMMENT ON COLUMN users.is_admin IS 'Whether user has admin dashboard access';
COMMENT ON COLUMN users.admin_notes IS 'Internal admin notes about this user';
