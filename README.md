# Discussion Analyzer using AI

## Project Overview

Discussion Analyzer is an AI-powered system that automatically transcribes, analyzes, and stores meeting discussions. The system processes audio recordings, identifies speakers, generates transcripts, performs AI-based analysis, and stores results in a PostgreSQL database.

The project is designed to help organizations, researchers, and decision-makers quickly understand the key topics, sentiments, and outcomes of meetings without manually reviewing lengthy recordings.

---

## Objectives

* Convert meeting audio into text using AI.
* Identify different speakers in the discussion.
* Generate structured transcripts with timestamps.
* Analyze discussions using a Large Language Model (LLM).
* Extract themes, sentiment, key discussion points, and summaries.
* Store transcripts and analyses in PostgreSQL for future retrieval.

---

## Features

### Speech-to-Text

Uses OpenAI Whisper to convert audio recordings into text.

### Speaker Diarization

Uses PyAnnote Audio to identify and separate speakers.

### Transcript Processing

Creates structured transcripts with timestamps.

### AI-Based Analysis

Uses Llama 3.2 through Ollama to generate:

* Main Themes
* Overall Sentiment
* Key Discussion Points
* Participant Insights
* Executive Summary

### Database Storage

Stores:

* Meeting transcripts
* AI-generated analysis
* Metadata and timestamps

---

## Technology Stack

### Programming Language

* Python 3.12

### AI Models

* OpenAI Whisper
* PyAnnote Audio
* Llama 3.2 (Ollama)

### Database

* PostgreSQL

### Libraries

* openai-whisper
* pyannote.audio
* psycopg2-binary
* pandas
* requests
* torch

### Development Tools

* Visual Studio Code
* Git
* GitHub

---

## System Architecture

Audio File
↓
Whisper Speech-to-Text
↓
Speaker Diarization
↓
Transcript Processing
↓
Llama 3.2 Analysis
↓
PostgreSQL Database
↓
Reports and Insights

---

## Database Schema

### transcripts

| Column          | Type         |
| --------------- | ------------ |
| id              | SERIAL       |
| filename        | VARCHAR(255) |
| transcript_text | TEXT         |
| created_at      | TIMESTAMP    |

### analyses

| Column        | Type      |
| ------------- | --------- |
| id            | SERIAL    |
| transcript_id | INTEGER   |
| themes        | TEXT      |
| sentiment     | TEXT      |
| summary       | TEXT      |
| full_analysis | TEXT      |
| created_at    | TIMESTAMP |

---

## Project Structure

DiscussionAnalyzer/

├── analysis/

├── data/

│ └── audio_files/

├── database/

│ ├── db_connection.py

│ └── database_manager.py

├── src/

│ ├── whisper_transcription.py

│ ├── diarization.py

│ ├── transcript_merger.py

│ └── llm_analysis.py

├── transcripts/

├── requirements.txt

└── README.md

---

## How to Run

### Activate Virtual Environment

```bash
source venv/bin/activate
```

### Run Transcription

```bash
python src/whisper_transcription.py
```

### Run Speaker Diarization

```bash
python src/diarization.py
```

### Run AI Analysis

```bash
python -m src.llm_analysis
```

---

## Sample Output

The system generates:

* Full transcript
* Speaker-separated transcript
* Discussion themes
* Sentiment analysis
* Executive summary
* Database records

---

## Future Enhancements

* Streamlit Dashboard
* Real-time Meeting Analysis
* Speaker Statistics
* Topic Modeling
* Meeting Search Engine
* Automated Report Generation

---

## Conclusion

The Discussion Analyzer demonstrates the integration of Speech Recognition, Speaker Diarization, Natural Language Processing, Large Language Models, and Database Management into a single intelligent system capable of transforming raw meeting recordings into actionable insights.
