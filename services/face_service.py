import streamlit as st
from insightface.app import FaceAnalysis


@st.cache_resource
def load_face_model():
    """Load InsightFace model with caching."""
    app = FaceAnalysis(name="buffalo_l")
    app.prepare(ctx_id=0, det_size=(640, 640))
    return app


def detect_face(image):
    """Detect faces in image and return faces."""
    face_app = load_face_model()
    faces = face_app.get(image)
    return faces


def validate_single_face(faces):
    """Validate that exactly one face is detected."""
    if len(faces) == 0:
        raise ValueError("No face detected in the image.")
    if len(faces) > 1:
        raise ValueError("Multiple faces detected. Please upload an image with exactly one face.")
    return faces[0]


def generate_embedding(face):
    """Generate face embedding from detected face."""
    return face.embedding
