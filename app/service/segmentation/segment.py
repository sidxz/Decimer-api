from typing import List
import numpy as np
from decimer_segmentation import segment_chemical_structures
from app.core.logging_config import logger

def segment_images(image: np.ndarray) -> List[np.ndarray]:
    """
    Segment chemical structures from a list of images.

    Args:
        image np.ndarray: The image to segment.

    Returns:
        List[np.ndarray]: A list of segmented chemical structures.
    """
    try:
        logger.info(f"Starting segmentation on image...")
        segments = segment_chemical_structures(image)
        logger.info(f"Successfully segmented {len(segments)} structures.")
        return segments

    except Exception as e:
        logger.error(f"An error occurred during segmentation: {str(e)}")
        return []
