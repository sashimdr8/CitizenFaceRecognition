# Face Recognition User Registration System

A simple face-recognition user registration system built with Streamlit, InsightFace, and Supabase.

## Features

- **User Registration**: Register users with name, citizenship number, address, state, and face photo
- **Face Recognition**: Upload or capture a photo to identify registered users
- **Recognition Logging**: Automatically logs all recognition attempts with status, similarity, and photo
- **Vector Search**: Uses pgvector for efficient face embedding similarity search
- **Secure**: Masks citizenship numbers in recognition results

## Technology Stack

- **Language**: Python
- **UI**: Streamlit
- **Face Recognition**: InsightFace
- **ML Runtime**: ONNX Runtime
- **Database**: Supabase PostgreSQL with pgvector
- **Deployment**: Railway (Docker)

## Prerequisites

- Python 3.11+
- Supabase account (Free tier available)
- Railway account (Free tier available)

## Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd FaceRecongtion
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Open the SQL Editor and run the following:

```sql
-- Enable pgvector
create extension if not exists vector;

-- Create users table
create table users (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    citizenship_number text not null unique,
    address text not null,
    state text not null,
    photo_url text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Create face_embeddings table (replace 512 with your model's dimension)
create table face_embeddings (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    embedding vector(512) not null,
    created_at timestamptz not null default now()
);

-- Create indexes
create index idx_users_citizenship on users(citizenship_number);
create index idx_face_embeddings_user on face_embeddings(user_id);

-- Create similarity search function (replace 512 with your model's dimension)
create or replace function match_face(
    query_embedding vector(512),
    match_threshold float,
    match_count int
)
returns table (
    user_id uuid,
    similarity float
)
language sql
as $$
    select
        fe.user_id,
        1 - (fe.embedding <=> query_embedding) as similarity
    from face_embeddings fe
    where 1 - (fe.embedding <=> query_embedding) >= match_threshold
    order by fe.embedding <=> query_embedding
    limit match_count;
$$;

-- Create recognition_logs table to track all recognition attempts
create table recognition_logs (
    id uuid primary key default gen_random_uuid(),
    status text not null,  -- 'success', 'no_match', 'error'
    matched_user_id uuid references users(id) on delete set null,
    similarity float,
    photo_url text,  -- URL to photo stored in Supabase Storage
    error_message text,
    created_at timestamptz not null default now()
);

-- Create index for recognition logs
create index idx_recognition_logs_created on recognition_logs(created_at desc);
```

3. Create a Storage bucket for recognition photos:
   - Go to "Storage" in the left sidebar
   - Click "New bucket"
   - Name it `recognition-photos`
   - Make it public (or configure appropriate access policies)

4. Get your Supabase URL and Key from Project Settings > API

### 5. Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_KEY
```

### 6. Run Locally

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

## Docker Deployment

### Build Docker Image

```bash
docker build -t face-recognition .
```

### Run with Docker

```bash
docker run -p 8501:8501 --env-file .env face-recognition
```

## Railway Deployment

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo>
git push -u origin main
```

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Select "Deploy from GitHub Repo"
4. Choose your repository
5. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
6. Deploy

## Project Structure

```
FaceRecongtion/
├── app.py                      # Main Streamlit application
├── requirements.txt             # Python dependencies
├── Dockerfile                  # Docker configuration
├── .dockerignore              # Docker ignore file
├── .gitignore                 # Git ignore file
├── .env.example               # Environment variables template
├── README.md                  # This file
├── DEVELOPMENT_GUIDE.md       # Detailed development guide
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── database/
│   └── supabase_client.py     # Supabase client setup
├── services/
│   ├── face_service.py        # Face detection and embedding
│   └── user_service.py        # User operations
└── utils/
    └── image_utils.py         # Image processing utilities
```

## Usage

### Register User

1. Navigate to "Register User" page
2. Fill in the form:
   - Name
   - Citizenship Number
   - Address
   - State / Province
   - Upload a photo (must contain exactly one face)
3. Click "Register User"

### Recognize Face

1. Navigate to "Recognize Face" page
2. Either:
   - Capture a photo using the camera, or
   - Upload a photo
3. Click "Recognize"
4. View the matched user information

**Note**: All recognition attempts are automatically logged to the `recognition_logs` table with:
- Status (success, no_match, error)
- Matched user ID (if applicable)
- Similarity score (if successful)
- Photo URL (stored in Supabase Storage to avoid database bloat)
- Error message (if failed)

## Important Notes

- The similarity threshold is set to 0.5 by default. Adjust this based on your testing.
- Citizenship numbers are masked in recognition results for security.
- The InsightFace model uses the "buffalo_l" model by default.
- Railway's free tier has 0.5 GB RAM - ensure your model fits within this limit.

## Security Considerations

- Never commit `.env` file to version control
- Enable Row Level Security (RLS) in Supabase for production
- Implement authentication before production deployment
- Do not log face embeddings or sensitive user data

## Troubleshooting

### Model Loading Issues

If the InsightFace model fails to load due to memory constraints:
- Try a smaller model in `services/face_service.py`
- Upgrade to a paid Railway plan with more RAM

### Database Connection Issues

- Verify your Supabase URL and Key in `.env`
- Check that pgvector is enabled in your Supabase project
- Ensure the `match_face` function is created in SQL Editor

### Face Detection Issues

- Ensure uploaded images contain exactly one face
- Check image quality and lighting
- Verify the image format is supported (jpg, jpeg, png)

## License

This project is provided as-is for educational and development purposes.
