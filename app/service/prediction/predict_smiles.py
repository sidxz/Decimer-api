import numpy as np
from DECIMER import predict_SMILES
from PIL import Image
import io
from app.core.logging_config import logger
from typing import Tuple, Optional

from app.service.prediction.calculate_confidence import calculate_overall_confidence

def predict_smiles_from_segment(segment: np.ndarray) -> Optional[Tuple[str, float]]:
    """
    Predict a SMILES string and its confidence score from a single segmented chemical structure.

    Args:
        segment (np.ndarray): A segmented image (numpy array).

    Returns:
        Optional[Tuple[str, float]]: The predicted SMILES string and confidence score, or None if prediction fails.
    """
    if not isinstance(segment, np.ndarray):
        logger.error("Input segment is not a numpy ndarray.")
        raise ValueError("Input must be a numpy ndarray.")
    
    try:
        # Convert the numpy array to a PIL Image
        segment_img = Image.fromarray(segment)

        # Save the image to an in-memory buffer in PNG format
        with io.BytesIO() as img_buffer:
            segment_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)  # Rewind to the start of the buffer

            # Predict SMILES and confidence using the DECIMER model
            actual_result = predict_SMILES(img_buffer, confidence=True)
            
            smiles = actual_result[0]
            confidence = calculate_overall_confidence(actual_result)
            
            
        if smiles:
            logger.info(f"Decoded SMILES: {smiles} with confidence: {confidence}")
            return smiles, confidence
        else:
            logger.warning("No SMILES decoded.")
            return None

    except Exception as e:
        logger.error(f"Error during SMILES prediction: {str(e)}", exc_info=True)
        return None
