-- Add photo_url column to users table if it doesn't exist
-- Run this in your Supabase SQL Editor

-- Check if column exists and add it if not
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'photo_url'
    ) THEN
        ALTER TABLE users ADD COLUMN photo_url TEXT;
        RAISE NOTICE 'Column photo_url added to users table';
    ELSE
        RAISE NOTICE 'Column photo_url already exists in users table';
    END IF;
END $$;

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users';
