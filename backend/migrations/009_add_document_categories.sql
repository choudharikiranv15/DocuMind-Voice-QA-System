-- Add categories and metadata to documents table
-- This enables document organization and search functionality

-- Add new columns to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'general';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS page_count INTEGER;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS chunk_count INTEGER;

-- Create index for category searches
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);

-- Create GIN index for tag searches (fast array searches)
CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents USING GIN(tags);

-- Create full-text search index on filename and description
CREATE INDEX IF NOT EXISTS idx_documents_search ON documents USING GIN(to_tsvector('english', filename || ' ' || COALESCE(description, '')));

-- Update existing documents to have default values
UPDATE documents SET category = 'general' WHERE category IS NULL;
UPDATE documents SET tags = '{}' WHERE tags IS NULL;

-- Create document_categories reference table for predefined categories
CREATE TABLE IF NOT EXISTS document_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50),
    color VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default categories
INSERT INTO document_categories (name, icon, color, description) VALUES
    ('general', '📄', '#6B7280', 'General documents and files'),
    ('study', '📚', '#3B82F6', 'Study materials and notes'),
    ('research', '🔬', '#8B5CF6', 'Research papers and articles'),
    ('work', '💼', '#10B981', 'Work-related documents'),
    ('personal', '👤', '#F59E0B', 'Personal documents'),
    ('other', '📁', '#6B7280', 'Other documents')
ON CONFLICT (name) DO NOTHING;
