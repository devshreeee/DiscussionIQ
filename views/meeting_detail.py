"""
DiscussionIQ - Meeting Detail View

Displays the complete information for one meeting:
- Meeting metadata
- Transcript
- Speaker-attributed transcript
- AI summary
- Sentiment
- Themes
- Key points
- Decisions
- Action items
- Unresolved issues
- Participant analytics
"""

import json

import streamlit as st

from ui.components import (
    format_duration,
    status_badge,
    empty_state,
)

from database.dashboard_queries import (
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
    """
    Safely convert a value to text.
    """

    if value is None:
        return default

    return str(value)


def format_timestamp(seconds):
    """
    Convert seconds into MM:SS or HH:MM:SS.
    """

    if seconds is None:
        return "00:00"

    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "00:00"

    if seconds < 0:
        seconds = 0

    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


def format_date(value):
    """
    Format a PostgreSQL datetime safely.
    """

    if value is None:
        return "Date unavailable"

    try:
        return value.strftime(
            "%d %b %Y · %I:%M %p"
        )
    except AttributeError:
        return str(value)


def parse_full_analysis(value):
    """
    Parse full_analysis when PostgreSQL returns it as JSON text.
    """

    if value is None:
        return None

    if isinstance(value, dict):
        return value

    if isinstance(value, list):
        return value

    if isinstance(value, str):

        try:
            return json.loads(value)
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            return value

    return value


# ============================================================
# MAIN PAGE
# ============================================================

def show_meeting_detail(meeting_id):
    """
    Render a complete meeting detail page.
    """

    # --------------------------------------------------------
    # Validate meeting ID
    # --------------------------------------------------------

    if meeting_id is None:

        st.warning(
            "No meeting has been selected."
        )

        if st.button(
            "← Back to Meetings",
            key="missing_meeting_back",
        ):

            st.session_state.page = "Meetings"
            st.rerun()

        return

    # --------------------------------------------------------
    # Load meeting
    # --------------------------------------------------------

    try:

        meeting = get_meeting(
            meeting_id
        )

    except Exception as e:

        st.error(
            "Unable to load this meeting."
        )

        with st.expander(
            "Technical error"
        ):
            st.exception(e)

        return

    if meeting is None:

        st.error(
            f"Meeting #{meeting_id} was not found."
        )

        if st.button(
            "← Back to Meetings",
            key="not_found_back",
        ):

            st.session_state.page = "Meetings"
            st.rerun()

        return

    # --------------------------------------------------------
    # Load transcript
    # --------------------------------------------------------

    transcript = None

    try:

        transcript = get_transcript(
            meeting_id
        )

    except Exception:

        transcript = None

    # --------------------------------------------------------
    # Load analysis
    # --------------------------------------------------------

    analysis = None

    if transcript:

        try:

            analysis = get_analysis(
                transcript["id"]
            )

        except Exception:

            analysis = None

    # --------------------------------------------------------
    # Load speaker segments
    # --------------------------------------------------------

    speaker_segments = []

    if transcript:

        try:

            speaker_segments = (
                get_speaker_segments(
                    transcript["id"]
                )
                or []
            )

        except Exception:

            speaker_segments = []

    # --------------------------------------------------------
    # Load speaker analytics
    # --------------------------------------------------------

    speaker_analytics = []

    if transcript:

        try:

            speaker_analytics = (
                get_speaker_analytics(
                    transcript["id"]
                )
                or []
            )

        except Exception:

            speaker_analytics = []

    # --------------------------------------------------------
    # Load structured analysis
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Back button
    # --------------------------------------------------------

    if st.button(
        "← Back to Meetings",
        key="meeting_detail_back",
    ):

        st.session_state.page = "Meetings"
        st.rerun()

    st.write("")

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
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

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = meeting.get(
        "status",
        "unknown",
    )

    status_badge(
        status
    )

    st.write("")

    # ========================================================
    # OVERVIEW METRICS
    # ========================================================

    participant_count = len(
        speaker_analytics
    )

    if participant_count == 0 and speaker_segments:

        unique_speakers = set()

        for segment in speaker_segments:

            speaker = segment.get(
                "speaker"
            )

            if speaker:
                unique_speakers.add(
                    speaker
                )

        participant_count = len(
            unique_speakers
        )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(
            "Duration",
            format_duration(
                meeting.get(
                    "duration_seconds",
                    0,
                )
            )
        )

    with col2:

        st.metric(
            "Participants",
            participant_count,
        )

    with col3:

        st.metric(
            "Transcript",
            "Available"
            if transcript
            else "Unavailable",
        )

    with col4:

        st.metric(
            "AI Analysis",
            "Available"
            if analysis
            else "Unavailable",
        )

    st.divider()

    # ========================================================
    # TABS
    # ========================================================

    transcript_tab, analysis_tab, participants_tab = st.tabs(
        [
            "📝 Transcript",
            "🧠 AI Analysis",
            "👥 Participants",
        ]
    )

    # ========================================================
    # TRANSCRIPT TAB
    # ========================================================

    with transcript_tab:

        st.subheader(
            "Discussion Transcript"
        )

        if not transcript:

            empty_state(
                "Transcript unavailable",
                "No transcript has been generated for this meeting.",
            )

        else:

            transcript_text = safe_text(
                transcript.get(
                    "transcript_text"
                )
            )

            # ------------------------------------------------
            # Speaker-attributed transcript
            # ------------------------------------------------

            if speaker_segments:

                st.caption(
                    f"{len(speaker_segments)} speaker segments"
                )

                for index, segment in enumerate(
                    speaker_segments
                ):

                    speaker = safe_text(
                        segment.get(
                            "speaker",
                            "Unknown Speaker",
                        ),
                        "Unknown Speaker",
                    )

                    start = format_timestamp(
                        segment.get(
                            "start"
                        )
                    )

                    end = format_timestamp(
                        segment.get(
                            "end"
                        )
                    )

                    text = safe_text(
                        segment.get(
                            "text"
                        ),
                        "[No text]",
                    )

                    with st.container(
                        border=True
                    ):

                        col1, col2 = st.columns(
                            [4, 1]
                        )

                        with col1:

                            st.markdown(
                                f"**{speaker}**"
                            )

                        with col2:

                            st.caption(
                                f"{start} → {end}"
                            )

                        st.write(
                            text
                        )

            elif transcript_text:

                # ------------------------------------------------
                # Plain transcript fallback
                # ------------------------------------------------

                st.text_area(
                    "Transcript",
                    value=transcript_text,
                    height=550,
                    disabled=True,
                    label_visibility="collapsed",
                )

            else:

                empty_state(
                    "Transcript is empty",
                    "The transcript record exists, but no transcript text was found.",
                )

    # ========================================================
    # AI ANALYSIS TAB
    # ========================================================

    with analysis_tab:

        st.subheader(
            "AI Discussion Intelligence"
        )

        if not analysis:

            empty_state(
                "AI analysis unavailable",
                "This meeting does not have a completed AI analysis yet.",
            )

        else:

            # ------------------------------------------------
            # Summary
            # ------------------------------------------------

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

            # ------------------------------------------------
            # Sentiment
            # ------------------------------------------------

            st.markdown(
                "### Sentiment"
            )

            sentiment = safe_text(
                analysis.get(
                    "sentiment",
                    "Unknown",
                ),
                "Unknown",
            )

            sentiment_score = analysis.get(
                "sentiment_score"
            )

            if sentiment_score is not None:

                try:

                    sentiment_score_text = (
                        f"{float(sentiment_score):.2f}"
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    sentiment_score_text = str(
                        sentiment_score
                    )

            else:

                sentiment_score_text = "—"

            col1, col2 = st.columns(
                2
            )

            with col1:

                st.metric(
                    "Overall Sentiment",
                    sentiment.title(),
                )

            with col2:

                st.metric(
                    "Sentiment Score",
                    sentiment_score_text,
                )

            # ------------------------------------------------
            # Themes
            # ------------------------------------------------

            if themes:

                st.markdown(
                    "### Key Themes"
                )

                theme_names = []

                for theme in themes:

                    theme_name = safe_text(
                        theme.get(
                            "theme"
                        )
                    )

                    if theme_name:

                        theme_names.append(
                            theme_name
                        )

                if theme_names:

                    columns = st.columns(
                        min(
                            len(theme_names),
                            4
                        )
                    )

                    for index, theme_name in enumerate(
                        theme_names
                    ):

                        with columns[
                            index % len(columns)
                        ]:

                            st.info(
                                f"🏷️ {theme_name}"
                            )

            # ------------------------------------------------
            # Key Points
            # ------------------------------------------------

            if key_points:

                st.markdown(
                    "### Key Discussion Points"
                )

                for point in key_points:

                    point_text = safe_text(
                        point.get(
                            "point"
                        )
                    )

                    if point_text:

                        st.markdown(
                            f"• {point_text}"
                        )

            # ------------------------------------------------
            # Decisions
            # ------------------------------------------------

            if decisions:

                st.markdown(
                    "### Decisions"
                )

                for decision in decisions:

                    decision_text = safe_text(
                        decision.get(
                            "decision"
                        )
                    )

                    speaker = safe_text(
                        decision.get(
                            "speaker"
                        )
                    )

                    if decision_text:

                        if speaker:

                            st.success(
                                f"✓ {decision_text}\n\n"
                                f"Decision by: {speaker}"
                            )

                        else:

                            st.success(
                                f"✓ {decision_text}"
                            )

            # ------------------------------------------------
            # Action Items
            # ------------------------------------------------

            if action_items:

                st.markdown(
                    "### Action Items"
                )

                for action in action_items:

                    task = safe_text(
                        action.get(
                            "task"
                        )
                    )

                    speaker = safe_text(
                        action.get(
                            "speaker"
                        )
                    )

                    priority = safe_text(
                        action.get(
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

                            st.checkbox(
                                f"{task}  —  "
                                f"{' · '.join(details)}",
                                value=False,
                                key=(
                                    f"action_"
                                    f"{meeting_id}_"
                                    f"{action.get('id', task)}"
                                ),
                            )

                        else:

                            st.checkbox(
                                task,
                                value=False,
                                key=(
                                    f"action_"
                                    f"{meeting_id}_"
                                    f"{action.get('id', task)}"
                                ),
                            )

            # ------------------------------------------------
            # Unresolved Issues
            # ------------------------------------------------

            if unresolved_issues:

                st.markdown(
                    "### Unresolved Issues"
                )

                for issue in unresolved_issues:

                    issue_text = safe_text(
                        issue.get(
                            "issue"
                        )
                    )

                    if issue_text:

                        st.warning(
                            f"⚠️ {issue_text}"
                        )

            # ------------------------------------------------
            # Raw structured analysis
            # ------------------------------------------------

            full_analysis = parse_full_analysis(
                analysis.get(
                    "full_analysis"
                )
            )

            if full_analysis:

                st.markdown(
                    "### Detailed AI Output"
                )

                with st.expander(
                    "View full analysis"
                ):

                    if isinstance(
                        full_analysis,
                        (dict, list),
                    ):

                        st.json(
                            full_analysis
                        )

                    else:

                        st.write(
                            full_analysis
                        )

    # ========================================================
    # PARTICIPANTS TAB
    # ========================================================

    with participants_tab:

        st.subheader(
            "Participant Insights"
        )

        if not speaker_analytics:

            if speaker_segments:

                st.info(
                    "Speaker-labelled transcript is available, "
                    "but speaker analytics have not been calculated."
                )

            else:

                empty_state(
                    "No participant data",
                    "Speaker information is not available for this meeting.",
                )

        else:

            total_words = sum(
                int(
                    speaker.get(
                        "word_count",
                        0
                    )
                    or 0
                )
                for speaker in speaker_analytics
            )

            total_segments = sum(
                int(
                    speaker.get(
                        "segment_count",
                        0
                    )
                    or 0
                )
                for speaker in speaker_analytics
            )

            col1, col2, col3 = st.columns(
                3
            )

            with col1:

                st.metric(
                    "Participants",
                    len(
                        speaker_analytics
                    )
                )

            with col2:

                st.metric(
                    "Total Words",
                    f"{total_words:,}"
                )

            with col3:

                st.metric(
                    "Speaking Segments",
                    f"{total_segments:,}"
                )

            st.divider()

            st.markdown(
                "### Speaking Contribution"
            )

            for speaker in speaker_analytics:

                speaker_name = safe_text(
                    speaker.get(
                        "speaker",
                        "Unknown",
                    ),
                    "Unknown",
                )

                speaking_time = float(
                    speaker.get(
                        "speaking_time_seconds",
                        0,
                    )
                    or 0
                )

                participation = float(
                    speaker.get(
                        "participation_percentage",
                        0,
                    )
                    or 0
                )

                word_count = int(
                    speaker.get(
                        "word_count",
                        0,
                    )
                    or 0
                )

                segment_count = int(
                    speaker.get(
                        "segment_count",
                        0,
                    )
                    or 0
                )

                st.markdown(
                    f"**{speaker_name}**"
                )

                col1, col2 = st.columns(
                    [5, 1]
                )

                with col1:

                    st.progress(
                        min(
                            max(
                                participation / 100,
                                0,
                            ),
                            1,
                        )
                    )

                with col2:

                    st.markdown(
                        f"**{participation:.1f}%**"
                    )

                st.caption(
                    f"Speaking time: "
                    f"{format_duration(speaking_time)} · "
                    f"{word_count:,} words · "
                    f"{segment_count} segments"
                )

                st.write("")

            # ------------------------------------------------
            # Table
            # ------------------------------------------------

            st.markdown(
                "### Participation Details"
            )

            table_rows = []

            for speaker in speaker_analytics:

                table_rows.append(
                    {
                        "Speaker": speaker.get(
                            "speaker",
                            "Unknown",
                        ),
                        "Speaking Time": format_duration(
                            speaker.get(
                                "speaking_time_seconds",
                                0,
                            )
                        ),
                        "Segments": speaker.get(
                            "segment_count",
                            0,
                        ),
                        "Words": speaker.get(
                            "word_count",
                            0,
                        ),
                        "Participation": (
                            f"{float(
                                speaker.get(
                                    'participation_percentage',
                                    0,
                                )
                                or 0
                            ):.1f}%"
                        ),
                    }
                )

            if table_rows:

                st.dataframe(
                    table_rows,
                    use_container_width=True,
                    hide_index=True,
                )