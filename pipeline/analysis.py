import json
import re
from typing import Any

import requests


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)

DEFAULT_MODEL = "llama3.2"


# ============================================================
# ANALYSIS PROMPT
# ============================================================

def build_analysis_prompt(
    transcript
):
    """
    Build the structured qualitative-analysis prompt.
    """

    return f"""
You are an expert qualitative research analyst.

Analyze the following discussion transcript carefully.

Your task is to identify meaningful discussion patterns,
topics, participant contributions, decisions, and follow-up
actions.

Return ONLY valid JSON.

Do not use Markdown.
Do not add explanations before or after the JSON.

Use exactly this structure:

{{
    "executive_summary": "A concise summary of the discussion.",

    "overall_sentiment": "Positive, Neutral, Negative, or Mixed",

    "sentiment_score": 0.0,

    "themes": [
        "Theme 1",
        "Theme 2"
    ],

    "key_points": [
        "Important discussion point 1",
        "Important discussion point 2"
    ],

    "participant_insights": [
        {{
            "speaker": "SPEAKER_00",
            "insight": "What this participant contributed."
        }}
    ],

    "decisions": [
        {{
            "decision": "Decision that was made.",
            "speaker": "SPEAKER_00"
        }}
    ],

    "action_items": [
        {{
            "task": "Action that needs to be completed.",
            "speaker": "SPEAKER_00",
            "priority": "High, Medium, or Low"
        }}
    ],

    "unresolved_issues": [
        "Issue that remains unresolved."
    ]
}}

Rules:

1. Do not invent information.
2. Only use information present in the transcript.
3. If no decisions were made, return an empty decisions list.
4. If no action items were identified, return an empty action_items list.
5. If no unresolved issues were identified, return an empty unresolved_issues list.
6. sentiment_score must be between -1.0 and 1.0.
7. Keep the executive summary concise.
8. Themes should represent meaningful recurring topics.
9. Participant insights must be based on actual statements.
10. Return valid JSON only.

Transcript:

{transcript}
"""


# ============================================================
# OLLAMA CLIENT
# ============================================================

class OllamaAnalyzer:
    """
    Client for local Ollama LLM analysis.
    """

    def __init__(
        self,
        model_name=DEFAULT_MODEL,
        ollama_url=OLLAMA_URL,
        timeout=300
    ):

        self.model_name = model_name

        self.ollama_url = ollama_url

        self.timeout = timeout

    # ========================================================
    # CHECK OLLAMA
    # ========================================================

    def check_connection(self):
        """
        Check whether Ollama is running.
        """

        try:

            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=10
            )

            return response.status_code == 200

        except requests.RequestException:

            return False

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        prompt
    ):
        """
        Send a prompt to Ollama.
        """

        try:

            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=self.timeout
            )

        except requests.RequestException as e:

            raise RuntimeError(
                "Could not connect to Ollama. "
                "Make sure Ollama is running."
            ) from e

        if response.status_code != 200:

            raise RuntimeError(
                f"Ollama returned HTTP "
                f"{response.status_code}: "
                f"{response.text}"
            )

        try:

            payload = response.json()

        except ValueError as e:

            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from e

        if "response" not in payload:

            raise RuntimeError(
                "Ollama response does not contain "
                "the expected 'response' field."
            )

        return payload["response"]

    # ========================================================
    # PARSE JSON
    # ========================================================

    def parse_analysis(
        self,
        response_text
    ):
        """
        Parse the JSON returned by the LLM.
        """

        text = response_text.strip()

        # ----------------------------------------------------
        # Remove accidental Markdown code fences
        # ----------------------------------------------------

        text = re.sub(
            r"^```json\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"^```\s*",
            "",
            text
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        text = text.strip()

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:

            analysis = json.loads(
                text
            )

        except json.JSONDecodeError:

            # Attempt to find JSON object inside response

            start = text.find("{")

            end = text.rfind("}")

            if start == -1 or end == -1:

                raise ValueError(
                    "LLM did not return valid JSON."
                )

            try:

                analysis = json.loads(
                    text[start:end + 1]
                )

            except json.JSONDecodeError as e:

                raise ValueError(
                    "Could not parse LLM JSON response."
                ) from e

        return self.validate_analysis(
            analysis
        )

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate_analysis(
        self,
        analysis
    ):
        """
        Ensure the LLM response has the required structure.
        """

        if not isinstance(
            analysis,
            dict
        ):

            raise ValueError(
                "Analysis must be a JSON object."
            )

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------

        defaults = {

            "executive_summary": "",

            "overall_sentiment": "Neutral",

            "sentiment_score": 0.0,

            "themes": [],

            "key_points": [],

            "participant_insights": [],

            "decisions": [],

            "action_items": [],

            "unresolved_issues": []
        }

        for key, default in defaults.items():

            if key not in analysis:

                analysis[key] = default

        # ----------------------------------------------------
        # Ensure lists
        # ----------------------------------------------------

        list_fields = [

            "themes",
            "key_points",
            "participant_insights",
            "decisions",
            "action_items",
            "unresolved_issues"
        ]

        for field in list_fields:

            if not isinstance(
                analysis[field],
                list
            ):

                analysis[field] = []

        # ----------------------------------------------------
        # Sentiment score
        # ----------------------------------------------------

        try:

            sentiment_score = float(
                analysis["sentiment_score"]
            )

        except (
            TypeError,
            ValueError
        ):

            sentiment_score = 0.0

        sentiment_score = max(
            -1.0,
            min(
                1.0,
                sentiment_score
            )
        )

        analysis[
            "sentiment_score"
        ] = sentiment_score

        # ----------------------------------------------------
        # Sentiment
        # ----------------------------------------------------

        sentiment = str(
            analysis[
                "overall_sentiment"
            ]
        ).strip()

        allowed_sentiments = {
            "Positive",
            "Neutral",
            "Negative",
            "Mixed"
        }

        if sentiment not in allowed_sentiments:

            sentiment = "Neutral"

        analysis[
            "overall_sentiment"
        ] = sentiment

        # ----------------------------------------------------
        # Summary
        # ----------------------------------------------------

        analysis[
            "executive_summary"
        ] = str(
            analysis[
                "executive_summary"
            ]
        ).strip()

        return analysis

    # ========================================================
    # COMPLETE ANALYSIS
    # ========================================================

    def analyze(
        self,
        transcript
    ):
        """
        Analyze a transcript and return structured data.
        """

        if not transcript or not transcript.strip():

            raise ValueError(
                "Transcript is empty."
            )

        prompt = build_analysis_prompt(
            transcript
        )

        response = self.generate(
            prompt
        )

        analysis = self.parse_analysis(
            response
        )

        return analysis


# ============================================================
# TRANSCRIPT FORMATTING
# ============================================================

def format_segments_for_llm(
    segments
):
    """
    Convert structured transcript segments into readable
    speaker-labelled text for the LLM.

    Example:

    SPEAKER_00:
    Hello everyone.

    SPEAKER_01:
    Good morning.
    """

    lines = []

    for segment in segments:

        speaker = segment.get(
            "speaker",
            "UNKNOWN"
        )

        text = segment.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        lines.append(
            f"{speaker}:"
        )

        lines.append(
            text
        )

        lines.append("")

    return "\n".join(
        lines
    )


# ============================================================
# SAVE STRUCTURED ANALYSIS
# ============================================================

def save_analysis_json(
    analysis,
    output_file
):
    """
    Save structured analysis as JSON.
    """

    output_path = (
        output_file
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            analysis,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# SAVE HUMAN-READABLE REPORT
# ============================================================

def save_analysis_report(
    analysis,
    output_file
):
    """
    Save a readable text report.
    """

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "DISCUSSION ANALYSIS REPORT\n"
        )

        file.write(
            "=" * 60
            + "\n\n"
        )

        file.write(
            "EXECUTIVE SUMMARY\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            analysis[
                "executive_summary"
            ]
            + "\n\n"
        )

        file.write(
            "OVERALL SENTIMENT\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        file.write(
            f"{analysis['overall_sentiment']}\n"
        )

        file.write(
            f"Score: "
            f"{analysis['sentiment_score']}\n\n"
        )

        file.write(
            "MAIN THEMES\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for theme in analysis["themes"]:

            file.write(
                f"• {theme}\n"
            )

        file.write("\n")

        file.write(
            "KEY DISCUSSION POINTS\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for point in analysis["key_points"]:

            file.write(
                f"• {point}\n"
            )

        file.write("\n")

        file.write(
            "PARTICIPANT INSIGHTS\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for item in analysis[
            "participant_insights"
        ]:

            if isinstance(
                item,
                dict
            ):

                speaker = item.get(
                    "speaker",
                    "UNKNOWN"
                )

                insight = item.get(
                    "insight",
                    ""
                )

                file.write(
                    f"• {speaker}: "
                    f"{insight}\n"
                )

        file.write("\n")

        file.write(
            "DECISIONS\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for item in analysis[
            "decisions"
        ]:

            if isinstance(
                item,
                dict
            ):

                decision = item.get(
                    "decision",
                    ""
                )

                speaker = item.get(
                    "speaker",
                    "UNKNOWN"
                )

                file.write(
                    f"• {decision} "
                    f"({speaker})\n"
                )

        file.write("\n")

        file.write(
            "ACTION ITEMS\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for item in analysis[
            "action_items"
        ]:

            if isinstance(
                item,
                dict
            ):

                task = item.get(
                    "task",
                    ""
                )

                speaker = item.get(
                    "speaker",
                    "UNKNOWN"
                )

                priority = item.get(
                    "priority",
                    "Medium"
                )

                file.write(
                    f"• [{priority}] "
                    f"{task} "
                    f"({speaker})\n"
                )

        file.write("\n")

        file.write(
            "UNRESOLVED ISSUES\n"
        )

        file.write(
            "-" * 60
            + "\n"
        )

        for issue in analysis[
            "unresolved_issues"
        ]:

            file.write(
                f"• {issue}\n"
            )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def analyze_transcript(
    transcript,
    model_name=DEFAULT_MODEL,
    json_output="analysis/analysis.json",
    report_output="analysis/llm_report.txt"
):
    """
    Complete LLM analysis workflow.
    """

    analyzer = OllamaAnalyzer(
        model_name=model_name
    )

    analysis = analyzer.analyze(
        transcript
    )

    Path = __import__(
        "pathlib"
    ).Path

    Path(
        json_output
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        report_output
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    save_analysis_json(
        analysis,
        json_output
    )

    save_analysis_report(
        analysis,
        report_output
    )

    return analysis