from typing import List, Optional, Any
import numpy as np
from pydantic import BaseModel, ConfigDict, Field
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
    daikon_molecule_id: Optional[str] = Field(None, title="The molecule identifier")
    daikon_molecule_name: Optional[str] = Field(None, title="The molecule name")
    history: List[PipelineHistory] = Field(default_factory=list)

    def add_history(self, step: str, status: str, details: Optional[str] = None):
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

    def print_result(self):
        print("=" * 20)
        print(f"File path: {self.file_path}")
        print(f"Page: {self.page}")
        print(f"Predicted SMILES: {self.predicted_smiles}")
        print(f"Daikon molecule ID: {self.daikon_molecule_id}")
        print(f"Daikon molecule name: {self.daikon_molecule_name}")
        print("History:")
        for entry in self.history:
            print(f"[{entry.timestamp}] {entry.step} - {entry.status}: {entry.details}")
