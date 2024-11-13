from typing import List, Optional, Any
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
import pytz


class PipelineHistory(BaseModel):
    step: str
    timestamp: datetime
    status: str
    details: Optional[str] = None


class PredictionResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    file_path: str = Field(..., title="The path to the input file")
    page: int = Field(..., title="The page number of the document")
    segmented_image: Optional[np.ndarray] = Field(None, title="The segmented image as a numpy array")
    predicted_smiles: Optional[str] = Field(None, title="The predicted SMILES string")
    confidence_f: Optional[float] = Field(None, title="The confidence score of the prediction")
    daikon_molecule_id: Optional[str] = Field(None, title="The molecule identifier")
    daikon_molecule_name: Optional[str] = Field(None, title="The molecule name")
    history: List[PipelineHistory] = Field(default_factory=list)
    
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
