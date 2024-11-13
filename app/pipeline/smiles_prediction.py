import os
from app.core.logging_config import logger
from typing import Optional
from app.service.doc_loader.utils import get_file_type
from app.service.doc_loader.pdf_loader import pdf_to_images
from app.service.segmentation.segment import segment_images
from app.service.prediction.predict_smiles import predict_smiles_from_segments
def predict_smiles(file_location: str):

    
    # 1. Read the document and extract images
    img_doc = []
    try:
        logger.info("[START] Pre-processing document")
        logger.info(f"Document location: {file_location}")

        # Validate file existence
        if not os.path.isfile(file_location):
            logger.error(f"File not found: {file_location}")
            return None

        # Identify the file type
        file_type = get_file_type(file_location)

        if "PDF" not in file_type:
            logger.warning("Unsupported document type. Only PDF files are supported.")
            return None

        logger.info("PDF document detected. Proceeding with PDF processing.")
        img_doc = pdf_to_images(file_location)

        if not img_doc:
            logger.error("Failed to load or extract content from PDF document.")
            return None

    except FileNotFoundError:
        logger.error(f"File not found: {file_location}")
        return None
    except Exception as e:
        logger.error(f"An error occurred during document pre-processing: {str(e)}")
        return None
    finally:
        logger.info("[END] Pre-processing document")
        
    # 2. Segment the chemical structures from the images
    segmented_images = []
    try:
        logger.info("[START] Segmentation")
        
            # Process each image one by one
        for img in img_doc:
            segments = segment_images(img)  # Pass a single image, not a list
            if segments:
                segmented_images.extend(segments)
        

        if not segmented_images:
            logger.warning("Failed to segment chemical structures from the document.")
            return None

    except Exception as e:
        logger.error(f"An error occurred during segmentation: {str(e)}")
        return None
    finally:
        logger.info("[END] Segmentation")
    
    # 3. Predict SMILES strings from the segmented images
    smiles_predictions = []
    try:
        logger.info("[START] SMILES prediction")
        smiles_predictions = predict_smiles_from_segments(segmented_images)

        if not smiles_predictions:
            logger.warning("No SMILES strings were predicted.")
            return None

    except Exception as e:
        logger.error(f"An error occurred during SMILES prediction: {str(e)}")
        return None
    finally:
        logger.info("[END] SMILES prediction")
    


predict_smiles("./uploads/PurF_v2.pdf")