"""
Receipt extraction using Google Gemini Vision API.

This module provides functions for extracting structured information
from receipt images using only the Gemini Vision API.
"""

import json
from google import genai


# Prompt template for receipt extraction
RECEIPT_EXTRACTION_PROMPT = """
Analyze this receipt image and extract all relevant information.

Extract the following information in JSON format:
{
    "merchant_name": "Name of the business/store",
    "date": "Date in YYYY-MM-DD format",
    "time": "Time in HH:MM format (24-hour)",
    "total": "Total amount as a number",
    "subtotal": "Subtotal before tax (if available)",
    "tax": "Tax amount (if available)",
    "payment_method": "Payment method (Cash, Credit Card, Debit Card, etc.)",
    "items": [
        {
            "name": "Item name",
            "quantity": "Quantity as number",
            "price": "Price per unit as number"
        }
    ],
    "category": "Expense category (one of: Meals & Entertainment, Travel, Office Supplies, Transportation, Lodging, Other)",
    "address": "Store address (if available)",
    "phone": "Store phone number (if available)",
    "receipt_number": "Receipt/transaction number (if available)"
}

Important notes:
- Extract all amounts as numbers (e.g., 12.45, not "$12.45")
- Use standard date format YYYY-MM-DD
- Categorize based on the merchant and items purchased
- If information is not available, use null
- Be accurate with item names and prices
- For category, choose the most appropriate from the list provided

Respond with ONLY the JSON object, no additional text.
"""


def extract_receipt_info(images, api_key, model='gemini-2.0-flash-exp'):
    """Extract structured information from receipt using Gemini Vision API.
    
    Args:
        images: List of PIL Images (receipt pages, usually just 1)
        api_key: Google API key for Gemini
        model: Model name to use (default: gemini-2.0-flash-exp)
        
    Returns:
        Tuple of (extracted_info dict, usage_metadata)
    """
    # Initialize Gemini client
    genai_client = genai.Client(api_key=api_key)
    
    # Prepare multimodal content (images + text prompt)
    contents = [
        images,
        {"text": RECEIPT_EXTRACTION_PROMPT}
    ]
    
    print("🔍 Extracting receipt information using Gemini Vision...")
    
    # Call Gemini API
    response = genai_client.models.generate_content(
        model=model,
        contents=contents
    )
    
    # Access the usage metadata
    usage_metadata = response.usage_metadata
    
    # Parse JSON response
    try:
        # Clean up any markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith('```'):
            # Remove code block markers
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        extracted_information = json.loads(response_text)
        
        # Add auto-calculated fields
        if extracted_information.get('items') and not extracted_information.get('subtotal'):
            # Calculate subtotal from items if not provided
            subtotal = sum(
                item.get('price', 0) * item.get('quantity', 1) 
                for item in extracted_information['items']
            )
            if subtotal > 0:
                extracted_information['subtotal'] = round(subtotal, 2)
        
        print("✅ Successfully extracted receipt information")
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse JSON response: {e}")
        print(f"Raw response: {response.text}")
        # Return a basic structure with the error
        extracted_information = {
            "error": "Failed to parse receipt",
            "raw_response": response.text
        }
    
    return extracted_information, usage_metadata


def categorize_expense(merchant_name, items):
    """
    Helper function to suggest expense category based on merchant and items.
    This is a fallback if the LLM doesn't categorize properly.
    
    Args:
        merchant_name: Name of the merchant
        items: List of items purchased
        
    Returns:
        Suggested category string
    """
    merchant_lower = merchant_name.lower() if merchant_name else ""
    
    # Food & Dining
    food_keywords = ['restaurant', 'cafe', 'coffee', 'starbucks', 'burger', 'pizza', 'diner', 'bar']
    if any(keyword in merchant_lower for keyword in food_keywords):
        return "Meals & Entertainment"
    
    # Office Supplies
    office_keywords = ['staples', 'office', 'depot', 'supplies', 'amazon']
    if any(keyword in merchant_lower for keyword in office_keywords):
        return "Office Supplies"
    
    # Transportation
    transport_keywords = ['uber', 'lyft', 'taxi', 'parking', 'gas', 'fuel', 'shell', 'chevron']
    if any(keyword in merchant_lower for keyword in transport_keywords):
        return "Transportation"
    
    # Lodging
    lodging_keywords = ['hotel', 'motel', 'airbnb', 'inn', 'resort']
    if any(keyword in merchant_lower for keyword in lodging_keywords):
        return "Lodging"
    
    # Travel
    travel_keywords = ['airline', 'airport', 'flight', 'train', 'rental']
    if any(keyword in merchant_lower for keyword in travel_keywords):
        return "Travel"
    
    return "Other"
