from typing import List, Optional
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status
from app.core.mongo_config import get_async_collection, get_sync_collection
from app.schema.results.prediction_result import PredictionResult
from app.core.logging_config import logger
from app.utils.img_decode import decode_image_from_base64


def save_prediction_results_sync(results: List[PredictionResult]):
    """
    Save prediction results to MongoDB synchronously.
    """
    logger.info("Saving prediction results to MongoDB (sync)")

    # Check if there are results to save
    if not results:
        logger.warning("No prediction results to save")
        return  # No results to save

    # Get the synchronous collection
    collection = get_sync_collection("prediction_results")

    try:
        # Convert the results to JSON-serializable format (with Base64 encoded images)
        documents = [result.json_serializable() for result in results]

        # Perform batch insertion
        if documents:
            collection.insert_many(documents)
            logger.info(f"Successfully saved {len(documents)} prediction results")
        else:
            logger.warning("No valid documents to insert")
    except PyMongoError as e:
        logger.error(f"Error saving prediction results (sync): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving prediction results: {str(e)}",
        )


async def save_prediction_results(results: List[PredictionResult]):
    logger.info("Saving prediction results to MongoDB")
    """Save prediction results to MongoDB."""
    if not results:
        logger.warning("No results to save")
        return  # No results to save

    collection = await get_async_collection("prediction_results")
    try:
        # Prepare the list of documents for batch insertion
        documents = [result.json_serializable() for result in results]
        await collection.insert_many(documents)
    except PyMongoError as e:
        logger.error(f"Error saving prediction results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving prediction results: {str(e)}",
        )


from pymongo import DESCENDING
from fastapi import HTTPException, status


def get_latest_prediction_results_sync(
    document_id: str, max_run_id: int = -1
) -> List[PredictionResult]:
    """
    Retrieve all prediction results with the highest run_id for a given document ID.

    :param document_id: The UUID of the document to retrieve results for.
    :param max_run_id: The maximum run_id to filter by. If -1, it will be calculated.
    :return: A list of PredictionResult objects with the highest run_id, or an empty list if no results are found.
    """
    logger.info(
        f"[FETCH] Retrieving the latest prediction results for document ID: {document_id}"
    )
    try:
        collection = get_sync_collection("prediction_results")

        # Find the maximum run_id for the document_id if not provided
        if max_run_id == -1:
            logger.info("Max run_id not provided. Calculating the maximum run_id...")
            max_run_id_doc = collection.find_one(
                {"document_id": document_id},
                sort=[("run_id", DESCENDING)],  # Sort by run_id descending
                projection={"run_id": 1},  # Only fetch the run_id field
            )

            if not max_run_id_doc:
                logger.warning(
                    f"No prediction results found for document ID: {document_id}"
                )
                return []

            max_run_id = max_run_id_doc["run_id"]
            logger.info(f"Calculated max run_id: {max_run_id}")
        else:
            logger.info(f"Using provided max run_id: {max_run_id}")

        # Fetch all documents with the highest run_id
        results = collection.find({"document_id": document_id, "run_id": max_run_id})

        prediction_results = []
        for result in results:
            # Deserialize the segmented_image field if it exists
            if "segmented_image" in result and result["segmented_image"]:
                result["segmented_image"] = decode_image_from_base64(
                    result["segmented_image"]
                )
            # Convert the result to a PredictionResult object
            prediction_results.append(PredictionResult(**result))

        return prediction_results

    except PyMongoError as e:
        logger.error(f"Error retrieving the latest prediction results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch the latest prediction results.",
        )
