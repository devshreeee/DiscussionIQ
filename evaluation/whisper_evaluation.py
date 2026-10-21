# evaluation/whisper_evaluation.py
import re
import logging
from typing import List, Dict

try:
    import jiwer
except ImportError:
    raise ImportError("Please install jiwer (pip install jiwer) for WER calculation.")

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    """
    Normalizes text for ASR evaluation.
    Removes punctuation, converts to lowercase, and strips extra whitespace.
    """
    # Remove punctuation and special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Convert to lowercase and strip excess spaces
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def calculate_wer(reference_transcript: str, hypothesis_transcript: str) -> Dict[str, float]:
    """
    Calculates the Word Error Rate (WER) between a human-verified reference
    transcript and the Whisper-generated hypothesis transcript.
    
    WER = (Substitutions + Deletions + Insertions) / Number of words in reference
    """
    ref_norm = normalize_text(reference_transcript)
    hyp_norm = normalize_text(hypothesis_transcript)
    
    if not ref_norm:
        logger.warning("Reference transcript is empty after normalization.")
        return {"wer": 0.0, "substitutions": 0, "deletions": 0, "insertions": 0, "hits": 0}

    # jiwer provides detailed output including hits, substitutions, deletions, and insertions
    measures = jiwer.compute_measures(ref_norm, hyp_norm)
    
    return {
        "wer": measures["wer"],
        "substitutions": measures["substitutions"],
        "deletions": measures["deletions"],
        "insertions": measures["insertions"],
        "hits": measures["hits"]
    }

def batch_evaluate_wer(dataset: List[Dict[str, str]]) -> float:
    """
    Evaluates WER across a batch of recordings.
    Dataset format: [{'reference': '...', 'hypothesis': '...'}]
    """
    if not dataset:
        return 0.0
        
    references = [normalize_text(item["reference"]) for item in dataset]
    hypotheses = [normalize_text(item["hypothesis"]) for item in dataset]
    
    return jiwer.wer(references, hypotheses)
