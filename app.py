from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO
import uuid
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

class ImageProcessor:
    # Position presets
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_CENTER = "bottom_center"
    TOP_CENTER = "top_center"

    def __init__(self, temp_dir="temp"):
        # Default settings
        self.font_path = "Arial.ttf"  # System font
        self.font_size = 24
        self.text_color = "white"
        self.padding = 20  # Padding from edges
        self.temp_dir = temp_dir
        
        # Create temp directory if it doesn't exist
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Load default font
        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except:
            # Fallback to default system font if Arial not found
            self.font = ImageFont.load_default().font_variant(size=self.font_size)

    def _get_text_position(self, image_size, text_size, position):
        """Calculate text position based on preset options"""
        width, height = image_size
        text_width, text_height = text_size
        
        positions = {
            self.BOTTOM_RIGHT: (
                width - text_width - self.padding,
                height - text_height - self.padding
            ),
            self.BOTTOM_CENTER: (
                (width - text_width) // 2,
                height - text_height - self.padding
            ),
            self.TOP_CENTER: (
                (width - text_width) // 2,
                self.padding
            )
        }
        
        return positions.get(position, positions[self.BOTTOM_RIGHT])

    def download_image(self, url):
        """
        Download image from URL and return path to temporary file
        """
        try:
            # Generate unique filename
            temp_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            
            # Download and save image
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            img.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None

    def process_image_url(
        self,
        image_url,
        text,
        output_path=None,
        position=BOTTOM_RIGHT,
        font_size=None,
        text_color=None,
        cleanup=True
    ):
        """
        Download image, add text, and optionally cleanup temporary files
        """
        temp_path = None
        try:
            # Download image
            temp_path = self.download_image(image_url)
            if not temp_path:
                return None
                
            # Generate output path if not provided
            if not output_path:
                output_filename = f"processed_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                output_path = os.path.join(self.temp_dir, output_filename)
            
            # Add text overlay
            result = self.add_text(
                temp_path,
                text,
                output_path,
                position,
                font_size,
                text_color
            )
            
            return result
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
            
        finally:
            # Cleanup temporary files if requested
            if cleanup and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass

    def add_text(
        self,
        image_path,
        text,
        output_path=None,
        position=BOTTOM_RIGHT,
        font_size=None,
        text_color=None
    ):
        """
        Add text to an image and save it
        """
        try:
            # Open image
            img = Image.open(image_path)
            
            # Create drawing object
            draw = ImageDraw.Draw(img)
            
            # Configure font
            if font_size:
                try:
                    font = ImageFont.truetype(self.font_path, font_size)
                except:
                    font = ImageFont.load_default().font_variant(size=font_size)
            else:
                font = self.font
                
            # Get text size
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_size = (
                text_bbox[2] - text_bbox[0],
                text_bbox[3] - text_bbox[1]
            )
            
            # Get position
            text_position = self._get_text_position(
                img.size,
                text_size,
                position
            )
            
            # Draw text
            draw.text(
                text_position,
                text,
                font=font,
                fill=text_color or self.text_color
            )
            
            # Save image
            output_path = output_path or image_path
            img.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error adding text to image: {str(e)}")
            return None

# Initialize global ImageProcessor instance
processor = ImageProcessor()

@app.route('/process-image', methods=['POST'])
def process_image_endpoint():
    """
    Flask endpoint to process images
    
    Expected JSON payload:
    {
        "image_url": "https://example.com/image.jpg",
        "text": "Watermark text",
        "position": "bottom_right",  // optional
        "font_size": 24,            // optional
        "text_color": "white"       // optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'image_url' not in data or 'text' not in data:
            return jsonify({
                'error': 'Missing required fields: image_url and text'
            }), 400
            
        # Process image
        output_path = processor.process_image_url(
            image_url=data['image_url'],
            text=data['text'],
            position=data.get('position', ImageProcessor.BOTTOM_RIGHT),
            font_size=data.get('font_size', None),
            text_color=data.get('text_color', None)
        )
        
        if not output_path:
            return jsonify({
                'error': 'Failed to process image'
            }), 500
            
        # Return processed image
        return send_file(output_path, mimetype='image/png')
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    # Use PORT environment variable for Cloud Run
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
