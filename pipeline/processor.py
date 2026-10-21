"""
DiscussionIQ - Discussion Processing Pipeline

Complete audio-to-insights processing pipeline.

Pipeline:

    Audio
      ↓
    Audio Duration
      ↓
    Meeting Record
      ↓
    WAV Conversion
      ↓
    Whisper Transcription
      ↓
    Speaker Diarization
      ↓
    Transcript Merge
      ↓
    PostgreSQL Transcript
      ↓
    Speaker Analytics
      ↓
    Llama AI Analysis
      ↓
    PostgreSQL Analysis
      ↓
    Completed

If any stage fails:

    processing → failed
"""

from pathlib import Path
from typing import Callable, Optional


# ============================================================
# AUDIO
# ============================================================

from pipeline.audio import (
    convert_to_wav,
    get_audio_duration,
)


# ============================================================
# TRANSCRIPTION
# ============================================================

from pipeline.transcription import (
    WhisperTranscriber,
)


# ============================================================
# DIARIZATION
# ============================================================

from pipeline.diarization import (
    SpeakerDiarizer,
)


# ============================================================
# TRANSCRIPT MERGING
# ============================================================

from pipeline.transcript_merger import (
    merge_transcript,
    save_merged_json,
    save_merged_text,
)


# ============================================================
# SPEAKER ANALYTICS
# ============================================================

from pipeline.speaker_analytics import (
    calculate_speaker_analytics,
)


# ============================================================
# AI ANALYSIS
# ============================================================

from pipeline.analysis import (
    OllamaAnalyzer,
    format_segments_for_llm,
    save_analysis_json,
    save_analysis_report,
)


# ============================================================
# DATABASE
# ============================================================

from database.database_manager import (
    create_meeting,
    update_meeting_status,
    save_transcript,
    save_speaker_segments,
    save_analysis,
    save_themes,
    save_key_points,
    save_decisions,
    save_action_items,
    save_unresolved_issues,
    save_speaker_analytics,
)


# ============================================================
# DIRECTORIES
# ============================================================

DATA_DIR = Path("data")

AUDIO_DIR = DATA_DIR / "audio_files"

TRANSCRIPT_DIR = Path("transcripts")

ANALYSIS_DIR = Path("analysis")


# ============================================================
# PROCESSING RESULT
# ============================================================

class ProcessingResult:
    """
    Stores the result of a completed discussion analysis.
    """

    def __init__(
        self,
        meeting_id,
        transcript_id,
        analysis_id,
        filename,
        duration_seconds,
        segments,
        speaker_analytics,
        analysis,
    ):

        self.meeting_id = meeting_id

        self.transcript_id = transcript_id

        self.analysis_id = analysis_id

        self.filename = filename

        self.duration_seconds = duration_seconds

        self.segments = segments

        self.speaker_analytics = speaker_analytics

        self.analysis = analysis

    def to_dict(self):

        return {
            "meeting_id": self.meeting_id,
            "transcript_id": self.transcript_id,
            "analysis_id": self.analysis_id,
            "filename": self.filename,
            "duration_seconds": self.duration_seconds,
            "segments": self.segments,
            "speaker_analytics": self.speaker_analytics,
            "analysis": self.analysis,
        }


# ============================================================
# DISCUSSION PROCESSOR
# ============================================================

class DiscussionProcessor:
    """
    Main backend pipeline for DiscussionIQ.
    """

    def __init__(
        self,
        whisper_model="base",
        llama_model="llama3.2",
        progress_callback: Optional[
            Callable[[str], None]
        ] = None,
    ):

        self.whisper_model = whisper_model

        self.llama_model = llama_model

        self.progress_callback = progress_callback

        # ----------------------------------------------------
        # Model initialization
        # ----------------------------------------------------

        self._progress(
            "Initializing Whisper..."
        )

        self.transcriber = WhisperTranscriber(
            model_name=whisper_model
        )

        self._progress(
            "Initializing speaker diarization..."
        )

        self.diarizer = SpeakerDiarizer()

        self._progress(
            "Initializing Llama analyzer..."
        )

        self.analyzer = OllamaAnalyzer(
            model_name=llama_model
        )

    # ========================================================
    # PROGRESS
    # ========================================================

    def _progress(
        self,
        message,
    ):
        """
        Send progress information to:
        - Terminal
        - Streamlit UI callback
        """

        if message:

            print(
                f"[DiscussionIQ] {message}",
                flush=True,
            )

        if self.progress_callback:

            try:

                self.progress_callback(
                    message
                )

            except Exception as callback_error:

                print(
                    "[DiscussionIQ] "
                    f"Progress callback error: "
                    f"{callback_error}",
                    flush=True,
                )

    # ========================================================
    # PROCESS MEETING
    # ========================================================

    def process_meeting(
        self,
        audio_file,
    ):
        """
        Run the complete discussion-analysis pipeline.

        Args:
            audio_file:
                Path to uploaded audio file.

        Returns:
            ProcessingResult
        """

        audio_path = Path(
            audio_file
        )

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        if not audio_path.is_file():

            raise ValueError(
                f"Provided audio path is not a file: "
                f"{audio_path}"
            )

        filename = audio_path.name

        # ----------------------------------------------------
        # Create directories
        # ----------------------------------------------------

        AUDIO_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        TRANSCRIPT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        ANALYSIS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        meeting_id = None

        transcript_id = None

        analysis_id = None

        try:

            # =================================================
            # STEP 1 — AUDIO INFORMATION
            # =================================================

            self._progress(
                "1/10  Reading audio information..."
            )

            duration_seconds = get_audio_duration(
                audio_path
            )

            self._progress(
                f"Audio duration: "
                f"{duration_seconds:.2f} seconds"
            )

            # =================================================
            # STEP 2 — CREATE MEETING
            # =================================================

            self._progress(
                "2/10  Creating meeting record..."
            )

            meeting_id = create_meeting(
                filename=filename,
                duration_seconds=duration_seconds,
                status="processing",
            )

            self._progress(
                f"Meeting created: #{meeting_id}"
            )

            # =================================================
            # STEP 3 — CONVERT AUDIO
            # =================================================

            self._progress(
                "3/10  Preparing audio..."
            )

            wav_path = (
                AUDIO_DIR
                / f"{audio_path.stem}_processed.wav"
            )

            convert_to_wav(
                audio_path,
                wav_path,
            )

            if not wav_path.exists():

                raise FileNotFoundError(
                    "Audio conversion completed "
                    "but WAV file was not created: "
                    f"{wav_path}"
                )

            self._progress(
                f"Audio prepared: {wav_path}"
            )

            # =================================================
            # STEP 4 — WHISPER
            # =================================================

            self._progress(
                "4/10  Transcribing with Whisper..."
            )

            transcript_json = (
                TRANSCRIPT_DIR
                / f"{audio_path.stem}_transcript.json"
            )

            whisper_result = (
                self.transcriber.transcribe(
                    wav_path
                )
            )

            if whisper_result is None:

                raise RuntimeError(
                    "Whisper returned no transcription result."
                )

            self.transcriber.save_result(
                whisper_result,
                transcript_json,
            )

            if not transcript_json.exists():

                raise FileNotFoundError(
                    "Whisper completed but transcript "
                    "JSON was not created."
                )

            self._progress(
                "Whisper transcription completed."
            )

            # =================================================
            # STEP 5 — SPEAKER DIARIZATION
            # =================================================

            self._progress(
                "5/10  Detecting speakers..."
            )

            speaker_file = (
                TRANSCRIPT_DIR
                / f"{audio_path.stem}_speakers.txt"
            )

            speaker_segments = (
                self.diarizer.diarize(
                    wav_path
                )
            )

            if speaker_segments is None:

                raise RuntimeError(
                    "Speaker diarization returned no result."
                )

            self.diarizer.save_result(
                speaker_segments,
                speaker_file,
            )

            if not speaker_file.exists():

                raise FileNotFoundError(
                    "Speaker diarization completed "
                    "but speaker file was not created."
                )

            self._progress(
                f"Speaker detection completed: "
                f"{len(speaker_segments)} segments"
            )

            # =================================================
            # STEP 6 — MERGE TRANSCRIPT
            # =================================================

            self._progress(
                "6/10  Building speaker-aware transcript..."
            )

            merged_segments = merge_transcript(
                transcript_json,
                speaker_file,
            )

            if not merged_segments:

                raise RuntimeError(
                    "Transcript merge produced no segments."
                )

            merged_json = (
                ANALYSIS_DIR
                / f"{audio_path.stem}_merged.json"
            )

            merged_text = (
                ANALYSIS_DIR
                / f"{audio_path.stem}_merged.txt"
            )

            save_merged_json(
                merged_segments,
                merged_json,
            )

            save_merged_text(
                merged_segments,
                merged_text,
            )

            if not merged_text.exists():

                raise FileNotFoundError(
                    "Merged transcript text was not created."
                )

            self._progress(
                f"Transcript merged: "
                f"{len(merged_segments)} segments"
            )

            # =================================================
            # IMPORTANT DATABASE CHANGE
            #
            # Save transcript NOW.
            #
            # The old pipeline waited until AFTER Llama.
            # This caused PostgreSQL to show:
            #
            #     processing
            #
            # with zero transcript rows.
            #
            # =================================================

            self._progress(
                "Saving transcript to PostgreSQL..."
            )

            transcript_text = (
                merged_text.read_text(
                    encoding="utf-8"
                )
            )

            if not transcript_text.strip():

                raise RuntimeError(
                    "Merged transcript is empty."
                )

            transcript_id = save_transcript(
                filename=filename,
                transcript_text=transcript_text,
                meeting_id=meeting_id,
            )

            if transcript_id is None:

                raise RuntimeError(
                    "Database did not return a transcript ID."
                )

            self._progress(
                f"Transcript saved: #{transcript_id}"
            )

            # -------------------------------------------------
            # Save speaker segments immediately
            # -------------------------------------------------

            self._progress(
                "Saving speaker segments..."
            )

            save_speaker_segments(
                transcript_id,
                merged_segments,
            )

            self._progress(
                "Speaker segments saved."
            )

            # =================================================
            # STEP 7 — SPEAKER ANALYTICS
            # =================================================

            self._progress(
                "7/10  Calculating speaker participation..."
            )

            speaker_analytics = (
                calculate_speaker_analytics(
                    merged_segments
                )
            )

            if speaker_analytics is None:

                speaker_analytics = []

            self._progress(
                f"Speaker analytics calculated for "
                f"{len(speaker_analytics)} speakers."
            )

            # -------------------------------------------------
            # Save speaker analytics
            # -------------------------------------------------

            if speaker_analytics:

                save_speaker_analytics(
                    transcript_id,
                    speaker_analytics,
                )

                self._progress(
                    "Speaker analytics saved."
                )

            # =================================================
            # STEP 8 — LLM ANALYSIS
            # =================================================

            self._progress(
                "8/10  Generating AI insights..."
            )

            llm_transcript = (
                format_segments_for_llm(
                    merged_segments
                )
            )

            if not llm_transcript:

                raise RuntimeError(
                    "No transcript content available "
                    "for Llama analysis."
                )

            self._progress(
                "Sending transcript to Llama..."
            )

            analysis = (
                self.analyzer.analyze(
                    llm_transcript
                )
            )

            if analysis is None:

                raise RuntimeError(
                    "Llama analyzer returned no result."
                )

            if not isinstance(
                analysis,
                dict,
            ):

                raise TypeError(
                    "Llama analyzer returned an "
                    f"unexpected result type: "
                    f"{type(analysis).__name__}"
                )

            analysis_json = (
                ANALYSIS_DIR
                / f"{audio_path.stem}_analysis.json"
            )

            analysis_report = (
                ANALYSIS_DIR
                / f"{audio_path.stem}_report.txt"
            )

            save_analysis_json(
                analysis,
                analysis_json,
            )

            save_analysis_report(
                analysis,
                analysis_report,
            )

            self._progress(
                "AI analysis completed."
            )

            # =================================================
            # STEP 9 — SAVE AI RESULTS
            # =================================================

            self._progress(
                "9/10  Saving AI results to PostgreSQL..."
            )

            analysis_id = save_analysis(
                transcript_id=transcript_id,

                themes=analysis.get(
                    "themes",
                    [],
                ),

                sentiment=analysis.get(
                    "overall_sentiment",
                    "Neutral",
                ),

                summary=analysis.get(
                    "executive_summary",
                    "",
                ),

                full_analysis=analysis,

                sentiment_score=analysis.get(
                    "sentiment_score",
                    0.0,
                ),
            )

            if analysis_id is None:

                raise RuntimeError(
                    "Database did not return an analysis ID."
                )

            self._progress(
                f"Analysis saved: #{analysis_id}"
            )

            # -------------------------------------------------
            # Themes
            # -------------------------------------------------

            themes = analysis.get(
                "themes",
                [],
            )

            if themes:

                save_themes(
                    analysis_id,
                    themes,
                )

            # -------------------------------------------------
            # Key points
            # -------------------------------------------------

            key_points = analysis.get(
                "key_points",
                [],
            )

            if key_points:

                save_key_points(
                    analysis_id,
                    key_points,
                )

            # -------------------------------------------------
            # Decisions
            # -------------------------------------------------

            decisions = analysis.get(
                "decisions",
                [],
            )

            if decisions:

                save_decisions(
                    analysis_id,
                    decisions,
                )

            # -------------------------------------------------
            # Action items
            # -------------------------------------------------

            action_items = analysis.get(
                "action_items",
                [],
            )

            if action_items:

                save_action_items(
                    analysis_id,
                    action_items,
                )

            # -------------------------------------------------
            # Unresolved issues
            # -------------------------------------------------

            unresolved_issues = analysis.get(
                "unresolved_issues",
                [],
            )

            if unresolved_issues:

                save_unresolved_issues(
                    analysis_id,
                    unresolved_issues,
                )

            self._progress(
                "All AI results saved."
            )

            # =================================================
            # STEP 10 — COMPLETE
            # =================================================

            self._progress(
                "10/10  Finalizing meeting..."
            )

            update_meeting_status(
                meeting_id,
                "completed",
            )

            self._progress(
                "Meeting marked as completed."
            )

            # =================================================
            # FINAL LOG
            # =================================================

            self._progress(
                ""
            )

            self._progress(
                "========================================"
            )

            self._progress(
                "DISCUSSION ANALYSIS COMPLETED"
            )

            self._progress(
                "========================================"
            )

            self._progress(
                f"Meeting ID: {meeting_id}"
            )

            self._progress(
                f"Transcript ID: {transcript_id}"
            )

            self._progress(
                f"Analysis ID: {analysis_id}"
            )

            self._progress(
                f"Speakers: {len(speaker_analytics)}"
            )

            self._progress(
                f"Segments: {len(merged_segments)}"
            )

            self._progress(
                "========================================"
            )

            # =================================================
            # RETURN
            # =================================================

            return ProcessingResult(
                meeting_id=meeting_id,

                transcript_id=transcript_id,

                analysis_id=analysis_id,

                filename=filename,

                duration_seconds=duration_seconds,

                segments=merged_segments,

                speaker_analytics=speaker_analytics,

                analysis=analysis,
            )

        except Exception as e:

            # =================================================
            # FAILURE HANDLING
            # =================================================

            self._progress(
                ""
            )

            self._progress(
                "========================================"
            )

            self._progress(
                "DISCUSSION ANALYSIS FAILED"
            )

            self._progress(
                "========================================"
            )

            self._progress(
                f"Meeting ID: {meeting_id}"
            )

            self._progress(
                f"Stage error: {type(e).__name__}"
            )

            self._progress(
                f"Error: {e}"
            )

            self._progress(
                "========================================"
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Always mark meeting as failed.
            # ------------------------------------------------

            if meeting_id is not None:

                try:

                    update_meeting_status(
                        meeting_id,
                        "failed",
                    )

                    self._progress(
                        f"Meeting #{meeting_id} "
                        "marked as failed."
                    )

                except Exception as status_error:

                    self._progress(
                        "WARNING: Could not update "
                        "meeting status to failed: "
                        f"{status_error}"
                    )

            # ------------------------------------------------
            # Re-raise so Streamlit displays the actual error.
            # ------------------------------------------------

            raise