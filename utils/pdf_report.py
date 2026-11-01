"""
RentLens AI - PDF Report Generator.
Generates an elegant, publication-quality Property Safety Inspection Report
matching the classic real-estate aesthetic (dark navy, muted forest-green, warm accents).
"""

import io
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.pdfgen import canvas

from utils.models import FullInspectionReport, RiskLevel


class NumberedCanvas(canvas.Canvas):
    """Adds a dynamic footer with page numbers (Page X of Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))  # Slate grey

        # Top subtle rule
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)

        # Footer
        self.line(40, 40, letter[0] - 40, 40)
        self.drawString(40, 28, "RentLens AI — Property Safety & Lease Intelligence Report (Confidential)")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 28, page_text)
        self.restoreState()


def get_risk_colors(risk: RiskLevel):
    """Maps RiskLevel to harmonious real-estate palette colors."""
    if risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        return colors.HexColor("#7F1D1D"), colors.HexColor("#FEF2F2")  # Deep Crimson, Rose Soft
    elif risk == RiskLevel.MEDIUM:
        return colors.HexColor("#92400E"), colors.HexColor("#FFFBEB")  # Ochre, Amber Soft
    elif risk == RiskLevel.LOW:
        return colors.HexColor("#14532D"), colors.HexColor("#F0FDF4")  # Forest Green, Mint Soft
    else:
        return colors.HexColor("#1E293B"), colors.HexColor("#F8FAFC")  # Navy, Slate Soft


def generate_inspection_pdf(report: FullInspectionReport) -> bytes:
    """
    Builds a PDF document from a FullInspectionReport.
    Returns bytes buffer ready for download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Typography
    primary_color = colors.HexColor("#0F172A")    # Deep Navy
    accent_green = colors.HexColor("#1F4E46")     # Muted Forest Teal
    text_muted = colors.HexColor("#475569")       # Slate
    border_color = colors.HexColor("#E2E8F0")     # Light border

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=text_muted
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=accent_green,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=primary_color
    )

    meta_label = ParagraphStyle(
        "MetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=text_muted
    )

    meta_val = ParagraphStyle(
        "MetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=primary_color
    )

    story = []

    # 1. Header & Title Block
    header_data = [
        [
            Paragraph("<b>RENTLENS AI</b> — PROPERTY SAFETY REPORT", title_style),
            Paragraph(f"<b>Report ID:</b> {report.report_id}<br/><b>Date:</b> {report.created_at}", meta_label)
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 170])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_green, spaceBefore=4, spaceAfter=12))

    # 2. Property Overview & Overall Risk Banner
    risk_fg, risk_bg = get_risk_colors(report.overall_property_risk)
    
    banner_data = [
        [
            Paragraph(f"<b>Property Assessed:</b> {report.property_name}", meta_val),
            Paragraph(f"<b>Overall Risk:</b> <font color='{risk_fg.hexval()}'><b>{report.overall_property_risk.value.upper()}</b></font>", ParagraphStyle("RiskBanner", parent=body_style, fontSize=11, fontName="Helvetica-Bold")),
            Paragraph(f"<b>Photos Analyzed:</b> {report.images_evaluated_count} file(s)", meta_val),
            Paragraph(f"<b>Hazards Flagged:</b> {len(report.all_hazards)} issue(s)", meta_val),
        ]
    ]
    banner_table = Table(banner_data, colWidths=[160, 120, 120, 130])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 12))

    # 3. Executive Summary
    story.append(Paragraph("EXECUTIVE SAFETY SUMMARY", section_heading))
    summary_text = report.executive_summary or (
        "Preliminary visual inspection performed by local vision AI. Hazards have been cataloged "
        "by severity and operational category. Prior to lease execution, all highlighted items "
        "should be presented to the landlord or verified in person."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # 4. Identified Safety Hazards Breakdown
    story.append(Paragraph(f"IDENTIFIED HAZARDS & DEFECTS ({len(report.all_hazards)})", section_heading))
    
    if not report.all_hazards:
        no_haz_p = Paragraph(
            "<b>No significant safety hazards were detected in the evaluated photographs.</b> "
            "Surfaces appeared reasonably intact in the visible frame.",
            body_style
        )
        story.append(no_haz_p)
    else:
        # Table of Hazards
        haz_rows = [
            [
                Paragraph("<b># / Category</b>", meta_label),
                Paragraph("<b>Hazard & Location</b>", meta_label),
                Paragraph("<b>Risk & Urgency</b>", meta_label),
                Paragraph("<b>Tenant Action Recommendation</b>", meta_label)
            ]
        ]

        for idx, h in enumerate(report.all_hazards, 1):
            h_fg, _ = get_risk_colors(h.risk_level)
            col0 = Paragraph(f"<b>#{idx}</b><br/>{h.category}", meta_val)
            col1 = Paragraph(f"<b>{h.title}</b><br/><font color='#64748B'>Location: {h.location_in_image}</font><br/>{h.description}", body_style)
            col2 = Paragraph(f"<font color='{h_fg.hexval()}'><b>{h.risk_level.value}</b></font><br/><font color='#64748B'>{h.urgency}</font>", meta_val)
            col3 = Paragraph(f"{h.tenant_recommendation}<br/><i>Impact: {h.potential_consequences}</i>", body_style)
            haz_rows.append([col0, col1, col2, col3])

        haz_table = Table(haz_rows, colWidths=[95, 175, 90, 170])
        haz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(haz_table)

    story.append(Spacer(1, 14))

    # 5. Key Tenant Recommendations & Pre-Move-In Steps
    recs = report.key_recommendations or [
        "Present this inspection summary to the landlord and obtain written confirmation of repairs.",
        "Include a formal condition addendum attached to the lease prior to signing or paying security deposit.",
        "Take high-resolution, timestamped photographs of all noted areas upon key exchange.",
        "Verify operational status of smoke alarms and carbon monoxide detectors on move-in day."
    ]
    story.append(Paragraph("RECOMMENDED TENANT ACTIONS", section_heading))
    for r in recs:
        story.append(Paragraph(f"• <b>{r}</b>", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 12))

    # 6. Limitations & Disclaimer Box
    story.append(Paragraph("INSPECTION SCOPE & DISCLAIMER", section_heading))
    disc_text = (
        "<b>LEGAL & TECHNICAL DISCLAIMER:</b> RentLens AI is an automated preliminary evaluation "
        "utility intended for informational decision-support only. This assessment is based exclusively "
        "on the visible photographic evidence submitted by the user. It cannot detect internal plumbing "
        "corrosion, structural framing defects behind drywall, non-visible airborne mold spores, or faulty "
        "in-wall electrical circuits. This report does not constitute a municipal building inspection, licensed "
        "home inspection, legal advice, or guarantee of habitability. RentLens AI and its operators accept no "
        "liability for conditions not detected in photographic material."
    )
    disc_table = Table([[Paragraph(disc_text, ParagraphStyle("Disc", parent=body_style, fontSize=7.5, leading=10, textColor=text_muted))]], colWidths=[530])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(disc_table)

    # Build PDF with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
