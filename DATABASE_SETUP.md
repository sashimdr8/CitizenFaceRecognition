# Database Setup Instructions

## Issue: photo_url not being saved

The `photo_url` column may be missing from your `users` table in Supabase.

## Solution

### Step 1: Add the photo_url column

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `add_photo_url_column.sql`
4. Click **Run** to execute the SQL

### Step 2: Verify the column exists

After running the SQL, you should see output confirming the column was added.

You can also check in the **Table Editor**:
1. Go to **Table Editor** in Supabase
2. Select the `users` table
3. Verify that `photo_url` column exists (type: TEXT)

### Step 3: Test registration

1. Run your Streamlit app
2. Try registering a new user with a photo
3. Check the terminal/console for debug messages:
   - `[DEBUG] Creating user with photo_url: <url>` - Confirms photo_url is being passed
   - `[SUCCESS] Photo uploaded successfully!` - Confirms upload worked
   - `[DEBUG] Created user: {...}` - Shows the created user data

### Step 4: Verify in database

1. Go to **Table Editor** in Supabase
2. Select the `users` table
3. Check that the newly created user has a `photo_url` value

## Storage Setup

Make sure you have the storage bucket configured:

1. Go to **Storage** in Supabase Dashboard
2. Create a bucket named `recognition-photos` if it doesn't exist
3. Make the bucket **public** (or configure appropriate policies)
4. Create folders: `users` and `logs`

## Common Issues

- **"Bucket not found"**: Create the `recognition-photos` bucket
- **"Permission denied"**: Make the bucket public or add storage policies
- **Column still empty**: The column might not exist - run the SQL migration
- **NULL values in photo_url**: Old users won't have photos - only new registrations will have them
