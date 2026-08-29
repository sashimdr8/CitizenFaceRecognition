# Face Recognition User Registration System

## Streamlit + InsightFace + Supabase + pgvector

---

# 1. Overview

This project is a simple face-recognition user registration system.

Users can register their personal information and a face photo:

- Name
- Citizenship Number
- Address
- State / Province
- Face Photo

The application uses InsightFace to generate a face embedding from the uploaded photo.

The embedding is stored in Supabase PostgreSQL using pgvector.

Later, a user can upload or capture another face photo and the application will search the stored embeddings to identify the matching registered user.

The system does **not** include:

- Attendance
- Check-in/check-out
- Organisations
- Leave management
- Payroll
- Scheduling
- Analytics
- Redis
- Celery
- Background workers

The goal is to keep the first version simple and easy to deploy.

---

# 2. Core Features

## User Registration

The registration form contains:

```text
Name
Citizenship Number
Address
State / Province
Photo
```

Example:

```
Name:
John Doe

Citizenship Number:
12-34-56-78901

Address:
Kathmandu

State / Province:
Bagmati

Photo:
[ Upload Photo ]

[ Register User ]
```

## 3. Face Recognition

The recognition page allows a user to:

- Upload a photo or capture one using the camera.
- Detect the face.
- Generate a face embedding.
- Search registered embeddings.
- Find the closest matching face.
- Verify that the similarity is above the configured threshold.
- Display the registered person's information.

Example:

```
Uploaded Photo
      |
      v
InsightFace
      |
      v
Face Detection
      |
      v
Face Embedding
      |
      v
Supabase pgvector
      |
      v
Similarity Search
      |
      v
Matching User
```

# 4. Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| UI | Streamlit |
| Face Recognition | InsightFace |
| ML Runtime | ONNX Runtime |
| Image Processing | OpenCV |
| Database | Supabase PostgreSQL |
| Vector Search | pgvector |
| Image Storage | Supabase Storage |
| Container | Docker |
| Hosting | Railway |
| Source Control | GitHub / GitLab |

# 5. Architecture

```
                         Browser
                            |
                            v
                 +----------------------+
                 |      Streamlit       |
                 |      Python App      |
                 +----------+-----------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
     +-------------------+       +-------------------+
     |    InsightFace    |       |     Supabase      |
     |-------------------|       |-------------------|
     | Face Detection    |       | PostgreSQL        |
     | Face Embeddings   |       | pgvector          |
     | ONNX Runtime      |       | Storage           |
     +---------+---------+       +-------------------+
               |                           |
               +-------------+-------------+
                             |
                             v
                    Registered Users
```

# 6. Application Pages

The application should initially have only two pages.

```
Face Recognition
│
├── Register User
│
└── Recognize Face
```

# 7. Register User Page

The registration page should contain:

```
Register User

Name
[____________________________]

Citizenship Number
[____________________________]

Address
[____________________________]

State / Province
[____________________________]

Photo
[ Upload Photo ]

[ Register User ]
```

Registration process:

```
User Information
       |
       v
Photo Upload
       |
       v
Image Validation
       |
       v
Face Detection
       |
       v
Exactly One Face?
       |
       +---- No ----> Show Error
       |
       +---- Yes
              |
              v
        Generate Embedding
              |
              v
       Store User Information
              |
              v
       Store Face Embedding
              |
              v
          Success
```

# 8. Recognize Face Page

The recognition page should contain:

```
Recognize Face

[ Upload Photo ]

or

[ Capture Photo ]

[ Recognize ]
```

Result:

```
Match Found

Name:
John Doe

Citizenship:
******8901

Address:
Kathmandu

State:
Bagmati

Similarity:
0.XX
```

The complete citizenship number should preferably not be displayed after recognition unless the application specifically requires it.

# 9. Project Structure

Recommended structure:

```
face-recognition/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
├── README.md
│
├── .streamlit/
│   └── config.toml
│
├── database/
│   └── supabase_client.py
│
├── services/
│   ├── face_service.py
│   └── user_service.py
│
├── pages/
│   ├── register.py
│   └── recognize.py
│
└── utils/
    ├── image_utils.py
    └── validators.py
```

# 10. Minimal MVP Structure

If the application is very small, it can initially be:

```
face-recognition/
│
├── app.py
├── face_service.py
├── supabase_client.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

Refactor into separate services once the application grows.

# 11. Database Design

Only two main tables are required.

```
users
  |
  +---- face_embeddings
```

# 12. Users Table

Create the table in Supabase SQL Editor:

```sql
create table users (
    id uuid primary key default gen_random_uuid(),

    name text not null,

    citizenship_number text not null unique,

    address text not null,

    state text not null,

    photo_url text,

    created_at timestamptz
        not null default now(),

    updated_at timestamptz
        not null default now()
);
```

# 13. Face Embeddings Table

First enable pgvector:

```sql
create extension if not exists vector;
```

The embedding dimension depends on the InsightFace model being used.

Replace `YOUR_DIMENSION` with the actual dimension produced by the selected model.

```sql
create table face_embeddings (
    id uuid primary key default gen_random_uuid(),

    user_id uuid not null
        references users(id)
        on delete cascade,

    embedding vector(YOUR_DIMENSION) not null,

    created_at timestamptz
        not null default now()
);
```

# 14. Database Indexes

Create an index for user lookup:

```sql
create index idx_users_citizenship
on users(citizenship_number);
```

Create an index for embeddings:

```sql
create index idx_face_embeddings_user
on face_embeddings(user_id);
```

For larger datasets, add an appropriate pgvector index after benchmarking the selected distance metric and workload.

# 15. Supabase Setup

Create a Supabase project.

Then:

- Open SQL Editor.
- Enable pgvector.
- Create `users`.
- Create `face_embeddings`.
- Create indexes.
- Create a Storage bucket if storing uploaded photos.
- Configure authentication if login is required.
- Configure Row Level Security for production.

Supabase provides PostgreSQL and supports pgvector for storing and searching vectors. (Supabase)

# 16. Supabase Storage

You have two choices.

## Option A — Store Only Embeddings

Recommended if the original photo is not required after registration.

```
Uploaded Photo
      |
      v
InsightFace
      |
      v
Embedding
      |
      v
Database
      |
      v
Delete temporary image
```

This minimizes storage of raw biometric images.

## Option B — Store the Photo

If the application needs to display the registered person's photo:

```
Photo
  |
  +----> Supabase Storage
  |
  +----> InsightFace
             |
             v
         Embedding
```

Store only the URL/path in:

```
users.photo_url
```

Do not store large binary images directly inside PostgreSQL.

# 17. Supabase Storage Bucket

Create a bucket:

```
user-photos
```

Suggested structure:

```
user-photos/
    user-id/
        profile.jpg
```

Avoid using citizenship numbers as filenames or public paths.

Use the generated user UUID instead.

# 18. Environment Variables

Create `.env.example` with:

```
SUPABASE_URL=
SUPABASE_KEY=
```

Do not commit the real values.

Local `.env`:

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_KEY
```

# 19. Git Ignore

Create `.gitignore`:

Example:

```
.venv/
__pycache__/
*.pyc

.env
.env.*

.streamlit/secrets.toml

.DS_Store
```

# 20. Supabase Python Client

Install:

```bash
pip install supabase
```

Create `database/supabase_client.py`:

Example:

```python
import os

from supabase import create_client


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
```

Never hard-code Supabase credentials.

# 21. InsightFace Installation

Install:

```bash
pip install insightface
```

For CPU deployment:

```bash
pip install onnxruntime
```

Use `onnxruntime` rather than a GPU-specific runtime unless GPU infrastructure is intentionally being used.

# 22. Requirements

Initial `requirements.txt`:

```
streamlit
insightface
onnxruntime
opencv-python-headless
numpy
Pillow
supabase
```

After the project is working, pin the versions that have been tested together.

Example:

```
streamlit==TESTED_VERSION
insightface==TESTED_VERSION
onnxruntime==TESTED_VERSION
opencv-python-headless==TESTED_VERSION
numpy==TESTED_VERSION
Pillow==TESTED_VERSION
supabase==TESTED_VERSION
```

Do not blindly copy old package versions because InsightFace, NumPy, OpenCV, ONNX Runtime, and Python versions need to remain compatible.

# 23. Face Service

Create `services/face_service.py`.

Responsibilities:

- Load InsightFace
- Detect faces
- Validate number of faces
- Generate embeddings
- Return the embedding

Example:

```python
import streamlit as st

from insightface.app import FaceAnalysis


@st.cache_resource
def load_face_model():

    app = FaceAnalysis(
        name="YOUR_MODEL"
    )

    app.prepare(
        ctx_id=0,
        det_size=(640, 640)
    )

    return app
```

Then:

```python
face_app = load_face_model()
```

# 24. Why Use `st.cache_resource`

Streamlit reruns application code during interactions.

Without caching, the InsightFace model could be initialized repeatedly.

Use `@st.cache_resource` to keep the model loaded within the Streamlit process.

This is particularly important because ML model initialization can be relatively expensive.

# 25. Image Conversion

Create `utils/image_utils.py`:

Example:

```python
import cv2
import numpy as np


def bytes_to_image(image_bytes):

    array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        array,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "Invalid image."
        )

    return image
```

# 26. Face Detection

Example:

```python
faces = face_app.get(image)
```

Validate:

```python
if len(faces) == 0:
    raise ValueError(
        "No face detected."
    )

if len(faces) > 1:
    raise ValueError(
        "Multiple faces detected."
    )
```

For this application, registration and recognition should initially require exactly one face.

# 27. Generate Embedding

After detection:

```python
face = faces[0]

embedding = face.embedding
```

The embedding should be stored as a vector.

Do not expose the embedding to users.

Do not log the embedding.

# 28. User Registration Service

Create `services/user_service.py`.

Responsibilities:

- Create user
- Upload photo
- Generate embedding
- Store embedding
- Find user

Registration:

1. Validate user information
2. Validate citizenship number
3. Validate uploaded photo
4. Detect face
5. Require exactly one face
6. Generate embedding
7. Create user
8. Store photo if required
9. Store embedding
10. Return success

# 29. Registration Transaction

The logical sequence should be:

```
Validate fields
      |
      v
Validate photo
      |
      v
Detect face
      |
      v
Generate embedding
      |
      v
Create user
      |
      v
Upload photo
      |
      v
Store embedding
```

If a later operation fails, clean up any partially created data.

For example:

```
User created
Photo uploaded
Embedding storage failed
```

should not leave an incomplete user registration.

# 30. Duplicate Citizenship Number

Before registration:

```
Check citizenship_number
        |
        +---- Exists ----> Reject
        |
        +---- Doesn't exist
                         |
                         v
                    Continue
```

The database's `unique` constraint should remain the final protection.

Never rely only on frontend validation.

# 31. Duplicate Face Detection

Optionally, when registering a new user:

```
New Face
   |
   v
Generate Embedding
   |
   v
Search Existing Embeddings
   |
   v
High similarity?
   |
   +---- Yes ----> Possible duplicate
   |
   +---- No -----> Register
```

This can help prevent the same person from being registered multiple times.

However, the threshold should be carefully tested before automatically rejecting registrations.

For the MVP, it is acceptable to omit duplicate-face detection and add it later.

# 32. Face Recognition

The recognition flow:

```
Upload / Camera
      |
      v
Validate Image
      |
      v
Detect Face
      |
      v
Generate Embedding
      |
      v
Search pgvector
      |
      v
Get Best Match
      |
      v
Check Threshold
      |
      +---- Fail ----> No Match
      |
      +---- Pass ----> Return User
```

# 33. Vector Similarity Function

Create a PostgreSQL function.

Replace `YOUR_DIMENSION` with the actual model dimension.

```sql
create or replace function match_face(
    query_embedding vector(YOUR_DIMENSION),
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

        1 - (
            fe.embedding <=> query_embedding
        ) as similarity

    from face_embeddings fe

    where
        1 - (
            fe.embedding <=> query_embedding
        ) >= match_threshold

    order by
        fe.embedding <=> query_embedding

    limit match_count;
$$;
```

The distance operator and threshold must be validated against the specific model.

# 34. Similarity Threshold

Do not assume that `0.5`, `0.6`, `0.7`, `0.8`, `0.9` is automatically a correct threshold.

The threshold depends on:

- Model
- Embedding normalization
- Distance metric
- Image quality
- Camera
- Lighting
- Dataset

Create a test dataset and determine an appropriate threshold experimentally.

# 35. Recognition Result

If a match is found:

```json
{
    "user_id": "...",
    "similarity": 0.XX
}
```

Then retrieve `users` using the returned `user_id`.

Display:

- Name
- Citizenship
- Address
- State
- Photo

Prefer masking the citizenship number:

```
******8901
```

# 36. Streamlit Camera Input

Streamlit supports camera input:

```python
image = st.camera_input(
    "Capture face"
)
```

Example:

```python
image = st.camera_input(
    "Take a photo"
)

if image:

    image_bytes = image.getvalue()

    # Convert image
    # Detect face
    # Generate embedding
    # Search database
```

Also support file upload:

```python
uploaded_file = st.file_uploader(
    "Upload photo",
    type=[
        "jpg",
        "jpeg",
        "png"
    ]
)
```

# 37. Registration Page

Example:

```python
import streamlit as st


st.title("Register User")

name = st.text_input("Name")

citizenship = st.text_input(
    "Citizenship Number"
)

address = st.text_area(
    "Address"
)

state = st.text_input(
    "State / Province"
)

photo = st.file_uploader(
    "Upload Photo",
    type=["jpg", "jpeg", "png"]
)

if st.button("Register User"):

    if not name:
        st.error("Name is required.")

    elif not citizenship:
        st.error(
            "Citizenship number is required."
        )

    elif not address:
        st.error("Address is required.")

    elif not state:
        st.error(
            "State / Province is required."
        )

    elif not photo:
        st.error("Photo is required.")

    else:
        # Registration service
        pass
```

The actual database and face-recognition logic should remain in services rather than being placed entirely inside the Streamlit page.

# 38. Recognition Page

Example:

```python
import streamlit as st


st.title("Recognize Face")

photo = st.camera_input(
    "Capture Face"
)

uploaded = st.file_uploader(
    "Or Upload Photo",
    type=["jpg", "jpeg", "png"]
)

image = photo or uploaded

if image:

    if st.button("Recognize"):

        # Generate embedding
        # Search Supabase
        # Display result

        pass
```

# 39. Recommended UI

```
=====================================
       Face Recognition System
=====================================

[ Register User ]

[ Recognize Face ]
```

Registration:

```
=====================================
          Register User
=====================================

Name
[____________________________]

Citizenship Number
[____________________________]

Address
[____________________________]

State / Province
[____________________________]

Photo
[ Upload Photo ]

[ Register User ]
```

Recognition:

```
=====================================
          Recognize Face
=====================================

[ Upload Photo ]

OR

[ Camera ]

[ Recognize ]

-------------------------------------

Match Found

Name:
John Doe

Citizenship:
******8901

Address:
Kathmandu

State:
Bagmati

Similarity:
0.XX
```

# 40. Authentication

If this application is only for internal use, authentication should be implemented before production deployment.

Recommended: Supabase Auth

Basic flow:

```
Login
  |
  v
Supabase Auth
  |
  +---- Failure ----> Login Error
  |
  +---- Success ----> Application
```

For an initial local MVP, authentication can be postponed.

For production, it should not be omitted.

# 41. Authorization

If only administrators should register and recognize users:

```
Admin
   |
   +-- Register User
   +-- Recognize Face
   +-- View User Data
```

Normal users should not automatically have access to citizenship information.

# 42. Security

This application stores:

- Name
- Citizenship Number
- Address
- Face Photo
- Face Embedding

This is sensitive information.

Minimum security requirements:

- HTTPS
- Authentication
- Authorization
- Secure environment variables
- Database access control
- Row Level Security where appropriate
- No embedding logs
- No API key in frontend code
- No raw biometric data in application logs
- Controlled photo access
- Data deletion capability
- Secure backups

# 43. Citizenship Number Security

Do not use the citizenship number as:

- Database ID
- File name
- Photo path
- URL parameter
- Log identifier

Use the generated UUID:

```
user.id
```

instead.

Example:

```
user-photos/
    7f2a3e8c-....
        profile.jpg
```

instead of:

```
user-photos/
    citizenship-123456.jpg
```

# 44. Face Embedding Security

Never display:

```
[0.1234, -0.2345, ...]
```

to users.

Never log it.

Never put it in URLs.

Never expose it through Streamlit session state unnecessarily.

The embedding should remain an internal database/service value.

# 45. Image Security

Validate uploaded files.

Check:

- File type
- File size
- Image dimensions
- Image decoding
- Number of faces

Recommended maximum upload size:

```
5 MB
```

The exact limit can be adjusted.

# 46. Data Deletion

The application should eventually provide:

```
Delete User
```

Deleting a user should delete:

```
users
    |
    +-- face_embeddings
    |
    +-- stored photo
```

Because `face_embeddings.user_id` uses:

```
on delete cascade
```

the embedding record will automatically be removed when the user is deleted.

The Storage object should also be explicitly deleted.

# 47. Dockerfile

Recommended:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
```

# 48. Streamlit Configuration

Create `.streamlit/config.toml`:

```toml
[server]
headless = true
enableCORS = false
enableXsrfProtection = true
```

# 49. Docker Ignore

Create `.dockerignore`:

```
.git
.github
.venv
__pycache__
*.pyc

.env
.env.*

.streamlit/secrets.toml
```

# 50. Local Development

Create virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Open:

```
http://localhost:8501
```

# 51. Local Docker Testing

Build:

```bash
docker build -t face-recognition .
```

Run:

```bash
docker run \
  -p 8501:8501 \
  --env-file .env \
  face-recognition
```

Open:

```
http://localhost:8501
```

Test:

- Registration
- Photo upload
- Face detection
- Embedding generation
- Database storage
- Recognition
- Similarity matching

# 52. Railway Deployment

Railway is the preferred deployment target for the complete Streamlit + InsightFace application.

Railway supports Docker deployments and GitHub-based deployments. (Railway Docs)

Current Railway Free plan:

- $0/month
- It currently provides:
  - 1 vCPU maximum
  - 0.5 GB RAM maximum
  - 1 GB ephemeral storage
  - $1/month free resource credit

The initial Railway trial provides $5 of credits for up to 30 days, after which the account can move to the Free plan. (Railway Docs)

Important:

The Free plan is suitable for experimentation and a small application, but it is not unlimited free compute.

# 53. Railway Deployment Steps

## Step 1

Push the project to GitHub.

```bash
git init

git add .

git commit -m "Initial face recognition application"

git branch -M main

git remote add origin YOUR_REPOSITORY

git push -u origin main
```

## Step 2

Open Railway.

Create a new project.

Select:

```
Deploy from GitHub Repo
```

Select your repository.

## Step 3

Railway should detect the Dockerfile:

```
Dockerfile
```

and build the application.

## Step 4

Add environment variables:

```
SUPABASE_URL
SUPABASE_KEY
```

Do not commit these values to Git.

## Step 5

Deploy.

The application should start:

```
streamlit run app.py
```

Railway will expose the application through its generated public URL.

# 54. Railway Resource Consideration

InsightFace can require significant memory when loading its models.

The Railway Free plan currently provides only 0.5 GB RAM per service. (Railway Docs)

Therefore:

```
Small model
+
CPU
+
0.5 GB RAM
```

should be tested carefully.

If the selected InsightFace model exceeds the available memory, the application may fail to start.

If that happens, possible solutions include:

- Use a smaller model
  - OR
- Increase Railway resources
  - OR
- Use another hosting platform

Do not assume every InsightFace model will fit comfortably into the free Railway tier.

# 55. Railway Free Storage

Do not store uploaded photos on the Railway filesystem.

Railway's service storage on the Free plan is ephemeral. (Railway Docs)

Incorrect:

```
/uploaded_photos
```

inside the Railway container.

Correct:

```
Photo
  |
  v
Supabase Storage
```

The Railway filesystem should be treated as temporary.

# 56. Supabase Free Plan

Supabase currently offers a Free plan.

The Free plan includes:

- PostgreSQL
- 500 MB database size per project
- 2 free projects

and other quotas/limits. Free projects can also be paused after inactivity. (Supabase)

For a small face-registration prototype, this can be sufficient.

# 57. Vercel Deployment

**Important**

Do not deploy the Streamlit application directly to Vercel as the primary architecture.

Vercel is better suited to:

- Next.js
- React
- Serverless Functions

rather than a long-running Streamlit + InsightFace application.

Recommended architecture:

```
                    Browser
                       |
                       v
                  Vercel
                 Next.js
                       |
                       v
              Face Recognition API
                       |
             +---------+---------+
             |                   |
             v                   v
        InsightFace          Supabase
```

# 58. Vercel Option

If you specifically want to use Vercel, change the architecture to:

```
Frontend
    |
    v
Next.js
    |
    v
Vercel
    |
    v
Python FastAPI
    |
    +---- InsightFace
    |
    +---- Supabase
```

The Streamlit application can remain as an internal/admin prototype.

Vercel should not be treated as the recommended host for the Streamlit + InsightFace server itself.

# 59. Recommended Free Architecture

For the current Streamlit application:

```
                 Browser
                    |
                    v
               Railway Free
                    |
          +---------+---------+
          |                   |
          v                   v
     Streamlit           InsightFace
          |              ONNX Runtime
          |                   |
          +---------+---------+
                    |
                    v
               Supabase Free
                    |
          +---------+---------+
          |                   |
          v                   v
     PostgreSQL           Storage
          |
          v
       pgvector
```

This is the simplest deployment.

# 60. Alternative Vercel Architecture

If the application eventually needs a modern frontend:

```
                    Browser
                       |
                       v
                   Vercel
                  Next.js
                       |
                       v
                  FastAPI API
                       |
              +--------+--------+
              |                 |
              v                 v
         InsightFace        Supabase
```

The migration path is:

Current:

```
Streamlit
    |
    +-- InsightFace
    +-- Supabase
```

Future:

```
Next.js
    |
    v
FastAPI
    |
    +-- InsightFace
    +-- Supabase
```

# 61. Development Phases

## Phase 1 — Supabase

Implement:

- `users`
- `face_embeddings`
- `pgvector`
- `Storage`

## Phase 2 — User Registration

Implement:

- Name
- Citizenship
- Address
- State
- Photo upload

## Phase 3 — Face Registration

Implement:

- Face detection
- One-face validation
- Embedding generation
- Embedding storage

## Phase 4 — Recognition

Implement:

- Photo upload
- Camera
- Face detection
- Embedding
- pgvector search
- Threshold
- User result

## Phase 5 — Security

Implement:

- Authentication
- Authorization
- RLS
- Secure Storage
- Data deletion

## Phase 6 — Deployment

Implement:

- Docker
- Railway
- Environment variables
- HTTPS
- Production testing

# 62. Testing

## Registration Tests

Test:

- Valid user
- Missing name
- Missing citizenship
- Missing address
- Missing state
- Missing photo
- Invalid image
- No face
- Multiple faces
- Large image
- Duplicate citizenship

# 63. Recognition Tests

Test:

- Known user
- Unknown user
- Wrong person
- Multiple faces
- No face
- Poor lighting
- Different camera
- Different angle
- Different image quality

# 64. Security Tests

Test:

- Unauthenticated access
- Unauthorized database access
- Photo URL access
- Citizenship exposure
- Embedding exposure
- User deletion
- Database permissions
- Storage permissions

# 65. Face Recognition Accuracy

Do not judge the system from one or two photos.

Create a test dataset.

For every registered person:

```
5-20 test photos
```

Use different:

- Lighting
- Angles
- Distance
- Expression
- Camera
- Background

Also test similar-looking people.

Measure:

- True Match Rate
- False Match Rate
- False Rejection Rate
- Average Recognition Time

# 66. Similarity Threshold

The threshold should be selected experimentally.

Example process:

```
Collect test images
       |
       v
Generate embeddings
       |
       v
Calculate similarity
       |
       v
Compare same-person scores
       |
       v
Compare different-person scores
       |
       v
Choose threshold
```

Do not blindly use a threshold from another application.

# 67. Performance

For a small user database:

```
1 - 1,000 users
```

a simple pgvector search can be sufficient.

As the number of users increases, benchmark:

- Database query time
- Embedding generation time
- Total recognition time
- Memory usage

Add vector indexes when appropriate.

# 68. Data Model

Final MVP data model:

```
+----------------------+
| users                |
+----------------------+
| id                   |
| name                 |
| citizenship_number   |
| address              |
| state                |
| photo_url            |
| created_at           |
| updated_at           |
+----------+-----------+
           |
           | 1:N
           |
+----------v-----------+
| face_embeddings      |
+----------------------+
| id                   |
| user_id              |
| embedding            |
| created_at           |
+----------------------+
```

# 69. Final API / Service Operations

Even though Streamlit is the UI, structure the application around these logical operations:

```
create_user()
register_face()
recognize_face()
get_user()
delete_user()
```

Example:

```python
user = create_user(
    name=name,
    citizenship_number=citizenship,
    address=address,
    state=state
)
```

Then:

```python
embedding = generate_face_embedding(
    image
)
```

Then:

```python
save_embedding(
    user_id=user.id,
    embedding=embedding
)
```

Recognition:

```python
embedding = generate_face_embedding(
    image
)

match = recognize_face(
    embedding
)
```

# 70. Important Design Decision

Do not combine all logic into `app.py`.

Avoid:

```
app.py
  |
  +-- UI
  +-- SQL
  +-- InsightFace
  +-- Image processing
  +-- Authentication
```

Instead:

```
app.py
   |
   +-- UI
   |
   +-- services/
   |
   +-- database/
   |
   +-- utils/
```

This will make it much easier to migrate from Streamlit to Next.js/FastAPI later.

# 71. Final Recommended Stack

```
Frontend
    |
    v
Streamlit
    |
    +------------------+
    |                  |
    v                  v
InsightFace        Supabase
ONNX Runtime          |
                      +-- PostgreSQL
                      +-- pgvector
                      +-- Storage
```

Deployment:

```
Streamlit + InsightFace
          |
          v
      Railway
       Free*
          |
          v
      Supabase
       Free*
```

* Free tiers have usage limits and may not be sufficient for a high-traffic production system.

# 72. Recommended Deployment Choice

For this exact project:

## Development / MVP

```
Streamlit
+
InsightFace
+
Supabase
+
Railway Free
```

Use this first.

## Future Production

```
Next.js
     |
   Vercel
     |
 FastAPI
     |
InsightFace
     |
Supabase
```

Move to this architecture only if you need:

- A more sophisticated frontend
- Better API separation
- Mobile application integration
- Multiple client applications
- Independent backend scaling

# 73. Final Checklist

## Supabase

- Create project
- Enable pgvector
- Create users table
- Create face_embeddings table
- Create indexes
- Create Storage bucket
- Configure RLS
- Configure authentication

## Application

- Create Streamlit application
- Implement registration form
- Implement photo upload
- Implement camera capture
- Implement InsightFace
- Generate embeddings
- Store embeddings
- Implement vector search
- Implement similarity threshold
- Display matched user

## Security

- Protect Supabase credentials
- Enable authentication
- Restrict database access
- Protect citizenship information
- Protect face embeddings
- Protect uploaded photos
- Do not log biometric data
- Implement user deletion
- Define data retention policy

## Deployment

- Create Dockerfile
- Test Docker locally
- Push to GitHub/GitLab
- Create Railway project
- Configure environment variables
- Deploy
- Test production URL
- Monitor memory usage

# 74. Final Architecture

```
                         USER
                           |
                           v
                  +----------------+
                  |   Streamlit    |
                  |     UI         |
                  +-------+--------+
                          |
             +------------+------------+
             |                         |
             v                         v
     +---------------+          +---------------+
     |  InsightFace  |          |   Supabase   |
     |               |          |               |
     | Face Detect   |          | PostgreSQL    |
     | Embeddings    |          | pgvector      |
     | ONNX Runtime  |          | Storage       |
     +-------+-------+          +-------+-------+
             |                          |
             +------------+-------------+
                          |
                          v
                   Registered User
```

Deployment:

```
       GitHub / GitLab
              |
              v
         Railway Free
              |
              v
      Streamlit + InsightFace
              |
              v
         Supabase Free
```

# 75. Conclusion

The simplest architecture for the current requirement is:

```
Python
  +
Streamlit
  +
InsightFace
  +
ONNX Runtime
  +
Supabase PostgreSQL
  +
pgvector
  +
Supabase Storage
  +
Railway
```

Start with the Streamlit + Railway architecture.

Do not introduce Vercel unless you later replace Streamlit with a frontend such as Next.js.

The most important implementation priorities are:

- Correct face embedding generation.
- Reliable face matching.
- Secure handling of citizenship and biometric data.
- Proper Supabase access control.
- Keeping raw photos out of the Railway filesystem.
- Testing the InsightFace model's memory requirements against Railway's free resources.
- Testing the similarity threshold with real images before relying on recognition in production.

### Deployment recommendation

For **your current requirements**, I would use **Railway + Supabase**, not Vercel:

**Railway:** Streamlit + InsightFace  
**Supabase:** PostgreSQL + pgvector + photo storage

Railway's current free tier is $0 with limited monthly resource credit, while Supabase has a $0 Free plan suitable for an MVP.

If the Railway free container's **0.5 GB RAM** isn't enough for your selected InsightFace model, the next step would be either a smaller model or a paid/different compute provider.

For **Vercel**, I'd only use it later if you change the UI to **Next.js** and put InsightFace behind a separate Python API.
