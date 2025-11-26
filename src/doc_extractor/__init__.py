"""
Document Extractor - Intelligent PDF document information extraction.

This package provides tools for extracting structured information from PDF documents
using OpenCV preprocessing, Tesseract OCR, and Google Gemini LLM.
"""

from .preprocessing import (
    convert_pdf_to_image,
    convert_to_grayscale,
    reduce_noise,
    binarize_image,
    deskew_image,
    process_one_image
)

from .extraction import (
    extract_text_from_image,
    extract_resume_info
)

from .pipeline import (
    process_resume_dataset
)

__version__ = '0.1.0'

__all__ = [
    # Preprocessing
    'convert_pdf_to_image',
    'convert_to_grayscale',
    'reduce_noise',
    'binarize_image',
    'deskew_image',
    'process_one_image',
    
    # Extraction
    'extract_text_from_image',
    'extract_resume_info',
    
    # Pipeline
    'process_resume_dataset',
]
