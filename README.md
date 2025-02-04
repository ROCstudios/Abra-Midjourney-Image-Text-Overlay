<img align="right" width="250" src="https://github.com/user-attachments/assets/35206713-75c8-4cb7-97d1-22393f271d28"/>

<h3>Midjourney Image Labeller in Python</h3>

```
#### Deploy as little Google Cloud Service

# 1. Install Google Cloud SDK
# Visit: https://cloud.google.com/sdk/docs/install

# 2. Initialize GCP and set your project
gcloud init
gcloud config set project YOUR_PROJECT_ID

# 3. Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com

# 4. Build and deploy to Cloud Run (do this from your project directory)
gcloud run deploy image-processor \

  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Use it**

```
# Health check
curl https://image-processor-xxxxx-uc.a.run.app/health

# Process image
curl -X POST https://image-processor-xxxxx-uc.a.run.app/process-image \
-H "Content-Type: application/json" \
-d '{
    "image_url": "https://example.com/some-image.jpg",
    "text": "Test Watermark",
    "position": "bottom_right"
}'
```

### Basic SSH
```
ssh USERNAME@PUBLIC_IP

```

Here's how we get python environment working without sudo access and installing pythong:
### Flask App Setup on Cloudways
```bash
# 1. Install virtualenv locally (without sudo)
pip3 install --user virtualenv

# 2. Create virtual environment using the local virtualenv
~/.local/bin/virtualenv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Install Flask
pip install flask

# 5. Create a basic Flask app (app.py)
cat > app.py << 'EOL'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
EOL
```
