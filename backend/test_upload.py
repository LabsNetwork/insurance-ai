#!/usr/bin/env python3
"""
Test script for the upload-policy endpoint
"""

import requests
from pathlib import Path
import tempfile
import PyPDF2

# Create a sample PDF for testing
def create_sample_pdf(filename):
    """Create a simple PDF file for testing"""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    try:
        from reportlab.pdfgen import canvas
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Sample Insurance Policy")
        c.drawString(100, 720, "Coverage: Up to $100,000")
        c.drawString(100, 690, "Deductible: $500")
        c.save()
        
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        return True
    except ImportError:
        # If reportlab not available, create a minimal PDF manually
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Sample Insurance Policy) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000244 00000 n
0000000333 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
428
%%EOF"""
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        return True

def test_upload_endpoint():
    """Test the /upload-policy endpoint"""
    BASE_URL = 'http://localhost:5000'
    
    # Create test PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_path = tmp.name
    
    create_sample_pdf(pdf_path)
    print(f"✓ Created test PDF: {pdf_path}")
    
    # Test upload
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/upload-policy', files=files)
        
        print(f"✓ Response status: {response.status_code}")
        print(f"✓ Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ PDF upload and text extraction successful!")
        else:
            print("✗ Upload failed")
    
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to backend. Make sure server is running on port 5000")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Cleanup
        Path(pdf_path).unlink(missing_ok=True)

if __name__ == '__main__':
    test_upload_endpoint()
