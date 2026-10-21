import streamlit as st
import subprocess
import os
import re
import time
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DiscussionIQ",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #0b0f19;
        color: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white;
    }

    /* ---------- HEADER ---------- */

    .brand {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -1px;
        color: white;
    }

    .brand span {
        color: #7c3aed;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 15px;
        margin-top: -8px;
    }

    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #161d31 0%,
            #111827 55%,
            #1b1634 100%
        );

        border: 1px solid #293246;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
    }

    .hero-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-description {
        color: #a7b0c0;
        font-size: 16px;
        max-width: 850px;
        line-height: 1.6;
    }

    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: #111827;
        border: 1px solid #263044;
        border-radius: 16px;
        padding: 20px;
        min-height: 125px;
    }

    .metric-label {
        color: #8f9aae;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .metric-value {
        color: white;
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-sub {
        color: #6ee7b7;
        font-size: 12px;
        margin-top: 4px;
    }

    /* ---------- SECTION ---------- */

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: white;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    /* ---------- INSIGHT CARD ---------- */

    .insight-card {
        background: #111827;
        border: 1px solid #293246;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .insight-title {
        font-weight: 700;
        font-size: 15px;
        color: white;
        margin-bottom: 5px;
    }

    .insight-text {
        color: #aab2c1;
        font-size: 14px;
        line-height: 1.55;
    }

    /* ---------- UPLOAD ---------- */

    .upload-box {
        background: #111827;
        border: 1px dashed #4b5563;
        border-radius: 18px;
        padding: 25px;
        text-align: center;
    }

    /* ---------- STATUS ---------- */

    .status {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-ready {
        background: #064e3b;
        color: #6ee7b7;
    }

    .status-processing {
        background: #422006;
        color: #fcd34d;
    }

    /* ---------- TABS ---------- */

    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 44px;
    }

    /* ---------- DIVIDER ---------- */

    hr {
        border-color: #1f2937;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "analysis_complete": False,
    "transcript": "",
    "report": "",
    "uploaded_name": "",
    "processing": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def convert_to_wav(input_file, output_file):

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            input_file,
            "-ar",
            "16000",
            "-ac",
            "1",
            "-acodec",
            "pcm_s16le",
            output_file
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )


def run_pipeline(wav_file):

    steps = [
        (
            "Audio Processing",
            [
                "ffmpeg",
                "-y",
                "-i",
                wav_file,
                "-ar",
                "16000",
                "-ac",
                "1",
                "-acodec",
                "pcm_s16le",
                wav_file
            ]
        )
    ]


def count_speakers(transcript):

    speakers = set()

    pattern = r"(SPEAKER[_ ]?\d+)"

    matches = re.findall(
        pattern,
        transcript,
        re.IGNORECASE
    )

    for speaker in matches:
        speakers.add(speaker.upper())

    return len(speakers)


def count_words(text):

    return len(
        text.split()
    )


def extract_insights(report):

    insights = []

    lines = report.split("\n")

    for line in lines:

        clean = line.strip()

        if clean.startswith("-"):
            insights.append(
                clean[1:].strip()
            )

    return insights[:6]


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="brand">Discussion<span>IQ</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">AI-powered discussion intelligence</div>',
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "",
        [
            "🏠 Dashboard",
            "🎙️ Analyze Discussion",
            "📄 Transcript",
            "🧠 AI Insights"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### AI Pipeline")

    st.markdown("""
    **🎤 Whisper**  
    Speech-to-text

    **🗣️ PyAnnote**  
    Speaker diarization

    **🧠 Llama 3.2**  
    Qualitative analysis

    **🗄️ PostgreSQL**  
    Data storage
    """)

    st.divider()

    st.caption(
        "Capstone Project • Discussion Intelligence Platform"
    )


# ============================================================
# TOP HEADER
# ============================================================

st.markdown(
    """
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:25px;
    ">

        <div>
            <div class="brand">
                AI Discussion Analyzer
            </div>

            <div class="subtitle">
                Turn conversations into structured intelligence.
            </div>
        </div>

        <div class="status status-ready">
            ● SYSTEM READY
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Discussion Intelligence Dashboard
            </div>

            <div class="hero-description">
                Analyze meetings, group discussions and interviews
                using speech recognition, speaker identification and
                LLM-powered qualitative analysis.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Metrics

    col1, col2, col3, col4 = st.columns(4)

    speaker_count = count_speakers(
        st.session_state.transcript
    )

    word_count = count_words(
        st.session_state.transcript
    )

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Discussions Analyzed
                </div>

                <div class="metric-value">
                    {"1" if st.session_state.analysis_complete else "0"}
                </div>

                <div class="metric-sub">
                    Current session
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Speakers Detected
                </div>

                <div class="metric-value">
                    {speaker_count}
                </div>

                <div class="metric-sub">
                    Via speaker diarization
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Transcript Words
                </div>

                <div class="metric-value">
                    {word_count:,}
                </div>

                <div class="metric-sub">
                    Speech converted to text
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        status = (
            "Complete"
            if st.session_state.analysis_complete
            else "Waiting"
        )

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-label">
                    Analysis Status
                </div>

                <div class="metric-value">
                    {status}
                </div>

                <div class="metric-sub">
                    AI pipeline
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Quick action

    st.markdown(
        '<div class="section-title">Quick Start</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns([2, 1])

    with c1:

        st.markdown(
            """
            <div class="insight-card">

                <div class="insight-title">
                    🎙️ Analyze a new discussion
                </div>

                <div class="insight-text">
                    Upload an MP3, WAV, M4A or other supported
                    recording to generate a transcript and
                    AI-powered discussion report.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        if st.button(
            "Start New Analysis →",
            use_container_width=True
        ):

            st.session_state.analysis_complete = False

            st.session_state.transcript = ""

            st.session_state.report = ""

            st.rerun()

    # Existing results

    if st.session_state.analysis_complete:

        st.markdown(
            '<div class="section-title">Latest Analysis</div>',
            unsafe_allow_html=True
        )

        tab1, tab2 = st.tabs(
            [
                "📄 Transcript",
                "🧠 AI Insights"
            ]
        )

        with tab1:

            st.text_area(
                "Transcript",
                st.session_state.transcript,
                height=400,
                label_visibility="collapsed"
            )

        with tab2:

            insights = extract_insights(
                st.session_state.report
            )

            if insights:

                for insight in insights:

                    st.markdown(
                        f"""
                        <div class="insight-card">

                            <div class="insight-text">
                                💡 {insight}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            else:

                st.markdown(
                    st.session_state.report
                )


# ============================================================
# ANALYZE PAGE
# ============================================================

elif page == "🎙️ Analyze Discussion":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Analyze a Discussion
            </div>

            <div class="hero-description">
                Upload your recording and let the AI pipeline
                transform raw conversation into structured insights.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Drop your audio file here",
        type=[
            "wav",
            "mp3",
            "m4a",
            "aac",
            "flac",
            "ogg"
        ]
    )

    if uploaded_file:

        os.makedirs(
            "data/audio_files",
            exist_ok=True
        )

        extension = uploaded_file.name.split(
            "."
        )[-1].lower()

        original_file = (
            f"data/audio_files/uploaded_audio.{extension}"
        )

        wav_file = (
            "data/audio_files/current_meeting.wav"
        )

        with open(
            original_file,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        st.success(
            f"✓ {uploaded_file.name} uploaded successfully"
        )

        st.audio(
            uploaded_file
        )

        st.divider()

        if st.button(
            "🚀 Run AI Analysis",
            use_container_width=True,
            type="primary"
        ):

            try:

                st.session_state.processing = True

                progress = st.progress(0)

                status = st.empty()

                # -------------------------
                # STEP 1
                # -------------------------

                status.info(
                    "⚙️ Preparing and normalizing audio..."
                )

                convert_to_wav(
                    original_file,
                    wav_file
                )

                progress.progress(20)

                # -------------------------
                # STEP 2
                # -------------------------

                status.info(
                    "🎤 Transcribing conversation with Whisper..."
                )

                subprocess.run(
                    [
                        "python",
                        "src/whisper_transcription.py",
                        wav_file
                    ],
                    check=True
                )

                progress.progress(45)

                # -------------------------
                # STEP 3
                # -------------------------

                status.info(
                    "🗣️ Identifying speakers..."
                )

                subprocess.run(
                    [
                        "python",
                        "src/diarization.py",
                        wav_file
                    ],
                    check=True
                )

                progress.progress(65)

                # -------------------------
                # STEP 4
                # -------------------------

                status.info(
                    "🧩 Building speaker-aware transcript..."
                )

                subprocess.run(
                    [
                        "python",
                        "src/transcript_merger.py"
                    ],
                    check=True
                )

                progress.progress(80)

                # -------------------------
                # STEP 5
                # -------------------------

                status.info(
                    "🧠 Generating AI insights..."
                )

                subprocess.run(
                    [
                        "python",
                        "src/llm_analysis.py"
                    ],
                    check=True
                )

                progress.progress(100)

                # -------------------------
                # RESULTS
                # -------------------------

                with open(
                    "analysis/merged_transcript.txt",
                    "r",
                    encoding="utf-8"
                ) as file:

                    st.session_state.transcript = (
                        file.read()
                    )

                with open(
                    "analysis/llm_report.txt",
                    "r",
                    encoding="utf-8"
                ) as file:

                    st.session_state.report = (
                        file.read()
                    )

                st.session_state.analysis_complete = True

                st.session_state.processing = False

                status.success(
                    "✓ Analysis completed successfully!"
                )

                time.sleep(1)

                st.rerun()

            except Exception as e:

                st.session_state.processing = False

                st.error(
                    f"Pipeline failed: {str(e)}"
                )


# ============================================================
# TRANSCRIPT PAGE
# ============================================================

elif page == "📄 Transcript":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Conversation Transcript
            </div>

            <div class="hero-description">
                Speaker-aware transcript generated from the uploaded
                discussion recording.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Words",
                f"{count_words(st.session_state.transcript):,}"
            )

        with col2:

            st.metric(
                "Speakers",
                count_speakers(
                    st.session_state.transcript
                )
            )

        with col3:

            st.metric(
                "Status",
                "Processed"
            )

        st.divider()

        st.download_button(
            "⬇ Download Transcript",
            st.session_state.transcript,
            file_name="discussion_transcript.txt",
            use_container_width=True
        )

        st.text_area(
            "Transcript",
            st.session_state.transcript,
            height=700,
            label_visibility="collapsed"
        )

    else:

        st.info(
            "No transcript available yet. Upload and analyze a discussion first."
        )


# ============================================================
# AI INSIGHTS PAGE
# ============================================================

elif page == "🧠 AI Insights":

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                AI Discussion Insights
            </div>

            <div class="hero-description">
                LLM-generated qualitative analysis of the conversation,
                including themes, sentiment, key observations and
                discussion patterns.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.analysis_complete:

        insights = extract_insights(
            st.session_state.report
        )

        if insights:

            st.markdown(
                '<div class="section-title">Key Findings</div>',
                unsafe_allow_html=True
            )

            for i, insight in enumerate(
                insights,
                start=1
            ):

                st.markdown(
                    f"""
                    <div class="insight-card">

                        <div class="insight-title">
                            Insight {i}
                        </div>

                        <div class="insight-text">
                            {insight}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown(
            '<div class="section-title">Full AI Report</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            st.session_state.report
        )

        st.download_button(
            "⬇ Download AI Report",
            st.session_state.report,
            file_name="discussion_analysis.txt",
            use_container_width=True
        )

    else:

        st.info(
            "AI insights will appear here after the discussion is analyzed."
        )