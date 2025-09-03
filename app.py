import os
import logging
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid
import mimetypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Enable CORS for all routes to support Tilda form submissions
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension and is actually an image"""
    if not filename:
        return False
    
    # Check extension
    has_allowed_ext = '.' in filename and \
                     filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    return has_allowed_ext

def is_image_file(file_path):
    """Verify that the file is actually an image by checking MIME type"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type and mime_type.startswith('image/')

@app.route('/')
def index():
    """Display test form for development purposes"""
    return render_template('test_form.html')

@app.route('/submit', methods=['POST'])
def handle_form_submission():
    """Handle form submissions from Tilda or other sources"""
    try:
        # Get keyword from form data
        keyword = request.form.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': 'Keyword is required'
            }), 400
        
        # Handle file uploads
        uploaded_files = []
        files = request.files.getlist('files') or request.files.getlist('file')
        
        # Also check for single file upload with different field names
        if not files:
            for field_name in request.files:
                file = request.files[field_name]
                if file and file.filename:
                    files = [file]
                    break
        
        if not files or all(not file.filename for file in files):
            return jsonify({
                'success': False,
                'error': 'At least one file is required'
            }), 400
        
        for file in files:
            if file and file.filename:
                # Validate file type
                if not allowed_file(file.filename):
                    return jsonify({
                        'success': False,
                        'error': f'Invalid file type: {file.filename}. Only image files are allowed.'
                    }), 400
                
                # Generate unique filename to prevent conflicts
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                
                # Save file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Verify it's actually an image
                if not is_image_file(file_path):
                    os.remove(file_path)  # Clean up invalid file
                    return jsonify({
                        'success': False,
                        'error': f'File {original_filename} is not a valid image'
                    }), 400
                
                uploaded_files.append({
                    'original_name': original_filename,
                    'saved_name': unique_filename,
                    'path': file_path
                })
                
                logging.info(f"Successfully saved file: {original_filename} as {unique_filename}")
        
        # Return success response
        response_data = {
            'success': True,
            'keyword': keyword,
            'files': uploaded_files,
            'message': f'Successfully processed {len(uploaded_files)} file(s)'
        }
        
        logging.info(f"Form submission processed successfully: keyword='{keyword}', files={len(uploaded_files)}")
        
        return jsonify(response_data), 200
        
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum size allowed is {MAX_FILE_SIZE // (1024*1024)}MB'
        }), 413
        
    except Exception as e:
        logging.error(f"Error processing form submission: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error occurred while processing your request'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size': f"{MAX_FILE_SIZE // (1024*1024)}MB",
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    }), 200

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size allowed is {MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle method not allowed errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
