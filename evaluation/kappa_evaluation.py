# evaluation/kappa_evaluation.py
import logging
from typing import List, Dict, Any
from sklearn.metrics import cohen_kappa_score, classification_report, confusion_matrix

logger = logging.getLogger(__name__)

def evaluate_classification_agreement(
    human_annotations: List[str], 
    ai_predictions: List[str], 
    labels: List[str]
) -> Dict[str, Any]:
    """
    Calculates Cohen's Kappa and other classification metrics to evaluate the 
    agreement between the LLM's predictions and human ground-truth annotations.
    """
    if len(human_annotations) != len(ai_predictions):
        raise ValueError("The number of human annotations must match the number of AI predictions.")
    
    if not human_annotations:
        logger.warning("Empty annotation lists provided. Cannot compute Kappa.")
        return {"kappa_score": None}

    # Calculate Cohen's Kappa
    # kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
    kappa = cohen_kappa_score(human_annotations, ai_predictions, labels=labels)
    
    # Generate per-class precision, recall, and F1-score
    report = classification_report(
        human_annotations, 
        ai_predictions, 
        labels=labels, 
        output_dict=True,
        zero_division=0
    )
    
    # Confusion matrix for identifying specific category confusion
    conf_matrix = confusion_matrix(human_annotations, ai_predictions, labels=labels)

    return {
        "kappa_score": kappa,
        "classification_report": report,
        "confusion_matrix": conf_matrix.tolist()
    }
