import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from app.utils.http_client import api_client

# Load environment variables from a .env file (if available)
load_dotenv()

def get_molecule_by_smiles(smiles: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a molecule's data using its SMILES string.

    Args:
        smiles (str): The SMILES string representing the molecule.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the API, or None if an error occurs.
    """
    base_url = os.getenv("DAIKON_MLX_URL")
    endpoint = "/molecule/similar/"
    params = {"SMILES": smiles, "Threshold": 1, "Limit": 1, "WithMeta": "false"}
    return api_client(base_url=base_url, endpoint=endpoint, params=params)
