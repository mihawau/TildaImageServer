from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Pexels API configuration
PEXELS_API_KEY = "7poOKbnjMnx0lz2Ku8yxgidIoarKBwAM7y7ZQih2XvfQwcJQVmqtwwIu"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

@app.route("/")
def home():
    return "Pexels API search is running. Use /search?keyword=cat"

@app.route("/search")
def search_images():
    keyword = request.args.get('keyword')
    
    if not keyword:
        return jsonify({
            "error": "Keyword parameter is required"
        }), 400
    
    # Prepare headers for Pexels API
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    # Prepare parameters for API request
    params = {
        "query": keyword,
        "per_page": 7
    }
    
    try:
        # Make request to Pexels API
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        photos = data.get("photos", [])
        
        # Extract medium-sized image URLs
        image_urls = []
        for photo in photos:
            if "src" in photo and "medium" in photo["src"]:
                image_urls.append(photo["src"]["medium"])
        
        return jsonify({
            "keyword": keyword,
            "images": image_urls,
            "count": len(image_urls)
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Failed to fetch images from Pexels API: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)