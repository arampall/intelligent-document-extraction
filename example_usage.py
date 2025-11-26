"""
Example script showing how to use the doc_extractor package.

"""

import os
import sys

# Add src to path so we can import doc_extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from doc_extractor import process_resume_dataset


def main():
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: Please set GOOGLE_API_KEY environment variable")
        print("Example: export GOOGLE_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Example: Process a list of resume PDFs
    # Replace with actual file paths
    file_paths = [
        # 'path/to/resume1.pdf',
        # 'path/to/resume2.pdf',
    ]
    
    if not file_paths:
        print("Please add PDF file paths to the file_paths list in this script")
        return
    
    print(f"Processing {len(file_paths)} resume files...")
    
    results = process_resume_dataset(
        file_paths=file_paths,
        api_key=api_key,
        model='gemini-2.0-flash-exp',
        sleep_time=60  # Adjust based on your API rate limits
    )
    
    print(f"\n{'='*80}")
    print("PROCESSING COMPLETE")
    print(f"{'='*80}\n")
    
    # Print summary
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {os.path.basename(result['file_path'])}")
        print(f"   Category: {result['extracted_info'].get('category', 'N/A')}")
        print(f"   Experience: {result['extracted_info'].get('Experience', 'N/A')}")
        print(f"   Education: {result['extracted_info'].get('education', 'N/A')}")
        print(f"   Tokens: {result['token_usage']['total']}")
    
    # TODO: Save results to JSON/CSV file
    # import json
    # with open('extraction_results.json', 'w') as f:
    #     json.dump(results, f, indent=2)


if __name__ == '__main__':
    main()
