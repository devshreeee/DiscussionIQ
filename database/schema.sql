-- ============================================================
-- DISCUSSIONIQ DATABASE SCHEMA
-- ============================================================
--
-- This schema extends the existing Discussion Analyzer
-- database into a complete discussion intelligence platform.
--
-- IMPORTANT:
-- Do NOT run this file blindly against the existing database.
-- We will migrate the existing tables safely after reviewing
-- their current structure.
-- ============================================================


-- ============================================================
-- MEETINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS meetings (

    id SERIAL PRIMARY KEY,

    filename VARCHAR(255) NOT NULL,

    duration_seconds NUMERIC(12, 3),

    status VARCHAR(30) DEFAULT 'completed',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- TRANSCRIPTS
-- ============================================================

CREATE TABLE IF NOT EXISTS transcripts (

    id SERIAL PRIMARY KEY,

    meeting_id INTEGER
        REFERENCES meetings(id)
        ON DELETE CASCADE,

    filename VARCHAR(255) NOT NULL,

    transcript_text TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- SPEAKER SEGMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS speaker_segments (

    id SERIAL PRIMARY KEY,

    transcript_id INTEGER NOT NULL
        REFERENCES transcripts(id)
        ON DELETE CASCADE,

    speaker VARCHAR(100) NOT NULL,

    start_time NUMERIC(12, 3) NOT NULL,

    end_time NUMERIC(12, 3) NOT NULL,

    text TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- ANALYSES
-- ============================================================

CREATE TABLE IF NOT EXISTS analyses (

    id SERIAL PRIMARY KEY,

    transcript_id INTEGER NOT NULL
        REFERENCES transcripts(id)
        ON DELETE CASCADE,

    themes TEXT,

    sentiment VARCHAR(50),

    sentiment_score NUMERIC(6, 4),

    summary TEXT,

    full_analysis TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- THEMES
-- ============================================================

CREATE TABLE IF NOT EXISTS themes (

    id SERIAL PRIMARY KEY,

    analysis_id INTEGER NOT NULL
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    theme TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- KEY DISCUSSION POINTS
-- ============================================================

CREATE TABLE IF NOT EXISTS key_points (

    id SERIAL PRIMARY KEY,

    analysis_id INTEGER NOT NULL
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    point TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- DECISIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS decisions (

    id SERIAL PRIMARY KEY,

    analysis_id INTEGER NOT NULL
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    decision TEXT NOT NULL,

    speaker VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- ACTION ITEMS
-- ============================================================

CREATE TABLE IF NOT EXISTS action_items (

    id SERIAL PRIMARY KEY,

    analysis_id INTEGER NOT NULL
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    task TEXT NOT NULL,

    speaker VARCHAR(100),

    priority VARCHAR(30),

    status VARCHAR(30) DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- UNRESOLVED ISSUES
-- ============================================================

CREATE TABLE IF NOT EXISTS unresolved_issues (

    id SERIAL PRIMARY KEY,

    analysis_id INTEGER NOT NULL
        REFERENCES analyses(id)
        ON DELETE CASCADE,

    issue TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- SPEAKER ANALYTICS
-- ============================================================

CREATE TABLE IF NOT EXISTS speaker_analytics (

    id SERIAL PRIMARY KEY,

    transcript_id INTEGER NOT NULL
        REFERENCES transcripts(id)
        ON DELETE CASCADE,

    speaker VARCHAR(100) NOT NULL,

    speaking_time_seconds NUMERIC(12, 3),

    segment_count INTEGER,

    word_count INTEGER,

    participation_percentage NUMERIC(6, 3),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- MODEL EVALUATION
-- ============================================================

CREATE TABLE IF NOT EXISTS model_evaluations (

    id SERIAL PRIMARY KEY,

    transcript_id INTEGER
        REFERENCES transcripts(id)
        ON DELETE CASCADE,

    wer NUMERIC(8, 6),

    accuracy_percentage NUMERIC(8, 4),

    evaluation_type VARCHAR(100),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_transcripts_created_at
ON transcripts(created_at);


CREATE INDEX IF NOT EXISTS idx_transcripts_meeting_id
ON transcripts(meeting_id);


CREATE INDEX IF NOT EXISTS idx_speaker_segments_transcript
ON speaker_segments(transcript_id);


CREATE INDEX IF NOT EXISTS idx_speaker_segments_speaker
ON speaker_segments(speaker);


CREATE INDEX IF NOT EXISTS idx_analyses_transcript
ON analyses(transcript_id);


CREATE INDEX IF NOT EXISTS idx_themes_analysis
ON themes(analysis_id);


CREATE INDEX IF NOT EXISTS idx_action_items_analysis
ON action_items(analysis_id);


CREATE INDEX IF NOT EXISTS idx_decisions_analysis
ON decisions(analysis_id);


CREATE INDEX IF NOT EXISTS idx_evaluations_transcript
ON model_evaluations(transcript_id);