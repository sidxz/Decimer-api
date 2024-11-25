import base64
from typing import Optional
import cv2
import numpy as np
from app.core.logging_config import logger


def decode_image_from_base64(base64_string: str) -> Optional[np.ndarray]:
    """
    Decode a base64-encoded string into a numpy array.

    :param base64_string: Base64-encoded image string.
    :return: Decoded numpy array (image), or None if decoding fails.
    """
    try:
        decoded_data = base64.b64decode(base64_string)
        image_array = np.frombuffer(decoded_data, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {str(e)}")
        return None
