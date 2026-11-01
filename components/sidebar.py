"""
RentLens AI - Sidebar Component.
Provides brand identity, navigation controls, live Ollama connection status,
and model configuration selectors.
"""

import streamlit as st
from utils.ollama_client import check_ollama_connection, get_categorized_models

NAV_OPTIONS = [
    "Dashboard",
    "Property Inspection",
    "Safety Report",
    "Lease Review",
    "Safety Checklist",
    "About & Disclaimer"
]

NAV_ICONS = {
    "Dashboard": "🏛️",
    "Property Inspection": "🔍",
    "Safety Report": "📋",
    "Lease Review": "📑",
    "Safety Checklist": "✅",
    "About & Disclaimer": "ℹ️"
}


def render_sidebar() -> str:
    """
    Renders the unified left sidebar with brand logo, status indicator,
    model configuration, and page selector.
    Returns: selected page name
    """
    with st.sidebar:
        # Brand Header
        st.markdown(
            """
            <div style="padding-bottom: 1rem; border-bottom: 1px solid #CBD5E1; margin-bottom: 1.25rem;">
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <div style="background-color: #1F4E46; color: white; width: 34px; height: 34px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.1rem;">
                        RL
                    </div>
                    <div>
                        <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; line-height: 1.1;">RentLens AI</div>
                        <div style="font-size: 0.72rem; color: #475569; text-transform: uppercase; letter-spacing: 0.04em;">Rental Safety Inspector</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Navigation Selector
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;'>Navigation</p>", unsafe_allow_html=True)
        
        # Initialize session state for navigation
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        selected_page = st.radio(
            "Go to page",
            options=NAV_OPTIONS,
            format_func=lambda opt: f"{NAV_ICONS.get(opt, '•')} {opt}",
            index=NAV_OPTIONS.index(st.session_state.current_page) if st.session_state.current_page in NAV_OPTIONS else 0,
            label_visibility="collapsed",
            key="sidebar_nav_radio"
        )
        st.session_state.current_page = selected_page

        st.markdown("<hr style='margin: 1.5rem 0 1rem 0; border: none; border-top: 1px solid #CBD5E1;' />", unsafe_allow_html=True)

        # Local Ollama Connection Status & Configuration
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Local AI Engine</p>", unsafe_allow_html=True)
        
        host = st.session_state.get("ollama_host", "http://localhost:11434")
        is_online, conn_msg, installed_models = check_ollama_connection(host)

        if is_online:
            st.markdown(
                f"""
                <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="height: 8px; width: 8px; background-color: #16A34A; border-radius: 50%; display: inline-block;"></span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #166534;">Ollama Connected</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span style="height: 8px; width: 8px; background-color: #DC2626; border-radius: 50%; display: inline-block;"></span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: #991B1B;">Ollama Offline</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption("Start Ollama with `ollama serve` in your terminal.")

        # Model Selection
        model_data = get_categorized_models(host)
        all_models = model_data.get("all", [])
        vision_models = model_data.get("vision", [])
        text_models = model_data.get("text", [])

        # Vision Model Choice
        st.markdown("<span style='font-size: 0.8rem; font-weight: 600; color: #334155;'>Vision Model (Images)</span>", unsafe_allow_html=True)
        vision_options = vision_models if vision_models else (all_models if all_models else ["moondream", "llama3.2-vision", "llava"])
        
        default_vis_idx = 0
        if "moondream" in vision_options:
            default_vis_idx = vision_options.index("moondream")
        elif "llama3.2-vision" in vision_options:
            default_vis_idx = vision_options.index("llama3.2-vision")

        selected_vision_model = st.selectbox(
            "Select Vision Model",
            options=vision_options,
            index=default_vis_idx,
            label_visibility="collapsed",
            key="selected_vision_model"
        )

        # Lease Text Model Choice
        st.markdown("<span style='font-size: 0.8rem; font-weight: 600; color: #334155; margin-top: 0.4rem; display: block;'>Lease Model (RAG QA)</span>", unsafe_allow_html=True)
        text_options = text_models if text_models else (all_models if all_models else ["gemma3:1b", "llama3.2", "mistral"])
        
        default_text_idx = 0
        if "gemma3:1b" in text_options:
            default_text_idx = text_options.index("gemma3:1b")

        selected_text_model = st.selectbox(
            "Select Text Model",
            options=text_options,
            index=default_text_idx,
            label_visibility="collapsed",
            key="selected_text_model"
        )

        # Quick Inspection Counter
        st.markdown("<hr style='margin: 1.25rem 0 1rem 0; border: none; border-top: 1px solid #CBD5E1;' />", unsafe_allow_html=True)
        current_report = st.session_state.get("current_report", None)
        if current_report:
            st.markdown(
                f"""
                <div style="background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; padding: 0.75rem; font-size: 0.78rem;">
                    <div style="font-weight: 600; color: #1F4E46; margin-bottom: 0.25rem;">Active Assessment</div>
                    <div style="color: #0F172A; font-weight: 500;">{current_report.property_name[:20]}</div>
                    <div style="color: #64748B; margin-top: 0.2rem;">{len(current_report.all_hazards)} hazards cataloged</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Footer Notice
        st.markdown(
            """
            <div style="margin-top: 2rem; font-size: 0.7rem; color: #64748B; line-height: 1.4;">
                <b>Private & Local:</b> Images and documents are processed locally on your machine via Ollama.
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_page
