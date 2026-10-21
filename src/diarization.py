from pyannote.audio import Pipeline
import sys
import os

# ==========================
# INPUT FILE
# ==========================

if len(sys.argv) < 2:
    raise RuntimeError(
        "Audio file path not provided."
    )

audio_file = sys.argv[1]

if not os.path.exists(audio_file):
    raise FileNotFoundError(
        f"Audio file not found: {audio_file}"
    )

print("Loading pipeline...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-community-1"
)

print("Pipeline loaded!")
print("Running speaker diarization...")

# ==========================
# RUN DIARIZATION
# ==========================

result = pipeline(audio_file) # type: ignore

# v4 API
speaker_diarization = result.speaker_diarization

# ==========================
# SAVE OUTPUT
# ==========================

os.makedirs(
    "transcripts",
    exist_ok=True
)

with open(
    "transcripts/speakers.txt",
    "w",
    encoding="utf-8"
) as file:

    for turn, _, speaker in speaker_diarization.itertracks(
        yield_label=True
    ):

        line = (
            f"[{turn.start:.3f} --> "
            f"{turn.end:.3f}] "
            f"{speaker}\n"
        )

        print(line.strip())

        file.write(line)

print("Speaker diarization saved!")