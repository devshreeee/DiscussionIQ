import json
import re


def load_speakers():

    speakers = []

    with open(
        "transcripts/speakers.txt",
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            match = re.search(
                r"\[(.*?) --> (.*?)\]\s+(SPEAKER_\d+)",
                line
            )

            if match:

                start = float(
                    match.group(1).strip()
                )

                end = float(
                    match.group(2).strip()
                )

                speaker = match.group(3)

                speakers.append(
                    {
                        "start": start,
                        "end": end,
                        "speaker": speaker
                    }
                )

    return speakers


def find_speaker(
    start_time,
    end_time,
    speakers
):

    best_speaker = "UNKNOWN"
    best_overlap = 0

    for segment in speakers:

        overlap = min(
            end_time,
            segment["end"]
        ) - max(
            start_time,
            segment["start"]
        )

        if overlap > best_overlap:

            best_overlap = overlap
            best_speaker = segment["speaker"]

    return best_speaker


with open(
    "transcripts/transcript.json",
    "r",
    encoding="utf-8"
) as file:

    transcript = json.load(file)

speaker_segments = load_speakers()

print(
    f"Loaded {len(speaker_segments)} speaker segments"
)

print(
    speaker_segments[:5]
)

with open(
    "analysis/merged_transcript.txt",
    "w",
    encoding="utf-8"
) as output:

    output.write(
        "=== TRANSCRIPT ===\n\n"
    )

    for segment in transcript["segments"]:

        start = segment["start"]
        end = segment["end"]

        text = segment["text"].strip()

        speaker = find_speaker(
            start,
            end,
            speaker_segments
        )

        output.write(
            f"[{start:.2f}s - {end:.2f}s]\n"
        )

        output.write(
            f"{speaker}\n"
        )

        output.write(
            f"{text}\n\n"
        )

print(
    "Speaker-aware transcript created!"
)