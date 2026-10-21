# pipeline/transcript_merger.py
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def get_intersection(start1: float, end1: float, start2: float, end2: float) -> float:
    """Calculates the temporal overlap between two time segments."""
    return max(0, min(end1, end2) - max(start1, start2))

def align_transcript_with_speakers(
    whisper_segments: List[Dict[str, Any]], 
    pyannote_segments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Fuses Whisper ASR segments with Pyannote diarization boundaries.
    whisper_segments format: [{'start': 0.0, 'end': 2.5, 'text': 'Hello'}]
    pyannote_segments format: [{'start': 0.0, 'end': 3.0, 'speaker': 'SPEAKER_00'}]
    """
    aligned_transcript = []

    for w_seg in whisper_segments:
        w_start = w_seg['start']
        w_end = w_seg['end']
        w_text = w_seg['text'].strip()
        
        best_speaker = "UNKNOWN"
        max_overlap = 0.0
        
        # Find the speaker segment that overlaps most with this text segment
        for p_seg in pyannote_segments:
            overlap = get_intersection(w_start, w_end, p_seg['start'], p_seg['end'])
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = p_seg['speaker']
        
        # If no strict overlap is found but text exists, default to the nearest previous speaker
        if max_overlap == 0.0 and pyannote_segments:
            logger.warning(f"No speaker overlap found for segment [{w_start}-{w_end}]. Assigning UNKNOWN.")

        aligned_transcript.append({
            "speaker_label": best_speaker,
            "start_time": w_start,
            "end_time": w_end,
            "transcript_text": w_text
        })

    return aligned_transcript
