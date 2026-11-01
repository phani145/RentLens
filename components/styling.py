"""
RentLens AI - Classic Professional Styling & Custom CSS.
Implements the warm off-white, dark navy, and muted forest-green/teal aesthetic
designed for a prestigious real-estate inspection dashboard.
"""

import streamlit as st


def apply_custom_styling():
    """Injects custom CSS adhering strictly to the classic, professional real-estate design."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Global Root Variables */
    :root {
        --rl-bg: #F8F9F8;
        --rl-card-bg: #FFFFFF;
        --rl-text-main: #0F172A;
        --rl-text-muted: #475569;
        --rl-accent-forest: #1F4E46;
        --rl-accent-teal: #0D5C58;
        --rl-accent-light: #EBF3F1;
        --rl-border: #E2E8F0;
        --rl-border-hover: #CBD5E1;
        --rl-shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
        --rl-shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
    }

    /* Overall App Background & Typography */
    .stApp {
        background-color: var(--rl-bg) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--rl-text-main) !important;
    }

    /* Main container max width & padding */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1200px !important;
    }

    /* Headings */
    h1, h2, h3 {
        color: var(--rl-text-main) !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em;
    }

    h1 {
        font-size: 2.1rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.5rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        border-bottom: 1px solid var(--rl-border);
        padding-bottom: 0.4rem;
    }

    h3 {
        font-size: 1.2rem !important;
        margin-top: 1rem !important;
    }

    p, span, label, li {
        color: var(--rl-text-main);
        font-size: 0.95rem;
        line-height: 1.55;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F1F4F3 !important;
        border-right: 1px solid var(--rl-border) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Custom Cards */
    .rl-card {
        background: var(--rl-card-bg);
        border: 1px solid var(--rl-border);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: var(--rl-shadow-sm);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .rl-card:hover {
        border-color: var(--rl-border-hover);
        box-shadow: var(--rl-shadow-md);
    }

    .rl-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 0.6rem;
    }

    .rl-card-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--rl-text-main);
        margin: 0;
    }

    /* Metric Badges */
    .rl-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .rl-badge-low {
        background-color: #F0FDF4;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }

    .rl-badge-medium {
        background-color: #FFFBEB;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    .rl-badge-high {
        background-color: #FEF2F2;
        color: #B91C1C;
        border: 1px solid #FECACA;
    }

    .rl-badge-neutral {
        background-color: #F1F5F9;
        color: #475569;
        border: 1px solid #E2E8F0;
    }

    /* KPI Stat Widget */
    .rl-kpi-container {
        background: #FFFFFF;
        border: 1px solid var(--rl-border);
        border-radius: 8px;
        padding: 1.15rem 1.25rem;
        box-shadow: var(--rl-shadow-sm);
        display: flex;
        flex-direction: column;
    }

    .rl-kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--rl-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }

    .rl-kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: var(--rl-text-main);
        line-height: 1.2;
    }

    .rl-kpi-subtext {
        font-size: 0.78rem;
        color: var(--rl-text-muted);
        margin-top: 0.4rem;
    }

    /* Primary and Secondary Streamlit Buttons */
    div.stButton > button:first-child {
        background-color: var(--rl-accent-forest) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--rl-accent-forest) !important;
        border-radius: 6px !important;
        padding: 0.55rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.15s ease-in-out !important;
    }

    div.stButton > button:first-child:hover {
        background-color: #173B35 !important;
        border-color: #173B35 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    /* Secondary action buttons */
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: var(--rl-text-main) !important;
        border: 1px solid var(--rl-border) !important;
    }

    button[kind="secondary"]:hover {
        background-color: #F8FAFC !important;
        border-color: var(--rl-border-hover) !important;
    }

    /* Download Buttons */
    div.stDownloadButton > button {
        background-color: var(--rl-accent-teal) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--rl-accent-teal) !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    div.stDownloadButton > button:hover {
        background-color: #094744 !important;
        border-color: #094744 !important;
    }

    /* Streamlit Status / Alert Banners */
    div[data-testid="stAlert"] {
        border-radius: 6px !important;
        border: 1px solid var(--rl-border) !important;
        padding: 0.85rem 1.15rem !important;
    }

    /* Citation Quotes in RAG */
    .rl-citation-box {
        background: #F8FAFC;
        border-left: 3px solid var(--rl-accent-forest);
        padding: 0.85rem 1.1rem;
        margin: 0.75rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.88rem;
    }

    .rl-citation-title {
        font-weight: 600;
        color: var(--rl-accent-forest);
        font-size: 0.82rem;
        margin-bottom: 0.35rem;
    }

    /* Checklist Item Box */
    .rl-checklist-box {
        background: #FFFFFF;
        border: 1px solid var(--rl-border);
        border-radius: 6px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
    }

    /* Footer styling */
    .rl-footer {
        text-align: center;
        padding-top: 2rem;
        margin-top: 3rem;
        border-top: 1px solid var(--rl-border);
        color: var(--rl-text-muted);
        font-size: 0.82rem;
    }

    /* Hide default Streamlit Hamburger & Footer safely */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
