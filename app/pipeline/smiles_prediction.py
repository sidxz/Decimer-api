from app.core.celery_config import celery_app
import uuid
from app.core.mongo_config import get_sync_collection
from app.hooks.registry import execute_hooks
from app.schema.inputs.document import Document
from app.schema.results.prediction_result import PredictionResult
from app.repositories.document_sync import (
    get_document_by_file_path_sync,
    save_document_sync,
)
from app.repositories.prediction_results import (
    get_latest_prediction_result_sync,
    save_prediction_results_sync,
)
from app.service.doc_loader.pdf_loader import pdf_to_images
from app.service.segmentation.segment import segment_images
from app.service.prediction.predict_smiles import predict_smiles_from_segment
from app.utils.daikon_api import get_molecule_by_smiles
from app.utils.file_hash import calculate_file_hash
from app.service.doc_loader.utils import get_file_type
from app.core.logging_config import logger
import os


@celery_app.task(bind=True)
def predict_smiles(self, file_location: str):
    try:
        results = []
        serialized_results = []

        # Generate a document ID and metadata
        logger.info("[START] Generating document ID and metadata")
        document_id = uuid.uuid4()
        run_id = 0
        document = Document(id=document_id, file_path=file_location)
        document.file_type = get_file_type(file_location)
        document.doc_hash = calculate_file_hash(file_location)
        logger.info("[END] Generating document ID and metadata")

        # Check if the document already exists in the database and compare hashes
        logger.info("[CHECK] Checking for existing document in the database")
        existing_document = get_document_by_file_path_sync(file_location)
        if existing_document:
            run_id = existing_document.run_id + 1
            document.id = existing_document.id
            if existing_document.doc_hash == document.doc_hash:
                logger.info(
                    "Document already exists in the database with the same hash."
                )

                # Retrieve the latest prediction result using the repository function
                latest_result = get_latest_prediction_result_sync(existing_document.id)
                if latest_result:
                    logger.info(
                        "Returning the latest result for the existing document."
                    )
                    return latest_result.json_serializable()  # Serialize the result
                else:
                    logger.warning(
                        "No prediction results found for the existing document."
                    )
                    return None  # No results available
            else:
                logger.warning(
                    "Document exists but hash mismatch. Proceeding with new processing."
                )
        document.run_id = run_id
        # Step 1: Read the document and extract images
        logger.info("[START] Pre-processing document")
        if not os.path.isfile(file_location):
            logger.error(f"File not found: {file_location}")
            return []

        if "PDF" not in document.file_type:
            logger.warning("Unsupported document type. Only PDF files are supported.")
            return []

        img_doc = pdf_to_images(file_location)
        if not img_doc:
            logger.error("Failed to extract content from PDF document.")
            return []
        logger.info("[END] Pre-processing document")

        # Step 2: Segment the chemical structures
        logger.info("[START] Segmenting images")
        segmented_images = []
        for page_number, img in enumerate(img_doc):
            segments = segment_images(img)
            if segments:
                for segment in segments:
                    result = PredictionResult(
                        document_id=document.id,
                        file_path=file_location,
                        page=page_number + 1,
                        segmented_image=segment,
                        history=[],
                    )
                    result.add_history(
                        "Segmentation", "Success", "Segmented image extracted"
                    )
                    segmented_images.append(result)
        logger.info("[END] Segmenting images")

        # Step 3: Predict SMILES strings
        logger.info("[START] Predicting SMILES strings")
        for result in segmented_images:
            smiles, confidence = predict_smiles_from_segment(result.segmented_image)
            if smiles:
                result.predicted_smiles = smiles
                result.confidence = confidence
                result.add_history(
                    "SMILES Prediction",
                    "Success" if confidence >= 0.5 else "Low confidence",
                    f"Predicted SMILES: {smiles} with confidence {confidence}",
                )
                document.predicted_smiles_list.append(smiles)
            else:
                result.add_history(
                    "SMILES Prediction", "Failed", "Failed to predict SMILES string"
                )
            result.run_id = run_id
            results.append(result)
        logger.info("[END] Predicting SMILES strings")
        
        # Step 4. TRY hooks Molecule Search
        logger.info("[START] Executing Search hooks")
        execute_hooks(
            pipeline="smiles_pred_mol_search", document=document, results=results
        )
        logger.info("[END] Executing Search hooks")

        # Step 5: Save to MongoDB
        logger.info("[START] Saving results to MongoDB")
        try:
            save_document_sync(document)
            save_prediction_results_sync(results)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        logger.info("[END] Saving results to MongoDB")
        
        # Step 6: Run Post hooks
        logger.info("[START] Executing Post hooks")
        execute_hooks(
            pipeline="smiles_pred_res_post", document=document, results=results
        )

        # Step 6: Serialize results
        for res in results:
            serialized_results.append(res.json_serializable())
        return serialized_results

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []
