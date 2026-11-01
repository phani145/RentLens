"""
RentLens AI - Verification & Integration Test Suite.
Verifies all core subsystems: Pydantic schemas, file validation,
PDF report generation, PyMuPDF extraction, ChromaDB RAG, and Ollama connectivity.
"""

import os
import sys
import unittest

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.models import (
    RiskLevel,
    HazardCategory,
    HazardItem,
    FullInspectionReport,
    LeaseQAResponse
)
from utils.file_validator import validate_image_file, validate_pdf_file
from utils.pdf_report import generate_inspection_pdf
from utils.lease_rag import LeaseRAGEngine
from utils.ollama_client import check_ollama_connection, get_categorized_models


class TestRentLensAI(unittest.TestCase):

    def setUp(self):
        self.sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data")
        self.sample_pdf = os.path.join(self.sample_dir, "sample_lease.pdf")
        self.sample_img1 = os.path.join(self.sample_dir, "sample_undersink_damage.jpg")

    def test_pydantic_models(self):
        """Tests Pydantic models validation and serialization."""
        item = HazardItem(
            id="haz-test-1",
            title="Mold under kitchen sink",
            category=HazardCategory.MOLD.value,
            risk_level=RiskLevel.HIGH,
            confidence=0.92,
            location_in_image="Under pipe",
            description="Dark black fungal spots",
            potential_consequences="Respiratory irritation",
            tenant_recommendation="Request mold remediation",
            urgency="Immediate"
        )
        self.assertEqual(item.risk_level, RiskLevel.HIGH)
        self.assertAlmostEqual(item.confidence, 0.92)

        report = FullInspectionReport(
            report_id="RL-TEST-001",
            property_name="Unit 4A",
            created_at="2026-11-01 10:00",
            images_evaluated_count=1,
            overall_property_risk=RiskLevel.HIGH,
            executive_summary="Critical issues detected.",
            all_hazards=[item],
            risk_breakdown={"High": 1}
        )
        data = report.model_dump()
        self.assertEqual(data["report_id"], "RL-TEST-001")
        self.assertEqual(len(data["all_hazards"]), 1)

    def test_pdf_report_generation(self):
        """Tests ReportLab PDF generator builds valid PDF binary."""
        item = HazardItem(
            id="haz-test-2",
            title="Exposed ceiling wire",
            category=HazardCategory.ELECTRICAL.value,
            risk_level=RiskLevel.CRITICAL,
            confidence=0.95,
            location_in_image="Hallway fixture",
            description="Bare wire ends hanging from junction box",
            potential_consequences="Electrocution and fire danger",
            tenant_recommendation="Landlord must cap and mount fixture",
            urgency="Immediate"
        )
        report = FullInspectionReport(
            report_id="RL-PDF-001",
            property_name="Test Property Suite 100",
            created_at="2026-11-01 12:00",
            images_evaluated_count=2,
            overall_property_risk=RiskLevel.HIGH,
            executive_summary="Executive report test summary.",
            all_hazards=[item],
            risk_breakdown={"High": 1, "Medium": 0, "Low": 0}
        )
        pdf_bytes = generate_inspection_pdf(report)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_lease_pdf_extraction_and_rag(self):
        """Tests PyMuPDF text extraction, chunking, and ChromaDB search."""
        self.assertTrue(os.path.exists(self.sample_pdf), "Sample lease PDF must exist")
        
        with open(self.sample_pdf, "rb") as f:
            pdf_bytes = f.read()

        engine = LeaseRAGEngine()
        pages = engine.extract_text_from_pdf(pdf_bytes, "sample_lease.pdf")
        self.assertTrue(len(pages) >= 1)
        self.assertIn("Security Deposit", pages[0]["text"] + pages[-1]["text"])

        chunks = engine.chunk_document(pages)
        self.assertTrue(len(chunks) > 0)

        # Index in ChromaDB
        coll_name = engine.index_lease("test_lease", chunks)
        self.assertTrue(bool(coll_name))

        # Retrieve relevant chunks for security deposit
        results = engine.retrieve_relevant_chunks(
            collection_name=coll_name,
            query="When will the security deposit be returned?",
            top_k=2,
            all_chunks_fallback=chunks
        )
        self.assertTrue(len(results) > 0)
        combined_text = " ".join([r["text"] for r in results]).lower()
        self.assertTrue("deposit" in combined_text or "security" in combined_text)

    def test_ollama_client_check(self):
        """Tests Ollama connectivity check."""
        is_online, msg, models = check_ollama_connection()
        self.assertTrue(is_online, "Local Ollama daemon should be reachable on localhost:11434")
        self.assertIn("moondream", [m.split(":")[0] for m in models])


if __name__ == "__main__":
    unittest.main()
