"""
DiscussionIQ - Analytics View

Cross-meeting analytics dashboard.
"""

import streamlit as st
import pandas as pd

from ui.components import (
    format_duration,
    empty_state,
)

from database.dashboard_queries import (
    get_dashboard_stats,
    get_recent_meetings,
)


# ============================================================
# HELPERS
# ============================================================

def format_date(value):
    """
    Format database datetime safely.
    """

    if value is None:
        return "Unknown"

    try:
        return value.strftime(
            "%d %b %Y"
        )
    except AttributeError:
        return str(value)


# ============================================================
# MAIN PAGE
# ============================================================

def show_analytics():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "Analytics"
    )

    st.caption(
        "Cross-meeting discussion analytics and activity overview."
    )

    st.write("")

    # ========================================================
    # LOAD DATA
    # ========================================================

    try:

        stats = get_dashboard_stats()

        meetings = get_recent_meetings(
            limit=100
        )

    except Exception as e:

        st.error(
            "Unable to load analytics."
        )

        with st.expander(
            "Technical error details"
        ):

            st.exception(e)

        return

    # ========================================================
    # EMPTY STATE
    # ========================================================

    if not meetings:

        empty_state(
            "No analytics available",
            "Process some meetings first to build your discussion analytics.",
        )

        return

    # ========================================================
    # CALCULATE METRICS
    # ========================================================

    total_meetings = int(
        stats.get(
            "total_meetings",
            0
        )
        or 0
    )

    completed_meetings = int(
        stats.get(
            "completed_meetings",
            0
        )
        or 0
    )

    failed_meetings = int(
        stats.get(
            "failed_meetings",
            0
        )
        or 0
    )

    total_duration = float(
        stats.get(
            "total_duration",
            0
        )
        or 0
    )

    success_rate = (
        completed_meetings
        / total_meetings
        * 100
        if total_meetings > 0
        else 0
    )

    average_duration = (
        total_duration
        / completed_meetings
        if completed_meetings > 0
        else 0
    )

    # ========================================================
    # TOP KPI CARDS
    # ========================================================

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
            completed_meetings,
        )

    with col3:

        st.metric(
            "Avg. Duration",
            format_duration(
                average_duration
            ),
        )

    with col4:

        st.metric(
            "Success Rate",
            f"{success_rate:.0f}%",
        )

    st.write("")

    # ========================================================
    # SECONDARY METRICS
    # ========================================================

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Total Discussion Time",
            format_duration(
                total_duration
            ),
        )

    with col2:

        st.metric(
            "Failed Meetings",
            failed_meetings,
        )

    with col3:

        st.metric(
            "Analyzed Meetings",
            completed_meetings,
        )

    st.divider()

    # ========================================================
    # PREPARE DATAFRAME
    # ========================================================

    rows = []

    for meeting in meetings:

        duration = float(
            meeting.get(
                "duration_seconds",
                0
            )
            or 0
        )

        status = str(
            meeting.get(
                "status",
                "unknown"
            )
        ).lower()

        rows.append(
            {
                "id": meeting.get(
                    "id"
                ),
                "filename": meeting.get(
                    "filename",
                    "Untitled Meeting",
                ),
                "duration": duration,
                "duration_display": format_duration(
                    duration
                ),
                "status": status,
                "date": format_date(
                    meeting.get(
                        "created_at"
                    )
                ),
                "created_at": meeting.get(
                    "created_at"
                ),
            }
        )

    df = pd.DataFrame(
        rows
    )

    # ========================================================
    # DURATION ANALYSIS
    # ========================================================

    st.subheader(
        "Meeting Duration"
    )

    st.caption(
        "Compare the length of your recent discussions."
    )

    duration_df = df[
        [
            "filename",
            "duration",
        ]
    ].copy()

    duration_df = duration_df.rename(
        columns={
            "filename": "Meeting",
            "duration": "Duration (seconds)",
        }
    )

    if not duration_df.empty:

        chart_df = duration_df.set_index(
            "Meeting"
        )

        st.bar_chart(
            chart_df[
                "Duration (seconds)"
            ]
        )

    st.write("")

    # ========================================================
    # STATUS DISTRIBUTION
    # ========================================================

    col1, col2 = st.columns(
        2
    )

    with col1:

        st.subheader(
            "Meeting Status"
        )

        status_counts = (
            df["status"]
            .value_counts()
            .rename_axis(
                "Status"
            )
            .to_frame(
                "Meetings"
            )
        )

        if not status_counts.empty:

            st.bar_chart(
                status_counts
            )

    # ========================================================
    # STATUS SUMMARY
    # ========================================================

    with col2:

        st.subheader(
            "Status Summary"
        )

        status_display = {
            "completed": "Completed",
            "processing": "Processing",
            "failed": "Failed",
            "unknown": "Unknown",
        }

        for status, count in (
            df["status"]
            .value_counts()
            .items()
        ):

            label = status_display.get(
                status, # type: ignore
                str(status).title(),
            ) # type: ignore

            st.metric(
                label,
                int(count),
            )

    st.divider()

    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    st.subheader(
        "Recent Discussion Activity"
    )

    recent_df = df[
        [
            "filename",
            "duration_display",
            "status",
            "date",
        ]
    ].copy()

    recent_df.columns = [
        "Meeting",
        "Duration",
        "Status",
        "Date",
    ]

    recent_df["Status"] = (
        recent_df["Status"]
        .str.title()
    )

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )

    st.write("")

    # ========================================================
    # DISCUSSION STATISTICS
    # ========================================================

    st.subheader(
        "Discussion Statistics"
    )

    # --------------------------------------------------------
    # Longest meeting
    # --------------------------------------------------------

    longest_meeting = None

    if not df.empty:

        longest_index = df[
            "duration"
        ].idxmax()

        longest_meeting = df.loc[
            longest_index
        ]

    # --------------------------------------------------------
    # Shortest meeting
    # --------------------------------------------------------

    shortest_meeting = None

    if not df.empty:

        shortest_index = df[
            "duration"
        ].idxmin()

        shortest_meeting = df.loc[
            shortest_index
        ]

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.metric(
            "Average Duration",
            format_duration(
                average_duration
            ),
        )

    with col2:

        if longest_meeting is not None:

            st.metric(
                "Longest Discussion",
                format_duration(
                    longest_meeting[
                        "duration"
                    ]
                ),
            )

            st.caption(
                str(
                    longest_meeting[
                        "filename"
                    ]
                )
            )

        else:

            st.metric(
                "Longest Discussion",
                "—",
            )

    with col3:

        if shortest_meeting is not None:

            st.metric(
                "Shortest Discussion",
                format_duration(
                    shortest_meeting[
                        "duration"
                    ]
                ),
            )

            st.caption(
                str(
                    shortest_meeting[
                        "filename"
                    ]
                )
            )

        else:

            st.metric(
                "Shortest Discussion",
                "—",
            )

    st.divider()

    # ========================================================
    # EXPORT ANALYTICS
    # ========================================================

    st.subheader(
        "Export Analytics"
    )

    export_df = df[
        [
            "id",
            "filename",
            "duration_display",
            "status",
            "date",
        ]
    ].copy()

    export_df.columns = [
        "Meeting ID",
        "Meeting",
        "Duration",
        "Status",
        "Date",
    ]

    csv_data = export_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Analytics CSV",
        data=csv_data,
        file_name="discussioniq_analytics.csv",
        mime="text/csv",
        use_container_width=True,
        key="download_analytics_csv",
    )