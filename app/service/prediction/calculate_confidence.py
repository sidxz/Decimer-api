from typing import List, Tuple

import numpy as np


def calculate_overall_confidence(smiles_with_confidence: Tuple[str, List[Tuple[str, float]]]) -> float:
    """
    Calculate the overall confidence score for a predicted SMILES string.

    Args:
        smiles_with_confidence (Tuple[str, List[Tuple[str, float]]]): 
        A tuple where the first element is the predicted SMILES string, 
        and the second element is a list of tuples containing each character and its confidence.

    Returns:
        float: The overall confidence score.
    """
    _, confidence_list = smiles_with_confidence
    if not confidence_list:
        return 0.0
    
    # Extract confidence values and calculate the mean
    confidence_values = [confidence for _, confidence in confidence_list]
    overall_confidence = calculate_geometric_mean_confidence(confidence_values)
    #print(f"Mean confidence: {calculate_mean_confidence(confidence_values)}")
    #print(f"Geometric mean confidence: {overall_confidence}")
    #print(f"Harmonic mean confidence: {calculate_harmonic_mean_confidence(confidence_values)}")
    #print(f"Minimum confidence: {calculate_minimum_confidence(confidence_values)}")
    
    
    return overall_confidence
  

# The arithmetic mean is a simple way to calculate the overall confidence score.
def calculate_mean_confidence(confidences: List[float]) -> float:
    return np.mean(confidences)
  
# The geometric mean is a good option when you want to ensure that a single low-confidence character has a larger impact on reducing the overall score.
def calculate_geometric_mean_confidence(confidences: List[float]) -> float:
    return np.prod(confidences) ** (1 / len(confidences)) if confidences else 0.0
  
# Useful if you want to prioritize a conservative estimate where every character needs to be confidently predicted.
def calculate_harmonic_mean_confidence(confidences: List[float]) -> float:
    return len(confidences) / sum(1 / conf for conf in confidences) if confidences else 0.0
  
# This metric is useful when accuracy of the entire string is critical and a single incorrect character can invalidate the result.
def calculate_minimum_confidence(confidences: List[float]) -> float:
    return np.min(confidences)