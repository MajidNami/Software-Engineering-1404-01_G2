-- AI Service Database Schema
-- PostgreSQL Schema for ML Analysis Results

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enums
CREATE TYPE analysis_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- Media Analysis Table
CREATE TABLE media_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    media_ref_id UUID NOT NULL, -- Logical Reference to Backend DB (media.media_id)
    
    -- ML Model Outputs
    detected_location VARCHAR(100),
    is_safe_media BOOLEAN,
    is_safe_caption BOOLEAN,
    confidence_score FLOAT,
    model_version VARCHAR(20),
    
    -- Status Tracking
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Text Analysis Table (for comments)
CREATE TABLE text_analysis (
    analysis_id BIGSERIAL PRIMARY KEY,
    post_ref_id BIGINT NOT NULL, -- Logical Ref to Backend DB (posts.post_id)
    
    -- ML Model Outputs
    extracted_tags TEXT,
    is_spam BOOLEAN DEFAULT FALSE,
    sentiment_score FLOAT,
    
    -- Status Tracking
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Place Summaries Table
CREATE TABLE place_summaries (
    summary_id BIGSERIAL PRIMARY KEY,
    place_ref_id BIGINT NOT NULL, -- Logical Reference to Backend DB (places.place_id)
    summary_text TEXT,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for Reference Lookups
CREATE INDEX idx_media_analysis_ref ON media_analysis(media_ref_id);
CREATE INDEX idx_media_analysis_status ON media_analysis(status);
CREATE INDEX idx_media_analysis_completed ON media_analysis(analyzed_at DESC) WHERE status = 'COMPLETED';

CREATE INDEX idx_text_analysis_ref ON text_analysis(post_ref_id);
CREATE INDEX idx_text_analysis_status ON text_analysis(status);
CREATE INDEX idx_text_analysis_completed ON text_analysis(analyzed_at DESC) WHERE status = 'COMPLETED';

CREATE INDEX idx_place_summaries_ref ON place_summaries(place_ref_id);
CREATE INDEX idx_place_summaries_active ON place_summaries(place_ref_id, is_active) WHERE is_active = TRUE;

-- Unique Constraints (Prevent duplicate completed analysis)
CREATE UNIQUE INDEX idx_media_analysis_unique ON media_analysis(media_ref_id) 
WHERE status = 'COMPLETED';

CREATE UNIQUE INDEX idx_text_analysis_unique ON text_analysis(post_ref_id) 
WHERE status = 'COMPLETED';
