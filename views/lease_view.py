"""
RentLens AI - Lease Document Review & RAG Q&A View.
Extracts PDF text using PyMuPDF, chunks with LangChain, vectors into ChromaDB,
and executes grounded tenant-advocate question answering with clause citations.
"""

import os
import streamlit as st
from components.cards import render_section_header, render_kpi_card
from utils.file_validator import validate_pdf_file
from utils.lease_rag import LeaseRAGEngine, SAMPLE_LEASE_QUESTIONS
from utils.ollama_client import (
    generate_rag_answer,
    check_ollama_connection,
    OllamaServiceException
)
from utils.models import LeaseQAResponse


def get_rag_engine() -> LeaseRAGEngine:
    """Initializes or retrieves singleton RAG engine in session state."""
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = LeaseRAGEngine()
    return st.session_state.rag_engine


def render_lease_page():
    """Renders the Lease Review and Document RAG workspace."""
    render_section_header(
        title="Lease Document Review & Intelligence",
        subtitle="Upload your lease PDF to identify disadvantageous terms, hidden penalties, deposit rules, and repair duties.",
        icon="📑"
    )

    host = st.session_state.get("ollama_host", "http://localhost:11434")
    text_model = st.session_state.get("selected_text_model", "gemma3:1b")
    is_online, conn_msg, installed_models = check_ollama_connection(host)

    if not is_online:
        st.warning(
            f"""
            **Ollama is currently unreachable on `{host}`.**  
            To perform automated lease clause question answering, start Ollama with `ollama serve`.
            """
        )

    # Document Source Selection: Upload PDF or Use Built-in Sample Lease
    tab_upload, tab_sample = st.tabs(["📤 Upload My Lease PDF", "📄 Test with Sample Lease"])

    rag_engine = get_rag_engine()
    pdf_bytes_to_process = None
    doc_filename = None

    with tab_upload:
        uploaded_pdf = st.file_uploader(
            "Upload Residential Lease Agreement (.pdf)",
            type=["pdf"],
            help="Files are processed strictly locally in your machine's memory."
        )
        if uploaded_pdf:
            is_valid, err_msg, meta = validate_pdf_file(uploaded_pdf)
            if is_valid:
                pdf_bytes_to_process = uploaded_pdf.getvalue()
                doc_filename = meta["filename"]
                st.success(f"✓ '{doc_filename}' verified ({meta['page_count']} pages, {meta['size_formatted']}).")
            else:
                st.error(f"⚠️ {err_msg}")

    with tab_sample:
        st.markdown(
            """
            Don't have a lease PDF at hand? Use our pre-built **Standard 2026 Residential Lease Agreement** 
            containing realistic clauses on deposits, landlord entry, repairs, pets, and early termination.
            """
        )
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_lease.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                sample_bytes = f.read()
            if st.button("📥 Load Sample Lease Agreement", type="secondary"):
                pdf_bytes_to_process = sample_bytes
                doc_filename = "sample_lease.pdf"
                st.session_state.active_lease_name = doc_filename
                st.session_state.active_lease_bytes = sample_bytes
                st.rerun()

    # Check if active lease is in session state
    if pdf_bytes_to_process:
        st.session_state.active_lease_bytes = pdf_bytes_to_process
        st.session_state.active_lease_name = doc_filename
    elif "active_lease_bytes" in st.session_state:
        pdf_bytes_to_process = st.session_state.active_lease_bytes
        doc_filename = st.session_state.get("active_lease_name", "active_lease.pdf")

    # If document loaded, index into ChromaDB
    if pdf_bytes_to_process:
        if st.session_state.get("indexed_lease_name") != doc_filename:
            with st.spinner(f"Extracting text with PyMuPDF and indexing into ChromaDB..."):
                try:
                    pages_data = rag_engine.extract_text_from_pdf(pdf_bytes_to_process, doc_filename)
                    chunks = rag_engine.chunk_document(pages_data)
                    collection_name = rag_engine.index_lease(doc_filename, chunks)
                    
                    st.session_state.indexed_lease_name = doc_filename
                    st.session_state.active_collection_name = collection_name
                    st.session_state.active_chunks = chunks
                    st.session_state.active_pages_data = pages_data
                    st.session_state.lease_qa_history = []
                    st.toast("Lease successfully indexed into ChromaDB!", icon="✅")
                except Exception as e:
                    st.error(f"Failed to process PDF: {str(e)}")
                    return

        # Show Document Stats
        pages_data = st.session_state.get("active_pages_data", [])
        chunks = st.session_state.get("active_chunks", [])
        total_words = sum(p["word_count"] for p in pages_data)

        st.markdown("<hr style='margin: 1.25rem 0;' />", unsafe_allow_html=True)
        stat1, stat2, stat3, stat4 = st.columns(4)
        with stat1:
            render_kpi_card("Document", doc_filename[:18], "Active agreement", "PDF", "neutral")
        with stat2:
            render_kpi_card("Total Pages", str(len(pages_data)), "Read by PyMuPDF", "Pages", "low")
        with stat3:
            render_kpi_card("Word Count", f"{total_words:,}", "Extracted text content", "Words", "neutral")
        with stat4:
            render_kpi_card("Vector Chunks", str(len(chunks)), "ChromaDB indexed embeddings", "Chroma", "low")

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

        # Interactive RAG Q&A Section
        st.markdown("<h2>Ask Questions Grounded in Your Lease</h2>", unsafe_allow_html=True)
        st.caption("All answers are derived strictly from your document clauses. Citations and excerpts are displayed below.")

        # Preset Quick Query Buttons
        st.markdown("<span style='font-size: 0.82rem; font-weight: 600; color: #475569;'>Suggested Tenant Audit Questions:</span>", unsafe_allow_html=True)
        btn_cols = st.columns(3)
        for idx, q_text in enumerate(SAMPLE_LEASE_QUESTIONS[:6]):
            col = btn_cols[idx % 3]
            short_label = q_text[:38] + "..."
            if col.button(short_label, key=f"qbtn_{idx}", use_container_width=True):
                st.session_state.selected_lease_query = q_text

        # Query Input
        user_query = st.text_input(
            "Enter your question regarding the lease:",
            value=st.session_state.get("selected_lease_query", "What are the rules regarding security deposit return and deductions?"),
            placeholder="e.g. Can the landlord enter without notice? What are the penalties for breaking the lease early?",
            key="lease_query_input"
        )

        # Run Query Action
        if st.button("🔍 Analyze Lease Clause", type="primary", use_container_width=True):
            if not user_query.strip():
                st.warning("Please enter a question to analyze.")
            elif not is_online:
                st.error("Ollama is not running. Please start Ollama (`ollama serve`) to evaluate queries.")
            else:
                with st.spinner(f"Retrieving relevant clauses from ChromaDB and querying `{text_model}`..."):
                    try:
                        # 1. Retrieve top chunks from ChromaDB
                        collection_name = st.session_state.get("active_collection_name", "lease_collection")
                        relevant_chunks = rag_engine.retrieve_relevant_chunks(
                            collection_name=collection_name,
                            query=user_query,
                            top_k=4,
                            all_chunks_fallback=chunks
                        )

                        if not relevant_chunks:
                            st.warning("No relevant clauses matching your query were found in this document.")
                        else:
                            # 2. Generate grounded response with Ollama
                            qa_response: LeaseQAResponse = generate_rag_answer(
                                query=user_query,
                                context_chunks=relevant_chunks,
                                model_name=text_model,
                                host=host
                            )

                            # Save to session history
                            if "lease_qa_history" not in st.session_state:
                                st.session_state.lease_qa_history = []
                            st.session_state.lease_qa_history.insert(0, (qa_response, relevant_chunks))

                    except OllamaServiceException as ose:
                        st.error(f"Ollama Error: {ose.message}")
                        st.info(f"Troubleshooting: {ose.advice}")
                    except Exception as ex:
                        st.error(f"Analysis failed: {str(ex)}")

        # Render Q&A History
        qa_history = st.session_state.get("lease_qa_history", [])
        if qa_history:
            st.markdown("<h2>Analysis Findings & Clause Citations</h2>", unsafe_allow_html=True)
            for idx, (res, context_chunks) in enumerate(qa_history):
                # Risk level styling
                risk_style = "neutral"
                risk_lower = res.risk_assessment.lower()
                if "red flag" in risk_lower or "high risk" in risk_lower:
                    risk_style = "high"
                elif "warning" in risk_lower or "caution" in risk_lower:
                    risk_style = "medium"
                elif "favorable" in risk_lower or "standard" in risk_lower or "fair" in risk_lower:
                    risk_style = "low"

                st.markdown(
                    f"""
                    <div class="rl-card" style="margin-bottom: 1.5rem;">
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 0.75rem;">
                            <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">
                                ❓ {res.question}
                            </div>
                            <span class="rl-badge rl-badge-{risk_style}">{res.risk_assessment}</span>
                        </div>
                        
                        <div style="font-size: 0.95rem; color: #1E293B; line-height: 1.6; margin-bottom: 1rem;">
                            {res.answer}
                        </div>

                        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 0.85rem 1rem; margin-bottom: 0.85rem;">
                            <div style="font-weight: 600; font-size: 0.82rem; color: #1F4E46; margin-bottom: 0.25rem;">
                                💡 Tenant Strategic Advice:
                            </div>
                            <div style="font-size: 0.88rem; color: #334155;">
                                {res.actionable_tenant_advice}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Show exact citations
                if res.citations:
                    with st.expander(f"📜 View Exact Lease Excerpts ({len(res.citations)} citations)", expanded=True):
                        for c_idx, cit in enumerate(res.citations):
                            page_str = f"Page {cit.page_number}" if cit.page_number else "Document"
                            st.markdown(
                                f"""
                                <div class="rl-citation-box">
                                    <div class="rl-citation-title">{cit.clause_title} ({page_str})</div>
                                    <div style="font-style: italic; color: #1E293B; margin-bottom: 0.35rem;">
                                        "{cit.excerpt}"
                                    </div>
                                    <div style="font-size: 0.8rem; color: #64748B;">
                                        <b>Why this matters:</b> {cit.relevance_explanation}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

    else:
        st.markdown(
            """
            <div class="rl-card" style="text-align: center; padding: 2.5rem 1.5rem; margin-top: 1.5rem;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📑</div>
                <h3 style="margin: 0 0 0.5rem 0; color: #0F172A;">No Lease Document Loaded</h3>
                <p style="color: #64748B; max-width: 520px; margin: 0 auto 1.25rem auto;">
                    Upload your lease PDF above or click "Test with Sample Lease" to experience grounded RAG analysis on residential rental agreements.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
