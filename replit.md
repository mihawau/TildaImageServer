# Image Upload Service

## Overview

This is a Flask-based web application designed to handle file uploads, specifically optimized for image processing. The service provides a RESTful API endpoint for receiving image files along with keywords, with built-in file validation, security measures, and optimization capabilities. The application is designed to integrate with external form services like Tilda, enabling seamless file upload functionality for web forms.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask**: Lightweight Python web framework chosen for its simplicity and flexibility in handling file uploads
- **CORS Support**: Enabled across all routes to support cross-origin requests from external form services
- **File Upload Handling**: Built-in support for multipart form data with configurable size limits

### File Management System
- **Upload Directory**: Dedicated `uploads` folder for storing processed files
- **File Validation**: Multi-layer security including extension checking and MIME type verification
- **Size Restrictions**: 16MB maximum file size limit to prevent abuse
- **Allowed Formats**: Restricted to common image formats (PNG, JPG, JPEG, GIF, WebP, BMP, SVG)

### Security Measures
- **Filename Sanitization**: Uses Werkzeug's secure_filename utility
- **MIME Type Verification**: Double-checks file types beyond extension validation
- **Request Size Limiting**: Flask's MAX_CONTENT_LENGTH configuration prevents oversized uploads
- **Secret Key Management**: Environment variable-based session secret with fallback

### Frontend Interface
- **Bootstrap 5**: Modern, responsive UI framework with dark theme
- **Test Interface**: Development form for testing upload functionality
- **Real-time Feedback**: JavaScript-based form handling with progress indicators
- **Font Awesome Icons**: Enhanced visual interface elements

### Application Structure
- **Modular Design**: Separate app.py and main.py for clean application factory pattern
- **Template System**: Jinja2 templating for dynamic HTML generation
- **Static Assets**: CSS customizations and client-side JavaScript
- **Error Handling**: Comprehensive exception handling for upload failures

### Image Processing Pipeline
- **PIL/Pillow Integration**: Referenced in attached assets for image optimization
- **SEO-Friendly Naming**: Keyword-based filename generation with timestamps
- **Quality Optimization**: Configurable compression settings for storage efficiency

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-CORS**: Cross-origin resource sharing support
- **Werkzeug**: Secure filename handling and HTTP utilities
- **Pillow (PIL)**: Image processing and optimization (referenced in assets)

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome 6**: Icon library for enhanced visual elements

### Development Tools
- **Python Logging**: Built-in logging configuration for debugging
- **Environment Variables**: Configuration management for deployment flexibility

### Potential Integrations
- **Tilda Forms**: Primary target for form submission integration
- **File Storage Services**: Can be extended to support cloud storage solutions
- **CDN Integration**: Architecture supports future CDN implementation for optimized file delivery