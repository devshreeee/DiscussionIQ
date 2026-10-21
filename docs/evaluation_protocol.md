# Evaluation Protocol

## 1. Speech Recognition Evaluation (WER)
*   **Metric**: Word Error Rate (WER).
*   **Methodology**: `jiwer` will be used to compute the Levenshtein distance between human-verified reference transcripts and the Whisper ASR output.
*   **Text Normalization**: Punctuation is stripped, text is converted to lowercase, and multiple spaces are collapsed to single spaces prior to evaluation.
*   **Current Status**: Evaluation pipeline implemented (`evaluation/whisper_evaluation.py`). **Actual results pending** manual transcription of the multilingual test corpus.

## 2. Classification Evaluation (Cohen's Kappa & F1)
*   **Metrics**: Cohen's Kappa, Macro-F1, Per-class Precision/Recall.
*   **Methodology**: `scikit-learn` is used to calculate Cohen's Kappa between two independent raters (e.g., Human vs. LLM, or Human 1 vs. Human 2 for baseline agreement).
*   **Annotation Unit**: The classification unit is a single diarized utterance/turn.
*   **Current Status**: Evaluation pipeline implemented (`evaluation/kappa_evaluation.py`). **Actual results pending** independent human coding of the evaluation dataset.
