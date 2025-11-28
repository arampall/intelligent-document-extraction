# Receipt Scanner

Automatically extract and categorize expense information from receipt images using **Google Gemini Vision AI**.

## Overview

This application uses Google's Gemini Vision API to intelligently extract structured information from receipt images:
- 📸 **Merchant details** - Name, address, phone number
- 💰 **Financial info** - Total, subtotal, tax, payment method
- 🛒 **Line items** - Individual products with quantities and prices
- 📂 **Auto-categorization** - Automatic expense category assignment
- 📊 **Export** - JSON and CSV formats for accounting software

---

## 🚀 Quick Start

### Option 1: Streamlit Web App (Recommended)

The easiest way to get started with a beautiful web interface:

```bash
# Automated setup (installs everything)
chmod +x setup.sh
./setup.sh

# Then run the app
streamlit run app.py
```

The app will open at `http://localhost:8501` with:
- 📤 Drag-and-drop receipt upload (images or PDFs)
- 📊 Real-time processing with AI
- 📋 Beautiful results with category breakdown
- 💾 Export to JSON and CSV

### Option 2: Python API (For Developers)

For programmatic access and integration:

```python
import os
from src.doc_extractor import process_receipt_dataset

api_key = os.getenv('GOOGLE_API_KEY')
file_paths = ['receipts/starbucks.jpg', 'receipts/uber.pdf']

results = process_receipt_dataset(
    file_paths=file_paths,
    api_key=api_key,
    model='gemini-2.0-flash-exp'
)

# Access extracted data
for result in results:
    info = result['extracted_info']
    print(f"{info['merchant_name']}: ${info['total']:.2f}")
```

---

## Installation

### Automated Setup (Recommended)

Run the setup script to install all dependencies automatically:

```bash
./setup.sh
```

This will:
- ✅ Install Poppler (for PDF conversion)
- ✅ Create a virtual environment
- ✅ Install all Python dependencies

### Manual Setup

#### Prerequisites

**System Dependencies:**

- **Python 3.8+**
- **Poppler** (for PDF to image conversion only)

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
- Poppler: Download from [oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases/)

**Note:** Unlike traditional OCR solutions, this app does NOT require Tesseract or OpenCV!

#### Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

---

## Usage

### Web UI

1. **Run the app:**
   ```bash
   streamlit run app.py
   ```

2. **Configure in the sidebar:**
   - Enter your Google API key
   - Select Gemini model (`gemini-2.0-flash-exp` recommended)
   - Adjust rate limiting if needed

3. **Upload and scan:**
   - Drag and drop receipt images (JPG, PNG) or PDFs
   - Click "Scan Receipts"
   - View extracted data in organized tabs

4. **Export results:**
   - Download as JSON for detailed data
   - Download as CSV for accounting software (QuickBooks, Excel)

### Python API

#### Full Pipeline

```python
import os
from src.doc_extractor import process_receipt_dataset

# Set your Google API key
api_key = os.getenv('GOOGLE_API_KEY')  # or 'your-api-key-here'

# Process receipts
file_paths = [
    'receipts/starbucks_receipt.jpg',
    'receipts/hotel_receipt.pdf',
]

results = process_receipt_dataset(
    file_paths=file_paths,
    api_key=api_key,
    model='gemini-2.0-flash-exp',
    sleep_time=2  # seconds between receipts
)

# Access results
for result in results:
    info = result['extracted_info']
    print(f"Merchant: {info['merchant_name']}")
    print(f"Date: {info['date']}")
    print(f"Total: ${info['total']:.2f}")
    print(f"Category: {info['category']}")
    print(f"Items: {len(info['items'])}")
```

#### Individual Receipt

```python
from src.doc_extractor.extraction import extract_receipt_info
from pdf2image import convert_from_path

# Load receipt image
images = convert_from_path('receipt.pdf')

# Extract information
info, usage = extract_receipt_info(
    images=images,
    api_key=api_key,
    model='gemini-2.0-flash-exp'
)

print(info)  # Structured JSON data
```

---

## Extracted Information

The scanner extracts the following structured data:

```json
{
  "merchant_name": "Starbucks",
  "date": "2025-11-27",
  "time": "08:15",
  "total": 12.45,
  "subtotal": 11.50,
  "tax": 0.95,
  "payment_method": "Credit Card",
  "items": [
    {
      "name": "Latte",
      "quantity": 1,
      "price": 5.75
    },
    {
      "name": "Croissant",
      "quantity": 1,
      "price": 5.75
    }
  ],
  "category": "Meals & Entertainment",
  "address": "123 Main St, San Francisco, CA",
  "phone": "(555) 123-4567",
  "receipt_number": "1234567890"
}
```

### Automatic Categories

- 🍔 **Meals & Entertainment** - Restaurants, cafes, bars
- ✈️ **Travel** - Flights, trains, rental cars
- 📎 **Office Supplies** - Staples, office equipment
- 🚗 **Transportation** - Uber, taxis, gas, parking
- 🏨 **Lodging** - Hotels, motels, Airbnb
- 📦 **Other** - Everything else

---

## Configuration

### Environment Variables

Set your Google API key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

### Model Selection

Choose the right model for your needs:

| Model | Speed | Cost | Quality | Use Case |
|-------|-------|------|---------|----------|
| `gemini-2.0-flash-exp` | ⚡⚡⚡ | $ | Good | Default choice |
| `gemini-2.5-flash-lite` | ⚡⚡⚡ | $ | Good | Fast processing |
| `gemini-2.5-flash` | ⚡⚡ | $$ | Better | Complex receipts |
| `gemini-2.5-pro` | ⚡ | $$$ | Best | Maximum accuracy |

---

## Why This Approach?

### Advantages of Vision-Only (No OCR)

✅ **Simpler** - No Tesseract, OpenCV, or complex preprocessing  
✅ **More Accurate** - Gemini understands layout and context  
✅ **Handles Complexity** - Tables, multiple columns, mixed content  
✅ **Fewer Dependencies** - Easier deployment  
✅ **Better with Photos** - Works with crumpled, folded receipts  

### When to Use This

- ✅ Processing modern receipts and invoices
- ✅ Mobile receipt capture (photos)
- ✅ Complex layouts with tables
- ✅ Low to medium volume (< 10,000/month)
- ✅ Need quick setup and deployment

---

## Troubleshooting

### Common Issues

#### `PDFInfoNotInstalledError: Unable to get page count`
**Problem:** Poppler is not installed or not in PATH.

**Solution:**
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

Or run: `./setup.sh`

#### API Key Required
Enter your Google API key in the sidebar or set the `GOOGLE_API_KEY` environment variable.

#### Low Extraction Accuracy
- Use higher quality images (good lighting, not blurry)
- Try `gemini-2.5-pro` for better accuracy
- Ensure receipt is fully visible in image

#### Import Errors
Make sure you've activated your virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Project Structure

```
receipt-scanner/
├── src/
│   └── doc_extractor/          # Main package
│       ├── __init__.py          # Package initialization
│       ├── extraction.py        # Gemini Vision extraction
│       └── pipeline.py          # Batch processing
├── app.py                       # Streamlit web application
├── setup.sh                     # Automated setup script
├── requirements.txt             # Python dependencies (simplified!)
├── example_usage.py             # Example Python API usage
└── README.md                    # This file
```

---

## Real-World Use Cases

### 💼 Business Expense Management
- Employees scan receipts via mobile
- Auto-categorize for accounting
- Export to QuickBooks/Xero
- Eliminate manual data entry

### 🏪 Small Business Bookkeeping
- Process vendor invoices
- Track business expenses
- Prepare tax documents
- Reconcile accounts

### 👤 Personal Finance
- Track spending by category
- Prepare tax deductions
- Budget management
- Warranty/return tracking

---

## API Costs

Typical costs with Gemini 2.0 Flash:

- **Per receipt**: ~$0.0002 - $0.0005
- **1,000 receipts**: ~$0.20 - $0.50
- **10,000 receipts**: ~$2 - $5

Much cheaper than manual data entry at $0.50 - $2 per receipt!

---

## Roadmap

Future enhancements:

- [ ] Batch folder processing
- [ ] Receipt history database
- [ ] Duplicate detection
- [ ] Multi-currency support
- [ ] QuickBooks/Xero direct integration
- [ ] Mobile app (iOS/Android)
- [ ] Custom extraction templates
- [ ] Fraud detection (unusual amounts)

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT License

---

**Built with ❤️ using Streamlit and Google Gemini Vision API**