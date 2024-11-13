import cv2
import numpy as np
from pdf2image import convert_from_path
from typing import List, Optional
from app.core.logging_config import logger


def pdf_to_images(pdf_path: str) -> List[np.ndarray]:
    """
    Convert each page of a PDF to a numpy array.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        List[np.ndarray]: A list of numpy arrays, each representing a page of the PDF.
    """
    try:
        # Convert PDF pages to PIL images
        logger.info(f"Converting PDF '{pdf_path}' to images...")
        pil_images = convert_from_path(pdf_path)

        # Convert each PIL image to a numpy array
        page_images = [cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) for image in pil_images]

        logger.info(f"Successfully converted {len(page_images)} pages.")
        return page_images

    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        return []
    except Exception as e:
        logger.error(f"An error occurred during PDF to image conversion: {str(e)}")
        return []