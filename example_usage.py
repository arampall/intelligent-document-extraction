"""
Example script showing how to use the receipt scanner package.
"""

import os
import sys
import json

# Add src to path so we can import doc_extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from doc_extractor import process_receipt_dataset


def main():
    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: Please set GOOGLE_API_KEY environment variable")
        print("Example: export GOOGLE_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Example: Process a list of receipt images or PDFs
    # Replace with actual file paths
    file_paths = [
        # 'receipts/starbucks_receipt.jpg',
        # 'receipts/uber_receipt.pdf',
        # 'receipts/hotel_receipt.png',
    ]
    
    if not file_paths:
        print("Please add receipt file paths to the file_paths list in this script")
        print("\nExample:")
        print("  file_paths = [")
        print("      'path/to/receipt1.jpg',")
        print("      'path/to/receipt2.pdf',")
        print("  ]")
        return
    
    print(f"Processing {len(file_paths)} receipt(s)...")
    
    results = process_receipt_dataset(
        file_paths=file_paths,
        api_key=api_key,
        model='gemini-2.0-flash-exp',
        sleep_time=2  # Adjust based on your API rate limits
    )
    
    print(f"\n{'='*80}")
    print("PROCESSING COMPLETE")
    print(f"{'='*80}\n")
    
    # Calculate totals
    total_amount = sum(
        r['extracted_info'].get('total', 0)
        for r in results
        if isinstance(r['extracted_info'].get('total'), (int, float))
    )
    
    # Print summary
    print("\n📊 SUMMARY")
    print(f"Total Receipts: {len(results)}")
    print(f"Total Amount: ${total_amount:.2f}")
    print(f"Total Tokens: {sum(r['token_usage']['total'] for r in results):,}")
    
    # Print individual receipt summaries
    print("\n📋 RECEIPTS")
    for i, result in enumerate(results, 1):
        info = result['extracted_info']
        if 'error' in info:
            print(f"\n{i}. ERROR: {info['error']}")
            continue
            
        print(f"\n{i}. {info.get('merchant_name', 'Unknown')}")
        print(f"   Date: {info.get('date', 'N/A')}")
        print(f"   Total: ${info.get('total', 0):.2f}")
        print(f"   Category: {info.get('category', 'N/A')}")
        print(f"   Items: {len(info.get('items', []))}")
        print(f"   Tokens: {result['token_usage']['total']:,}")
    
    # Save results to JSON file
    output_file = 'receipt_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Optionally export to CSV
    export_csv = input("\nExport to CSV? (y/N): ").strip().lower()
    if export_csv == 'y':
        import csv
        
        csv_file = 'receipt_results.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Date', 'Merchant', 'Category', 'Subtotal', 'Tax', 'Total', 'Payment Method'
            ])
            writer.writeheader()
            
            for r in results:
                info = r['extracted_info']
                if 'error' not in info:
                    writer.writerow({
                        'Date': info.get('date', ''),
                        'Merchant': info.get('merchant_name', ''),
                        'Category': info.get('category', ''),
                        'Subtotal': info.get('subtotal', 0),
                        'Tax': info.get('tax', 0),
                        'Total': info.get('total', 0),
                        'Payment Method': info.get('payment_method', '')
                    })
        
        print(f"💾 CSV exported to: {csv_file}")


if __name__ == '__main__':
    main()
