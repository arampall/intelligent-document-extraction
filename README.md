# Intelligent Document Extraction

Extract structured information from PDF documents using OpenCV preprocessing, Tesseract OCR, and Google Gemini LLM.

## Overview

It application uses a hybrid approach combining traditional computer vision with modern AI:
1. **OpenCV** - Image preprocessing (grayscale, noise reduction, binarization, deskew correction)
2. **Tesseract** - Optical Character Recognition (OCR)
3. **Google Gemini** - Intelligent information extraction from images + text

## Project Structure

```
intelligent-document-extraction/
├── src/
│   └── doc_extractor/          # Main package
│       ├── __init__.py          # Package initialization
│       ├── preprocessing.py     # OpenCV image preprocessing
│       ├── extraction.py        # OCR + LLM extraction
│       └── pipeline.py          # End-to-end processing
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Poppler** (for PDF to image conversion):
   ```bash
   # macOS
   brew install poppler
   
   # Ubuntu/Debian
   sudo apt-get install poppler-utils
   
   # Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/
   ```

3. **Tesseract OCR**:
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### 1. Python API

```python
import os
from src.doc_extractor import process_resume_dataset

# Set your Google API key
api_key = os.getenv('GOOGLE_API_KEY')  # or 'your-api-key-here'

# Process PDFs
file_paths = [
    'path/to/file1.pdf',
    'path/to/file2.pdf',
]

results = process_resume_dataset(
    file_paths=file_paths,
    api_key=api_key,
    model='gemini-2.0-flash-exp',  # or 'gemini-1.5-flash'
    sleep_time=60  # seconds between API calls
)

# Access results
for result in results:
    print(f"File: {result['file_path']}")
    print(f"Info: {result['extracted_info']}")
    print(f"Tokens used: {result['token_usage']['total']}")
```

### 2. Using Individual Components

```python
from src.doc_extractor.preprocessing import convert_pdf_to_image, process_one_image
from src.doc_extractor.extraction import extract_text_from_image
import numpy as np

# Convert PDF to images
images = convert_pdf_to_image('resume.pdf')

# Process first page
processed = process_one_image(np.array(images[0]))

# Extract text
text = extract_text_from_image(processed)
print(text)
```

## Configuration

### Environment Variables

Set your Google API key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

### API Rate Limiting

The default sleep time between API calls is 60 seconds. Adjust based on your quota:
```python
results = process_resume_dataset(
    file_paths=file_paths,
    api_key=api_key,
    sleep_time=30  # Reduce to 30 seconds
)
```