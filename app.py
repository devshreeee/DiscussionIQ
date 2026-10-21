"""
DiscussionIQ
============

Main Streamlit application.

Features:
- Dashboard
- New Analysis
- Meetings
- Meeting Detail
- Analytics
- Reports
- PostgreSQL
- Whisper
- PyAnnote
- Llama
"""

import os
import tempfile
from pathlib import Path

import streamlit as st

from ui.styles import load_css

from ui.components import (
    format_duration,
    status_badge,
    empty_state,
)

from database.dashboard_queries import (
    get_dashboard_stats,
    get_recent_meetings,
)

from pipeline.processor import (
    DiscussionProcessor,
)

from views.meeting_detail import (
    show_meeting_detail,
)

from views.analytics import (
    show_analytics,
)

from views.reports import (
    show_reports,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DiscussionIQ",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

load_css()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "selected_meeting" not in st.session_state:
    st.session_state.selected_meeting = None

if "processing" not in st.session_state:
    st.session_state.processing = False


# ============================================================
# NAVIGATION
# ============================================================

def navigate_to(page, meeting_id=None):

    st.session_state.page = page

    if meeting_id is not None:
        st.session_state.selected_meeting = meeting_id

    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🎙️ DiscussionIQ")

    st.caption(
        "AI-powered discussion intelligence"
    )

    st.divider()

    st.markdown("### Workspace")

    if st.button(
        "▣  Dashboard",
        use_container_width=True,
        key="nav_dashboard",
    ):
        navigate_to("Dashboard")

    if st.button(
        "＋  New Analysis",
        use_container_width=True,
        key="nav_new_analysis",
    ):
        navigate_to("New Analysis")

    if st.button(
        "◷  Meetings",
        use_container_width=True,
        key="nav_meetings",
    ):
        navigate_to("Meetings")

    if st.button(
        "◉  Analytics",
        use_container_width=True,
        key="nav_analytics",
    ):
        navigate_to("Analytics")

    if st.button(
        "▤  Reports",
        use_container_width=True,
        key="nav_reports",
    ):
        navigate_to("Reports")

    st.divider()

    st.markdown("### System")

    st.caption("● PostgreSQL")
    st.caption("● Whisper")
    st.caption("● PyAnnote")
    st.caption("● Ollama / Llama 3.2")

    st.divider()

    st.caption("DiscussionIQ")
    st.caption("Capstone Project")


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    try:

        stats = get_dashboard_stats()

        meetings = get_recent_meetings(
            limit=8
        )

    except Exception as e:

        st.error(
            "Unable to load dashboard data."
        )

        with st.expander(
            "Technical error details"
        ):
            st.exception(e)

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    col1, col2 = st.columns(
        [5, 1]
    )

    with col1:

        st.title(
            "Dashboard"
        )

        st.caption(
            "Your discussion intelligence overview"
        )

    with col2:

        if st.button(
            "＋ New Analysis",
            use_container_width=True,
            type="primary",
            key="dashboard_new_analysis",
        ):
            navigate_to(
                "New Analysis"
            )

    st.write("")

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total_meetings = stats.get(
        "total_meetings",
        0,
    )

    completed = stats.get(
        "completed_meetings",
        0,
    )

    total_duration = stats.get(
        "total_duration",
        0,
    )

    success_rate = (
        completed / total_meetings * 100
        if total_meetings
        else 0
    )

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(
            "Total Meetings",
            total_meetings,
        )

    with col2:

        st.metric(
            "Completed",
            completed,
        )

    with col3:

        st.metric(
            "Total Duration",
            format_duration(
                total_duration
            ),
        )

    with col4:

        st.metric(
            "Success Rate",
            f"{success_rate:.0f}%",
        )

    st.write("")

    # --------------------------------------------------------
    # RECENT DISCUSSIONS
    # --------------------------------------------------------

    st.subheader(
        "Recent Discussions"
    )

    st.caption(
        "Your latest processed meeting recordings"
    )

    if not meetings:

        empty_state(
            "No discussions yet",
            "Upload your first meeting recording to get started.",
        )

        return

    # --------------------------------------------------------
    # MEETINGS
    # --------------------------------------------------------

    for meeting in meetings:

        meeting_id = meeting.get(
            "id"
        )

        filename = meeting.get(
            "filename",
            "Untitled Meeting",
        )

        duration = meeting.get(
            "duration_seconds",
            0,
        )

        status = meeting.get(
            "status",
            "unknown",
        )

        created_at = meeting.get(
            "created_at"
        )

        if created_at:

            try:

                date_text = created_at.strftime(
                    "%d %b %Y · %I:%M %p"
                )

            except AttributeError:

                date_text = str(
                    created_at
                )

        else:

            date_text = "Date unavailable"

        with st.container():

            col1, col2, col3, col4 = st.columns(
                [4, 1.5, 1.5, 1]
            )

            with col1:

                st.markdown(
                    f"**{filename}**"
                )

                st.caption(
                    date_text
                )

            with col2:

                st.caption(
                    format_duration(
                        duration
                    )
                )

            with col3:

                status_badge(
                    status
                )

            with col4:

                if meeting_id is not None:

                    if st.button(
                        "Open",
                        key=(
                            f"dashboard_open_"
                            f"{meeting_id}"
                        ),
                    ):

                        navigate_to(
                            "Meeting",
                            meeting_id,
                        )

            st.divider()


# ============================================================
# NEW ANALYSIS
# ============================================================

def show_new_analysis():

    st.title(
        "New Analysis"
    )

    st.caption(
        "Upload a discussion recording and generate AI-powered insights."
    )

    st.write("")

    # --------------------------------------------------------
    # Upload instructions
    # --------------------------------------------------------

    st.info(
        "🎙️ Upload a discussion recording. "
        "Whisper will transcribe the audio, "
        "PyAnnote will identify speakers, "
        "and Llama will generate discussion insights."
    )

    # --------------------------------------------------------
    # File uploader
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Choose an audio file",

        type=[
            "wav",
            "mp3",
            "m4a",
            "aac",
            "flac",
            "ogg",
        ],

        help=(
            "Supported formats: WAV, MP3, M4A, "
            "AAC, FLAC and OGG."
        ),

        key="discussion_audio_uploader",
    )

    if uploaded_file is None:

        st.info(
            "Upload an audio recording to begin."
        )

        return

    # --------------------------------------------------------
    # File information
    # --------------------------------------------------------

    st.success(
        f"Ready to analyze: {uploaded_file.name}"
    )

    st.audio(
        uploaded_file
    )

    st.write("")

    file_size_mb = (
        uploaded_file.size
        / (1024 * 1024)
    )

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "File",
            uploaded_file.name,
        )

    with col2:

        st.metric(
            "Size",
            f"{file_size_mb:.2f} MB",
        )

    with col3:

        st.metric(
            "Format",
            uploaded_file.type or "Audio",
        )

    st.write("")

    # --------------------------------------------------------
    # Analyze
    # --------------------------------------------------------

    analyze = st.button(
        "🚀 Analyze Discussion",
        type="primary",
        use_container_width=True,
        key="start_discussion_analysis",
    )

    if not analyze:

        return

    temp_path = None

    try:

        st.session_state.processing = True

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        suffix = Path(
            uploaded_file.name
        ).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_file.write(
                uploaded_file.getbuffer()
            )

            temp_path = Path(
                temp_file.name
            )

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        st.subheader(
            "Processing Discussion"
        )

        st.caption(
            "Please keep this page open while processing."
        )

        progress_bar = st.progress(
            0
        )

        status_text = st.empty()

        progress_map = {
            "1/10": 0.10,
            "2/10": 0.20,
            "3/10": 0.30,
            "4/10": 0.40,
            "5/10": 0.50,
            "6/10": 0.60,
            "7/10": 0.70,
            "8/10": 0.80,
            "9/10": 0.90,
            "10/10": 1.00,
        }

        def update_progress(message):

            if message:

                message = str(
                    message
                )

                status_text.info(
                    message
                )

                for stage, value in progress_map.items():

                    if message.startswith(
                        stage
                    ):

                        progress_bar.progress(
                            value
                        )

                        break

        # ----------------------------------------------------
        # Processor
        # ----------------------------------------------------

        processor = DiscussionProcessor(
            whisper_model="base",
            llama_model="llama3.2",
            progress_callback=update_progress,
        )

        result = processor.process_meeting(
            temp_path
        )

        progress_bar.progress(
            1.0
        )

        status_text.success(
            "Analysis completed successfully."
        )

        st.session_state.processing = False

        # ----------------------------------------------------
        # Get meeting ID
        # ----------------------------------------------------

        meeting_id = None

        if hasattr(
            result,
            "meeting_id"
        ):

            meeting_id = result.meeting_id

        elif isinstance(
            result,
            dict
        ):

            meeting_id = (
                result.get(
                    "meeting_id"
                )
                or result.get(
                    "id"
                )
            )

        if meeting_id is None:

            st.warning(
                "Analysis completed, but no meeting ID was returned."
            )

            with st.expander(
                "Processing result"
            ):

                st.write(
                    result
                )

            return

        st.session_state.selected_meeting = (
            meeting_id
        )

        st.success(
            "Discussion analysis completed successfully!"
        )

        if st.button(
            "View Analysis →",
            type="primary",
            use_container_width=True,
            key="view_completed_analysis",
        ):

            st.session_state.selected_meeting = meeting_id
            st.session_state.page = "Meeting"

            st.rerun()

    except Exception as e:

        st.session_state.processing = False

        st.error(
            "Analysis failed."
        )

        with st.expander(
            "Technical error details"
        ):

            st.exception(
                e
            )

    finally:

        if temp_path is not None:

            try:

                os.unlink(
                    temp_path
                )

            except OSError:

                pass


# ============================================================
# MEETINGS
# ============================================================

def show_meetings():

    col1, col2 = st.columns(
        [5, 1]
    )

    with col1:

        st.title(
            "Meetings"
        )

        st.caption(
            "Browse and manage your processed discussions."
        )

    with col2:

        if st.button(
            "＋ New Analysis",
            use_container_width=True,
            type="primary",
            key="meetings_new_analysis",
        ):

            navigate_to(
                "New Analysis"
            )

    st.write("")

    try:

        meetings = get_recent_meetings(
            limit=100
        )

    except Exception as e:

        st.error(
            "Unable to load meetings."
        )

        with st.expander(
            "Technical error details"
        ):

            st.exception(e)

        return

    if not meetings:

        empty_state(
            "No meetings found",
            "Your analyzed discussions will appear here.",
        )

        return

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    col1, col2 = st.columns(
        [3, 1]
    )

    with col1:

        search = st.text_input(
            "Search meetings",
            placeholder="Search by filename...",
            key="meeting_search",
        )

    with col2:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "completed",
                "processing",
                "failed",
            ],
            key="meeting_status_filter",
        )

    filtered_meetings = []

    for meeting in meetings:

        filename = str(
            meeting.get(
                "filename",
                ""
            )
        )

        status = str(
            meeting.get(
                "status",
                ""
            )
        ).lower()

        if search:

            if search.lower() not in filename.lower():

                continue

        if status_filter != "All":

            if status != status_filter:

                continue

        filtered_meetings.append(
            meeting
        )

    st.caption(
        f"{len(filtered_meetings)} meeting(s)"
    )

    if not filtered_meetings:

        empty_state(
            "No matching meetings",
            "Try changing your search or status filter.",
        )

        return

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    for meeting in filtered_meetings:

        meeting_id = meeting.get(
            "id"
        )

        filename = meeting.get(
            "filename",
            "Untitled Meeting",
        )

        duration = meeting.get(
            "duration_seconds",
            0,
        )

        status = meeting.get(
            "status",
            "unknown",
        )

        created_at = meeting.get(
            "created_at"
        )

        if created_at:

            try:

                date_text = created_at.strftime(
                    "%d %b %Y · %I:%M %p"
                )

            except AttributeError:

                date_text = str(
                    created_at
                )

        else:

            date_text = "Date unavailable"

        col1, col2, col3, col4 = st.columns(
            [4, 1.5, 1.5, 1]
        )

        with col1:

            st.markdown(
                f"**{filename}**"
            )

            st.caption(
                date_text
            )

        with col2:

            st.caption(
                format_duration(
                    duration
                )
            )

        with col3:

            status_badge(
                status
            )

        with col4:

            if meeting_id is not None:

                if st.button(
            "View",
            key=f"view_meeting_{meeting_id}",
        ):

                    st.session_state.selected_meeting = meeting_id
            st.session_state.page = "Meeting"

            st.rerun()

        st.divider()


# ============================================================
# ROUTER
# ============================================================

if st.session_state.page == "Dashboard":

    show_dashboard()

elif st.session_state.page == "New Analysis":

    show_new_analysis()

elif st.session_state.page == "Meetings":

    show_meetings()

elif st.session_state.page == "Meeting":

    show_meeting_detail(
        st.session_state.selected_meeting
    )

elif st.session_state.page == "Analytics":

    show_analytics()

elif st.session_state.page == "Reports":

    show_reports()

else:

    st.session_state.page = "Dashboard"

    st.rerun()