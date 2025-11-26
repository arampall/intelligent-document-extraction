"""
OCR and LLM-based information extraction.

This module contains functions for extracting text using Tesseract
and extracting structured information using Gemini LLM.
"""

import pytesseract
import json
from google import genai


# Prompt template for LLM extraction
PROMPT_TEMPLATE = """
Extract the information from the given list of images corresponding to a resume. The images are to be read in the order.
Information to be extracted: category, total years of experience in the category, highest education.
The images has been converted to grayscale, noise reduced, binarized, and deskewed using opencv.
Always give your response in the following format:
{
    "category": "category",
    "Experience": "total years of experience in the category",
    "education": "highest education",
}
Also, the text has been extracted from the images using tesseract.
Use the extracted text as support for extracting information.
If you believe the text extraction is incorrect somewhere, you may correct it yourself and provide corrected information.
Respond with the extracted information only in the specified format.
Here is the text extracted from all the images of the resume:


"""


def extract_text_from_image(processed_image):
    """Extract text from preprocessed image using Tesseract OCR.
    
    Args:
        processed_image: Preprocessed image (numpy array)
        
    Returns:
        Extracted text as string
    """
    # TODO: Add error handling for OCR failures
    # TODO: Add custom Tesseract configuration options
    return pytesseract.image_to_string(processed_image)


def extract_resume_info(images, extracted_text, api_key, model='gemini-2.0-flash-exp'):
    """Extract structured information from resume using LLM.
    
    Args:
        images: List of PIL Images (all pages of resume)
        extracted_text: Combined OCR text from all images
        api_key: Google API key for Gemini
        model: Model name to use (default: gemini-2.0-flash-exp)
        
    Returns:
        Tuple of (extracted_info dict, usage_metadata)
    """
    # TODO: Fix prompt construction bug - currently prompt grows across iterations
    # TODO: Add error handling for API failures
    # TODO: Add retry logic with exponential backoff
    # TODO: Add rate limiting
    
    # Initialize Gemini client
    genai_client = genai.Client(api_key=api_key)
    
    # Build the prompt
    prompt = PROMPT_TEMPLATE + extracted_text
    
    # Prepare multimodal content (images + text)
    contents = [
        images,
        {
            "text": prompt
        }
    ]
    
    print("\nExtracting information from image and text using LLM")
    
    # Call Gemini API
    response = genai_client.models.generate_content(
        model=model,
        contents=contents
    )
    
    # Access the usage_metadata attribute
    usage_metadata = response.usage_metadata
    
    # Parse JSON response
    # TODO: Add better error handling for malformed JSON
    extracted_information = json.loads(
        response.text.replace('```json', '').replace('```', '')
    )
    
    return extracted_information, usage_metadata
