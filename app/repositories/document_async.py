from typing import List, Union
from fastapi import HTTPException, status
from pydantic import UUID4
from pymongo.errors import PyMongoError
from app.core.mongo_config import get_async_collection
from app.schema.inputs.document import Document
from app.core.logging_config import logger


async def save_document(document: Document) -> UUID4:
    """
    Save document metadata to MongoDB and return its ID.
    """
    logger.info("Saving document to MongoDB")
    try:
        collection = await get_async_collection("documents")
        doc_dict = document.model_dump()
        await collection.insert_one(doc_dict)
        return document.id
    except PyMongoError as e:
        logger.error(f"Failed to save document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save document: {str(e)}",
        )


async def get_document_by_field(
    field: str, value: Union[str, UUID4, List[str]]
) -> Document:
    """
    Retrieve a document from MongoDB based on a specified field and value.
    """
    try:
        collection = await get_async_collection("documents")
        query = {field: value}
        document = await collection.find_one(query)
        if document:
            return Document(**document)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with {field}='{value}' not found",
        )
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}",
        )


async def get_document_by_id(doc_id: UUID4) -> Document:
    """Retrieve a document by its ID."""
    return await get_document_by_field("id", doc_id)


async def get_document_by_hash(doc_hash: str) -> Document:
    """Retrieve a document by its hash."""
    return await get_document_by_field("doc_hash", doc_hash)


async def get_document_by_filename(filename: str) -> Document:
    """Retrieve a document by its filename."""
    return await get_document_by_field("filename", filename)


async def get_document_by_file_path(file_path: str) -> Document:
    """Retrieve a document by its file path."""
    return await get_document_by_field("file_path", file_path)


async def get_documents_by_tags(tags: List[str]) -> List[Document]:
    """Retrieve documents by tags."""
    try:
        collection = await get_async_collection("documents")
        cursor = collection.find({"tags": {"$in": tags}})
        results = await cursor.to_list(length=100)
        return [Document(**doc) for doc in results]
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}",
        )


async def get_documents_by_molecule_tags(molecule_tags: List[str]) -> List[Document]:
    """Retrieve documents by molecule tags."""
    return await get_documents_by_tags(molecule_tags)


async def get_documents_by_daikon_ids(daikon_ids: List[str]) -> List[Document]:
    """Retrieve documents by Daikon molecule IDs."""
    try:
        collection = await get_async_collection("documents")
        cursor = collection.find({"daikon_molecule_ids": {"$in": daikon_ids}})
        results = await cursor.to_list(length=100)
        return [Document(**doc) for doc in results]
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}",
        )
