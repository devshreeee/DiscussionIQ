import json
from pathlib import Path

import whisper


# ============================================================
# WHISPER TRANSCRIBER
# ============================================================

class WhisperTranscriber:
    """
    Wrapper around OpenAI Whisper.

    The model is loaded once when the transcriber is created,
    rather than every time transcription is requested.
    """

    def __init__(
        self,
        model_name="base"
    ):
        self.model_name = model_name

        print(
            f"Loading Whisper model: {model_name}"
        )

        self.model = whisper.load_model(
            model_name
        )

        print(
            "Whisper model loaded."
        )

    # ========================================================
    # TRANSCRIBE
    # ========================================================

    def transcribe(
        self,
        audio_file,
        language=None
    ):
        """
        Transcribe an audio file.

        Args:
            audio_file: Path to WAV/audio file.
            language: Optional language code such as "en".

        Returns:
            dict containing Whisper's transcription result.
        """

        audio_path = Path(
            audio_file
        )

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        options = {
            "verbose": False
        }

        if language:

            options["language"] = language

        print(
            f"Transcribing: {audio_path.name}"
        )

        result = self.model.transcribe(
            str(audio_path),
            **options # type: ignore
        )

        return result

    # ========================================================
    # SAVE RESULT
    # ========================================================

    def save_result(
        self,
        result,
        output_file
    ):
        """
        Save Whisper result as JSON.
        """

        output_path = Path(
            output_file
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            f"Transcription saved: {output_path}"
        )

        return output_path


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def transcribe_audio(
    audio_file,
    output_file="transcripts/transcript.json",
    model_name="base",
    language=None
):
    """
    Convenience function for the complete transcription step.

    This allows the pipeline to simply call:

        transcribe_audio(audio_file)

    """

    transcriber = WhisperTranscriber(
        model_name=model_name
    )

    result = transcriber.transcribe(
        audio_file,
        language=language
    )

    transcriber.save_result(
        result,
        output_file
    )

    return result