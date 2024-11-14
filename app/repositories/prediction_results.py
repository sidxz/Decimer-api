from typing import List
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status
from app.core.mongo_config import get_async_collection, get_sync_collection
from app.schema.results.prediction_result import PredictionResult
from app.core.logging_config import logger


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
