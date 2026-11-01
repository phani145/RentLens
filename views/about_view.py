"""
RentLens AI - About & Legal Disclaimer View.
Documents the technical architecture, local-first privacy principles,
system limitations, and mandatory legal disclaimers.
"""

import streamlit as st
from components.cards import render_section_header


def render_about_page():
    """Renders project documentation, technical stack, and legal disclaimers."""
    render_section_header(
        title="About RentLens AI & Disclaimers",
        subtitle="Mission, local artificial intelligence architecture, privacy guarantees, and usage limitations.",
        icon="ℹ️"
    )

    # Project Goal
    st.markdown(
        """
        <div class="rl-card">
            <h3 style="margin-top: 0; color: #1F4E46;">Mission: Empowering Renters Before They Sign</h3>
            <p style="color: #1E293B; line-height: 1.6; margin-bottom: 0.5rem;">
                Signing a residential lease is among the most consequential financial and legal contracts an individual enters into. 
                Yet tenants routinely tour properties under time pressure, missing subtle signs of toxic mold, sub-floor water damage, 
                pest harborage, or ungrounded wiring. Simultaneously, 30+ page lease contracts often conceal aggressive penalty clauses, 
                unannounced entry terms, and unfair deposit forfeiture rules.
            </p>
            <p style="color: #1E293B; line-height: 1.6; margin: 0;">
                <b>RentLens AI</b> acts as a personal safety advisor and lease auditor—analyzing room photographs with vision models and 
                auditing contracts using Retrieval-Augmented Generation (RAG)—so renters can spot red flags, negotiate amendments, 
                and protect their deposit.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Technical Architecture
    st.markdown("<h2>System Architecture & Tech Stack</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            <div class="rl-card" style="height: 100%;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">👁️ Vision Hazard Detection</div>
                <ul style="color: #334155; font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                    <li><b>Model Runtime:</b> Ollama (Local daemon on <code>localhost:11434</code>)</li>
                    <li><b>Vision Engine:</b> <code>moondream</code>, <code>llama3.2-vision</code>, or <code>llava</code></li>
                    <li><b>Validation:</b> Pydantic schemas enforcing strict hazard classification, urgency, and confidence scoring.</li>
                    <li><b>Image Sanitation:</b> PIL verifying dimensions, formats (JPG/PNG), and byte integrity.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="rl-card" style="height: 100%;">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;">📑 Lease Document RAG Pipeline</div>
                <ul style="color: #334155; font-size: 0.9rem; line-height: 1.6; padding-left: 1.2rem;">
                    <li><b>Extraction:</b> PyMuPDF (fitz) extracting clean page-by-page text.</li>
                    <li><b>Chunking:</b> LangChain RecursiveCharacterTextSplitter preserving clause boundaries.</li>
                    <li><b>Vector Database:</b> ChromaDB with local persistent cosine vector space.</li>
                    <li><b>Grounded LLM:</b> Local Ollama (<code>gemma3:1b</code>, <code>llama3.2</code>) strictly citing exact lease pages.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Privacy Guarantee
    st.markdown("<h2>Privacy & Security Architecture</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background-color: #F0FDF4; border: 1.5px solid #86EFAC; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 700; color: #166534; font-size: 1rem; margin-bottom: 0.35rem;">
                🔒 100% Local Processing — Zero Cloud Transmission
            </div>
            <div style="color: #14532D; font-size: 0.9rem; line-height: 1.55;">
                Unlike cloud AI services, RentLens AI operates on local models. Your uploaded rental photos, personal lease documents, 
                and landlord names remain entirely inside your computer. No data is logged, shared, or sent to external servers.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Setup Guide for Renters
    st.markdown("<h2>Quick Setup & Installation Guide</h2>", unsafe_allow_html=True)
    with st.expander("🛠️ How to set up Ollama and required models on your machine", expanded=False):
        st.markdown(
            """
            ### Step 1: Install & Launch Ollama
            1. Download Ollama from [https://ollama.com/download](https://ollama.com/download)
            2. Start the Ollama application or run in your terminal:
               ```bash
               ollama serve
               ```

            ### Step 2: Pull Vision & Text Models
            In a terminal or command prompt:
            ```bash
            # Pull the fast, lightweight vision model (~1.7GB)
            ollama pull moondream

            # Or pull Llama 3.2 Vision (~7GB)
            ollama pull llama3.2-vision

            # Pull text model for lease RAG
            ollama pull gemma3:1b
            ```

            ### Step 3: Run RentLens AI
            ```bash
            streamlit run app.py
            ```
            """
        )

    # Official Disclaimers
    st.markdown("<h2>Mandatory Legal & Inspection Disclaimers</h2>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background-color: #FFFBEB; border: 1.5px solid #FCD34D; border-radius: 8px; padding: 1.25rem 1.5rem; color: #78350F; line-height: 1.6; font-size: 0.88rem;">
            <b>IMPORTANT NOTICE — NOT CERTIFIED INSPECTION OR LEGAL ADVICE:</b><br/>
            RentLens AI is an experimental educational decision-support tool powered by machine learning models. 
            <ol style="margin: 0.5rem 0 0.5rem 0; padding-left: 1.2rem;">
                <li><b>No Physical Structural or Mold Certification:</b> Visual photographic analysis cannot detect hidden wall cavity moisture, internal conduit electrical faults, hazardous materials (asbestos, lead paint, radon), or non-visible fungal spores. It does not replace a certified home inspector or municipal housing code officer.</li>
                <li><b>No Legal Representation:</b> Lease interpretations provided by RentLens AI are for informational orientation only and do not establish an attorney-client relationship. Landlord-tenant laws vary substantially across local jurisdictions. Always consult a licensed attorney or certified tenant union for binding legal matters.</li>
                <li><b>No Warranty of Accuracy:</b> While designed with grounded retrieval and Pydantic validation, generative models may omit nuanced contractual clauses or misinterpret ambiguous visual textures. The user assumes all responsibility for independently verifying property conditions.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
