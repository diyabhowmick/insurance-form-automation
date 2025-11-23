"""
PDF Text Extraction Module
Extracts text from PDF files using PyMuPDF (fitz)
Handles both text-based and image-based PDFs
"""

import fitz  # PyMuPDF
import io
from typing import List, Dict

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file: Uploaded PDF file (BytesIO or file path)
        
    Returns:
        str: Extracted text from all pages
    """
    try:
        # Read the PDF file
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer for potential reuse
        else:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
        
        # Open PDF with PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_content = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():  # If text exists
                text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            else:
                # If no text, might be an image-based PDF
                # Note: For OCR, you'd need additional setup with pytesseract
                text_content.append(f"--- Page {page_num + 1} ---\n[Image-based page - OCR needed]")
        
        doc.close()
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_multiple_pdfs(pdf_files: List) -> Dict[str, str]:
    """
    Extract text from multiple PDF files.
    
    Args:
        pdf_files: List of uploaded PDF files
        
    Returns:
        dict: Dictionary mapping filename to extracted text
    """
    results = {}
    
    for pdf_file in pdf_files:
        filename = pdf_file.name if hasattr(pdf_file, 'name') else 'unknown.pdf'
        try:
            text = extract_text_from_pdf(pdf_file)
            results[filename] = text
        except Exception as e:
            results[filename] = f"Error: {str(e)}"
    
    return results


def get_pdf_info(pdf_file) -> Dict[str, any]:
    """
    Get metadata information about the PDF.
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        dict: PDF metadata (pages, size, etc.)
    """
    try:
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
        else:
            with open(pdf_file, 'rb') as f:
                pdf_bytes = f.read()
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        info = {
            'page_count': len(doc),
            'size_bytes': len(pdf_bytes),
            'metadata': doc.metadata
        }
        
        doc.close()
        return info
    
    except Exception as e:
        return {'error': str(e)}