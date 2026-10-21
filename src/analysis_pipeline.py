import subprocess


def run_pipeline(audio_file):

    print("Running Whisper...")

    subprocess.run(
        [
            "python",
            "src/whisper_transcription.py",
            audio_file
        ],
        check=True
    )

    print("Running Diarization...")

    subprocess.run(
        [
            "python",
            "src/diarization.py",
            audio_file
        ],
        check=True
    )

    print("Merging Transcript...")

    subprocess.run(
        [
            "python",
            "src/transcript_merger.py"
        ],
        check=True
    )

    print("Running LLM Analysis...")

    subprocess.run(
        [
            "python",
            "-m",
            "src.llm_analysis"
        ],
        check=True
    )