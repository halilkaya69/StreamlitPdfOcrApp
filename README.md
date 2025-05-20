# PDF OCR Application

This is a Streamlit-based web application that allows you to extract content from PDF files using different methods:

- **PDFPlumber**: Extracts text and tables directly from PDF files
- **PyTesseract (OCR)**: Uses Optical Character Recognition to extract text from PDF pages
- **PyMuPDF**: Fast PDF processing with support for text and image extraction

## Features

- Multiple extraction methods
- Support for Turkish language OCR
- Table extraction and display
- Image extraction from PDFs
- Output in both Markdown and JSON formats

## Installation

1. Install Python dependencies:
```console
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

3. Make sure Tesseract is in your system PATH or update the path in `app.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Usage - Local
Run
```console
streamlit run main.py
```
