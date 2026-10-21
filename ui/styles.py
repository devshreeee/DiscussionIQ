"""
DiscussionIQ UI Styles
=======================

Centralized styling for the DiscussionIQ Streamlit application.

This file contains:
- Global application styling
- Sidebar styling
- Dashboard cards
- Metric/stat cards
- Meeting cards
- Transcript styling
- AI analysis styling
- Participant analytics
- Action items
- Status badges
- Buttons
- Tabs
- Tables
- Upload area
- Responsive behavior

Usage:
    from ui.styles import load_css

    load_css()
"""

import streamlit as st


# ============================================================
# GLOBAL CSS
# ============================================================

CSS = r"""
<style>

/* ============================================================
   ROOT / GLOBAL APPLICATION
============================================================ */

:root {

    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --primary-light: #eef2ff;

    --success: #16a34a;
    --success-light: #dcfce7;

    --warning: #d97706;
    --warning-light: #fef3c7;

    --danger: #dc2626;
    --danger-light: #fee2e2;

    --text-primary: #111827;
    --text-secondary: #4b5563;
    --text-muted: #6b7280;
    --text-light: #9ca3af;

    --border: #e5e7eb;
    --border-light: #f1f5f9;

    --surface: #ffffff;
    --background: #f7f8fc;

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;

    --shadow-sm:
        0 2px 8px rgba(15, 23, 42, 0.04);

    --shadow-md:
        0 6px 18px rgba(15, 23, 42, 0.06);

    --shadow-lg:
        0 12px 30px rgba(15, 23, 42, 0.08);
}


/* Main application background */

.stApp {

    background: var(--background);

    color: var(--text-primary);
}


/* Main content width */

.block-container {

    max-width: 1400px;

    padding-top: 2rem;
    padding-bottom: 4rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}


/* Remove unnecessary top spacing */

.main .block-container {

    padding-top: 2rem;
}


/* ============================================================
   TYPOGRAPHY
============================================================ */

html,
body,
[class*="css"] {

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Helvetica,
        Arial,
        sans-serif;
}


h1,
h2,
h3,
h4,
h5,
h6 {

    color: var(--text-primary);

    letter-spacing: -0.025em;
}


h1 {

    font-size: 2.25rem !important;

    font-weight: 750 !important;

    line-height: 1.15 !important;

    margin-bottom: 0.4rem !important;
}


h2 {

    font-size: 1.55rem !important;

    font-weight: 700 !important;
}


h3 {

    font-size: 1.2rem !important;

    font-weight: 700 !important;
}


p {

    color: var(--text-secondary);

    line-height: 1.6;
}


/* ============================================================
   SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #111827 0%,
            #151b2b 100%
        );

    border-right: 1px solid rgba(255,255,255,0.05);
}


/* Sidebar content */

section[data-testid="stSidebar"] > div {

    padding-top: 1.2rem;
}


/* Sidebar text */

section[data-testid="stSidebar"] * {

    color: #f9fafb;
}


/* Sidebar captions */

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] small {

    color: #9ca3af !important;
}


/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton > button {

    background: transparent;

    color: #d1d5db;

    border: 1px solid transparent;

    border-radius: 10px;

    min-height: 42px;

    text-align: left;

    padding-left: 0.9rem;

    font-size: 0.9rem;

    font-weight: 550;

    transition:
        background 0.15s ease,
        color 0.15s ease;
}


section[data-testid="stSidebar"] .stButton > button:hover {

    background: rgba(255,255,255,0.08);

    color: white;

    border-color: rgba(255,255,255,0.08);
}


/* ============================================================
   SIDEBAR DIVIDER
============================================================ */

section[data-testid="stSidebar"] hr {

    border-color: rgba(255,255,255,0.08);
}


/* ============================================================
   BUTTONS
============================================================ */

.stButton > button {

    min-height: 42px;

    border-radius: 10px;

    border: 1px solid var(--border);

    background: white;

    color: var(--text-primary);

    font-weight: 600;

    font-size: 0.88rem;

    padding:
        0.55rem
        1rem;

    transition:
        all 0.15s ease;

    box-shadow: none;
}


.stButton > button:hover {

    border-color: #c7d2fe;

    color: var(--primary);

    background: #fafaff;

    box-shadow: var(--shadow-sm);
}


/* Primary button */

.stButton > button[kind="primary"] {

    background: var(--primary);

    border-color: var(--primary);

    color: white;

    font-weight: 650;

    box-shadow:
        0 4px 12px
        rgba(79, 70, 229, 0.18);
}


.stButton > button[kind="primary"]:hover {

    background: var(--primary-hover);

    border-color: var(--primary-hover);

    color: white;

    transform: translateY(-1px);

    box-shadow:
        0 6px 16px
        rgba(79, 70, 229, 0.22);
}


/* ============================================================
   METRIC COMPONENT
============================================================ */

[data-testid="stMetric"] {

    background: var(--surface);

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding:
        1.1rem
        1.25rem;

    box-shadow: var(--shadow-sm);
}


[data-testid="stMetricLabel"] {

    color: var(--text-muted) !important;

    font-size: 0.78rem !important;

    font-weight: 600 !important;
}


[data-testid="stMetricValue"] {

    color: var(--text-primary) !important;

    font-size: 1.65rem !important;

    font-weight: 750 !important;
}


[data-testid="stMetricDelta"] {

    font-size: 0.75rem !important;
}


/* ============================================================
   CUSTOM STAT CARDS
============================================================ */

.stat-card {

    position: relative;

    background: var(--surface);

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding: 1.25rem;

    min-height: 145px;

    box-shadow: var(--shadow-sm);

    transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        border-color 0.15s ease;
}


.stat-card:hover {

    transform: translateY(-2px);

    border-color: #dbeafe;

    box-shadow: var(--shadow-md);
}


.stat-icon {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 36px;

    height: 36px;

    border-radius: 10px;

    background: var(--primary-light);

    color: var(--primary);

    font-size: 1rem;

    margin-bottom: 0.8rem;
}


.stat-label {

    color: var(--text-muted);

    font-size: 0.76rem;

    font-weight: 600;

    margin-bottom: 0.2rem;
}


.stat-value {

    color: var(--text-primary);

    font-size: 1.75rem;

    font-weight: 750;

    letter-spacing: -0.025em;

    line-height: 1.2;
}


.stat-description {

    color: var(--text-light);

    font-size: 0.72rem;

    margin-top: 0.35rem;
}


/* ============================================================
   DASHBOARD CARD
============================================================ */

.dashboard-card {

    background: var(--surface);

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding: 1.25rem;

    box-shadow: var(--shadow-sm);

    transition:
        box-shadow 0.15s ease,
        border-color 0.15s ease;
}


.dashboard-card:hover {

    border-color: #dbeafe;

    box-shadow: var(--shadow-md);
}


.card-title {

    color: var(--text-primary);

    font-size: 1rem;

    font-weight: 700;

    margin-bottom: 0.35rem;
}


.card-subtitle {

    color: var(--text-muted);

    font-size: 0.82rem;

    line-height: 1.55;
}


/* ============================================================
   INFO BOX
============================================================ */

.info-box {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding: 1.25rem;

    margin-bottom: 1rem;

    box-shadow: var(--shadow-sm);
}


/* ============================================================
   MEETING HERO
============================================================ */

.meeting-hero {

    background:
        linear-gradient(
            135deg,
            #ffffff 0%,
            #fafaff 100%
        );

    border: 1px solid var(--border);

    border-radius: var(--radius-xl);

    padding: 1.6rem;

    margin-bottom: 1.25rem;

    box-shadow: var(--shadow-sm);
}


.meeting-hero h1 {

    margin-top: 0.25rem !important;

    margin-bottom: 0.35rem !important;
}


/* ============================================================
   MEETING ROW
============================================================ */

.meeting-row {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding: 1rem;

    margin-bottom: 0.65rem;

    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}


.meeting-row:hover {

    border-color: #c7d2fe;

    box-shadow: var(--shadow-sm);
}


/* ============================================================
   TRANSCRIPT
============================================================ */

.transcript-segment {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding:
        1rem
        1.15rem;

    margin-bottom: 0.65rem;

    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}


.transcript-segment:hover {

    border-color: #dbeafe;

    box-shadow: var(--shadow-sm);
}


.transcript-meta {

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 1rem;

    margin-bottom: 0.5rem;
}


.transcript-speaker {

    color: var(--text-primary);

    font-size: 0.84rem;

    font-weight: 700;
}


.transcript-time {

    color: var(--text-light);

    font-size: 0.72rem;

    white-space: nowrap;
}


.transcript-text {

    color: #374151;

    font-size: 0.9rem;

    line-height: 1.7;
}


/* ============================================================
   LEGACY TRANSCRIPT CLASSES
============================================================ */

.transcript-line {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding:
        0.9rem
        1rem;

    margin-bottom: 0.6rem;
}


.speaker-name {

    color: var(--text-primary);

    font-weight: 700;
}


.timestamp {

    color: var(--text-light);

    font-size: 0.72rem;

    margin-right: 0.65rem;
}


/* ============================================================
   AI ANALYSIS
============================================================ */

.analysis-summary {

    background:
        linear-gradient(
            135deg,
            #ffffff,
            #fafaff
        );

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding: 1.4rem;

    color: #374151;

    font-size: 0.92rem;

    line-height: 1.75;

    box-shadow: var(--shadow-sm);
}


/* ============================================================
   ANALYSIS TAGS
============================================================ */

.analysis-tag {

    display: inline-block;

    background: var(--primary-light);

    color: #4338ca;

    border: 1px solid #e0e7ff;

    padding:
        0.35rem
        0.7rem;

    border-radius: 999px;

    margin:
        0.2rem
        0.25rem
        0.2rem
        0;

    font-size: 0.75rem;

    font-weight: 650;
}


/* ============================================================
   THEMES
============================================================ */

.theme-card {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding: 1rem;

    min-height: 100px;

    box-shadow: var(--shadow-sm);
}


.theme-title {

    font-weight: 700;

    color: var(--text-primary);

    font-size: 0.88rem;
}


.theme-description {

    color: var(--text-muted);

    font-size: 0.76rem;

    margin-top: 0.35rem;

    line-height: 1.5;
}


/* ============================================================
   ACTION ITEMS
============================================================ */

.action-item {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding: 1rem;

    margin-bottom: 0.65rem;

    transition:
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}


.action-item:hover {

    border-color: #c7d2fe;

    box-shadow: var(--shadow-sm);
}


.priority-tag {

    display: inline-block;

    background: var(--warning-light);

    color: #92400e;

    padding:
        0.18rem
        0.5rem;

    border-radius: 6px;

    font-size: 0.68rem;

    font-weight: 650;
}


/* ============================================================
   DECISION CARD
============================================================ */

.decision-card {

    background: white;

    border: 1px solid var(--border);

    border-left: 4px solid var(--primary);

    border-radius: var(--radius-md);

    padding: 1rem;

    margin-bottom: 0.65rem;

    box-shadow: var(--shadow-sm);
}


/* ============================================================
   UNRESOLVED ISSUE
============================================================ */

.issue-card {

    background: #fffbeb;

    border: 1px solid #fde68a;

    border-left: 4px solid #f59e0b;

    border-radius: var(--radius-md);

    padding: 1rem;

    margin-bottom: 0.65rem;
}


/* ============================================================
   SPEAKER ANALYTICS
============================================================ */

.speaker-row {

    display: flex;

    align-items: center;

    justify-content: space-between;

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding:
        0.9rem
        1rem;

    margin-bottom: 0.4rem;
}


.speaker-name {

    color: var(--text-primary);

    font-size: 0.86rem;

    font-weight: 700;
}


.speaker-value {

    color: var(--text-muted);

    font-size: 0.75rem;
}


/* ============================================================
   PROGRESS BAR
============================================================ */

.stProgress > div > div > div {

    background: var(--primary);
}


.stProgress > div {

    background: #e5e7eb;

    border-radius: 999px;
}


.stProgress {

    margin-top: 0.25rem;

    margin-bottom: 0.8rem;
}


/* ============================================================
   STATUS BADGES
============================================================ */

.status-success {

    display: inline-flex;

    align-items: center;

    gap: 0.3rem;

    padding:
        0.3rem
        0.65rem;

    border-radius: 999px;

    background: var(--success-light);

    color: #166534;

    font-size: 0.7rem;

    font-weight: 650;
}


.status-processing {

    display: inline-flex;

    align-items: center;

    gap: 0.3rem;

    padding:
        0.3rem
        0.65rem;

    border-radius: 999px;

    background: var(--warning-light);

    color: #92400e;

    font-size: 0.7rem;

    font-weight: 650;
}


.status-failed {

    display: inline-flex;

    align-items: center;

    gap: 0.3rem;

    padding:
        0.3rem
        0.65rem;

    border-radius: 999px;

    background: var(--danger-light);

    color: #991b1b;

    font-size: 0.7rem;

    font-weight: 650;
}


/* ============================================================
   UPLOAD AREA
============================================================ */

[data-testid="stFileUploader"] {

    background: white;

    border: 2px dashed #d1d5db;

    border-radius: var(--radius-lg);

    padding: 0.5rem;

    transition:
        border-color 0.15s ease,
        background 0.15s ease;
}


[data-testid="stFileUploader"]:hover {

    border-color: #a5b4fc;

    background: #fafaff;
}


[data-testid="stFileUploaderDropzone"] {

    background: transparent !important;
}


/* ============================================================
   AUDIO PLAYER
============================================================ */

audio {

    width: 100%;

    border-radius: 10px;

    margin-top: 0.5rem;
}


/* ============================================================
   INPUTS
============================================================ */

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {

    border-radius: 10px;

    border-color: var(--border);

    background: white;
}


.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {

    border-color: #a5b4fc;

    box-shadow:
        0 0 0 1px #a5b4fc;
}


/* ============================================================
   CHECKBOX
============================================================ */

.stCheckbox {

    padding:
        0.35rem
        0;
}


.stCheckbox label {

    font-size: 0.85rem;
}


/* ============================================================
   TABS
============================================================ */

button[data-baseweb="tab"] {

    color: var(--text-muted);

    font-weight: 600;

    font-size: 0.84rem;

    padding:
        0.75rem
        1rem;
}


button[data-baseweb="tab"][aria-selected="true"] {

    color: var(--primary);
}


/* Tab underline */

div[data-baseweb="tab-highlight"] {

    background: var(--primary);
}


/* ============================================================
   EXPANDERS
============================================================ */

[data-testid="stExpander"] {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    overflow: hidden;
}


[data-testid="stExpander"] summary {

    font-weight: 650;
}


/* ============================================================
   DATAFRAME / TABLE
============================================================ */

[data-testid="stDataFrame"] {

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    overflow: hidden;

    box-shadow: var(--shadow-sm);
}


/* ============================================================
   ALERTS
============================================================ */

[data-testid="stAlert"] {

    border-radius: var(--radius-md);

    border-width: 1px;
}


/* ============================================================
   EMPTY STATE
============================================================ */

.empty-state {

    background: white;

    border: 1px dashed #d1d5db;

    border-radius: var(--radius-lg);

    padding:
        3rem
        2rem;

    text-align: center;

    margin-top: 1rem;
}


.empty-state-icon {

    font-size: 2.5rem;

    margin-bottom: 0.8rem;
}


.empty-state-title {

    color: var(--text-primary);

    font-size: 1rem;

    font-weight: 700;

    margin-bottom: 0.3rem;
}


.empty-state-message {

    color: var(--text-muted);

    font-size: 0.82rem;

    max-width: 500px;

    margin: auto;

    line-height: 1.6;
}


/* ============================================================
   DIVIDERS
============================================================ */

hr {

    border: none;

    border-top:
        1px solid var(--border);

    margin:
        1.2rem
        0;
}


/* ============================================================
   LINKS
============================================================ */

a {

    color: var(--primary);

    text-decoration: none;
}


a:hover {

    color: var(--primary-hover);

    text-decoration: underline;
}


/* ============================================================
   DOWNLOAD BUTTON
============================================================ */

.stDownloadButton > button {

    width: 100%;

    min-height: 42px;

    border-radius: 10px;

    border: 1px solid var(--border);

    background: white;

    color: var(--text-primary);

    font-weight: 600;

    transition:
        all 0.15s ease;
}


.stDownloadButton > button:hover {

    border-color: #a5b4fc;

    color: var(--primary);

    background: #fafaff;
}


/* ============================================================
   SPINNER
============================================================ */

.stSpinner > div {

    border-top-color: var(--primary) !important;
}


/* ============================================================
   TOAST
============================================================ */

[data-testid="stToast"] {

    border-radius: var(--radius-md);
}


/* ============================================================
   SCROLLBAR
============================================================ */

::-webkit-scrollbar {

    width: 7px;

    height: 7px;
}


::-webkit-scrollbar-track {

    background: #f1f5f9;
}


::-webkit-scrollbar-thumb {

    background: #cbd5e1;

    border-radius: 999px;
}


::-webkit-scrollbar-thumb:hover {

    background: #94a3b8;
}


/* ============================================================
   RESPONSIVE — TABLET
============================================================ */

@media (max-width: 1100px) {

    .block-container {

        padding-left: 1.5rem;

        padding-right: 1.5rem;
    }

}


/* ============================================================
   RESPONSIVE — MOBILE
============================================================ */

@media (max-width: 768px) {

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;

        padding-top: 1.25rem;
    }


    h1 {

        font-size: 1.8rem !important;
    }


    h2 {

        font-size: 1.35rem !important;
    }


    .stat-card {

        min-height: 125px;

        padding: 1rem;
    }


    .stat-value {

        font-size: 1.45rem;
    }


    .meeting-hero {

        padding: 1.15rem;
    }


    .transcript-meta {

        align-items: flex-start;

        flex-direction: column;

        gap: 0.2rem;
    }


    .transcript-text {

        font-size: 0.85rem;
    }


    .speaker-row {

        padding: 0.8rem;
    }

}


/* ============================================================
   REDUCE STREAMLIT DEFAULT SPACING
============================================================ */

.element-container {

    margin-bottom: 0.25rem;
}


/* ============================================================
   HIDE STREAMLIT BRANDING
============================================================ */

#MainMenu {

    visibility: hidden;
}


footer {

    visibility: hidden;
}


/* Keep sidebar collapse button visible */

button[kind="headerNoPadding"] {

    visibility: visible;
}


/* ============================================================
   CUSTOM PAGE HEADER
============================================================ */

.page-header {

    margin-bottom: 1.5rem;
}


.page-header-title {

    color: var(--text-primary);

    font-size: 2.1rem;

    font-weight: 750;

    letter-spacing: -0.03em;
}


.page-header-subtitle {

    color: var(--text-muted);

    font-size: 0.88rem;

    margin-top: 0.25rem;
}


/* ============================================================
   SEARCH BAR
============================================================ */

.search-container {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding: 0.4rem;

    margin-bottom: 1rem;
}


/* ============================================================
   REPORT CARD
============================================================ */

.report-card {

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-lg);

    padding: 1.25rem;

    box-shadow: var(--shadow-sm);

    min-height: 150px;
}


.report-card-icon {

    font-size: 1.5rem;

    margin-bottom: 0.7rem;
}


.report-card-title {

    color: var(--text-primary);

    font-weight: 700;

    font-size: 0.95rem;
}


.report-card-description {

    color: var(--text-muted);

    font-size: 0.78rem;

    line-height: 1.5;

    margin-top: 0.35rem;
}


/* ============================================================
   PROCESSING STEP
============================================================ */

.processing-step {

    display: flex;

    align-items: center;

    gap: 0.75rem;

    background: white;

    border: 1px solid var(--border);

    border-radius: var(--radius-md);

    padding: 0.8rem 1rem;

    margin-bottom: 0.5rem;
}


.processing-step-number {

    width: 28px;

    height: 28px;

    display: flex;

    align-items: center;

    justify-content: center;

    border-radius: 50%;

    background: var(--primary-light);

    color: var(--primary);

    font-size: 0.72rem;

    font-weight: 700;
}


.processing-step-text {

    color: var(--text-secondary);

    font-size: 0.82rem;
}


/* ============================================================
   SUCCESS STATE
============================================================ */

.success-card {

    background: var(--success-light);

    border: 1px solid #bbf7d0;

    border-radius: var(--radius-lg);

    padding: 1.25rem;
}


/* ============================================================
   WARNING STATE
============================================================ */

.warning-card {

    background: var(--warning-light);

    border: 1px solid #fde68a;

    border-radius: var(--radius-lg);

    padding: 1.25rem;
}


/* ============================================================
   ERROR STATE
============================================================ */

.error-card {

    background: var(--danger-light);

    border: 1px solid #fecaca;

    border-radius: var(--radius-lg);

    padding: 1.25rem;
}

</style>
"""


# ============================================================
# LOAD CSS
# ============================================================

def load_css():
    """
    Inject the complete DiscussionIQ CSS stylesheet
    into the Streamlit application.
    """

    st.markdown(
        CSS,
        unsafe_allow_html=True
    )