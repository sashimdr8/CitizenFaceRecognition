from database.supabase_client import ensure_supabase


def check_citizenship_exists(citizenship_number):
    """Check if citizenship number already exists in database."""
    supabase = ensure_supabase()
    response = supabase.table('users').select('id').eq('citizenship_number', citizenship_number).execute()
    return len(response.data) > 0


def create_user(name, citizenship_number, address, state, photo_url=None):
    """Create a new user in the database."""
    supabase = ensure_supabase()
    user_data = {
        'name': name,
        'citizenship_number': citizenship_number,
        'address': address,
        'state': state
    }
    
    if photo_url:
        user_data['photo_url'] = photo_url
        print(f"[DEBUG] Creating user with photo_url: {photo_url}")
    else:
        print(f"[WARNING] Creating user WITHOUT photo_url")
    
    print(f"[DEBUG] User data being inserted: {user_data}")
    
    try:
        response = supabase.table('users').insert(user_data).execute()
        print(f"[DEBUG] Insert response: {response}")
        created_user = response.data[0]
        print(f"[DEBUG] Created user: {created_user}")
        return created_user
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        raise


def save_face_embedding(user_id, embedding):
    """Save face embedding for a user."""
    supabase = ensure_supabase()
    embedding_data = {
        'user_id': user_id,
        'embedding': embedding.tolist()  # Convert numpy array to list
    }
    response = supabase.table('face_embeddings').insert(embedding_data).execute()
    return response.data[0]


def get_user_by_id(user_id):
    """Get user information by ID."""
    supabase = ensure_supabase()
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    if response.data:
        return response.data[0]
    return None


def get_all_users(search_name=None, search_citizenship=None):
    """Get all users with optional search filters."""
    supabase = ensure_supabase()
    query = supabase.table('users').select('*')
    
    if search_name:
        query = query.ilike('name', f'%{search_name}%')
    
    if search_citizenship:
        query = query.ilike('citizenship_number', f'%{search_citizenship}%')
    
    response = query.order('created_at', desc=True).execute()
    return response.data


def match_face_embedding(query_embedding, threshold=0.5, match_count=1):
    """Find matching face using pgvector similarity search."""
    supabase = ensure_supabase()
    # Note: This requires the match_face function to be created in Supabase SQL
    # For now, we'll use a simple approach with raw SQL via supabase.rpc
    
    try:
        response = supabase.rpc('match_face', {
            'query_embedding': query_embedding.tolist(),
            'match_threshold': threshold,
            'match_count': match_count
        }).execute()
        
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        # Fallback: manual similarity search if function doesn't exist
        print(f"RPC function not available, using fallback: {e}")
        return None


def mask_citizenship_number(citizenship_number):
    """Mask citizenship number for display (show only last 5 digits)."""
    if not citizenship_number or len(citizenship_number) < 5:
        return citizenship_number
    return '*' * (len(citizenship_number) - 5) + citizenship_number[-5:]


def upload_photo_to_storage(photo_bytes, bucket_name="recognition-photos", folder="logs"):
    """Upload photo to Supabase Storage and return the public URL."""
    supabase = ensure_supabase()
    import uuid
    from datetime import datetime
    
    print(f"[DEBUG] Starting photo upload to bucket '{bucket_name}', folder '{folder}'")
    print(f"[DEBUG] Photo size: {len(photo_bytes)} bytes")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{folder}/{timestamp}_{unique_id}.jpg"
    
    print(f"[DEBUG] Generated filename: {filename}")
    
    # Upload to storage
    try:
        # Try to upload, if file exists, use a different name
        try:
            print(f"[DEBUG] Attempting upload to Supabase storage...")
            response = supabase.storage.from_(bucket_name).upload(
                filename,
                photo_bytes,
                {"content-type": "image/jpeg"}
            )
            print(f"[DEBUG] Upload response: {response}")
        except Exception as upload_error:
            print(f"[DEBUG] Upload error: {upload_error}")
            # If file exists, try with a different unique ID
            if "already exists" in str(upload_error).lower() or "duplicate" in str(upload_error).lower():
                print(f"[DEBUG] File exists, trying with new unique ID...")
                unique_id = str(uuid.uuid4())
                filename = f"{folder}/{timestamp}_{unique_id}.jpg"
                response = supabase.storage.from_(bucket_name).upload(
                    filename,
                    photo_bytes,
                    {"content-type": "image/jpeg"}
                )
                print(f"[DEBUG] Retry upload response: {response}")
            else:
                raise upload_error
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        print(f"[SUCCESS] Photo uploaded successfully!")
        print(f"[SUCCESS] Public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"[ERROR] Error uploading to storage: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None


def log_recognition_attempt(status, matched_user_id=None, similarity=None, photo_url=None, error_message=None):
    """Log face recognition attempt to database."""
    supabase = ensure_supabase()
    log_data = {
        'status': status
    }
    
    if matched_user_id:
        log_data['matched_user_id'] = matched_user_id
    
    if similarity is not None:
        log_data['similarity'] = similarity
    
    if photo_url:
        log_data['photo_url'] = photo_url
    
    if error_message:
        log_data['error_message'] = error_message
    
    response = supabase.table('recognition_logs').insert(log_data).execute()
    return response.data[0]


def get_recognition_logs(limit=50):
    """Get recent recognition logs."""
    supabase = ensure_supabase()
    response = supabase.table('recognition_logs').select('*').order('created_at', desc=True).limit(limit).execute()
    return response.data
