-- Create migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(255) UNIQUE NOT NULL,
    executed_at TIMESTAMP DEFAULT NOW()
);

-- Create index on version
CREATE INDEX IF NOT EXISTS idx_migrations_version ON schema_migrations(version);
