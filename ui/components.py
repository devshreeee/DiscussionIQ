import streamlit as st


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(
    title,
    subtitle=None,
    action=None
):

    col1, col2 = st.columns(
        [5, 1]
    )

    with col1:

        st.title(title)

        if subtitle:

            st.caption(
                subtitle
            )

    with col2:

        if action:

            action()


# ============================================================
# STATUS BADGE
# ============================================================

def status_badge(
    status
):

    status = (
        status
        or "unknown"
    ).lower()

    if status == "completed":

        css_class = (
            "status-completed"
        )

        label = "Completed"

    elif status == "processing":

        css_class = (
            "status-processing"
        )

        label = "Processing"

    elif status == "failed":

        css_class = (
            "status-failed"
        )

        label = "Failed"

    else:

        css_class = (
            "status-processing"
        )

        label = status.title()

    st.markdown(
        f"""
        <span class="{css_class}">
            {label}
        </span>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# INSIGHT CARD
# ============================================================

def insight_card(
    title,
    content
):

    st.markdown(
        f"""
        <div class="dashboard-card">

            <div class="card-title">
                {title}
            </div>

            <div class="card-subtitle">
                {content}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# EMPTY STATE
# ============================================================

def empty_state(
    title,
    message
):

    st.markdown(
        f"""
        <div class="dashboard-card"
             style="text-align:center;">

            <div class="card-title">
                {title}
            </div>

            <div class="card-subtitle">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FORMAT DURATION
# ============================================================

def format_duration(
    seconds
):

    if seconds is None:

        return "—"

    seconds = int(
        seconds
    )

    hours = (
        seconds // 3600
    )

    minutes = (
        (seconds % 3600)
        // 60
    )

    remaining_seconds = (
        seconds % 60
    )

    if hours > 0:

        return (
            f"{hours}h "
            f"{minutes:02d}m"
        )

    return (
        f"{minutes}m "
        f"{remaining_seconds:02d}s"
    )


# ============================================================
# SPEAKER PARTICIPATION
# ============================================================

def speaker_participation(
    analytics
):

    if not analytics:

        empty_state(
            "No speaker data",
            "Speaker participation is not available."
        )

        return

    for speaker in analytics:

        name = speaker.get(
            "speaker",
            "Unknown"
        )

        percentage = float(
            speaker.get(
                "participation_percentage",
                0
            )
        )

        speaking_time = float(
            speaker.get(
                "speaking_time_seconds",
                0
            )
        )

        st.markdown(
            f"""
            <div class="speaker-row">

                <div>
                    <div class="speaker-name">
                        {name}
                    </div>

                    <div class="speaker-value">
                        {speaking_time:.1f}s speaking time
                    </div>
                </div>

                <div class="speaker-value">
                    {percentage:.1f}%
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.progress(
            min(
                percentage / 100,
                1.0
            )
        )

def section_header(title, subtitle=None):
    st.markdown(
        f"""
        <div style="margin-top:1.5rem;margin-bottom:0.9rem;">
            <div style="
                font-size:1.15rem;
                font-weight:700;
                color:#111827;
            ">
                {title}
            </div>

            {
                f'<div style="color:#6b7280;font-size:0.82rem;margin-top:0.2rem;">{subtitle}</div>'
                if subtitle else ""
            }
        </div>
        """,
        unsafe_allow_html=True
    )


def stat_card(label, value, description="", icon=""):
    st.markdown(
        f"""
        <div class="stat-card">

            <div class="stat-icon">
                {icon}
            </div>

            <div class="stat-label">
                {label}
            </div>

            <div class="stat-value">
                {value}
            </div>

            <div class="stat-description">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def transcript_segment(
    speaker,
    start,
    end,
    text
):
    st.markdown(
        f"""
        <div class="transcript-segment">

            <div class="transcript-meta">

                <span class="transcript-speaker">
                    {speaker}
                </span>

                <span class="transcript-time">
                    {start} → {end}
                </span>

            </div>

            <div class="transcript-text">
                {text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def tag(text):
    st.markdown(
        f"""
        <span class="analysis-tag">
            {text}
        </span>
        """,
        unsafe_allow_html=True
    )


def action_item_card(
    task,
    speaker=None,
    priority=None,
    status=None
):

    priority_html = ""

    if priority:
        priority_html = f"""
        <span class="priority-tag">
            {priority}
        </span>
        """

    speaker_html = (
        f"<span>👤 {speaker}</span>"
        if speaker else ""
    )

    status_html = (
        f"<span>• {status}</span>"
        if status else ""
    )

    st.markdown(
        f"""
        <div class="action-item">

            <div style="font-weight:600;">
                {task}
            </div>

            <div style="
                display:flex;
                gap:0.7rem;
                margin-top:0.5rem;
                color:#6b7280;
                font-size:0.78rem;
            ">

                {speaker_html}
                {status_html}
                {priority_html}

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )