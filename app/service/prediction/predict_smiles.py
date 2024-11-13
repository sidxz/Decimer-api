import numpy as np
from DECIMER import predict_SMILES
from PIL import Image
import io
from app.core.logging_config import logger

def predict_smiles_from_segment(segment: np.ndarray) -> str:
    """
    Predict a SMILES string from a single segmented chemical structure.

    Args:
        segment (np.ndarray): A segmented image (numpy array).

    Returns:
        str: The predicted SMILES string or None if prediction fails.
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

            # Predict SMILES using the DECIMER model
            smiles = predict_SMILES(img_buffer)

        if smiles:
            logger.info(f"Decoded SMILES: {smiles}")
            return smiles
        else:
            logger.warning("No SMILES decoded.")
            return None

    except Exception as e:
        logger.error(f"Error during SMILES prediction: {str(e)}", exc_info=True)
        return None
