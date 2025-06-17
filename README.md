# Construction Cost Breakdown Automation

This tool automates the process of extracting line items from builder documents (PDF, Excel, images) and populating a standardized Excel template using AI-powered text parsing.

## Features

- **Multi-format Support**: Works with PDF, Excel, and image files
- **AI-Powered Parsing**: Uses Google Gemini AI to intelligently extract line items and costs
- **OCR Support**: Extracts text from images and scanned PDFs using Tesseract
- **Template Population**: Automatically fills your Excel template with extracted data
- **Multiple Interfaces**: Command-line tool and GUI application

## Quick Start

### 1. Installation

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Set Up AI API Key

Get a free Google Gemini API key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable:

**Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Or edit `config.py`:**
```python
GEMINI_API_KEY = "your_actual_api_key_here"
```

### 3. Install Tesseract (for OCR)

**Windows:**
1. Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to your PATH or update `config.py`

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

## Usage

### GUI Application (Recommended)

Run the user-friendly interface:

```bash
python ui_app.py
```

1. Select your builder document (PDF, Excel, or image)
2. Confirm the template file path
3. Optionally specify an output file name
4. Click "Process Document"

### Command Line Interface

```bash
# Basic usage
python cli_app.py "Cost break down-Prem.pdf"

# Specify output file
python cli_app.py "Cost break down-Prem.pdf" --output "Prem_breakdown.xlsx"

# Use custom template
python cli_app.py "builder_doc.pdf" --template "my_template.xlsx"

# Provide API key directly
python cli_app.py "builder_doc.pdf" --api-key "your_api_key"
```

### Python API

```python
from construction_cost_automation import ConstructionCostAutomation

# Initialize with API key
automation = ConstructionCostAutomation("your_api_key")

# Process a document
result = automation.process_document(
    input_file="Cost break down-Prem.pdf",
    template_path="_Construction_Breakdown_Template_BLANK.xlsx",
    output_path="completed_breakdown.xlsx"
)

if result:
    print(f"Success! File saved to: {result}")
```

## File Structure

```
construction_cost_automation.py    # Main automation class
ui_app.py                         # GUI application
cli_app.py                        # Command line interface
config.py                         # Configuration settings
requirements.txt                  # Python dependencies
README.md                         # This file
```

## How It Works

1. **Text Extraction**: The tool extracts text from your document using:
   - PyMuPDF for PDFs
   - Pandas for Excel files
   - Tesseract OCR for images

2. **AI Parsing**: The extracted text is sent to Google Gemini AI with specific instructions to:
   - Identify line items and their costs
   - Exclude totals and administrative fees
   - Format the data as structured JSON

3. **Template Population**: The parsed data is inserted into your Excel template:
   - Line items go into the "Line Item" column
   - Amounts go into the "Original Contract Amount" column
   - Data is inserted starting from the first empty row

## Supported File Types

- **PDF**: `.pdf`
- **Excel**: `.xlsx`, `.xls`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`

## Template Format

Your Excel template should have these columns:
- `Construction Cost Breakdown\nLine Item\n(allowances in bold italics)`
- `Original Contract Amount`

The tool will find the first empty row and start inserting data there.

## Troubleshooting

### Common Issues

1. **"No text could be extracted"**
   - Check if the file is corrupted
   - For images, ensure they're clear and readable
   - Try a different file format

2. **"No line items could be extracted"**
   - Verify your API key is correct
   - Check your internet connection
   - The document might not contain recognizable cost data

3. **OCR not working**
   - Install Tesseract OCR
   - Update the `TESSERACT_PATH` in `config.py`

4. **Template not found**
   - Ensure the template file exists
   - Check the file path in `config.py`

### Getting Help

If you encounter issues:
1. Run with `--verbose` flag for detailed error messages
2. Check the log output in the GUI application
3. Verify all dependencies are installed correctly

## API Key Setup

### Option 1: Environment Variable (Recommended)
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Mac/Linux
export GEMINI_API_KEY=your_api_key_here
```

### Option 2: Config File
Edit `config.py`:
```python
GEMINI_API_KEY = "your_actual_api_key_here"
```

### Option 3: Command Line
```bash
python cli_app.py document.pdf --api-key your_api_key_here
```

## Examples

### Processing a PDF
```bash
python cli_app.py "Cost Breakdown -Constrution Arndt.pdf"
```

### Processing with Custom Output
```bash
python cli_app.py "Safranek cost.pdf" --output "Safranek_processed.xlsx"
```

### Batch Processing Multiple Files
```python
from construction_cost_automation import ConstructionCostAutomation

automation = ConstructionCostAutomation()
documents = [
    "Cost break down-Prem.pdf",
    "Cost Breakdown -Constrution Arndt.pdf",
    "Safranek cost.pdf"
]

for doc in documents:
    result = automation.process_document(
        doc, 
        "_Construction_Breakdown_Template_BLANK.xlsx"
    )
    if result:
        print(f"✅ Processed: {doc} -> {result}")
    else:
        print(f"❌ Failed: {doc}")
```

## License

This project is for internal use. Please ensure you comply with Google's API terms of service when using the Gemini AI service.
