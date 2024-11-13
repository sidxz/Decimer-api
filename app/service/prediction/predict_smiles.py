from typing import List
import numpy as np
from DECIMER import predict_SMILES
from PIL import Image
import io
from app.core.logging_config import logger

def predict_smiles_from_segments(segments: List[np.ndarray]) -> List[str]:
    """
    Predict SMILES strings for a list of segmented chemical structures.

    Args:
        segments (List[np.ndarray]): A list of segmented images (numpy arrays).

    Returns:
        List[str]: A list of predicted SMILES strings.
    """
    smiles_array = []
    
    logger.info(f"Starting SMILES prediction for {len(segments)} segments...")
    
    for i, segment in enumerate(segments):
        try:
            # Convert segment (numpy array) to a PIL image
            segment_img = Image.fromarray(segment)

            # Save the segment image into an in-memory buffer
            img_buffer = io.BytesIO()
            segment_img.save(img_buffer, format='PNG')
            img_buffer.seek(0)  # Rewind the buffer to the beginning

            # Predict SMILES directly from the in-memory image buffer
            smiles = predict_SMILES(img_buffer)
            
            if smiles:
                smiles_array.append(smiles)
                logger.info(f"Decoded SMILES for segment {i+1}: {smiles}")
            else:
                logger.warning(f"No SMILES decoded for segment {i+1}")
        
        except Exception as e:
            logger.error(f"Error predicting SMILES for segment {i+1}: {str(e)}")
    
    logger.info(f"SMILES prediction completed. Total SMILES decoded: {len(smiles_array)}")
    return smiles_array
