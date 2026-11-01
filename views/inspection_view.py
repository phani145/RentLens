"""
RentLens AI - Property Inspection View.
Allows renters to upload photographs, preview images, and trigger multimodal
Ollama vision analysis for mold, pests, water damage, and safety hazards.
"""

import time
import uuid
from datetime import datetime
import streamlit as st
from PIL import Image

from components.cards import render_section_header, render_hazard_card, render_risk_gauge
from utils.file_validator import validate_image_file
from utils.ollama_client import (
    analyze_property_image,
    check_ollama_connection,
    is_vision_capable_model,
    OllamaServiceException
)
from utils.models import (
    FullInspectionReport,
    ImageInspectionResult,
    RiskLevel
)
from utils.storage import save_inspection_to_history


def render_inspection_page():
    """Renders the Property Inspection upload, preview, and AI analysis page."""
    render_section_header(
        title="Property Visual Safety Inspection",
        subtitle="Upload photos of rooms, ceilings, plumbing, outlets, and corners to detect visible hazards before lease signing.",
        icon="🔍"
    )

    # Property Details Input
    prop_col1, prop_col2 = st.columns([2, 1])
    with prop_col1:
        property_name = st.text_input(
            "Property Name or Address",
            value=st.session_state.get("inspection_prop_name", "Prospective Rental Unit"),
            placeholder="e.g. 742 Evergreen Terrace, Apt 3B",
            help="Used to label and title your formal inspection report."
        )
        st.session_state.inspection_prop_name = property_name

    with prop_col2:
        inspection_date = st.date_input("Inspection Date", value=datetime.now())

    # Model Status Check & Instructions
    host = st.session_state.get("ollama_host", "http://localhost:11434")
    vision_model = st.session_state.get("selected_vision_model", "moondream")
    is_online, conn_msg, installed_models = check_ollama_connection(host)

    if not is_online:
        st.warning(
            f"""
            **Ollama is currently unreachable on `{host}`.**  
            To perform automated image inspections:
            1. Open your terminal and run `ollama serve` (or ensure the Ollama desktop app is running).
            2. Pull a vision model: `ollama pull moondream` or `ollama pull llama3.2-vision`.
            3. Refresh this page to connect.
            """
        )
    elif not is_vision_capable_model(vision_model):
        st.info(
            f"""
            ℹ️ Selected model **`{vision_model}`** may be text-only.  
            For optimal image inspection, we recommend **`moondream`** (`ollama pull moondream`) or **`llama3.2-vision`**.
            """
        )

    # Multi-Image File Uploader
    st.markdown("<h3 style='margin-top: 1.5rem;'>1. Upload Rental Property Photos</h3>", unsafe_allow_html=True)
    st.caption("Accepted formats: JPG, JPEG, PNG. Max size: 15MB per file. (Privacy: Files are processed locally and not stored externally).")

    uploaded_files = st.file_uploader(
        "Upload inspection photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    valid_images = []
    validation_errors = []

    if uploaded_files:
        # Validate each uploaded file
        for f in uploaded_files:
            is_valid, err_msg, meta = validate_image_file(f)
            if is_valid:
                valid_images.append((f, meta))
            else:
                validation_errors.append(err_msg)

        # Show any file validation errors gracefully
        if validation_errors:
            for err in validation_errors:
                st.error(f"⚠️ {err}")

        # Image Previews Grid
        if valid_images:
            st.markdown(f"<h3 style='margin-top: 1rem;'>2. Uploaded Photo Previews ({len(valid_images)} accepted)</h3>", unsafe_allow_html=True)
            
            # Responsive 3-column preview grid
            cols = st.columns(min(3, len(valid_images)))
            for idx, (img_file, meta) in enumerate(valid_images):
                col = cols[idx % 3]
                with col:
                    img = Image.open(img_file)
                    st.image(img, use_container_width=True, caption=f"{meta['filename']} ({meta['size_formatted']})")
                    st.caption(f"📐 Resolution: {meta['width']}×{meta['height']} px")

            # Analysis Action
            st.markdown("<hr style='margin: 1.5rem 0;' />", unsafe_allow_html=True)
            st.markdown("<h3>3. Execute AI Hazard Analysis</h3>", unsafe_allow_html=True)

            analyze_disabled = not is_online or len(valid_images) == 0

            if st.button("🚀 Run AI Property Safety Inspection", type="primary", disabled=analyze_disabled, use_container_width=True):
                progress_bar = st.progress(0, text="Initializing local vision model...")
                status_text = st.empty()

                all_image_results: list[ImageInspectionResult] = []
                aggregated_hazards = []
                start_time = time.time()

                for i, (img_file, meta) in enumerate(valid_images):
                    progress = int(((i + 0.5) / len(valid_images)) * 100)
                    progress_bar.progress(progress, text=f"Analyzing image {i+1} of {len(valid_images)}: {meta['filename']}...")
                    status_text.info(f"Scanning for visible water damage, mold, pest entry, and electrical defects in `{meta['filename']}` using `{vision_model}`...")

                    try:
                        img_bytes = img_file.getvalue()
                        result = analyze_property_image(
                            image_bytes=img_bytes,
                            filename=meta["filename"],
                            model_name=vision_model,
                            host=host
                        )
                        all_image_results.append(result)
                        aggregated_hazards.extend(result.hazards)
                    except OllamaServiceException as ose:
                        st.error(f"Inspection error on `{meta['filename']}`: {ose.message}")
                        st.info(f"Troubleshooting advice: {ose.advice}")
                        progress_bar.empty()
                        status_text.empty()
                        return
                    except Exception as ex:
                        st.error(f"Unexpected inspection failure on `{meta['filename']}`: {str(ex)}")
                        progress_bar.empty()
                        status_text.empty()
                        return

                progress_bar.progress(100, text="Finalizing safety assessment synthesis...")

                # Determine overall property risk
                highest_risk = RiskLevel.NONE
                if any(h.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] for h in aggregated_hazards):
                    highest_risk = RiskLevel.HIGH
                elif any(h.risk_level == RiskLevel.MEDIUM for h in aggregated_hazards):
                    highest_risk = RiskLevel.MEDIUM
                elif any(h.risk_level == RiskLevel.LOW for h in aggregated_hazards):
                    highest_risk = RiskLevel.LOW
                elif len(aggregated_hazards) == 0:
                    highest_risk = RiskLevel.LOW

                # Count risk breakdown
                risk_breakdown = {
                    "High": sum(1 for h in aggregated_hazards if h.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]),
                    "Medium": sum(1 for h in aggregated_hazards if h.risk_level == RiskLevel.MEDIUM),
                    "Low": sum(1 for h in aggregated_hazards if h.risk_level == RiskLevel.LOW),
                }

                # Construct synthesis summary
                elapsed = time.time() - start_time
                if highest_risk == RiskLevel.HIGH:
                    summary = (
                        f"Inspection completed across {len(valid_images)} photographs. "
                        f"Detected {len(aggregated_hazards)} issue(s), with severe concerns flagged that could impact tenant habitability. "
                        "Immediate professional remediation or formal landlord commitments should be secured before signing."
                    )
                elif highest_risk == RiskLevel.MEDIUM:
                    summary = (
                        f"Evaluated {len(valid_images)} photographs in {elapsed:.1f}s. "
                        f"Identified {len(aggregated_hazards)} moderate defect(s). Recommended repairs should be documented in an addendum before move-in."
                    )
                else:
                    summary = (
                        f"Evaluated {len(valid_images)} photographs in {elapsed:.1f}s. "
                        "No immediate hazardous conditions detected in the photographic frames. Standard cosmetic condition observed."
                    )

                # Assemble Full Report
                report = FullInspectionReport(
                    report_id=f"RL-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:4].upper()}",
                    property_name=property_name.strip() or "Prospective Rental Unit",
                    created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    images_evaluated_count=len(valid_images),
                    overall_property_risk=highest_risk,
                    executive_summary=summary,
                    all_hazards=aggregated_hazards,
                    risk_breakdown=risk_breakdown,
                    key_recommendations=[
                        "Document all noted items on the move-in condition inventory checklist.",
                        "Request formal written landlord remediation commitment for flagged items.",
                        "Retain original timestamped photographs as personal tenant records.",
                        "Check water pressure and electrical breaker box during the final walk-through."
                    ]
                )

                # Save report in session state and persistent history
                st.session_state.current_report = report
                st.session_state.last_analyzed_images = valid_images
                save_inspection_to_history(report)

                progress_bar.empty()
                status_text.empty()

                st.success("🎉 Property inspection completed successfully!")
                
                # Render results summary preview
                render_risk_gauge(report.overall_property_risk)

                col_view, col_pdf = st.columns([1, 1])
                with col_view:
                    if st.button("📋 View Complete Formal Safety Report", type="primary", use_container_width=True):
                        st.session_state.current_page = "Safety Report"
                        st.rerun()

    else:
        # Helpful guidance when no images are uploaded yet
        st.markdown(
            """
            <div class="rl-card" style="text-align: center; padding: 2.5rem 1.5rem; margin-top: 1.5rem;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📸</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #0F172A;">No Property Photos Uploaded Yet</h3>
                <p style="color: #64748B; max-width: 520px; margin: 0 auto 1.25rem auto;">
                    Use the upload area above to select photos from your device. RentLens AI will examine them for mold discoloration, leaks, pest traces, exposed wiring, and physical damage.
                </p>
                <div style="display: flex; justify-content: center; gap: 1.5rem; color: #475569; font-size: 0.85rem;">
                    <span>✓ Bathroom under-sink</span>
                    <span>✓ Ceiling corners</span>
                    <span>✓ Window frames</span>
                    <span>✓ Electrical receptacles</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
