"""
Generates a realistic 3-page Standard Residential Lease Agreement PDF
for demonstration and testing of RentLens AI's Lease Review and RAG capabilities.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle

def build_sample_lease():
    out_dir = os.path.dirname(__file__)
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "sample_lease.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LeaseTitle",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor("#0F172A")
    )

    h1_style = ParagraphStyle(
        "H1Style",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1F4E46"),
        spaceBefore=12,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "LeaseBody",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    story = []

    # Title
    story.append(Paragraph("STANDARD RESIDENTIAL LEASE AGREEMENT", title_style))
    story.append(Paragraph("STATE OF RESIDENTIAL HOUSING — MUNICIPAL COMPLIANT FORM 2026", ParagraphStyle("Sub", fontName="Helvetica", fontSize=8, alignment=1, textColor=colors.HexColor("#64748B"))))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=14))

    # Parties
    story.append(Paragraph("1. PARTIES AND PREMISES", h1_style))
    story.append(Paragraph(
        "This Agreement is entered into on this 1st day of November, 2026, by and between <b>Apex Property Management LLC</b> ('Landlord') "
        "and <b>John Doe & Jane Doe</b> ('Tenant'). Landlord agrees to rent to Tenant the real property located at <b>742 Evergreen Terrace, Unit 3B, Springfield</b> ('Premises').",
        body_style
    ))

    # Term & Rent
    story.append(Paragraph("2. TERM AND RENT PAYMENTS", h1_style))
    story.append(Paragraph(
        "The lease term shall commence on December 1, 2026, and terminate on November 30, 2027. "
        "The monthly rent for the Premises is <b>$1,850.00 USD</b>, payable in advance on or before the 1st calendar day of each month. "
        "Rent paid after the 5th calendar day of the month shall be subject to a <b>late fee of $75.00</b> plus $10.00 per day thereafter until paid in full.",
        body_style
    ))

    # Security Deposit
    story.append(Paragraph("3. SECURITY DEPOSIT & CONDITIONS FOR RETURN", h1_style))
    story.append(Paragraph(
        "Tenant has deposited with Landlord the sum of <b>$2,775.00 (1.5 months' rent)</b> as a Security Deposit. "
        "The deposit shall be held in an escrow account. Within <b>twenty-one (21) days</b> after Tenant vacates the Premises, "
        "Landlord shall return the full deposit or provide an itemized written statement of deductions for unpaid rent, excessive cleaning, "
        "or repairs beyond reasonable wear and tear. Landlord may NOT deduct for preexisting documented property defects or ordinary degradation of paint and carpets.",
        body_style
    ))

    # Landlord Entry
    story.append(Paragraph("4. LANDLORD ACCESS AND RIGHT OF ENTRY", h1_style))
    story.append(Paragraph(
        "Landlord or Landlord's designated agents may enter the Premises for inspection, repairs, or showing to prospective buyers or tenants. "
        "Except in cases of genuine emergency (such as active fire or flooding), Landlord MUST provide Tenant with at least <b>twenty-four (24) hours' written notice</b> "
        "specifying the purpose and estimated time of entry. Entry must take place during standard business hours (8:00 AM to 6:00 PM Monday through Friday) unless Tenant explicitly consents otherwise.",
        body_style
    ))

    # Maintenance & Mold
    story.append(Paragraph("5. MAINTENANCE, REPAIRS, AND HABITABILITY DEFECTS", h1_style))
    story.append(Paragraph(
        "Landlord shall maintain in good working order all electrical systems, plumbing pipes, heating, ventilation, air conditioning, and sanitary installations. "
        "Landlord is strictly responsible for prompt remediation of active water leaks, broken locks, hot water outages, and any visible mold or fungal contamination reported by Tenant. "
        "Tenant must notify Landlord in writing of any defect within forty-eight (48) hours of discovery. "
        "Tenant is responsible for minor upkeep including replacing interior light bulbs, maintaining smoke detector batteries, and keeping the premises in sanitary order.",
        body_style
    ))

    # Pets
    story.append(Paragraph("6. PET POLICY AND RESTRICTIONS", h1_style))
    story.append(Paragraph(
        "Domestic cats and dogs under 40 lbs are permitted subject to prior written approval by Landlord, with a maximum of two (2) pets per unit. "
        "A one-time refundable pet deposit of <b>$350.00</b> and a monthly pet rent of <b>$35.00 per pet</b> shall apply. "
        "Documented service animals and emotional assistance animals are exempt from all pet fees and breed restrictions pursuant to the Fair Housing Act.",
        body_style
    ))

    # Early Termination
    story.append(Paragraph("7. EARLY TERMINATION AND SUBLETTING", h1_style))
    story.append(Paragraph(
        "Tenant may terminate this Agreement prior to the expiration date by providing sixty (60) days' written notice and paying an early termination fee equivalent to one (1) month's rent ($1,850.00). "
        "Subletting or assignment of the lease is permitted ONLY with Landlord's prior written consent, which consent shall not be unreasonably withheld. "
        "Active duty military personnel may terminate the lease without penalty upon presentation of official military relocation orders.",
        body_style
    ))

    # Alterations & Fire Safety
    story.append(Paragraph("8. ALTERATIONS, LOCKS, AND SMOKE DETECTORS", h1_style))
    story.append(Paragraph(
        "Tenant shall not alter the premises, drill into structural columns, or paint walls without prior written authorization. "
        "Tenant shall not alter or add deadbolts without immediately providing Landlord with a duplicate key. "
        "Landlord has installed certified smoke alarms and carbon monoxide detectors as required by municipal safety codes. "
        "Tenant shall test alarms monthly and notify Landlord immediately if any detector unit is non-functional or missing.",
        body_style
    ))

    # Signatures
    story.append(Spacer(1, 14))
    sig_data = [
        [
            Paragraph("<b>LANDLORD / AGENT:</b><br/><br/>___________________________<br/>Apex Property Management LLC<br/>Date: 11/01/2026", body_style),
            Paragraph("<b>TENANT(S):</b><br/><br/>___________________________<br/>John Doe & Jane Doe<br/>Date: 11/01/2026", body_style),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    story.append(sig_table)

    doc.build(story)
    print("Generated sample lease PDF at:", pdf_path)

if __name__ == "__main__":
    build_sample_lease()
