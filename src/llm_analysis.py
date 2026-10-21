import requests

import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database.database_manager import (
    save_transcript,
    save_analysis
)

# Read merged transcript

with open(
    "analysis/merged_transcript.txt",
    "r",
    encoding="utf-8"
) as file:

    transcript_text = file.read()

# Save transcript to PostgreSQL

filename = "Uploaded Audio"

transcript_id = save_transcript(
    filename,
    transcript_text
)
print(
    f"Transcript saved with ID: {transcript_id}"
)

# Prompt

prompt = f"""
You are a qualitative research analyst.

Analyze the following discussion transcript.

Provide:

1. Main Themes
2. Overall Sentiment
3. Key Discussion Points
4. Participant Insights
5. Executive Summary

Transcript:

{transcript_text}
"""

# Call Ollama

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }
)

analysis = response.json()["response"]

print("\n===== ANALYSIS =====\n")
print(analysis)

# Save report file

with open(
    "analysis/llm_report.txt",
    "w",
    encoding="utf-8"
) as file:

    file.write(analysis)

# Save analysis to PostgreSQL

save_analysis(
    transcript_id,
    "Council Meeting, Grant Applications",
    "Neutral-Positive",
    analysis[:1000],
    analysis
)

print("\nLLM report saved!")
print("Analysis stored in PostgreSQL!")