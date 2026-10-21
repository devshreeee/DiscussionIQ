-- database/schema.sql

CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    duration FLOAT,
    processing_status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, completed, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS speakers (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    speaker_label VARCHAR(50) NOT NULL, -- e.g., 'SPEAKER_00'
    assigned_name VARCHAR(255),         -- Real human identity if assigned later
    UNIQUE(meeting_id, speaker_label)
);

CREATE TABLE IF NOT EXISTS transcript_segments (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    speaker_id INTEGER REFERENCES speakers(id) ON DELETE SET NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    transcript_text TEXT NOT NULL
);

-- AI Generated Classifications using the verified taxonomy
CREATE TABLE IF NOT EXISTS segment_classifications (
    id SERIAL PRIMARY KEY,
    segment_id INTEGER REFERENCES transcript_segments(id) ON DELETE CASCADE,
    taxonomy_version VARCHAR(50) DEFAULT 'v1.0',
    category_family VARCHAR(100),       -- e.g., 'Strategic & Analytical'
    category_name VARCHAR(100),         -- e.g., 'Negotiation'
    sentiment VARCHAR(20),              -- Positive, Neutral, Negative
    confidence_score FLOAT,
    evidence_span TEXT,                 -- Exact transcript quote supporting the claim
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Human Annotations for Cohen's Kappa Evaluation
CREATE TABLE IF NOT EXISTS human_annotations (
    id SERIAL PRIMARY KEY,
    segment_id INTEGER REFERENCES transcript_segments(id) ON DELETE CASCADE,
    annotator_id VARCHAR(100) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
