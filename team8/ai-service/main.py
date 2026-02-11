import os
import logging
import tempfile
import traceback
from contextlib import asynccontextmanager

import httpx
import boto3
from botocore.client import Config
from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import (
    AnalysisStatus, TextModeration, ImageModeration, ImageTagging, PlaceSummary,
)
from registry import get_model

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ai-service")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "team8-internal-secret-change-me")

INTERNAL_HEADERS = {"X-Internal-Key": INTERNAL_API_KEY}

# S3 / MinIO client (read-only, to download images for inference)

S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET = os.getenv("S3_SECRET_KEY", "minioadmin123")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "team8-media")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS,
    aws_secret_access_key=S3_SECRET,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def download_s3_image(s3_object_key: str) -> str:
    """Download image from MinIO to a temp file, return path."""
    suffix = "." + s3_object_key.rsplit(".", 1)[-1] if "." in s3_object_key else ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    s3.download_fileobj(S3_BUCKET, s3_object_key, tmp)
    tmp.close()
    return tmp.name


# Callback helpers (sync — these run inside background threads)

def callback_post_moderation(post_id: int, score: float):
    """Send raw toxicity score to backend. Backend decides the status."""
    httpx.patch(
        f"{BACKEND_URL}/api/internal/posts/{post_id}/ai-verdict/",
        json={"score": score},
        headers=INTERNAL_HEADERS,
        timeout=10,
    )


def callback_media_moderation(media_id: str, score: float):
    """Send raw NSFW score to backend. Backend decides the status."""
    httpx.patch(
        f"{BACKEND_URL}/api/internal/media/{media_id}/ai-verdict/",
        json={"score": score},
        headers=INTERNAL_HEADERS,
        timeout=10,
    )


def callback_image_tagging(media_id: str, detected_place: str | None, confidence: float):
    httpx.patch(
        f"{BACKEND_URL}/api/internal/media/{media_id}/tag/",
        json={"detected_place": detected_place, "confidence": confidence},
        headers=INTERNAL_HEADERS,
        timeout=10,
    )


# Background task runners

def run_text_moderation(post_id: int, content: str, row_id: int):
    db: Session = next(get_db())
    row = db.get(TextModeration, row_id)
    try:
        row.status = AnalysisStatus.PROCESSING
        db.commit()

        classifier = get_model("comment_classifier")
        scores = classifier.predict(content)

        row.score_clean = scores.get("clean")
        row.score_spam = scores.get("spam")
        row.score_hate = scores.get("hate")
        row.score_sexual = scores.get("sexual")
        row.score_violent = scores.get("violent")
        row.score_insult = scores.get("insult")

        bad_score = max(
            scores.get("spam", 0) or 0,
            scores.get("hate", 0) or 0,
            scores.get("sexual", 0) or 0,
            scores.get("violent", 0) or 0,
            scores.get("insult", 0) or 0,
        )
        row.is_approved = bad_score < 0.5
        row.status = AnalysisStatus.COMPLETED
        db.commit()

        callback_post_moderation(post_id, score=bad_score)

    except Exception as e:
        row.status = AnalysisStatus.FAILED
        row.error_message = traceback.format_exc()
        db.commit()
        log.error("Text moderation failed for post %s: %s", post_id, e)
    finally:
        db.close()


def run_image_moderation(media_id: str, s3_object_key: str, row_id: int):
    db: Session = next(get_db())
    row = db.get(ImageModeration, row_id)
    tmp_path = None
    try:
        row.status = AnalysisStatus.PROCESSING
        db.commit()

        tmp_path = download_s3_image(s3_object_key)
        detector = get_model("nsfw_detector")
        result = detector.detect(tmp_path)

        row.nsfw_score = result.get("nsfw", 0.0)
        row.safe_score = result.get("normal", 0.0)
        row.is_safe = row.nsfw_score < 0.5
        row.status = AnalysisStatus.COMPLETED
        db.commit()

        callback_media_moderation(media_id, score=row.nsfw_score)

    except Exception as e:
        row.status = AnalysisStatus.FAILED
        row.error_message = traceback.format_exc()
        db.commit()
        log.error("Image moderation failed for media %s: %s", media_id, e)
    finally:
        db.close()
        if tmp_path:
            os.unlink(tmp_path)


def run_image_tagging(media_id: str, s3_object_key: str, row_id: int):
    db: Session = next(get_db())
    row = db.get(ImageTagging, row_id)
    tmp_path = None
    try:
        row.status = AnalysisStatus.PROCESSING
        db.commit()

        tmp_path = download_s3_image(s3_object_key)
        tagger = get_model("image_tagger")
        result = tagger.predict(tmp_path)

        row.detected_place = result["label"]
        row.confidence = result["confidence"]
        row.status = AnalysisStatus.COMPLETED
        db.commit()

        callback_image_tagging(media_id, row.detected_place, row.confidence)

    except Exception as e:
        row.status = AnalysisStatus.FAILED
        row.error_message = traceback.format_exc()
        db.commit()
        log.error("Image tagging failed for media %s: %s", media_id, e)
    finally:
        db.close()
        if tmp_path:
            os.unlink(tmp_path)


def run_place_summary(place_id: int, comments: list[str], ratings: list[float], row_id: int):
    db: Session = next(get_db())
    row = db.get(PlaceSummary, row_id)
    try:
        row.status = AnalysisStatus.PROCESSING
        db.commit()

        summarizer = get_model("comment_summarizer")
        result = summarizer.summarize(comments, ratings)

        row.overall_sentiment = result.get("overall_sentiment")
        row.summary_liked = result.get("why_liked", "")
        row.summary_disliked = result.get("why_disliked", "")
        row.status = AnalysisStatus.COMPLETED
        db.commit()

    except Exception as e:
        row.status = AnalysisStatus.FAILED
        row.error_message = traceback.format_exc()
        db.commit()
        log.error("Place summary failed for place %s: %s", place_id, e)
    finally:
        db.close()


# App 

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="AI Service", version="1.0.0", lifespan=lifespan)


# Request schemas

class ModerateTextReq(BaseModel):
    post_id: int
    content: str

class ModerateImageReq(BaseModel):
    media_id: str
    s3_object_key: str

class TagImageReq(BaseModel):
    media_id: str
    s3_object_key: str

class SummarizePlaceReq(BaseModel):
    place_id: int
    comments: list[str]
    ratings: list[float]


# Endpoints

@app.get("/health")
async def health():
    return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/moderate-text/")
async def moderate_text(req: ModerateTextReq, bg: BackgroundTasks, db: Session = Depends(get_db)):
    row = TextModeration(post_ref_id=req.post_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    bg.add_task(run_text_moderation, req.post_id, req.content, row.id)
    return {"id": row.id, "status": "PENDING"}


@app.post("/api/moderate-image/")
async def moderate_image(req: ModerateImageReq, bg: BackgroundTasks, db: Session = Depends(get_db)):
    row = ImageModeration(media_ref_id=req.media_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    bg.add_task(run_image_moderation, req.media_id, req.s3_object_key, row.id)
    return {"id": row.id, "status": "PENDING"}


@app.post("/api/tag-image/")
async def tag_image(req: TagImageReq, bg: BackgroundTasks, db: Session = Depends(get_db)):
    row = ImageTagging(media_ref_id=req.media_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    bg.add_task(run_image_tagging, req.media_id, req.s3_object_key, row.id)
    return {"id": row.id, "status": "PENDING"}


@app.post("/api/summarize-place/")
async def summarize_place(req: SummarizePlaceReq, bg: BackgroundTasks, db: Session = Depends(get_db)):
    # Deactivate previous summaries for this place
    db.query(PlaceSummary).filter(
        PlaceSummary.place_ref_id == req.place_id,
        PlaceSummary.is_active == True,
    ).update({"is_active": False})

    row = PlaceSummary(place_ref_id=req.place_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    bg.add_task(run_place_summary, req.place_id, req.comments, req.ratings, row.id)
    return {"id": row.id, "status": "PENDING"}


@app.get("/api/place-summary/{place_id}")
async def get_place_summary(place_id: int, db: Session = Depends(get_db)):
    row = db.query(PlaceSummary).filter(
        PlaceSummary.place_ref_id == place_id,
        PlaceSummary.is_active == True,
        PlaceSummary.status == AnalysisStatus.COMPLETED,
    ).first()
    if not row:
        return {"summary": None}
    return {
        "place_id": row.place_ref_id,
        "overall_sentiment": row.overall_sentiment,
        "summary_liked": row.summary_liked,
        "summary_disliked": row.summary_disliked,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
    }


@app.get("/api/status/{table}/{row_id}")
async def get_analysis_status(table: str, row_id: int, db: Session = Depends(get_db)):
    model_map = {
        "text_moderation": TextModeration,
        "image_moderation": ImageModeration,
        "image_tagging": ImageTagging,
        "place_summaries": PlaceSummary,
    }
    model = model_map.get(table)
    if not model:
        return {"error": "invalid table"}
    row = db.get(model, row_id)
    if not row:
        return {"error": "not found"}
    return {"id": row_id, "status": row.status.value}
