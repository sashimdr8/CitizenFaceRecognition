import streamlit as st
from utils.image_utils import bytes_to_image, validate_image_size
from services.face_service import detect_face, validate_single_face, generate_embedding
from services.user_service import (
    check_citizenship_exists,
    create_user,
    save_face_embedding,
    get_user_by_id,
    get_all_users,
    match_face_embedding,
    mask_citizenship_number,
    log_recognition_attempt,
    upload_photo_to_storage
)

st.set_page_config(page_title="Face Recognition System", layout="centered")

def main():
    st.title("Face Recognition System")
    
    page = st.sidebar.radio("Select Page", ["Register User", "Recognize Face", "View Users"])
    
    if page == "Register User":
        register_user_page()
    elif page == "Recognize Face":
        recognize_face_page()
    else:
        view_users_page()

def register_user_page():
    st.header("Register User")
    
    with st.form("registration_form"):
        name = st.text_input("Name")
        citizenship_number = st.text_input("Citizenship Number")
        address = st.text_area("Address")
        state = st.text_input("State / Province")
        photo = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])
        
        submitted = st.form_submit_button("Register User")
        
        if submitted:
            # Validation
            if not name:
                st.error("Name is required.")
            elif not citizenship_number:
                st.error("Citizenship number is required.")
            elif not address:
                st.error("Address is required.")
            elif not state:
                st.error("State / Province is required.")
            elif not photo:
                st.error("Photo is required.")
            else:
                try:
                    with st.spinner("Processing registration..."):
                        # Validate image size
                        image_bytes = photo.getvalue()
                        validate_image_size(image_bytes)
                        
                        # Check for duplicate citizenship
                        if check_citizenship_exists(citizenship_number):
                            st.error("This citizenship number is already registered.")
                            return
                        
                        # Upload photo to storage
                        photo_url = upload_photo_to_storage(image_bytes, folder="users")
                        
                        if not photo_url:
                            st.error("Failed to upload photo to storage. Please check your Supabase storage configuration.")
                            st.info("Make sure the 'recognition-photos' bucket exists and is public.")
                            return
                        
                        # Convert image
                        image = bytes_to_image(image_bytes)
                        
                        # Detect and validate face
                        faces = detect_face(image)
                        face = validate_single_face(faces)
                        
                        # Generate embedding
                        embedding = generate_embedding(face)
                        
                        # Create user with photo URL
                        user = create_user(name, citizenship_number, address, state, photo_url)
                        
                        # Save embedding
                        save_face_embedding(user['id'], embedding)
                    
                    st.success("User registered successfully!")
                    st.info(f"User ID: {user['id']}")
                    if photo_url:
                        st.success(f"Photo uploaded successfully!")
                    
                except ValueError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())

def recognize_face_page():
    st.header("Recognize Face")
    
    col1, col2 = st.columns(2)
    
    with col1:
        photo = st.camera_input("Capture Face")
    
    with col2:
        uploaded = st.file_uploader("Or Upload Photo", type=["jpg", "jpeg", "png"])
    
    image = photo or uploaded
    
    if image:
        st.image(image, caption="Uploaded Photo", use_container_width=True)
        
        if st.button("Recognize"):
            try:
                # Validate image size
                image_bytes = image.getvalue()
                validate_image_size(image_bytes)
                
                # Upload photo to storage
                photo_url = upload_photo_to_storage(image_bytes)
                
                # Convert image
                img = bytes_to_image(image_bytes)
                
                # Detect and validate face
                faces = detect_face(img)
                face = validate_single_face(faces)
                
                # Generate embedding
                embedding = generate_embedding(face)
                
                # Match face
                match = match_face_embedding(embedding, threshold=0.5)
                
                if match:
                    user = get_user_by_id(match['user_id'])
                    if user:
                        st.success("Match Found!")
                        
                        st.subheader("User Information")
                        st.write(f"**Name:** {user['name']}")
                        st.write(f"**Citizenship:** {user['citizenship_number']}")
                        st.write(f"**Address:** {user['address']}")
                        st.write(f"**State:** {user['state']}")
                        st.write(f"**Similarity:** {match['similarity']:.2f}")
                        
                        # Log successful recognition
                        log_recognition_attempt(
                            status="success",
                            matched_user_id=match['user_id'],
                            similarity=match['similarity'],
                            photo_url=photo_url
                        )
                    else:
                        st.error("Match found but user data not available.")
                        log_recognition_attempt(
                            status="error",
                            error_message="Match found but user data not available",
                            photo_url=photo_url
                        )
                else:
                    st.warning("No matching face found in the database.")
                    log_recognition_attempt(
                        status="no_match",
                        photo_url=photo_url
                    )
                    
            except ValueError as e:
                st.error(str(e))
                # Upload photo even on error for logging
                photo_url = upload_photo_to_storage(image.getvalue()) if image else None
                log_recognition_attempt(
                    status="error",
                    error_message=str(e),
                    photo_url=photo_url
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                # Upload photo even on error for logging
                photo_url = upload_photo_to_storage(image.getvalue()) if image else None
                log_recognition_attempt(
                    status="error",
                    error_message=str(e),
                    photo_url=photo_url
                )

def view_users_page():
    st.header("Registered Users")
    
    # Search filters
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("Search by Name")
    with col2:
        search_citizenship = st.text_input("Search by Citizenship Number")
    
    search_button = st.button("Search")
    
    # Get users
    if search_button or search_name or search_citizenship:
        users = get_all_users(search_name if search_name else None, search_citizenship if search_citizenship else None)
    else:
        users = get_all_users()
    
    # Display users
    if users:
        st.success(f"Found {len(users)} user(s)")
        
        for user in users:
            with st.expander(f"{user['name']} - {mask_citizenship_number(user['citizenship_number'])}"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if user.get('photo_url'):
                        try:
                            st.image(user['photo_url'], caption="User Photo", use_container_width=True)
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")
                            st.write(f"Photo URL: {user['photo_url']}")
                    else:
                        st.info("No photo available")
                
                with col2:
                    st.write(f"**ID:** {user['id']}")
                    st.write(f"**Name:** {user['name']}")
                    st.write(f"**Citizenship Number:** {user['citizenship_number']}")
                    st.write(f"**Address:** {user['address']}")
                    st.write(f"**State:** {user['state']}")
    else:
        st.info("No users found")

if __name__ == "__main__":
    main()
