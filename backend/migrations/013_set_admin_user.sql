-- Set admin access for a specific user
-- Replace 'your-email@example.com' with your actual email address

-- IMPORTANT: Update the email below to your email address before running!
UPDATE users
SET is_admin = true,
    admin_notes = 'Primary admin - set via migration'
WHERE email = 'choudharikiranv2003@gmail.com';

-- Verify the update
SELECT id, email, is_admin, created_at
FROM users
WHERE is_admin = true;

-- Alternative: If you want to set the FIRST registered user as admin:
-- UPDATE users
-- SET is_admin = true,
--     admin_notes = 'Primary admin - first user'
-- WHERE id = (SELECT id FROM users ORDER BY created_at ASC LIMIT 1);
