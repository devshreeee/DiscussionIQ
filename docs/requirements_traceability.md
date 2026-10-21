# Requirements Traceability Matrix

Mapping professor remarks to system implementation.

| Remark | Interpretation | Relevant Feature | Implementation Files | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1. Blue Index | Composite participant engagement score. | Participant Analytics | `pipeline/speaker_analytics.py`, `views/analytics.py` | In Progress |
| 2. Kappa score | Cohen's Kappa for classification evaluation. | Evaluation Pipeline | `evaluation/whisper_evaluation.py` (to be expanded) | Pending Data |
| 3. CSK, NC, MTF | Unresolved terms. | Pending Specification | `src/llm_analysis.py` (Placeholders) | Unresolved |
| 4. Negotiations | Strategic classification category. | LLM Analysis Taxonomy | `src/llm_analysis.py` | Implemented |
| 5. Maintaining function | Communicative classification category. | LLM Analysis Taxonomy | `src/llm_analysis.py` | Implemented |
| 6. Strategising | Strategic classification category. | LLM Analysis Taxonomy | `src/llm_analysis.py` | Implemented |
| 7. Real-time analysis | Near-real-time streaming analytics. | Streaming Pipeline | N/A | Future Scope (Post-Submission) |
| 8. Stronger classification | Evidence-grounded multi-label taxonomy. | LLM Analysis layer | `src/llm_analysis.py` | In Progress |
