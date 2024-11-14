from typing import List, Optional, Any
import numpy as np
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
import pytz
import base64
import cv2

class PipelineHistory(BaseModel):
    step: str
    timestamp: datetime
    status: str
    details: Optional[str] = None


class PredictionResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    document_id: UUID4
    file_path: str = Field(..., title="The path to the input file")
    page: int = Field(..., title="The page number of the document")
    segmented_image: Optional[np.ndarray] = Field(None, title="The segmented image as a numpy array")
    predicted_smiles: Optional[str] = Field(None, title="The predicted SMILES string")
    confidence_f: Optional[float] = Field(None, title="The confidence score of the prediction")
    daikon_molecule_id: Optional[str] = Field(None, title="The molecule identifier")
    daikon_molecule_name: Optional[str] = Field(None, title="The molecule name")
    history: List[PipelineHistory] = Field(default_factory=list)
    run_date: Optional[datetime] = Field(default_factory=lambda: datetime.now(pytz.utc), title="The date and time of the run")
    
    
    @property
    def confidence(self) -> Optional[float]:
        """Get the rounded confidence value."""
        return self.confidence_f

    @confidence.setter
    def confidence(self, value: Optional[float]) -> None:
        """Set the confidence value and round it to 2 decimal places."""
        if value is not None:
            try:
                self.confidence_f = round(float(value), 2)
            except (ValueError, TypeError):
                raise ValueError("Confidence must be a valid float")
        else:
            self.confidence_f = value
            
    def json_serializable(self) -> dict:
        """Convert the object to a JSON-serializable dictionary."""
        return {
            "run_date": self.run_date.isoformat(),
            "document_id": self.document_id,
            "file_path": self.file_path,
            "page": self.page,
            "segmented_image": self.image_to_base64() if self.segmented_image is not None else None,
            "predicted_smiles": self.predicted_smiles,
            "confidence": self.confidence,
            "daikon_molecule_id": self.daikon_molecule_id,
            "daikon_molecule_name": self.daikon_molecule_name,
            "history": [entry.model_dump() for entry in self.history]
        }

    def image_to_base64(self) -> str:
        """Convert np.ndarray image to Base64 string."""
        if self.segmented_image is not None:
            _, buffer = cv2.imencode('.png', self.segmented_image)
            return base64.b64encode(buffer).decode('utf-8')
        return ""

    def add_history(self, step: str, status: str, details: Optional[str] = None) -> None:
        """Add a new entry to the processing history."""
        utc_now = datetime.now(pytz.utc)
        self.history.append(
            PipelineHistory(
                step=step,
                timestamp=utc_now,
                status=status,
                details=details
            )
        )

    def print_result(self) -> None:
        """Print the prediction result in a readable format."""
        print("=" * 20)
        print(f"File path: {self.file_path}")
        print(f"Page: {self.page}")
        print(f"Predicted SMILES: {self.predicted_smiles or 'N/A'}")
        print(f"Confidence: {self.confidence if self.confidence is not None else 'N/A'}")
        print(f"Daikon molecule ID: {self.daikon_molecule_id or 'N/A'}")
        print(f"Daikon molecule name: {self.daikon_molecule_name or 'N/A'}")
        print("History:")
        if not self.history:
            print("No history available.")
        else:
            for entry in self.history:
                print(f"[{entry.timestamp.isoformat()}] {entry.step} - {entry.status}: {entry.details or 'No details'}")
        print("=" * 20)
