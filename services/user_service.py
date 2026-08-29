from database.supabase_client import supabase


def check_citizenship_exists(citizenship_number):
    """Check if citizenship number already exists in database."""
    response = supabase.table('users').select('id').eq('citizenship_number', citizenship_number).execute()
    return len(response.data) > 0


def create_user(name, citizenship_number, address, state, photo_url=None):
    """Create a new user in the database."""
    user_data = {
        'name': name,
        'citizenship_number': citizenship_number,
        'address': address,
        'state': state
    }
    
    if photo_url:
        user_data['photo_url'] = photo_url
    
    response = supabase.table('users').insert(user_data).execute()
    return response.data[0]


def save_face_embedding(user_id, embedding):
    """Save face embedding for a user."""
    embedding_data = {
        'user_id': user_id,
        'embedding': embedding.tolist()  # Convert numpy array to list
    }
    response = supabase.table('face_embeddings').insert(embedding_data).execute()
    return response.data[0]


def get_user_by_id(user_id):
    """Get user information by ID."""
    response = supabase.table('users').select('*').eq('id', user_id).execute()
    if response.data:
        return response.data[0]
    return None


def get_all_users(search_name=None, search_citizenship=None):
    """Get all users with optional search filters."""
    query = supabase.table('users').select('*')
    
    if search_name:
        query = query.ilike('name', f'%{search_name}%')
    
    if search_citizenship:
        query = query.ilike('citizenship_number', f'%{search_citizenship}%')
    
    response = query.order('created_at', desc=True).execute()
    return response.data


def match_face_embedding(query_embedding, threshold=0.5, match_count=1):
    """Find matching face using pgvector similarity search."""
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
    import uuid
    from datetime import datetime
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{folder}/{timestamp}_{unique_id}.jpg"
    
    # Upload to storage
    try:
        response = supabase.storage.from_(bucket_name).upload(
            filename,
            photo_bytes,
            {"content-type": "image/jpeg"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        return public_url
    except Exception as e:
        print(f"Error uploading to storage: {e}")
        return None


def log_recognition_attempt(status, matched_user_id=None, similarity=None, photo_url=None, error_message=None):
    """Log face recognition attempt to database."""
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
    response = supabase.table('recognition_logs').select('*').order('created_at', desc=True).limit(limit).execute()
    return response.data
