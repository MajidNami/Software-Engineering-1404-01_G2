"""
AI Service Database Models
SQLAlchemy models matching the AI database schema
"""
from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Enum, Float, 
    String, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MediaAnalysis(Base):
    __tablename__ = "media_analysis"

    analysis_id = Column(BigInteger, primary_key=True, autoincrement=True)
    media_ref_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # ML Model Outputs
    detected_location = Column(String(100))
    is_safe_media = Column(Boolean)
    is_safe_caption = Column(Boolean)
    confidence_score = Column(Float)
    model_version = Column(String(20))
    
    # Status Tracking
    status = Column(
        Enum(AnalysisStatus, name="analysis_status"), 
        default=AnalysisStatus.PENDING,
        index=True
    )
    error_message = Column(Text)
    
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<MediaAnalysis(id={self.analysis_id}, media_ref={self.media_ref_id}, status={self.status})>"


class TextAnalysis(Base):
    __tablename__ = "text_analysis"

    analysis_id = Column(BigInteger, primary_key=True, autoincrement=True)
    post_ref_id = Column(BigInteger, nullable=False, index=True)
    
    # ML Model Outputs
    extracted_tags = Column(Text)
    is_spam = Column(Boolean, default=False)
    sentiment_score = Column(Float)
    
    # Status Tracking
    status = Column(
        Enum(AnalysisStatus, name="analysis_status"), 
        default=AnalysisStatus.PENDING,
        index=True
    )
    error_message = Column(Text)
    
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TextAnalysis(id={self.analysis_id}, post_ref={self.post_ref_id}, status={self.status})>"


class PlaceSummary(Base):
    __tablename__ = "place_summaries"

    summary_id = Column(BigInteger, primary_key=True, autoincrement=True)
    place_ref_id = Column(BigInteger, nullable=False, index=True)
    summary_text = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<PlaceSummary(id={self.summary_id}, place_ref={self.place_ref_id}, active={self.is_active})>"
