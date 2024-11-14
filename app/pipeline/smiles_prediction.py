import os
from app.core.logging_config import logger
from typing import List, Optional
from app.schema.results.prediction_result import PredictionResult
from app.service.doc_loader.utils import get_file_type
from app.service.doc_loader.pdf_loader import pdf_to_images
from app.service.segmentation.segment import segment_images
from app.service.prediction.predict_smiles import predict_smiles_from_segment
from app.core.celery_config import celery_app


@celery_app.task
def predict_smiles(file_location: str) -> Optional[List[PredictionResult]]:
    results = []
    serialized_results = []

    # 1. Read the document and extract images
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
    except Exception as e:
        logger.error(f"An error occurred during document pre-processing: {str(e)}")
        return None
    finally:
        logger.info("[END] Pre-processing document")
    
    # 2. Segment the chemical structures from the images
    segmented_images = []
    try:
        logger.info("[START] Segmentation")
        for page_number, img in enumerate(img_doc):
            segments = segment_images(img)
            if segments:
                for segment in segments:
                    result = PredictionResult(
                        file_path=file_location,
                        page=page_number + 1,
                        segmented_image=segment,
                        history=[]
                    )
                    result.add_history("Segmentation", "Success", "Segmented image extracted")
                    segmented_images.append(result)
            else:
                logger.warning(f"No segments found on page {page_number + 1}")
    except Exception as e:
        logger.error(f"An error occurred during segmentation: {str(e)}")
        return None
    finally:
        logger.info("[END] Segmentation")
    
    # 3. Predict SMILES strings from the segmented images
    try:
        logger.info("[START] SMILES prediction")
        for result in segmented_images:
            smiles, confidence = predict_smiles_from_segment(result.segmented_image)
            if smiles and confidence >= 0.5:
                result.predicted_smiles = smiles
                result.confidence = confidence
                result.add_history("SMILES Prediction", "Success", f"Predicted SMILES: {smiles} with confidence: {confidence}")
            elif smiles and confidence < 0.5:
                result.predicted_smiles = smiles
                result.confidence = confidence
                result.add_history("SMILES Prediction", "Failure", f"Low confidence: {confidence}")
            else:
                result.add_history("SMILES Prediction", "Failure", "No SMILES predicted")
            results.append(result)
    except Exception as e:
        logger.error(f"An error occurred during SMILES prediction: {str(e)}")
        return None
    finally:
        logger.info("[END] SMILES prediction")

    # Return all results with history
    for res in results:
        serialized_results.append(res.json_serializable())
    return serialized_results


# #Example usage
# results = predict_smiles("./uploads/2.pdf")
# if results:
#     for result in results:
#         result.print_result()
