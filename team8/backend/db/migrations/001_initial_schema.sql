-- Team 8 Database Schema
-- PostgreSQL Schema for Comments, Media & Ratings System

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enums
CREATE TYPE content_status AS ENUM ('PENDING_AI', 'PENDING_ADMIN', 'APPROVED', 'REJECTED');
CREATE TYPE report_status AS ENUM ('OPEN', 'RESOLVED', 'DISMISSED');
CREATE TYPE report_target AS ENUM ('MEDIA', 'POST');

-- Users table
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Provinces table (استان)
CREATE TABLE provinces (
    province_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    name_en VARCHAR(50)
);

-- Cities table (شهر)
CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    province_id INT NOT NULL REFERENCES provinces(province_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),
    
    CONSTRAINT unique_city_per_province UNIQUE (province_id, name)
);

-- Categories table
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    name_en VARCHAR(50)
);

-- Places table
CREATE TABLE places (
    place_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    city_id INT NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326),
    category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media table
CREATE TABLE media (
    media_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    place_id BIGINT NOT NULL REFERENCES places(place_id) ON DELETE CASCADE,
    
    -- S3 Storage Info
    s3_object_key VARCHAR(255) NOT NULL,
    bucket_name VARCHAR(50) NOT NULL DEFAULT 'tourism-prod-media',
    mime_type VARCHAR(50) NOT NULL,
    
    -- Moderation
    status content_status DEFAULT 'PENDING_AI',
    ai_confidence FLOAT,
    rejection_reason TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ -- Soft Delete
);

-- Posts table
CREATE TABLE posts (
    post_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    parent_id BIGINT REFERENCES posts(post_id) ON DELETE CASCADE,
    place_id BIGINT NOT NULL REFERENCES places(place_id) ON DELETE CASCADE,
    media_id UUID REFERENCES media(media_id) ON DELETE SET NULL,
    
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    status content_status DEFAULT 'PENDING_AI',
    
    -- Per-component AI verdicts
    text_ai_status content_status DEFAULT 'PENDING_AI',
    media_ai_status content_status,  -- NULL when post has no media
    ai_confidence FLOAT,
    rejection_reason TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ -- Soft Delete
);

-- Ratings table
CREATE TABLE ratings (
    rating_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    place_id BIGINT NOT NULL REFERENCES places(place_id) ON DELETE CASCADE,
    score SMALLINT NOT NULL CHECK (score >= 1 AND score <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_place_rating UNIQUE (user_id, place_id)
);

-- Post Votes table
CREATE TABLE post_votes (
    vote_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    post_id BIGINT NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    is_like BOOLEAN NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_post_vote UNIQUE (user_id, post_id)
);

-- Activity logs table
CREATE TABLE activity_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: Validate action_type values
    CONSTRAINT valid_action_type CHECK (
        action_type IN (
            'POST_CREATED', 'POST_UPDATED', 'POST_DELETED',
            'MEDIA_UPLOADED', 'MEDIA_DELETED',
            'RATING_CREATED', 'RATING_UPDATED',
            'VOTE_CREATED', 'VOTE_UPDATED',
            'REPORT_CREATED', 'REPORT_RESOLVED',
            'PLACE_CREATED', 'PLACE_UPDATED',
            'USER_LOGIN', 'USER_LOGOUT',
            'AI_TEXT_VERDICT', 'AI_MEDIA_VERDICT', 'AI_MEDIA_TAG',
            'ADMIN_APPROVED', 'ADMIN_REJECTED'
        )
    )
);

-- Notifications table
CREATE TABLE notifications (
    notification_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    report_id BIGSERIAL PRIMARY KEY,
    reporter_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    target_type report_target NOT NULL,
    
    -- Polymorphic Target Columns
    reported_media_id UUID REFERENCES media(media_id) ON DELETE SET NULL,
    reported_post_id BIGINT REFERENCES posts(post_id) ON DELETE SET NULL,
    
    reason TEXT NOT NULL,
    status report_status DEFAULT 'OPEN',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure correct ID is present based on type
    CONSTRAINT check_report_target CHECK (
        (target_type = 'MEDIA' AND reported_media_id IS NOT NULL) OR
        (target_type = 'POST' AND reported_post_id IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_media_user ON media(user_id);
CREATE INDEX idx_media_place_status ON media(place_id, status);
CREATE INDEX idx_media_deleted_at ON media(deleted_at) WHERE deleted_at IS NULL;

CREATE INDEX idx_posts_user ON posts(user_id);
CREATE INDEX idx_posts_place_status ON posts(place_id, status);
CREATE INDEX idx_posts_parent ON posts(parent_id);
CREATE INDEX idx_posts_deleted_at ON posts(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_posts_created_desc ON posts(created_at DESC); -- For feed sorting
CREATE INDEX idx_posts_media ON posts(media_id) WHERE media_id IS NOT NULL; -- Find posts with media

CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_place ON ratings(place_id);

CREATE INDEX idx_post_votes_user ON post_votes(user_id);
CREATE INDEX idx_post_votes_post ON post_votes(post_id);
CREATE INDEX idx_post_votes_post_like ON post_votes(post_id, is_like);

CREATE INDEX idx_reports_reporter ON reports(reporter_id);
CREATE INDEX idx_reports_status ON reports(status);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);

CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_action ON activity_logs(action_type);
CREATE INDEX idx_activity_logs_created ON activity_logs(created_at);

CREATE INDEX idx_places_location ON places USING GIST(location);
CREATE INDEX idx_places_category ON places(category_id);
CREATE INDEX idx_places_city ON places(city_id);
CREATE INDEX idx_cities_province ON cities(province_id);
