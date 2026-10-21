import os
from pathlib import Path

from pyannote.audio import Pipeline


# ============================================================
# DIARIZATION MODEL
# ============================================================

DEFAULT_MODEL = (
    "pyannote/speaker-diarization-community-1"
)


# ============================================================
# PYANNOTE DIARIZER
# ============================================================

class SpeakerDiarizer:
    """
    Wrapper around PyAnnote speaker diarization.

    Detects:
        - speaker identity
        - segment start time
        - segment end time
    """

    def __init__(
        self,
        model_name=DEFAULT_MODEL
    ):

        self.model_name = model_name

        print()
        print(
            f"Loading diarization model: "
            f"{model_name}"
        )

        # ----------------------------------------------------
        # Hugging Face token
        # ----------------------------------------------------

        hf_token = os.getenv(
            "HF_TOKEN"
        )

        # ----------------------------------------------------
        # Load PyAnnote
        # ----------------------------------------------------

        if hf_token:

            self.pipeline = (
                Pipeline.from_pretrained(
                    model_name,
                    token=hf_token
                )
            )

        else:

            self.pipeline = (
                Pipeline.from_pretrained(
                    model_name
                )
            )

        if self.pipeline is None:

            raise RuntimeError(
                "Failed to load PyAnnote diarization pipeline."
            )

        print(
            "Diarization model loaded."
        )

    # ========================================================
    # DIARIZE
    # ========================================================

    def diarize(
        self,
        audio_file
    ):
        """
        Run speaker diarization.

        Returns:

        [
            {
                "speaker": "SPEAKER_00",
                "start": 0.0,
                "end": 4.5
            },
            ...
        ]
        """

        audio_path = Path(
            audio_file
        )

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        print(
            f"Running speaker diarization on "
            f"{audio_path.name}"
        )

        result = self.pipeline(
            str(audio_path)
        ) # type: ignore

        # ----------------------------------------------------
        # PyAnnote Community-1 API
        # ----------------------------------------------------

        if hasattr(
            result,
            "speaker_diarization"
        ):

            diarization = (
                result.speaker_diarization
            )

        else:

            diarization = result

        segments = []

        for turn, _, speaker in (
            diarization.itertracks(
                yield_label=True
            )
        ):

            segments.append(
                {
                    "speaker": speaker,
                    "start": float(
                        turn.start
                    ),
                    "end": float(
                        turn.end
                    )
                }
            )

        print(
            f"Detected {len(segments)} "
            f"speaker segments."
        )

        return segments

    # ========================================================
    # SAVE RESULT
    # ========================================================

    def save_result(
        self,
        segments,
        output_file
    ):
        """
        Save diarization segments to a text file.
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

            for segment in segments:

                line = (
                    f"[{segment['start']:.3f} --> "
                    f"{segment['end']:.3f}] "
                    f"{segment['speaker']}\n"
                )

                file.write(line)

        print(
            f"Diarization saved: {output_path}"
        )

        return output_path


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def diarize_audio(
    audio_file,
    output_file="transcripts/speakers.txt",
    model_name=DEFAULT_MODEL
):
    """
    Run the complete diarization step.
    """

    diarizer = SpeakerDiarizer(
        model_name=model_name
    )

    segments = diarizer.diarize(
        audio_file
    )

    diarizer.save_result(
        segments,
        output_file
    )

    return segments