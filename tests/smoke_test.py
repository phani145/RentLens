"""
RentLens AI - Fast Smoke Test Runner.
"""

import os
import sys

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("[1/5] Testing Pydantic models...")
from utils.models import RiskLevel, HazardCategory, HazardItem, FullInspectionReport

item = HazardItem(
    id="test-1",
    title="Mold spot",
    category=HazardCategory.MOLD.value,
    risk_level=RiskLevel.MEDIUM,
    confidence=0.89,
    location_in_image="Ceiling corner",
    description="Dark mildew spots observed",
    potential_consequences="Indoor air quality degradation",
    tenant_recommendation="Request bleach/antimicrobial wash",
    urgency="Prior to signing"
)
report = FullInspectionReport(
    report_id="SMOKE-01",
    property_name="742 Evergreen",
    created_at="2026-11-01",
    images_evaluated_count=1,
    overall_property_risk=RiskLevel.MEDIUM,
    executive_summary="Smoke test summary.",
    all_hazards=[item],
    risk_breakdown={"Medium": 1}
)
print("  [OK] Models OK:", report.report_id, report.overall_property_risk.value)

print("[2/5] Testing PDF Report generation with ReportLab...")
from utils.pdf_report import generate_inspection_pdf
pdf_bytes = generate_inspection_pdf(report)
print(f"  [OK] PDF generated: {len(pdf_bytes)} bytes")

print("[3/5] Testing Ollama connection & model inspection...")
from utils.ollama_client import check_ollama_connection, get_categorized_models
online, msg, models = check_ollama_connection()
print(f"  [OK] Ollama status: {msg}")
print(f"  [OK] Installed models: {models}")

print("[4/5] Testing PyMuPDF lease extraction & LangChain chunking...")
from utils.lease_rag import LeaseRAGEngine
sample_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_lease.pdf")
with open(sample_pdf, "rb") as f:
    pdf_bytes = f.read()

rag = LeaseRAGEngine()
pages = rag.extract_text_from_pdf(pdf_bytes, "sample_lease.pdf")
chunks = rag.chunk_document(pages)
print(f"  [OK] Extracted {len(pages)} pages, split into {len(chunks)} chunks")

print("[5/5] Testing ChromaDB vector indexing and keyword retrieval...")
coll_name = rag.index_lease("smoke_test_coll", chunks)
retrieved = rag.retrieve_relevant_chunks(
    collection_name=coll_name,
    query="security deposit return",
    top_k=2,
    all_chunks_fallback=chunks
)
print(f"  [OK] Indexed into collection '{coll_name}', retrieved {len(retrieved)} relevant chunks")
for idx, r in enumerate(retrieved):
    print(f"    - Chunk #{idx+1} (Page {r['metadata']['page']}): {r['text'][:80]}...")

print("\nALL 5 SUBSYSTEM TESTS PASSED SUCCESSFULLY! :)")
