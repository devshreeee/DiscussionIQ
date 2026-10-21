import json
import re
from pathlib import Path


# ============================================================
# SPEAKER LOADING
# ============================================================

def load_speaker_segments(
    speaker_file
):
    """
    Load speaker diarization segments.

    Expected format:

    [0.000 --> 4.500] SPEAKER_00

    Returns:

    [
        {
            "speaker": "SPEAKER_00",
            "start": 0.0,
            "end": 4.5
        }
    ]
    """

    speaker_path = Path(
        speaker_file
    )

    if not speaker_path.exists():

        raise FileNotFoundError(
            f"Speaker file not found: {speaker_path}"
        )

    speakers = []

    pattern = re.compile(
        r"\[\s*(\d+(?:\.\d+)?)\s*-->\s*(\d+(?:\.\d+)?)\s*\]\s*(\S+)",
        re.VERBOSE
    )

    with open(
        speaker_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            match = pattern.search(
                line
            )

            if not match:
                continue

            speakers.append(
                {
                    "start": float(
                        match.group(1)
                    ),
                    "end": float(
                        match.group(2)
                    ),
                    "speaker": match.group(3)
                }
            )

    if not speakers:

        raise ValueError(
            "No speaker segments found."
        )

    return speakers


# ============================================================
# FIND BEST SPEAKER
# ============================================================

def find_speaker(
    start_time,
    end_time,
    speakers
):
    """
    Find the speaker with the greatest temporal overlap
    with a Whisper transcript segment.
    """

    best_speaker = "UNKNOWN"

    best_overlap = 0.0

    for segment in speakers:

        overlap = (
            min(
                end_time,
                segment["end"]
            )
            -
            max(
                start_time,
                segment["start"]
            )
        )

        if overlap > best_overlap:

            best_overlap = overlap

            best_speaker = (
                segment["speaker"]
            )

    return best_speaker


# ============================================================
# MERGE TRANSCRIPT
# ============================================================

def merge_transcript(
    transcript_file,
    speaker_file
):
    """
    Merge Whisper transcript segments with PyAnnote
    speaker information.

    Returns:

    [
        {
            "speaker": "SPEAKER_00",
            "start": 0.0,
            "end": 4.5,
            "text": "Hello everyone."
        }
    ]
    """

    transcript_path = Path(
        transcript_file
    )

    if not transcript_path.exists():

        raise FileNotFoundError(
            f"Transcript file not found: "
            f"{transcript_path}"
        )

    # --------------------------------------------------------
    # Load Whisper JSON
    # --------------------------------------------------------

    with open(
        transcript_path,
        "r",
        encoding="utf-8"
    ) as file:

        transcript = json.load(
            file
        )

    # --------------------------------------------------------
    # Load speakers
    # --------------------------------------------------------

    speakers = load_speaker_segments(
        speaker_file
    )

    merged_segments = []

    whisper_segments = (
        transcript.get(
            "segments",
            []
        )
    )

    if not whisper_segments:

        raise ValueError(
            "No Whisper transcript segments found."
        )

    # --------------------------------------------------------
    # Match segments
    # --------------------------------------------------------

    for segment in whisper_segments:

        start = float(
            segment["start"]
        )

        end = float(
            segment["end"]
        )

        text = (
            segment.get(
                "text",
                ""
            )
            .strip()
        )

        if not text:
            continue

        speaker = find_speaker(
            start,
            end,
            speakers
        )

        merged_segments.append(
            {
                "speaker": speaker,
                "start": start,
                "end": end,
                "text": text
            }
        )

    return merged_segments


# ============================================================
# SAVE JSON
# ============================================================

def save_merged_json(
    segments,
    output_file
):
    """
    Save merged transcript as JSON.
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
            segments,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_path


# ============================================================
# SAVE TEXT
# ============================================================

def save_merged_text(
    segments,
    output_file
):
    """
    Save a human-readable speaker-aware transcript.
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

        file.write(
            "=== DISCUSSION TRANSCRIPT ===\n\n"
        )

        for segment in segments:

            file.write(
                f"[{segment['start']:.2f}s - "
                f"{segment['end']:.2f}s]\n"
            )

            file.write(
                f"{segment['speaker']}\n"
            )

            file.write(
                f"{segment['text']}\n\n"
            )

    return output_path


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def build_merged_transcript(
    transcript_file="transcripts/transcript.json",
    speaker_file="transcripts/speakers.txt",
    json_output="analysis/merged_transcript.json",
    text_output="analysis/merged_transcript.txt"
):
    """
    Complete transcript merging step.

    Produces both:

        merged_transcript.json
        merged_transcript.txt

    Returns:
        list of merged segments
    """

    segments = merge_transcript(
        transcript_file,
        speaker_file
    )

    save_merged_json(
        segments,
        json_output
    )

    save_merged_text(
        segments,
        text_output
    )

    print(
        f"Merged {len(segments)} transcript segments."
    )

    print(
        f"JSON saved: {json_output}"
    )

    print(
        f"Text saved: {text_output}"
    )

    return segments