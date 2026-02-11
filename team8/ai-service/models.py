from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, Float,
    String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TextModeration(Base):
    __tablename__ = "text_moderation"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_ref_id = Column(BigInteger, nullable=False, index=True)
    is_approved = Column(Boolean)
    score_clean = Column(Float)
    score_spam = Column(Float)
    score_hate = Column(Float)
    score_sexual = Column(Float)
    score_violent = Column(Float)
    score_insult = Column(Float)
    model_version = Column(String(50))
    status = Column(Enum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, index=True)
    error_message = Column(Text)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class ImageModeration(Base):
    __tablename__ = "image_moderation"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    media_ref_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    is_safe = Column(Boolean)
    nsfw_score = Column(Float)
    safe_score = Column(Float)
    model_version = Column(String(50))
    status = Column(Enum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, index=True)
    error_message = Column(Text)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class ImageTagging(Base):
    __tablename__ = "image_tagging"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    media_ref_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    detected_place = Column(String(100))
    confidence = Column(Float)
    model_version = Column(String(50))
    status = Column(Enum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, index=True)
    error_message = Column(Text)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())


class PlaceSummary(Base):
    __tablename__ = "place_summaries"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    place_ref_id = Column(BigInteger, nullable=False, index=True)
    overall_sentiment = Column(String(20))
    summary_liked = Column(Text)
    summary_disliked = Column(Text)
    model_version = Column(String(50))
    status = Column(Enum(AnalysisStatus, name="analysis_status"), default=AnalysisStatus.PENDING, index=True)
    error_message = Column(Text)
    is_active = Column(Boolean, default=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
