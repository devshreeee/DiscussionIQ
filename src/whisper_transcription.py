import whisper
import json
import sys

audio_file = sys.argv[1]

model = whisper.load_model("base")

result = model.transcribe(audio_file)

with open(
    "transcripts/transcript.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        result,
        file,
        indent=4
    )

print("Transcription saved!")