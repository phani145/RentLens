"""
RentLens AI – AI-Powered Rental Safety Inspector.
Main application orchestrator and routing hub.
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="RentLens AI – Rental Safety Inspector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Classic Professional Real-Estate Styling
from components.styling import apply_custom_styling
apply_custom_styling()

# Import Views and Components
from components.sidebar import render_sidebar
from views.dashboard_view import render_dashboard
from views.inspection_view import render_inspection_page
from views.report_view import render_report_page
from views.lease_view import render_lease_page
from views.checklist_view import render_checklist_page
from views.about_view import render_about_page


def main():
    # Initialize core session state defaults
    if "ollama_host" not in st.session_state:
        st.session_state.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Render unified left sidebar and capture target page
    active_page = render_sidebar()

    # Route to Selected Page
    if active_page == "Dashboard":
        render_dashboard()
    elif active_page == "Property Inspection":
        render_inspection_page()
    elif active_page == "Safety Report":
        render_report_page()
    elif active_page == "Lease Review":
        render_lease_page()
    elif active_page == "Safety Checklist":
        render_checklist_page()
    elif active_page == "About & Disclaimer":
        render_about_page()
    else:
        render_dashboard()

    # Elegant subtle footer
    st.markdown(
        """
        <div class="rl-footer">
            <b>RentLens AI</b> — AI-Powered Rental Safety Inspector & Lease Audit Utility<br/>
            <span>Educational decision-support tool. Not certified home inspection or legal counsel.</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# Run main flow unconditionally
main()
