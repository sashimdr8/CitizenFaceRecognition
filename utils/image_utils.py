import cv2
import numpy as np


def bytes_to_image(image_bytes):
    """Convert image bytes to OpenCV image format."""
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Invalid image.")
    
    return image


def validate_image_size(image_bytes, max_size_mb=5):
    """Validate image size is within limits."""
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"Image size exceeds {max_size_mb}MB limit")
    return True
