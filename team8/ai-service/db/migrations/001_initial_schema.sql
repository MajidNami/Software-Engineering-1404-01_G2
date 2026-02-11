-- AI Service Database Schema

CREATE TYPE analysis_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- Post text moderation (spam, hate, sexual, violent, insult)
CREATE TABLE text_moderation (
    id BIGSERIAL PRIMARY KEY,
    post_ref_id BIGINT NOT NULL,
    is_approved BOOLEAN,
    score_clean FLOAT,
    score_spam FLOAT,
    score_hate FLOAT,
    score_sexual FLOAT,
    score_violent FLOAT,
    score_insult FLOAT,
    model_version VARCHAR(50),
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Image NSFW detection
CREATE TABLE image_moderation (
    id BIGSERIAL PRIMARY KEY,
    media_ref_id UUID NOT NULL,
    is_safe BOOLEAN,
    nsfw_score FLOAT,
    safe_score FLOAT,
    model_version VARCHAR(50),
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Image place tagging (Iranian landmark recognition)
CREATE TABLE image_tagging (
    id BIGSERIAL PRIMARY KEY,
    media_ref_id UUID NOT NULL,
    detected_place VARCHAR(100),
    confidence FLOAT,
    model_version VARCHAR(50),
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Place review/rating summaries
CREATE TABLE place_summaries (
    id BIGSERIAL PRIMARY KEY,
    place_ref_id BIGINT NOT NULL,
    overall_sentiment VARCHAR(20),
    summary_liked TEXT,
    summary_disliked TEXT,
    model_version VARCHAR(50),
    status analysis_status DEFAULT 'PENDING',
    error_message TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_text_mod_post ON text_moderation(post_ref_id);
CREATE INDEX idx_text_mod_status ON text_moderation(status);

CREATE INDEX idx_image_mod_media ON image_moderation(media_ref_id);
CREATE INDEX idx_image_mod_status ON image_moderation(status);

CREATE INDEX idx_image_tag_media ON image_tagging(media_ref_id);
CREATE INDEX idx_image_tag_status ON image_tagging(status);

CREATE INDEX idx_place_sum_place ON place_summaries(place_ref_id);
CREATE INDEX idx_place_sum_active ON place_summaries(place_ref_id) WHERE is_active = TRUE;
