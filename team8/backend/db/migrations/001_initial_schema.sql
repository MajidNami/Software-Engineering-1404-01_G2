-- Team 8 Database Schema
-- PostgreSQL Schema for Comments, Media & Ratings System

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enums
CREATE TYPE content_status AS ENUM ('PENDING_AI', 'PENDING_ADMIN', 'APPROVED', 'REJECTED');
CREATE TYPE report_status AS ENUM ('OPEN', 'RESOLVED', 'DISMISSED');
CREATE TYPE report_target AS ENUM ('MEDIA', 'POST');

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

-- Places table (basic info for user selection)
CREATE TABLE places (
    place_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    
    -- Location (just for categorization)
    city_id INT NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326), -- For "nearby places" search
    
    category_id INT REFERENCES categories(category_id) ON DELETE SET NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Media table (photos/videos) - just the file, no caption
CREATE TABLE media (
    media_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- User reference (no FK, stored as UUID)
    user_id UUID NOT NULL,
    user_name VARCHAR(150) NOT NULL,
    
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

-- Posts table (formerly comments)
CREATE TABLE posts (
    post_id BIGSERIAL PRIMARY KEY,
    
    -- User reference (denormalized - frozen at creation)
    user_id UUID NOT NULL,
    user_name VARCHAR(150) NOT NULL,
    
    -- Threading (Self-Reference for replies)
    parent_id BIGINT REFERENCES posts(post_id) ON DELETE CASCADE,
    
    -- Target place
    place_id BIGINT NOT NULL REFERENCES places(place_id) ON DELETE CASCADE,
    
    -- Optional media attachment
    media_id UUID REFERENCES media(media_id) ON DELETE SET NULL,
    
    content TEXT NOT NULL,
    is_edited BOOLEAN DEFAULT FALSE,
    status content_status DEFAULT 'PENDING_AI',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ -- Soft Delete
);

-- Ratings table
CREATE TABLE ratings (
    rating_id BIGSERIAL PRIMARY KEY,
    
    -- User reference (no FK, stored as UUID)
    user_id UUID NOT NULL,
    user_name VARCHAR(150) NOT NULL,
    
    place_id BIGINT NOT NULL REFERENCES places(place_id) ON DELETE CASCADE,
    score SMALLINT NOT NULL CHECK (score >= 1 AND score <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_place_rating UNIQUE (user_id, place_id)
);

-- Post Votes table (likes/dislikes)
CREATE TABLE post_votes (
    vote_id BIGSERIAL PRIMARY KEY,
    
    -- User reference
    user_id UUID NOT NULL,
    
    post_id BIGINT NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
    
    -- TRUE = like, FALSE = dislike
    is_like BOOLEAN NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_user_post_vote UNIQUE (user_id, post_id)
);

-- Activity logs table
CREATE TABLE activity_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id UUID,
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
            'USER_LOGIN', 'USER_LOGOUT'
        )
    )
);

-- Notifications table
CREATE TABLE notifications (
    notification_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reports table
CREATE TABLE reports (
    report_id BIGSERIAL PRIMARY KEY,
    
    -- Reporter info (denormalized)
    reporter_id UUID NOT NULL,
    reporter_email VARCHAR(100) NOT NULL,
    
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

-- Sample provinces data (Major Iranian provinces)
INSERT INTO provinces (name, name_en, region) VALUES
    ('تهران', 'Tehran', 'Central'),
    ('اصفهان', 'Isfahan', 'Central'),
-- Sample provinces data (All 31 Iranian provinces)
INSERT INTO provinces (name, name_en) VALUES
    ('تهران', 'Tehran'),
    ('اصفهان', 'Isfahan'),
    ('فارس', 'Fars'),
    ('خراسان رضوی', 'Razavi Khorasan'),
    ('آذربایجان شرقی', 'East Azerbaijan'),
    ('آذربایجان غربی', 'West Azerbaijan'),
    ('خوزستان', 'Khuzestan'),
    ('گیلان', 'Gilan'),
    ('مازندران', 'Mazandaran'),
    ('کرمان', 'Kerman'),
    ('هرمزگان', 'Hormozgan'),
    ('سیستان و بلوچستان', 'Sistan and Baluchestan'),
    ('کردستان', 'Kurdistan'),
    ('همدان', 'Hamadan'),
    ('کرمانشاه', 'Kermanshah'),
    ('لرستان', 'Lorestan'),
    ('مرکزی', 'Markazi'),
    ('بوشهر', 'Bushehr'),
    ('زنجان', 'Zanjan'),
    ('سمنان', 'Semnan'),
    ('یزد', 'Yazd'),
    ('اردبیل', 'Ardabil'),
    ('قم', 'Qom'),
    ('قزوین', 'Qazvin'),
    ('گلستان', 'Golestan'),
    ('خراسان شمالی', 'North Khorasan'),
    ('خراسان جنوبی', 'South Khorasan'),
    ('البرز', 'Alborz'),
    ('ایلام', 'Ilam'),
    ('چهارمحال و بختیاری', 'Chaharmahal and Bakhtiari'),
    ('کهگیلویه و بویراحمد', 'Kohgiluyeh and Boyer-Ahmad')
ON CONFLICT (name) DO NOTHING;

-- Sample cities (Provincial capitals + major cities - 180+ cities)
INSERT INTO cities (province_id, name, name_en) VALUES
    -- Tehran Province (1)
    (1, 'تهران', 'Tehran'),
    (1, 'ری', 'Rey'),
    (1, 'شهریار', 'Shahriar'),
    (1, 'ورامین', 'Varamin'),
    (1, 'اسلامشهر', 'Eslamshahr'),
    (1, 'پاکدشت', 'Pakdasht'),
    (1, 'دماوند', 'Damavand'),
    (1, 'رباط‌کریم', 'Robat Karim'),
    
    -- Isfahan Province (2)
    (2, 'اصفهان', 'Isfahan'),
    (2, 'کاشان', 'Kashan'),
    (2, 'نجف‌آباد', 'Najafabad'),
    (2, 'خمینی‌شهر', 'Khomeinishahr'),
    (2, 'شاهین‌شهر', 'Shahinshahr'),
    (2, 'نطنز', 'Natanz'),
    (2, 'فلاورجان', 'Falavarjan'),
    (2, 'گلپایگان', 'Golpayegan'),
    (2, 'اردستان', 'Ardestan'),
    (2, 'نائین', 'Naein'),
    
    -- Fars Province (3)
    (3, 'شیراز', 'Shiraz'),
    (3, 'مرودشت', 'Marvdasht'),
    (3, 'جهرم', 'Jahrom'),
    (3, 'فسا', 'Fasa'),
    (3, 'لار', 'Lar'),
    (3, 'کازرون', 'Kazerun'),
    (3, 'داراب', 'Darab'),
    (3, 'نی‌ریز', 'Neyriz'),
    (3, 'آباده', 'Abadeh'),
    (3, 'فیروزآباد', 'Firuzabad'),
    
    -- Razavi Khorasan (4)
    (4, 'مشهد', 'Mashhad'),
    (4, 'نیشابور', 'Neyshabur'),
    (4, 'سبزوار', 'Sabzevar'),
    (4, 'تربت حیدریه', 'Torbat-e Heydarieh'),
    (4, 'قوچان', 'Quchan'),
    (4, 'گناباد', 'Gonabad'),
    (4, 'کاشمر', 'Kashmar'),
    (4, 'تربت جام', 'Torbat-e Jam'),
    (4, 'چناران', 'Chenaran'),
    
    -- East Azerbaijan (5)
    (5, 'تبریز', 'Tabriz'),
    (5, 'مرند', 'Marand'),
    (5, 'میانه', 'Mianeh'),
    (5, 'مراغه', 'Maragheh'),
    (5, 'اهر', 'Ahar'),
    (5, 'سراب', 'Sarab'),
    (5, 'شبستر', 'Shabestar'),
    (5, 'بناب', 'Bonab'),
    (5, 'ملکان', 'Malekan'),
    (5, 'عجب‌شیر', 'Ajabshir'),
    
    -- West Azerbaijan (6)
    (6, 'ارومیه', 'Urmia'),
    (6, 'خوی', 'Khoy'),
    (6, 'مهاباد', 'Mahabad'),
    (6, 'بوکان', 'Bukan'),
    (6, 'میاندوآب', 'Miandoab'),
    (6, 'سلماس', 'Salmas'),
    (6, 'نقده', 'Naqadeh'),
    (6, 'پیرانشهر', 'Piranshahr'),
    (6, 'ماکو', 'Maku'),
    
    -- Khuzestan (7)
    (7, 'اهواز', 'Ahvaz'),
    (7, 'آبادان', 'Abadan'),
    (7, 'خرمشهر', 'Khorramshahr'),
    (7, 'دزفول', 'Dezful'),
    (7, 'اندیمشک', 'Andimeshk'),
    (7, 'شوشتر', 'Shushtar'),
    (7, 'بهبهان', 'Behbahan'),
    (7, 'ماهشهر', 'Mahshahr'),
    (7, 'ایذه', 'Izeh'),
    (7, 'شوش', 'Shush'),
    (7, 'رامهرمز', 'Ramhormoz'),
    (7, 'هندیجان', 'Hendijan'),
    
    -- Gilan (8)
    (8, 'رشت', 'Rasht'),
    (8, 'بندر انزلی', 'Bandar Anzali'),
    (8, 'لاهیجان', 'Lahijan'),
    (8, 'لنگرود', 'Langarud'),
    (8, 'رودسر', 'Rudsar'),
    (8, 'تالش', 'Talesh'),
    (8, 'آستارا', 'Astara'),
    (8, 'صومعه‌سرا', 'Sowme'eh Sara'),
    (8, 'فومن', 'Fuman'),
    (8, 'ماسال', 'Masal'),
    
    -- Mazandaran (9)
    (9, 'ساری', 'Sari'),
    (9, 'بابل', 'Babol'),
    (9, 'آمل', 'Amol'),
    (9, 'قائمشهر', 'Qaem Shahr'),
    (9, 'نوشهر', 'Nowshahr'),
    (9, 'چالوس', 'Chalus'),
    (9, 'بابلسر', 'Babolsar'),
    (9, 'تنکابن', 'Tonekabon'),
    (9, 'رامسر', 'Ramsar'),
    (9, 'نکا', 'Neka'),
    (9, 'محمودآباد', 'Mahmudabad'),
    (9, 'بهشهر', 'Behshahr'),
    
    -- Kerman (10)
    (10, 'کرمان', 'Kerman'),
    (10, 'رفسنجان', 'Rafsanjan'),
    (10, 'سیرجان', 'Sirjan'),
    (10, 'بم', 'Bam'),
    (10, 'جیرفت', 'Jiroft'),
    (10, 'کهنوج', 'Kahnooj'),
    (10, 'زرند', 'Zarand'),
    (10, 'شهربابک', 'Shahrbabak'),
    (10, 'بافت', 'Baft'),
    (10, 'انار', 'Anar'),
    
    -- Hormozgan (11)
    (11, 'بندرعباس', 'Bandar Abbas'),
    (11, 'قشم', 'Qeshm'),
    (11, 'میناب', 'Minab'),
    (11, 'بندر لنگه', 'Bandar Lengeh'),
    (11, 'کیش', 'Kish'),
    (11, 'جاسک', 'Jask'),
    (11, 'بندر خمیر', 'Bandar Khamir'),
    (11, 'رودان', 'Rudan'),
    
    -- Sistan and Baluchestan (12)
    (12, 'زاهدان', 'Zahedan'),
    (12, 'زابل', 'Zabol'),
    (12, 'چابهار', 'Chabahar'),
    (12, 'ایرانشهر', 'Iranshahr'),
    (12, 'خاش', 'Khash'),
    (12, 'سراوان', 'Saravan'),
    (12, 'نیکشهر', 'Nikshahr'),
    
    -- Kurdistan (13)
    (13, 'سنندج', 'Sanandaj'),
    (13, 'سقز', 'Saqqez'),
    (13, 'مریوان', 'Marivan'),
    (13, 'بانه', 'Baneh'),
    (13, 'قروه', 'Qorveh'),
    (13, 'بیجار', 'Bijar'),
    (13, 'کامیاران', 'Kamyaran'),
    
    -- Hamadan (14)
    (14, 'همدان', 'Hamadan'),
    (14, 'ملایر', 'Malayer'),
    (14, 'نهاوند', 'Nahavand'),
    (14, 'تویسرکان', 'Tuyserkan'),
    (14, 'اسدآباد', 'Asadabad'),
    (14, 'بهار', 'Bahar'),
    (14, 'رزن', 'Razan'),
    
    -- Kermanshah (15)
    (15, 'کرمانشاه', 'Kermanshah'),
    (15, 'اسلام‌آباد غرب', 'Eslamabad-e Gharb'),
    (15, 'پاوه', 'Paveh'),
    (15, 'کنگاور', 'Kangavar'),
    (15, 'هرسین', 'Harsin'),
    (15, 'سنقر', 'Sonqor'),
    (15, 'جوانرود', 'Javanrud'),
    (15, 'قصر شیرین', 'Qasr-e Shirin'),
    
    -- Lorestan (16)
    (16, 'خرم‌آباد', 'Khorramabad'),
    (16, 'بروجرد', 'Borujerd'),
    (16, 'دورود', 'Dorud'),
    (16, 'الیگودرز', 'Aligudarz'),
    (16, 'ازنا', 'Azna'),
    (16, 'کوهدشت', 'Kuhdasht'),
    (16, 'نورآباد', 'Nurabad'),
    
    -- Markazi (17)
    (17, 'اراک', 'Arak'),
    (17, 'ساوه', 'Saveh'),
    (17, 'خمین', 'Khomein'),
    (17, 'محلات', 'Mahallat'),
    (17, 'دلیجان', 'Delijan'),
    (17, 'تفرش', 'Tafresh'),
    (17, 'شازند', 'Shazand'),
    
    -- Bushehr (18)
    (18, 'بوشهر', 'Bushehr'),
    (18, 'برازجان', 'Borazjan'),
    (18, 'کنگان', 'Kangan'),
    (18, 'گناوه', 'Genaveh'),
    (18, 'دیر', 'Deyr'),
    (18, 'دیلم', 'Deylam'),
    
    -- Zanjan (19)
    (19, 'زنجان', 'Zanjan'),
    (19, 'ابهر', 'Abhar'),
    (19, 'خدابنده', 'Khodabandeh'),
    (19, 'خرمدره', 'Khorramdarreh'),
    (19, 'ماهنشان', 'Mahneshan'),
    
    -- Semnan (20)
    (20, 'سمنان', 'Semnan'),
    (20, 'شاهرود', 'Shahroud'),
    (20, 'دامغان', 'Damghan'),
    (20, 'گرمسار', 'Garmsar'),
    (20, 'مهدی‌شهر', 'Mahdishahr'),
    
    -- Yazd (21)
    (21, 'یزد', 'Yazd'),
    (21, 'اردکان', 'Ardakan'),
    (21, 'میبد', 'Meybod'),
    (21, 'مهریز', 'Mehriz'),
    (21, 'تفت', 'Taft'),
    (21, 'ابرکوه', 'Abarkuh'),
    (21, 'بافق', 'Bafq'),
    
    -- Ardabil (22)
    (22, 'اردبیل', 'Ardabil'),
    (22, 'مشگین‌شهر', 'Meshgin Shahr'),
    (22, 'خلخال', 'Khalkhal'),
    (22, 'پارس‌آباد', 'Parsabad'),
    (22, 'گرمی', 'Germi'),
    (22, 'نمین', 'Namin'),
    (22, 'نیر', 'Nir'),
    
    -- Qom (23)
    (23, 'قم', 'Qom'),
    
    -- Qazvin (24)
    (24, 'قزوین', 'Qazvin'),
    (24, 'تاکستان', 'Takestan'),
    (24, 'آبیک', 'Abyek'),
    (24, 'بوئین‌زهرا', 'Buin Zahra'),
    (24, 'آوج', 'Avaj'),
    
    -- Golestan (25)
    (25, 'گرگان', 'Gorgan'),
    (25, 'گنبد کاووس', 'Gonbad-e Kavus'),
    (25, 'علی‌آباد', 'Aliabad'),
    (25, 'بندر ترکمن', 'Bandar Torkaman'),
    (25, 'آق‌قلا', 'Aqqala'),
    (25, 'کردکوی', 'Kordkuy'),
    (25, 'مینودشت', 'Minudasht'),
    (25, 'آزادشهر', 'Azadshahr'),
    
    -- North Khorasan (26)
    (26, 'بجنورد', 'Bojnord'),
    (26, 'شیروان', 'Shirvan'),
    (26, 'اسفراین', 'Esfarayen'),
    (26, 'جاجرم', 'Jajarm'),
    (26, 'راز و جرگلان', 'Raz va Jargalan'),
    
    -- South Khorasan (27)
    (27, 'بیرجند', 'Birjand'),
    (27, 'قائن', 'Qaen'),
    (27, 'فردوس', 'Ferdows'),
    (27, 'طبس', 'Tabas'),
    (27, 'نهبندان', 'Nehbandan'),
    (27, 'بشرویه', 'Boshruyeh'),
    
    -- Alborz (28)
    (28, 'کرج', 'Karaj'),
    (28, 'ساوجبلاغ', 'Savojbolagh'),
    (28, 'نظرآباد', 'Nazarabad'),
    (28, 'طالقان', 'Taleghan'),
    (28, 'اشتهارد', 'Eshtehard'),
    (28, 'فردیس', 'Fardis'),
    (28, 'هشتگرد', 'Hashtgerd'),
    
    -- Ilam (29)
    (29, 'ایلام', 'Ilam'),
    (29, 'ایوان', 'Ivan'),
    (29, 'دهلران', 'Dehloran'),
    (29, 'آبدانان', 'Abdanan'),
    (29, 'مهران', 'Mehran'),
    (29, 'دره‌شهر', 'Darreh Shahr'),
    
    -- Chaharmahal and Bakhtiari (30)
    (30, 'شهرکرد', 'Shahrekord'),
    (30, 'بروجن', 'Borujen'),
    (30, 'فارسان', 'Farsan'),
    (30, 'لردگان', 'Lordegan'),
    (30, 'اردل', 'Ardal'),
    
    -- Kohgiluyeh and Boyer-Ahmad (31)
    (31, 'یاسوج', 'Yasuj'),
    (31, 'دوگنبدان', 'Dogonbadan'),
    (31, 'دهدشت', 'Dehdasht'),
    (31, 'گچساران', 'Gachsaran'),
    (31, 'دنا', 'Dena')
ON CONFLICT (province_id, name) DO NOTHING;

-- Sample categories data
INSERT INTO categories (name, name_en) VALUES
    ('تاریخی', 'Historical'),
    ('طبیعی', 'Nature'),
    ('مذهبی', 'Religious'),
    ('فرهنگی', 'Cultural'),
    ('رستوران', 'Restaurant'),
    ('کافه', 'Cafe'),
    ('هتل', 'Hotel'),
    ('پارک', 'Park'),
    ('موزه', 'Museum'),
    ('بازار', 'Bazaar')
ON CONFLICT (name) DO NOTHING;