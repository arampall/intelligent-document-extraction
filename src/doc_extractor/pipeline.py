"""
Main pipeline for processing receipt documents.
"""

import time
from pdf2image import convert_from_path
from .extraction import extract_receipt_info


def process_receipt_dataset(file_paths, api_key, model='gemini-2.0-flash-exp', sleep_time=2):
    """Process a list of receipt files and extract structured information.
    
    Args:
        file_paths: List of paths to receipt files (PDF or image)
        api_key: Google API key for Gemini
        model: Gemini model name to use
        sleep_time: Seconds to sleep between API calls (for rate limiting)
        
    Returns:
        List of extracted information dictionaries
    """
    start_time = time.time()
    results = []
    
    print(f"\n{'='*80}")
    print(f"📝 Processing {len(file_paths)} receipt(s)")
    print(f"{'='*80}\n")
    
    for num, file_path in enumerate(file_paths):
        print(f"📄 Receipt {num + 1}/{len(file_paths)}: {file_path}")
        
        try:
            # Convert PDF to images (if it's a PDF)
            # For image files, convert_from_path will still work
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path, fmt='jpg')
                print(f"   → Converted PDF to {len(images)} image(s)")
            else:
                # For direct image files, wrap in list
                from PIL import Image
                images = [Image.open(file_path)]
                print(f"   → Loaded image file")
            
            # Extract receipt information using Gemini Vision
            extracted_information, usage_metadata = extract_receipt_info(
                images, 
                api_key,
                model
            )
            
            # Display key information
            print(f"\n   ✅ Extraction Complete:")
            if 'merchant_name' in extracted_information:
                print(f"      Merchant: {extracted_information.get('merchant_name', 'N/A')}")
                print(f"      Date: {extracted_information.get('date', 'N/A')}")
                print(f"      Total: ${extracted_information.get('total', 0):.2f}")
                print(f"      Category: {extracted_information.get('category', 'N/A')}")
            
            # Print token usage
            print(f"\n   📊 Token Usage:")
            print(f"      Input: {usage_metadata.prompt_token_count:,}")
            print(f"      Output: {usage_metadata.candidates_token_count:,}")
            print(f"      Total: {usage_metadata.total_token_count:,}")
            
            results.append({
                'file_path': file_path,
                'extracted_info': extracted_information,
                'token_usage': {
                    'prompt': usage_metadata.prompt_token_count,
                    'thoughts': getattr(usage_metadata, 'thoughts_token_count', 0),
                    'output': usage_metadata.candidates_token_count,
                    'total': usage_metadata.total_token_count
                }
            })
            
        except Exception as e:
            print(f"   ❌ Error processing receipt: {str(e)}")
            results.append({
                'file_path': file_path,
                'extracted_info': {'error': str(e)},
                'token_usage': {
                    'prompt': 0,
                    'thoughts': 0,
                    'output': 0,
                    'total': 0
                }
            })
        
        print(f"\n{'-'*80}\n")
        
        # Rate limiting (skip sleep after last file)
        if num < len(file_paths) - 1:
            if sleep_time > 0:
                print(f"⏳ Waiting {sleep_time} seconds before next receipt...")
                time.sleep(sleep_time)
    
    elapsed_time = time.time() - start_time
    print(f"{'='*80}")
    print(f"✅ All receipts processed!")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"📊 Average: {elapsed_time/len(file_paths):.2f} seconds per receipt")
    print(f"{'='*80}\n")
    
    return results
