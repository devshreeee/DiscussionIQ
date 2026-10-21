from pathlib import Path
import subprocess


# ============================================================
# SUPPORTED AUDIO FORMATS
# ============================================================

SUPPORTED_AUDIO_FORMATS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".flac",
    ".ogg",
    ".mp4",
    ".webm"
}


# ============================================================
# AUDIO VALIDATION
# ============================================================

def validate_audio_file(
    audio_file
):
    """
    Validate that an audio file exists and has a supported
    file extension.

    Args:
        audio_file: File path as string or Path.

    Returns:
        Path: Validated audio path.

    Raises:
        FileNotFoundError
        ValueError
    """

    audio_path = Path(audio_file)

    if not audio_path.exists():

        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    if not audio_path.is_file():

        raise ValueError(
            f"Provided path is not a file: {audio_path}"
        )

    extension = (
        audio_path.suffix.lower()
    )

    if extension not in SUPPORTED_AUDIO_FORMATS:

        supported = ", ".join(
            sorted(SUPPORTED_AUDIO_FORMATS)
        )

        raise ValueError(
            f"Unsupported audio format: {extension}. "
            f"Supported formats: {supported}"
        )

    return audio_path


# ============================================================
# FFMPEG CHECK
# ============================================================

def check_ffmpeg():
    """
    Check whether FFmpeg is installed and available
    in the system PATH.

    Returns:
        bool
    """

    try:

        result = subprocess.run(
            [
                "ffmpeg",
                "-version"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

        return result.returncode == 0

    except FileNotFoundError:

        return False


# ============================================================
# AUDIO CONVERSION
# ============================================================

def convert_to_wav(
    input_file,
    output_file
):
    """
    Convert an audio file to a standardized WAV format.

    Output:
        Sample rate: 16 kHz
        Channels: 1
        Codec: PCM 16-bit

    This format is suitable for Whisper and PyAnnote.
    """

    input_path = validate_audio_file(
        input_file
    )

    output_path = Path(
        output_file
    )

    if not check_ffmpeg():

        raise RuntimeError(
            "FFmpeg is not installed or is not available "
            "in your system PATH."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                str(output_path)
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:

        error_message = (
            e.stderr.strip()
            if e.stderr
            else "Unknown FFmpeg error."
        )

        raise RuntimeError(
            f"Audio conversion failed:\n{error_message}"
        ) from e

    if not output_path.exists():

        raise RuntimeError(
            "FFmpeg completed but the output WAV file "
            "was not created."
        )

    return output_path


# ============================================================
# AUDIO DURATION
# ============================================================

def get_audio_duration(
    audio_file
):
    """
    Get audio duration in seconds using FFprobe.

    Returns:
        float: Duration in seconds.
    """

    audio_path = validate_audio_file(
        audio_file
    )

    try:

        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        duration = float(
            result.stdout.strip()
        )

        return duration

    except FileNotFoundError:

        raise RuntimeError(
            "FFprobe is not installed or is not available "
            "in your system PATH."
        )

    except (
        subprocess.CalledProcessError,
        ValueError
    ) as e:

        raise RuntimeError(
            f"Could not determine audio duration: {e}"
        ) from e