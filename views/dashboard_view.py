"""
RentLens AI - Dashboard View.
Executive landing page featuring welcome section, key metrics,
quick actions, recent inspection logs, and educational renter guides.
"""

import streamlit as st
from datetime import datetime
from components.cards import render_section_header, render_kpi_card
from utils.storage import load_inspection_history
from utils.models import RiskLevel


def render_dashboard():
    """Renders the executive real-estate safety dashboard."""
    # Welcome & Hero Banner
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 2rem 2.25rem; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem;">
                <div style="max-width: 680px;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #1F4E46; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.4rem;">
                        Residential Safety & Lease Intelligence
                    </div>
                    <h1 style="margin: 0 0 0.75rem 0; font-size: 2.2rem; color: #0F172A; line-height: 1.2;">
                        Inspect Properties. Audit Leases. Rent Confidently.
                    </h1>
                    <p style="color: #475569; font-size: 1.05rem; line-height: 1.6; margin: 0;">
                        RentLens AI leverages local vision intelligence to detect water damage, mold, pest hazards, and structural defects before you sign, alongside grounded lease RAG analysis to uncover hidden clauses and tenant risks.
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.6rem; align-self: center;">
                    <div style="font-size: 0.78rem; color: #64748B; font-weight: 600; text-align: center;">Ready to evaluate a unit?</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Start Inspection Quick Actions
    col_btn1, col_btn2, col_btn3 = st.columns([1.3, 1.3, 1.4])
    with col_btn1:
        if st.button("📸 Start Property Inspection", use_container_width=True, type="primary"):
            st.session_state.current_page = "Property Inspection"
            st.rerun()
    with col_btn2:
        if st.button("📑 Review Lease Agreement", use_container_width=True):
            st.session_state.current_page = "Lease Review"
            st.rerun()
    with col_btn3:
        if st.button("✅ Pre-Move Checklist", use_container_width=True):
            st.session_state.current_page = "Safety Checklist"
            st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Load history data
    history = load_inspection_history()
    total_inspections = len(history)
    high_risk_count = sum(1 for h in history if str(h.get("overall_property_risk")).lower() in ["high", "critical"])
    medium_risk_count = sum(1 for h in history if str(h.get("overall_property_risk")).lower() == "medium")
    low_risk_count = total_inspections - high_risk_count - medium_risk_count

    # KPI Metric Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        render_kpi_card("Total Audits", str(total_inspections), "Saved local inspections", "Verified", "neutral")
    with kpi_col2:
        render_kpi_card("Low Risk Units", str(max(0, low_risk_count)), "Clear habitability signs", "Good", "low")
    with kpi_col3:
        render_kpi_card("Caution Flagged", str(medium_risk_count), "Repairs needed prior to signing", "Watch", "medium")
    with kpi_col4:
        render_kpi_card("High Risk Defects", str(high_risk_count), "Urgent habitability concerns", "Action", "high")

    st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)

    # Recent Inspections Section
    st.markdown("<h2>Recent Property Assessments</h2>", unsafe_allow_html=True)
    
    if not history:
        st.info("No inspection reports saved yet. Click 'Start Property Inspection' to upload photos of your prospective rental.")
    else:
        for idx, item in enumerate(history[:5]):
            prop_name = item.get("property_name", "Untitled Property")
            created_at = item.get("created_at", "Unknown Date")
            risk = item.get("overall_property_risk", "Low")
            images_count = item.get("images_evaluated_count", 0)
            hazards_list = item.get("all_hazards", [])
            summary = item.get("executive_summary", "Inspection completed.")

            badge_style = "low"
            if str(risk).lower() in ["high", "critical"]:
                badge_style = "high"
            elif str(risk).lower() == "medium":
                badge_style = "medium"

            with st.container():
                st.markdown(
                    f"""
                    <div class="rl-card" style="margin-bottom: 0.9rem;">
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                            <div>
                                <span style="font-size: 0.75rem; font-weight: 700; color: #64748B; text-transform: uppercase;">{item.get('report_id', 'RL-REPORT')} • {created_at}</span>
                                <div style="font-size: 1.15rem; font-weight: 600; color: #0F172A; margin-top: 0.15rem;">{prop_name}</div>
                            </div>
                            <span class="rl-badge rl-badge-{badge_style}">{risk} Risk</span>
                        </div>
                        <p style="color: #475569; font-size: 0.88rem; margin: 0.6rem 0; line-height: 1.45;">
                            {summary[:190]}{'...' if len(summary) > 190 else ''}
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8rem; color: #64748B; border-top: 1px solid #F1F5F9; padding-top: 0.5rem; margin-top: 0.5rem;">
                            <span>📁 {images_count} image(s) analyzed • {len(hazards_list)} hazard(s) flagged</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # Renter Educational Guidance
    st.markdown("<h2>Essential Rental Inspection Protocol</h2>", unsafe_allow_html=True)
    tip_col1, tip_col2, tip_col3 = st.columns(3)
    
    with tip_col1:
        st.markdown(
            """
            <div class="rl-card" style="height: 100%;">
                <div style="font-size: 1.25rem; margin-bottom: 0.4rem;">💧</div>
                <div style="font-weight: 600; font-size: 0.98rem; color: #0F172A; margin-bottom: 0.35rem;">Check Under Every Sink</div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.45;">
                    Look for bowed plywood, circular water staining, or musty smells under kitchen and bathroom vanities. Hidden leaks are the #1 cause of toxic mold.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tip_col2:
        st.markdown(
            """
            <div class="rl-card" style="height: 100%;">
                <div style="font-size: 1.25rem; margin-bottom: 0.4rem;">🔌</div>
                <div style="font-weight: 600; font-size: 0.98rem; color: #0F172A; margin-bottom: 0.35rem;">Test GFCI & Outlets</div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.45;">
                    Bathroom and countertop receptacles must have functional "Test" and "Reset" buttons. Watch for loose faceplates or warm wall surfaces.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with tip_col3:
        st.markdown(
            """
            <div class="rl-card" style="height: 100%;">
                <div style="font-size: 1.25rem; margin-bottom: 0.4rem;">📝</div>
                <div style="font-weight: 600; font-size: 0.98rem; color: #0F172A; margin-bottom: 0.35rem;">Demand Written Addenda</div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.45;">
                    Verbal promises by property managers to 'fix this before you move in' are legally unenforceable in most jurisdictions. Require it in writing.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
