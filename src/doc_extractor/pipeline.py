"""
Main pipeline for processing resume documents.
"""

import time
import numpy as np
from .preprocessing import convert_pdf_to_image, process_one_image
from .extraction import extract_text_from_image, extract_resume_info


def process_resume_dataset(file_paths, api_key, model='gemini-2.0-flash-exp', sleep_time=60):
    """Process a list of resume PDF files and extract structured information.
    
    Args:
        file_paths: List of paths to PDF files
        api_key: Google API key for Gemini
        model: Gemini model name to use
        sleep_time: Seconds to sleep between API calls (for rate limiting)
        
    Returns:
        List of extracted information dictionaries
    """
    # TODO: Add output persistence - save results incrementally
    # TODO: Add progress tracking/reporting
    # TODO: Add error recovery - continue processing if one file fails
    # TODO: Return results instead of just printing
    
    start_time = time.time()
    results = []
    
    # for each pdf file
    for num, file_path in enumerate(file_paths):
        print(f"Begin processing the pdf file {num + 1}/{len(file_paths)} - {file_path}")
        
        # TODO: Add try-except for entire file processing
        
        # convert file to images
        images = convert_pdf_to_image(file_path)
        print(f"Converted the pdf file in {len(images)} images")
        
        # preprocess and extract from each image
        output = ''
        
        for i, image in enumerate(images):
            # preprocess image
            print(f"\n### IMAGE {i+1} ###")
            processed_image = process_one_image(np.array(image))
            
            # extract text from image using tesseract
            print("-> Extracting text from image using tesseract")
            text = extract_text_from_image(processed_image)
            output += f"\nPage {i} contents\n\n{text}"
            print("-> Completed data extraction from Image")
        
        # send prompt to llm for intelligent document extraction
        # TODO: BUG FIX - This is accumulating output across ALL files, not just current file
        extracted_information, usage_metadata = extract_resume_info(
            images, 
            output, 
            api_key,
            model
        )
        
        print("### OUTPUT ###")
        print(extracted_information)
        
        # Print the different token counts
        print("\n\n## SUMMARY ##")
        print(f"Input Token Count: {usage_metadata.prompt_token_count}")
        print(f"Thoughts Token Count: {usage_metadata.thoughts_token_count}")
        print(f"Output Token Count: {usage_metadata.candidates_token_count}")
        print(f"Total Token Count: {usage_metadata.total_token_count}\n\n")
        
        results.append({
            'file_path': file_path,
            'extracted_info': extracted_information,
            'token_usage': {
                'prompt': usage_metadata.prompt_token_count,
                'thoughts': usage_metadata.thoughts_token_count,
                'output': usage_metadata.candidates_token_count,
                'total': usage_metadata.total_token_count
            }
        })
        
        print("-" * 100)
        
        # Rate limiting
        if num < len(file_paths) - 1:  # Don't sleep after last file
            time.sleep(sleep_time)
    
    print("Information Extraction Completed.")
    print(f"Total time taken: {time.time() - start_time} seconds")
    
    return results
