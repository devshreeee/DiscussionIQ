# views/analytics.py
import streamlit as st
import pandas as pd
from pipeline.speaker_analytics import DiscussionAnalyticsEngine
from database.dashboard_queries import get_meeting_segments, get_meeting_classifications

def render_analytics_page(meeting_id: int):
    st.header("Communication & Negotiation Analytics")
    
    # Fetch data from the database
    segments = get_meeting_segments(meeting_id)
    classifications = get_meeting_classifications(meeting_id)
    
    if not segments:
        st.info("No transcript segments available for this meeting yet. Please check the processing status.")
        return

    engine = DiscussionAnalyticsEngine(segments, classifications)
    
    st.subheader("Participant Contributions")
    contributions = engine.get_participant_contributions()
    if contributions:
        df_contrib = pd.DataFrame.from_dict(contributions, orient='index')
        st.dataframe(df_contrib.style.format({"total_speaking_time_seconds": "{:.1f}s", "average_turn_duration": "{:.1f}s"}))
    else:
        st.write("Not enough data to calculate contributions.")

    st.subheader("Discussion Strategy & Category Distribution")
    distribution = engine.get_category_distribution()
    if distribution:
        st.bar_chart(pd.Series(distribution), use_container_width=True)
    else:
        st.write("Awaiting LLM classification data to render distribution.")
        
    st.subheader("Action Items & Decisions")
    actions = engine.extract_action_items()
    if actions:
        for action in actions:
            st.markdown(f"**{action['speaker_label']}** at `{action['start_time']}s` ({action['category_name']}):")
            st.markdown(f"> *\"{action['evidence_span']}\"*")
    else:
        st.write("No explicit decisions or action items detected in this discussion.")

    # Warning regarding interpretation (Addressing Phase 9 rules)
    st.caption("⚠️ **Note**: Speaking time does not strictly equate to influence or negotiation success. Sentiment and category predictions are model-generated and should be reviewed alongside the transcript evidence.")
