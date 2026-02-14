<!-- # AI Service

FastAPI service for AI model inference.

## Responsibilities

- **Spam Detection**: Detect spam/offensive content in comments
- **Place Recognition**: Recognize Iranian landmarks from images

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### POST /detect-spam
Detect spam in comment text

**Request:**
```json
{
  "comment_id": 123,
  "content": "متن کامنت"
}
```

**Response:**
```json
{
  "comment_id": 123,
  "is_spam": false,
  "confidence": 0.95,
  "categories": ["clean"]
}
```

### POST /recognize-place
Recognize place from image

**Request:**
```json
{
  "media_id": "uuid-here",
  "file_path": "path/to/image.jpg"
}
```

**Response:**
```json
{
  "media_id": "uuid-here",
  "predicted_place": "تخت_جمشید",
  "confidence": 0.87
}
```

## Model Files

Place these files in the `ai-service/models/` directory:

- `convnext_iranian_landmarksTop136.pth` - Place recognition model
- `persian_comment_model.pth` - Spam detection model

## For AI Team Members

The actual model implementation goes in `models.py`. The current `main.py` provides placeholder responses for integration testing. -->
