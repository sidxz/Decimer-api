from fastapi import APIRouter, FastAPI, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from app.pipeline.smiles_prediction import predict_smiles
import shutil
import os
from app.core.logging_config import logger
router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile, origin_ext_path: str):
    logger.info(f"Uploading file: {file.filename} {origin_ext_path}")
    upload_directory = os.getenv("UPLOAD_DIRECTORY")
    if not upload_directory:
        raise HTTPException(
            status_code=500, detail="Upload directory is not configured."
        )
    file_location = os.path.join(upload_directory, file.filename)
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # Handle file save errors gracefully
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Start the background task
    task = predict_smiles.delay(
        file_location=file_location, origin_ext_path=origin_ext_path
    )
    return {"task_id": task.id, "message": "Document processing started."}


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "PENDING":
        return {"status": "Processing", "task_id": task_id}
    elif task_result.state == "SUCCESS":
        return {"status": "Completed", "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"status": "Failed", "message": str(task_result.info)}
    return {"status": task_result.state}


@router.get("/results/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == "SUCCESS":
        return {"status": "Completed", "result": task_result.result}
    return {"status": "Not available"}
