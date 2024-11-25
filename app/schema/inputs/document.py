from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, UUID4
from typing import List, Optional
from uuid import uuid4
import pytz

class Document(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Unique identifier for the document, automatically generated
    id: UUID4 = Field(default_factory=uuid4, title="The unique identifier of the prediction result")
    run_id: Optional[int] = Field(0, title="The unique identifier of the prediction run")

    # Required fields
    file_path: str = Field(..., title="The path to the input file")

    # Optional file-related fields
    file_type: Optional[str] = Field(None, title="The type of the input file")
    ext_path: Optional[str] = Field(None, title="The original path to the input file")
    doc_hash: Optional[str] = Field(None, title="The SHA-256 hash of the input file")
    link: Optional[str] = Field(None, title="The link to the input file")
    ext_id: Optional[str] = Field(None, title="The external identifier of the input file")

    # Optional timestamps
    date_created: Optional[datetime] = Field(default_factory=lambda: datetime.now(pytz.utc), title="The date and time of the file upload")
    date_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(pytz.utc), title="The date and time of the last update")

    # Optional user-related fields
    created_by: Optional[str] = Field(None, title="The user who uploaded the file")
    updated_by: Optional[str] = Field(None, title="The user who last updated the file")

    # Optional document metadata
    author: Optional[str] = Field(None, title="The author of the document")
    date_published: Optional[datetime] = Field(None, title="The date of publication of the document")
    title: Optional[str] = Field(None, title="The title of the document")

    # Optional tags associated with the document
    tags: List[str] = Field(default_factory=list, title="Tags associated with the document")
    molecule_tags: List[str] = Field(default_factory=list, title="Molecule tags associated with the document")
    daikon_molecule_ids: List[str] = Field(default_factory=list, title="Daikon molecule IDs associated with the document")

    
    def json_serializable(self) -> dict:
        """Convert the object to a JSON-serializable dictionary."""
        return {
            "id": str(self.id),
            "run_id": self.run_id,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "ext_path": self.ext_path,
            "doc_hash": self.doc_hash,
            "link": self.link,
            "ext_id": self.ext_id,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "author": self.author,
            "date_published": self.date_published,
            "title": self.title,
            "tags": self.tags,
            "molecule_tags": self.molecule_tags,
            "daikon_molecule_ids": self.daikon_molecule_ids,
        }