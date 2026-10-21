"""
DiscussionIQ - Reports View

Generate and download complete discussion reports.
"""

import json
from datetime import datetime

import streamlit as st

from ui.components import (
    format_duration,
    empty_state,
)

from database.dashboard_queries import (
    get_recent_meetings,
    get_meeting,
    get_transcript,
    get_analysis,
    get_speaker_segments,
    get_speaker_analytics,
    get_themes,
    get_key_points,
    get_decisions,
    get_action_items,
    get_unresolved_issues,
)


# ============================================================
# HELPERS
# ============================================================

def safe_text(value, default=""):
    if value is None:
        return default

    return str(value)


def format_date(value):

    if value is None:
        return "Unavailable"

    try:
        return value.strftime(
            "%d %b %Y · %I:%M %p"
        )
    except AttributeError:
        return str(value)


def json_safe(value):

    if isinstance(value, dict):

        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, list):

        return [
            json_safe(v)
            for v in value
        ]

    if isinstance(value, tuple):

        return [
            json_safe(v)
            for v in value
        ]

    if isinstance(value, datetime):

        return value.isoformat()

    try:

        json.dumps(value)

        return value

    except (
        TypeError,
        ValueError,
    ):

        return str(value)


# ============================================================
# MAIN
# ============================================================

def show_reports():

    st.title(
        "Reports"
    )

    st.caption(
        "Generate and download a complete discussion intelligence report."
    )

    st.write("")

    # ========================================================
    # LOAD MEETINGS
    # ========================================================

    try:

        meetings = get_recent_meetings(
            limit=100
        )

    except Exception as e:

        st.error(
            "Unable to load meetings."
        )

        with st.expander(
            "Technical error"
        ):

            st.exception(e)

        return

    if not meetings:

        empty_state(
            "No meetings available",
            "Process a meeting first to generate a report.",
        )

        return

    # ========================================================
    # SELECT MEETING
    # ========================================================

    selected_id = st.session_state.get(
        "selected_meeting"
    )

    meeting_options = {}

    for meeting in meetings:

        meeting_id = meeting.get(
            "id"
        )

        filename = meeting.get(
            "filename",
            f"Meeting {meeting_id}"
        )

        status = meeting.get(
            "status",
            "unknown"
        )

        label = (
            f"#{meeting_id} — "
            f"{filename} — "
            f"{str(status).title()}"
        )

        meeting_options[label] = meeting_id

    labels = list(
        meeting_options.keys()
    )

    default_index = 0

    if selected_id is not None:

        for index, label in enumerate(labels):

            if meeting_options[label] == selected_id:

                default_index = index

                break

    selected_label = st.selectbox(
        "Select a meeting",
        labels,
        index=default_index,
        key="report_meeting_selector",
    )

    meeting_id = meeting_options[
        selected_label
    ]

    st.session_state.selected_meeting = (
        meeting_id
    )

    # ========================================================
    # LOAD SELECTED MEETING
    # ========================================================

    try:

        meeting = get_meeting(
            meeting_id
        )

    except Exception as e:

        st.error(
            "Unable to load the selected meeting."
        )

        with st.expander(
            "Technical error"
        ):

            st.exception(e)

        return

    if meeting is None:

        st.error(
            "Selected meeting was not found."
        )

        return

    # ========================================================
    # MEETING HEADER
    # ========================================================

    st.divider()

    st.subheader(
        safe_text(
            meeting.get(
                "filename",
                "Untitled Meeting",
            )
        )
    )

    st.caption(
        f"Meeting #{meeting_id} · "
        f"{format_date(meeting.get('created_at'))}"
    )

    # ========================================================
    # METADATA
    # ========================================================

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Duration",
            format_duration(
                meeting.get(
                    "duration_seconds",
                    0,
                )
            ),
        )

    with col2:

        st.metric(
            "Status",
            str(
                meeting.get(
                    "status",
                    "Unknown"
                )
            ).title(),
        )

    with col3:

        st.metric(
            "Meeting ID",
            meeting_id,
        )

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    transcript = None

    try:

        transcript = get_transcript(
            meeting_id
        )

    except Exception:

        transcript = None

    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis = None

    if transcript:

        try:

            analysis = get_analysis(
                transcript["id"]
            )

        except Exception:

            analysis = None

    # ========================================================
    # SPEAKERS
    # ========================================================

    speaker_segments = []

    speaker_analytics = []

    if transcript:

        transcript_id = transcript["id"]

        try:

            speaker_segments = (
                get_speaker_segments(
                    transcript_id
                )
                or []
            )

        except Exception:

            speaker_segments = []

        try:

            speaker_analytics = (
                get_speaker_analytics(
                    transcript_id
                )
                or []
            )

        except Exception:

            speaker_analytics = []

    # ========================================================
    # STRUCTURED ANALYSIS
    # ========================================================

    themes = []
    key_points = []
    decisions = []
    action_items = []
    unresolved_issues = []

    if analysis:

        analysis_id = analysis["id"]

        try:

            themes = (
                get_themes(
                    analysis_id
                )
                or []
            )

        except Exception:

            themes = []

        try:

            key_points = (
                get_key_points(
                    analysis_id
                )
                or []
            )

        except Exception:

            key_points = []

        try:

            decisions = (
                get_decisions(
                    analysis_id
                )
                or []
            )

        except Exception:

            decisions = []

        try:

            action_items = (
                get_action_items(
                    analysis_id
                )
                or []
            )

        except Exception:

            action_items = []

        try:

            unresolved_issues = (
                get_unresolved_issues(
                    analysis_id
                )
                or []
            )

        except Exception:

            unresolved_issues = []

    # ========================================================
    # BUILD REPORT
    # ========================================================

    report = {

        "application": "DiscussionIQ",

        "report_version": "1.0",

        "generated_at":
            datetime.now().isoformat(),

        "meeting": meeting,

        "transcript": transcript,

        "speaker_segments":
            speaker_segments,

        "speaker_analytics":
            speaker_analytics,

        "analysis":
            analysis,

        "themes":
            themes,

        "key_points":
            key_points,

        "decisions":
            decisions,

        "action_items":
            action_items,

        "unresolved_issues":
            unresolved_issues,
    }

    report = json_safe(
        report
    )

    json_data = json.dumps(
        report,
        indent=4,
        ensure_ascii=False,
    )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.divider()

    st.subheader(
        "Download Report"
    )

    st.caption(
        "The report contains meeting metadata, "
        "transcript data, speaker analytics, "
        "and AI-generated discussion insights."
    )

    base_name = safe_text(
        meeting.get(
            "filename",
            f"meeting_{meeting_id}",
        )
    )

    base_name = (
        base_name
        .replace(
            " ",
            "_"
        )
        .replace(
            "/",
            "_"
        )
        .replace(
            "\\",
            "_"
        )
    )

    report_filename = (
        f"discussioniq_"
        f"{base_name}_"
        f"{meeting_id}.json"
    )

    st.download_button(
        "⬇️ Download JSON Report",
        data=json_data,
        file_name=report_filename,
        mime="application/json",
        use_container_width=True,
        type="primary",
        key="download_report",
    )

    # ========================================================
    # PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "Report Preview"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if analysis:

        summary = safe_text(
            analysis.get(
                "summary"
            )
        )

        if summary:

            st.markdown(
                "### Executive Summary"
            )

            st.info(
                summary
            )

        # ----------------------------------------------------
        # Sentiment
        # ----------------------------------------------------

        sentiment = safe_text(
            analysis.get(
                "sentiment",
                "Unknown",
            ),
            "Unknown",
        )

        score = analysis.get(
            "sentiment_score"
        )

        st.markdown(
            "### Sentiment"
        )

        col1, col2 = st.columns(
            2
        )

        with col1:

            st.metric(
                "Sentiment",
                sentiment.title(),
            )

        with col2:

            if score is not None:

                try:

                    score = float(
                        score
                    )

                    st.metric(
                        "Score",
                        f"{score:.2f}",
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    st.metric(
                        "Score",
                        str(score),
                    )

            else:

                st.metric(
                    "Score",
                    "—",
                )

    else:

        st.warning(
            "AI analysis is not available for this meeting."
        )

    # --------------------------------------------------------
    # Themes
    # --------------------------------------------------------

    if themes:

        st.markdown(
            "### Key Themes"
        )

        for item in themes:

            theme = safe_text(
                item.get(
                    "theme"
                )
            )

            if theme:

                st.markdown(
                    f"• {theme}"
                )

    # --------------------------------------------------------
    # Key Points
    # --------------------------------------------------------

    if key_points:

        st.markdown(
            "### Key Discussion Points"
        )

        for item in key_points:

            point = safe_text(
                item.get(
                    "point"
                )
            )

            if point:

                st.markdown(
                    f"• {point}"
                )

    # --------------------------------------------------------
    # Decisions
    # --------------------------------------------------------

    if decisions:

        st.markdown(
            "### Decisions"
        )

        for item in decisions:

            decision = safe_text(
                item.get(
                    "decision"
                )
            )

            if decision:

                st.success(
                    f"✓ {decision}"
                )

    # --------------------------------------------------------
    # Action Items
    # --------------------------------------------------------

    if action_items:

        st.markdown(
            "### Action Items"
        )

        for item in action_items:

            task = safe_text(
                item.get(
                    "task"
                )
            )

            speaker = safe_text(
                item.get(
                    "speaker"
                )
            )

            priority = safe_text(
                item.get(
                    "priority"
                )
            )

            if task:

                details = []

                if speaker:

                    details.append(
                        f"Owner: {speaker}"
                    )

                if priority:

                    details.append(
                        f"Priority: {priority}"
                    )

                if details:

                    st.markdown(
                        f"☐ **{task}** — "
                        f"{' · '.join(details)}"
                    )

                else:

                    st.markdown(
                        f"☐ **{task}**"
                    )

    # --------------------------------------------------------
    # Unresolved Issues
    # --------------------------------------------------------

    if unresolved_issues:

        st.markdown(
            "### Unresolved Issues"
        )

        for item in unresolved_issues:

            issue = safe_text(
                item.get(
                    "issue"
                )
            )

            if issue:

                st.warning(
                    f"⚠️ {issue}"
                )

    # --------------------------------------------------------
    # Transcript
    # --------------------------------------------------------

    if transcript:

        st.markdown(
            "### Transcript"
        )

        transcript_text = safe_text(
            transcript.get(
                "transcript_text"
            )
        )

        if transcript_text:

            with st.expander(
                "View transcript"
            ):

                st.text_area(
                    "Transcript",
                    transcript_text,
                    height=500,
                    disabled=True,
                    label_visibility="collapsed",
                )

    # --------------------------------------------------------
    # Participants
    # --------------------------------------------------------

    if speaker_analytics:

        st.markdown(
            "### Participant Analytics"
        )

        rows = []

        for speaker in speaker_analytics:

            rows.append(
                {
                    "Speaker":
                        speaker.get(
                            "speaker",
                            "Unknown",
                        ),

                    "Speaking Time":
                        format_duration(
                            speaker.get(
                                "speaking_time_seconds",
                                0,
                            )
                        ),

                    "Segments":
                        speaker.get(
                            "segment_count",
                            0,
                        ),

                    "Words":
                        speaker.get(
                            "word_count",
                            0,
                        ),

                    "Participation":
                        (
                            f"{float(
                                speaker.get(
                                    "participation_percentage",
                                    0,
                                )
                                or 0
                            ):.1f}%"
                        ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
        )

    # ========================================================
    # RAW JSON
    # ========================================================

    with st.expander(
        "View raw JSON"
    ):

        st.code(
            json_data,
            language="json",
        )