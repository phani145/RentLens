"""
RentLens AI - Reusable UI Cards and Metric Indicators.
Constructs consistent, classic professional real-estate cards and hazard displays.
"""

import streamlit as st
from utils.models import HazardItem, RiskLevel


def render_section_header(title: str, subtitle: str = "", icon: str = ""):
    """Renders a standard clean section header with optional icon and subtitle."""
    icon_html = f"<span style='margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid #E2E8F0;">
            <h1 style="margin: 0; font-size: 1.85rem; font-weight: 700; color: #0F172A; display: flex; align-items: center;">
                {icon_html}{title}
            </h1>
            {f'<p style="margin: 0.35rem 0 0 0; color: #475569; font-size: 0.95rem;">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_card(label: str, value: str, subtext: str = "", badge: str = "", badge_type: str = "neutral"):
    """Renders an executive KPI metric box."""
    badge_html = ""
    if badge:
        badge_class = f"rl-badge-{badge_type}"
        badge_html = f"<span class='rl-badge {badge_class}' style='margin-left: auto;'>{badge}</span>"

    st.markdown(
        f"""
        <div class="rl-kpi-container">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span class="rl-kpi-label">{label}</span>
                {badge_html}
            </div>
            <div class="rl-kpi-value">{value}</div>
            {f'<div class="rl-kpi-subtext">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_hazard_card(hazard: HazardItem, index: int = 1):
    """Renders a detailed, color-coded safety hazard card."""
    risk_badges = {
        RiskLevel.LOW: ("Low Risk", "low"),
        RiskLevel.MEDIUM: ("Medium Risk", "medium"),
        RiskLevel.HIGH: ("High Risk", "high"),
        RiskLevel.CRITICAL: ("Critical Hazard", "high"),
        RiskLevel.NONE: ("Informational", "neutral"),
    }
    badge_label, badge_class = risk_badges.get(hazard.risk_level, ("Notice", "neutral"))

    st.markdown(
        f"""
        <div class="rl-card" style="border-left: 4px solid {'#B91C1C' if hazard.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else ('#D97706' if hazard.risk_level == RiskLevel.MEDIUM else '#15803D')};">
            <div class="rl-card-header">
                <div>
                    <span style="font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">Issue #{index} • {hazard.category}</span>
                    <h3 style="margin: 0.2rem 0 0 0; font-size: 1.15rem; color: #0F172A;">{hazard.title}</h3>
                </div>
                <div>
                    <span class="rl-badge rl-badge-{badge_class}">{badge_label}</span>
                </div>
            </div>
            
            <div style="margin-bottom: 0.75rem;">
                <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.3rem;">
                    <b>Visible Location:</b> <span style="color: #0F172A;">{hazard.location_in_image}</span>
                </div>
                <div style="font-size: 0.9rem; color: #1E293B; line-height: 1.5;">
                    {hazard.description}
                </div>
            </div>

            <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.75rem 1rem; margin-top: 0.75rem;">
                <div style="font-size: 0.82rem; font-weight: 600; color: #1F4E46; margin-bottom: 0.2rem;">
                    Recommended Tenant Action ({hazard.urgency}):
                </div>
                <div style="font-size: 0.88rem; color: #0F172A;">
                    {hazard.tenant_recommendation}
                </div>
                <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.35rem;">
                    <i>Potential Impact: {hazard.potential_consequences}</i>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_gauge(overall_risk: RiskLevel):
    """Renders a visual indicator for overall property risk score."""
    risk_colors = {
        RiskLevel.LOW: ("#15803D", "#F0FDF4", "LOW OVERALL RISK", "The property demonstrates standard maintenance with no major structural or immediate life safety violations."),
        RiskLevel.MEDIUM: ("#B45309", "#FFFBEB", "MODERATE RISK IDENTIFIED", "Issues requiring landlord repair were detected. Demand repair commitments in writing prior to signing."),
        RiskLevel.HIGH: ("#B91C1C", "#FEF2F2", "SIGNIFICANT SAFETY CONCERN", "Severe or urgent habitability hazards identified. Do not sign or move in until certified remediation occurs."),
        RiskLevel.CRITICAL: ("#991B1B", "#FEF2F2", "CRITICAL DEFECT DETECTED", "Immediate life-safety or structural hazard observed. Consult local tenant rights agency or housing inspector."),
        RiskLevel.NONE: ("#1F4E46", "#F1F5F9", "CLEAR / NO HAZARDS DETECTED", "Surfaces in provided photos appear intact and well-kept.")
    }
    color, bg, title, desc = risk_colors.get(overall_risk, risk_colors[RiskLevel.LOW])

    st.markdown(
        f"""
        <div style="background-color: {bg}; border: 1.5px solid {color}; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: flex-start; gap: 1rem;">
            <div style="background-color: {color}; color: white; width: 42px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0;">
                {'✓' if overall_risk == RiskLevel.LOW or overall_risk == RiskLevel.NONE else ('⚠️' if overall_risk == RiskLevel.MEDIUM else '⛔')}
            </div>
            <div>
                <div style="color: {color}; font-weight: 700; font-size: 1rem; letter-spacing: 0.03em;">{title}</div>
                <div style="color: #334155; font-size: 0.9rem; margin-top: 0.25rem; line-height: 1.45;">{desc}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
