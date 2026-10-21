# src/llm_analysis.py
import json
import logging
from typing import Dict, List, Optional
# Assuming usage of an LLM client like OpenAI or a local Llama 3.2 wrapper
# from openai import OpenAI 

logger = logging.getLogger(__name__)

# Verified Taxonomy based on Review 2 PPT (Slide 7)
TAXONOMY = {
    "Strategic & Analytical": [
        "Negotiation", 
        "Strategising",
        "Problem Solving", 
        "Decision Making"
    ],
    "Communicative": [
        "Information Sharing", 
        "Coordination",
        "Maintaining Function"
    ],
    "Interpersonal": [
        "Agreement / Disagreement", 
        "Questioning / Clarification"
    ],
    "Pending_Specification": [
        "CSK", # Unresolved professor remark
        "NC",  # Unresolved professor remark
        "MTF"  # Unresolved professor remark
    ]
}

def build_classification_prompt(transcript_segment: str, context: str = "") -> str:
    """
    Constructs an instructional, schema-constrained prompt for the LLM.
    Implements practices from Leça et al. and Barros et al. to prevent over-categorization.
    """
    schema = {
        "speaker_id": "string",
        "timestamp_start": "float",
        "timestamp_end": "float",
        "themes": ["string (max 3)"],
        "sentiment": "Positive | Neutral | Negative",
        "classifications": ["string (must be from the approved taxonomy)"],
        "evidence_span": "string (exact quote from segment)",
        "confidence_score": "float (0.0 to 1.0)"
    }
    
    prompt = f"""
    You are an expert qualitative researcher analyzing a multilingual group discussion.
    Analyze the following transcript segment and classify its communicative function.
    
    Context: {context}
    Segment: "{transcript_segment}"
    
    You MUST strictly use the following classification taxonomy:
    {json.dumps(TAXONOMY, indent=2)}
    
    Respond ONLY with a valid JSON object matching this schema:
    {json.dumps(schema, indent=2)}
    
    Do not hallucinate categories. If a segment's intent is ambiguous, use "Maintaining Function" or "Information Sharing".
    """
    return prompt

def parse_and_validate_llm_response(response_text: str) -> Dict:
    """Validates that the LLM output conforms to our exact schema and taxonomy."""
    try:
        data = json.loads(response_text)
        # Validate classifications against taxonomy
        valid_classes = [item for sublist in TAXONOMY.values() for item in sublist]
        validated_classes = [c for c in data.get("classifications", []) if c in valid_classes]
        
        data["classifications"] = validated_classes
        return data
    except json.JSONDecodeError:
        logger.error("LLM returned malformed JSON.")
        return {"error": "Invalid JSON response", "raw_output": response_text}

class PendingMetricsInterface:
    """
    Placeholder interface for unresolved professor metrics (CSK, NC, MTF).
    These will remain passive until operational definitions are provided.
    """
    @staticmethod
    def calculate_csk(data: Dict) -> Optional[float]:
        logging.warning("CSK calculation requested but metric is unresolved.")
        return None

    @staticmethod
    def calculate_nc(data: Dict) -> Optional[float]:
        logging.warning("NC calculation requested but metric is unresolved.")
        return None

    @staticmethod
    def calculate_mtf(data: Dict) -> Optional[float]:
        logging.warning("MTF calculation requested but metric is unresolved.")
        return None
