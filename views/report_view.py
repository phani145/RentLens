"""
RentLens AI - Safety Report View.
Presents the executive inspection dossier with risk breakdown, hazard cards,
photo evidence, tenant recommendations, and downloadable PDF report.
"""

import streamlit as st
from components.cards import (
    render_section_header,
    render_hazard_card,
    render_risk_gauge,
    render_kpi_card
)
from utils.models import FullInspectionReport, RiskLevel
from utils.pdf_report import generate_inspection_pdf
from utils.storage import load_inspection_history


def render_report_page():
    """Renders the comprehensive safety assessment report."""
    render_section_header(
        title="Property Safety Inspection Report",
        subtitle="Formal condition summary, identified safety defects, tenant remediation steps, and PDF export.",
        icon="📋"
    )

    current_report: FullInspectionReport = st.session_state.get("current_report", None)
    history = load_inspection_history()

    # If no active report in session, allow selecting from past inspections or loading a demo
    if not current_report:
        st.info("No active inspection in current session. You can review a previous report below or start a new inspection.")
        if history:
            report_options = {
                f"{h.get('property_name')} ({h.get('report_id')} - {h.get('created_at')})": h
                for h in history
            }
            selected_key = st.selectbox("Select Past Report to View:", options=list(report_options.keys()))
            if selected_key:
                selected_data = report_options[selected_key]
                try:
                    current_report = FullInspectionReport(**selected_data)
                    st.session_state.current_report = current_report
                except Exception:
                    st.error("Could not parse selected historical record.")
        else:
            if st.button("🔍 Go to Property Inspection to Analyze Photos", type="primary"):
                st.session_state.current_page = "Property Inspection"
                st.rerun()
            return

    if not current_report:
        return

    # Top Action Bar with Download PDF and Re-run
    top_col1, top_col2 = st.columns([3, 1.2])
    with top_col1:
        st.markdown(
            f"""
            <div style="font-size: 0.85rem; color: #64748B;">
                <b>Report ID:</b> <span style="color: #0F172A; font-family: monospace;">{current_report.report_id}</span> • 
                <b>Evaluated:</b> {current_report.created_at} • 
                <b>Property:</b> <span style="color: #1F4E46; font-weight: 600;">{current_report.property_name}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with top_col2:
        # Generate PDF Bytes
        try:
            pdf_bytes = generate_inspection_pdf(current_report)
            safe_filename = f"RentLens_Report_{current_report.report_id}.pdf"
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name=safe_filename,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF creation error: {str(e)}")

    st.markdown("<hr style='margin: 1rem 0 1.5rem 0;' />", unsafe_allow_html=True)

    # 1. Overall Property Risk Banner
    render_risk_gauge(current_report.overall_property_risk)

    # 2. Executive KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Images Evaluated", str(current_report.images_evaluated_count), "Photographic angles", "Photos", "neutral")
    with c2:
        high_cnt = current_report.risk_breakdown.get("High", 0)
        render_kpi_card("High Risk Defects", str(high_cnt), "Requires repair before signing", "High", "high" if high_cnt > 0 else "neutral")
    with c3:
        med_cnt = current_report.risk_breakdown.get("Medium", 0)
        render_kpi_card("Moderate Items", str(med_cnt), "Document in addendum", "Watch", "medium" if med_cnt > 0 else "neutral")
    with c4:
        low_cnt = current_report.risk_breakdown.get("Low", 0)
        render_kpi_card("Minor Observations", str(low_cnt), "Routine cosmetic wear", "Low", "low")

    # 3. Executive Summary
    st.markdown("<h2>Executive Summary</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="rl-card">
            <p style="color: #1E293B; font-size: 0.95rem; line-height: 1.6; margin: 0;">
                {current_report.executive_summary}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. Filterable Hazard Catalog
    st.markdown(f"<h2>Cataloged Safety & Maintenance Hazards ({len(current_report.all_hazards)})</h2>", unsafe_allow_html=True)

    if not current_report.all_hazards:
        st.markdown(
            """
            <div class="rl-card" style="text-align: center; padding: 2rem;">
                <div style="font-size: 2rem; color: #15803D;">✓</div>
                <h3 style="color: #15803D; margin-top: 0.5rem;">No Detectable Hazards Found</h3>
                <p style="color: #64748B; margin-bottom: 0;">The inspected photographic frames did not show evidence of water intrusion, mold, or severe safety defects.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Category and Severity Filter
        f_col1, f_col2 = st.columns([1, 1])
        with f_col1:
            all_categories = ["All Categories"] + sorted(list({h.category for h in current_report.all_hazards}))
            sel_cat = st.selectbox("Filter by Category:", options=all_categories)
        with f_col2:
            sel_risk = st.selectbox("Filter by Risk Level:", options=["All Risk Levels", "High", "Medium", "Low"])

        filtered_hazards = current_report.all_hazards
        if sel_cat != "All Categories":
            filtered_hazards = [h for h in filtered_hazards if h.category == sel_cat]
        if sel_risk != "All Risk Levels":
            filtered_hazards = [h for h in filtered_hazards if h.risk_level.value.lower() == sel_risk.lower()]

        if not filtered_hazards:
            st.info("No hazards match the selected filter criteria.")
        else:
            for idx, h in enumerate(filtered_hazards, 1):
                render_hazard_card(h, index=idx)

    # 5. Photographic Evidence Gallery
    images_analyzed = st.session_state.get("last_analyzed_images", [])
    if images_analyzed:
        st.markdown("<h2>Photographic Evidence Reviewed</h2>", unsafe_allow_html=True)
        img_cols = st.columns(min(3, len(images_analyzed)))
        for idx, (img_file, meta) in enumerate(images_analyzed):
            with img_cols[idx % 3]:
                st.image(img_file, use_container_width=True, caption=f"Evidence Frame #{idx+1}: {meta['filename']}")

    # 6. Tenant Protection & Negotiation Advice
    st.markdown("<h2>Actionable Steps for Prospective Tenants</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="rl-card">
            <ol style="margin: 0; padding-left: 1.25rem; color: #1E293B; line-height: 1.65;">
                <li style="margin-bottom: 0.5rem;"><b>Present this Report to the Leasing Agent:</b> Send the generated PDF report via email so you have a timestamped written record of preexisting defects.</li>
                <li style="margin-bottom: 0.5rem;"><b>Require a Written Repair Addendum:</b> Never rely on verbal statements such as "our handyman will take care of that." Attach a signed addendum with specific completion deadlines.</li>
                <li style="margin-bottom: 0.5rem;"><b>Retain Original Timestamped Photos:</b> Store your upload photos securely to prevent deposit deductions when moving out in the future.</li>
                <li><b>Final Walkthrough Verification:</b> On key-handover day, re-inspect every flagged item before transferring the first month's rent.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 7. Inspection Scope & Limitations
    st.markdown("<h2>Scope & Legal Disclaimers</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 1.1rem 1.25rem; font-size: 0.8rem; color: #64748B; line-height: 1.5;">
            <b>IMPORTANT NOTICE:</b> {current_report.disclaimer}
        </div>
        """,
        unsafe_allow_html=True
    )
