"""
Receipt extraction package.

This package provides functions for extracting structured information
from receipt images using Google Gemini Vision API.
"""

from .pipeline import process_receipt_dataset
from .extraction import extract_receipt_info

__all__ = ['process_receipt_dataset', 'extract_receipt_info']
