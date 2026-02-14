
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

/* 1) cmr_users :contentReference[oaicite:1]{index=1} */
CREATE TABLE IF NOT EXISTS cmr_users (
  id_user       CHAR(36)      NOT NULL,
  username      VARCHAR(100)  NOT NULL,
  email         VARCHAR(255)  NULL,
  is_moderator  BOOLEAN       NOT NULL DEFAULT FALSE,
  created_at    DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id_user),
  UNIQUE KEY uq_cmr_users_email (email),
  KEY idx_cmr_users_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 2) cmr_targets (+ target_name requested) :contentReference[oaicite:2]{index=2} */
CREATE TABLE IF NOT EXISTS cmr_targets (
  id_target    CHAR(36)      NOT NULL,
  entity_type  VARCHAR(50)   NULL,
  entity_id    CHAR(36)      NOT NULL,
  target_name  VARCHAR(255)  NULL,
  created_at   DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id_target),
  KEY idx_cmr_targets_entity (entity_type, entity_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



/* 3) cmr_comments :contentReference[oaicite:3]{index=3} */
CREATE TABLE IF NOT EXISTS cmr_comments (
  id_comment         CHAR(36)    NOT NULL,
  id_target          CHAR(36)    NOT NULL,
  user_id            CHAR(36)    NOT NULL,
  parent_comment_id  CHAR(36)    NULL,
  body               TEXT        NOT NULL,
  status             VARCHAR(20) NOT NULL DEFAULT 'pending',
  report_count       INT         NOT NULL DEFAULT 0,
  created_at         DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at         DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  deleted_at         DATETIME(3) NULL,

  PRIMARY KEY (id_comment),
  KEY idx_cmr_comments_target (id_target),
  KEY idx_cmr_comments_user (user_id),
  KEY idx_cmr_comments_parent (parent_comment_id),
  KEY idx_cmr_comments_status (status),
  CONSTRAINT fk_cmr_comments_target FOREIGN KEY (id_target) REFERENCES cmr_targets(id_target),
  CONSTRAINT fk_cmr_comments_user   FOREIGN KEY (user_id)   REFERENCES cmr_users(id_user),
  CONSTRAINT fk_cmr_comments_parent FOREIGN KEY (parent_comment_id) REFERENCES cmr_comments(id_comment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 4) cmr_ratings :contentReference[oaicite:4]{index=4} */
CREATE TABLE IF NOT EXISTS cmr_ratings (
  id_rating     CHAR(36)    NOT NULL,
  id_target     CHAR(36)    NOT NULL,
  user_id       CHAR(36)    NOT NULL,
  rating_value  TINYINT     NOT NULL,
  created_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  updated_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
  deleted_at    DATETIME(3) NULL,

  PRIMARY KEY (id_rating),
  KEY idx_cmr_ratings_target (id_target),
  KEY idx_cmr_ratings_user (user_id),
  CONSTRAINT chk_cmr_ratings_value CHECK (rating_value BETWEEN 1 AND 5),
  CONSTRAINT fk_cmr_ratings_target FOREIGN KEY (id_target) REFERENCES cmr_targets(id_target),
  CONSTRAINT fk_cmr_ratings_user   FOREIGN KEY (user_id)   REFERENCES cmr_users(id_user)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 5) cmr_rating_aggregates :contentReference[oaicite:5]{index=5} */
CREATE TABLE IF NOT EXISTS cmr_rating_aggregates (
  id_target     CHAR(36)      NOT NULL,
  rating_count  INT           NOT NULL DEFAULT 0,
  rating_sum    INT           NOT NULL DEFAULT 0,
  rating_avg    DECIMAL(4,2)  NOT NULL DEFAULT 0.00,
  updated_at    DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id_target),
  CONSTRAINT fk_cmr_rating_aggr_target FOREIGN KEY (id_target) REFERENCES cmr_targets(id_target)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 6) cmr_media :contentReference[oaicite:6]{index=6} */
CREATE TABLE IF NOT EXISTS cmr_media (
  id_media     CHAR(36)     NOT NULL,
  id_target    CHAR(36)     NOT NULL,
  user_id      CHAR(36)     NOT NULL,
  media_type   VARCHAR(10)  NULL,      -- image | video
  object_key   TEXT         NULL,
  public_url   TEXT         NULL,
  mime_type    VARCHAR(100) NULL,
  size_bytes   BIGINT       NULL,
  status       VARCHAR(20)  NOT NULL DEFAULT 'pending',
  report_count INT          NOT NULL DEFAULT 0,
  created_at   DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  deleted_at   DATETIME(3)  NULL,

  PRIMARY KEY (id_media),
  KEY idx_cmr_media_target (id_target),
  KEY idx_cmr_media_user (user_id),
  KEY idx_cmr_media_status (status),
  CONSTRAINT fk_cmr_media_target FOREIGN KEY (id_target) REFERENCES cmr_targets(id_target),
  CONSTRAINT fk_cmr_media_user   FOREIGN KEY (user_id)   REFERENCES cmr_users(id_user),
  CONSTRAINT chk_cmr_media_type CHECK (media_type IN ('image','video'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 7) cmr_reports :contentReference[oaicite:7]{index=7} */
CREATE TABLE IF NOT EXISTS cmr_reports (
  id_report         CHAR(36)    NOT NULL,
  reporter_user_id  CHAR(36)    NOT NULL,
  reason            VARCHAR(50) NULL,
  details           TEXT        NULL,
  status            VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending|valid|invalid
  id_comment        CHAR(36)    NULL,
  id_media          CHAR(36)    NULL,
  created_at        DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id_report),
  KEY idx_cmr_reports_reporter (reporter_user_id),
  KEY idx_cmr_reports_status (status),
  KEY idx_cmr_reports_comment (id_comment),
  KEY idx_cmr_reports_media (id_media),
  CONSTRAINT fk_cmr_reports_reporter FOREIGN KEY (reporter_user_id) REFERENCES cmr_users(id_user),
  CONSTRAINT fk_cmr_reports_comment  FOREIGN KEY (id_comment) REFERENCES cmr_comments(id_comment),
  CONSTRAINT fk_cmr_reports_media    FOREIGN KEY (id_media)   REFERENCES cmr_media(id_media),
  CONSTRAINT chk_cmr_reports_target CHECK (
    (id_comment IS NOT NULL AND id_media IS NULL) OR
    (id_comment IS NULL AND id_media IS NOT NULL)
  )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 8) cmr_ai_analysis :contentReference[oaicite:8]{index=8} */
CREATE TABLE IF NOT EXISTS cmr_ai_analysis (
  id_analysis     CHAR(36)     NOT NULL,
  id_comment      CHAR(36)     NULL,
  id_media        CHAR(36)     NULL,
  spam_score      DECIMAL(5,4) NULL,
  toxicity_score  DECIMAL(5,4) NULL,
  model_version   VARCHAR(50)  NULL,
  created_at      DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id_analysis),
  KEY idx_cmr_ai_comment (id_comment),
  KEY idx_cmr_ai_media (id_media),
  CONSTRAINT fk_cmr_ai_comment FOREIGN KEY (id_comment) REFERENCES cmr_comments(id_comment),
  CONSTRAINT fk_cmr_ai_media   FOREIGN KEY (id_media)   REFERENCES cmr_media(id_media),
  CONSTRAINT chk_cmr_ai_target CHECK (
    (id_comment IS NOT NULL AND id_media IS NULL) OR
    (id_comment IS NULL AND id_media IS NOT NULL)
  ),
  CONSTRAINT chk_cmr_ai_scores CHECK (spam_score BETWEEN 0 AND 1 AND toxicity_score BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* 9) cmr_comment_summaries :contentReference[oaicite:9]{index=9} */
CREATE TABLE IF NOT EXISTS cmr_comment_summaries (
  id_summary    CHAR(36)    NOT NULL,
  id_target     CHAR(36)    NOT NULL,
  summary_text  TEXT        NULL,
  created_at    DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  expires_at    DATETIME(3) NULL,

  PRIMARY KEY (id_summary),
  KEY idx_cmr_summaries_target (id_target),
  KEY idx_cmr_summaries_expires (expires_at),
  CONSTRAINT fk_cmr_summaries_target FOREIGN KEY (id_target) REFERENCES cmr_targets(id_target)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
