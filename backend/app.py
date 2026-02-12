from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import PyPDF2
import os
from pathlib import Path

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/Users/pratyush/insurance ai/insurance-ai/data'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure data directory exists
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

@app.route('/upload-policy', methods=['POST'])
def upload_policy():
    """
    Upload a PDF policy file and extract text.
    
    Request:
        - multipart/form-data with file field containing PDF
    
    Response:
        - JSON with success message and text extraction status
    """
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        base_name = filename.rsplit('.', 1)[0]
        
        # Save PDF temporarily
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Save extracted text to .txt file
        txt_filename = f"{base_name}_extracted.txt"
        txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(extracted_text)
        
        return jsonify({
            'message': 'Text extracted successfully',
            'pdf_file': filename,
            'text_file': txt_filename,
            'text_length': len(extracted_text)
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'Backend is running'}), 200

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(debug=True, port=port)
