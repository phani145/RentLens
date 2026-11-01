# 🔍 RentLens AI – AI-Powered Rental Safety Inspector

**RentLens AI** is an intelligent, privacy-first property inspection and lease auditing web application built for prospective tenants. It enables renters to evaluate photographic evidence of habitability defects (mold, water damage, pests, electrical hazards) and interrogate lease agreements with grounded RAG before signing binding contracts.

---

## 🏛️ Design Aesthetic

RentLens AI adheres strictly to a classic, prestigious real-estate dashboard philosophy:
- **Warm off-white background** (`#F8F9F8`) for reduced eye strain and an organic paper-like feel.
- **Deep navy typography** (`#0F172A`) for authoritative clarity.
- **Muted forest-green and teal accents** (`#1F4E46` & `#0D5C58`) evoking trust, stability, and professionalism.
- **Subtle borders, soft shadows, and clean KPI cards** without flashy neon gradients or disruptive animations.
- **Structured left sidebar navigation** with real-time Ollama daemon connection diagnostics.

---

## 🛠️ Technology Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend Framework** | **Streamlit** (v1.64.0) | High-performance reactive dashboard with custom CSS |
| **Local LLM Engine** | **Ollama** | 100% on-device private inference without cloud API leakage |
| **Vision Model** | **`moondream`** / **`llama3.2-vision`** | Multimodal photograph analysis for physical hazard detection |
| **Text Model** | **`gemma3:1b`** / **`llama3.2`** | Impartial lease clause analysis & tenant advocacy |
| **Document RAG** | **ChromaDB** & **LangChain** | Cosine vector space indexing & RecursiveCharacterTextSplitter |
| **PDF Extraction** | **PyMuPDF** (`pymupdf`) | Fast, accurate text & page provenance extraction |
| **Validation** | **Pydantic** (v2) | Strict schema validation for hazard items & structured JSON |
| **Report Generation** | **ReportLab** | Publication-grade downloadable PDF safety inspection dossiers |

---

## 🚀 Key Functional Modules

### 1. Executive Dashboard (`views/dashboard_view.py`)
- Welcome header and summary metrics (Total Audits, Low Risk Units, Caution Flagged, High Risk Defects).
- Recent inspections list with severity badges and inspection metadata.
- Quick navigation shortcuts: Start Property Inspection, Review Lease Agreement, Pre-Move Checklist.
- Practical educational guides for tenants (under-sink checks, GFCI testing, written addenda).

### 2. Property Visual Safety Inspection (`views/inspection_view.py`)
- Upload multiple property photos (JPG, JPEG, PNG).
- Integrity and dimension verification using PIL (rejects corrupted, oversized, or empty files).
- Responsive thumbnail preview gallery.
- Multimodal AI inspection scanning for:
  - **Mold & Mildew** (staining, discoloration, grout spores)
  - **Water Damage** (swelling baseboards, ceiling rings, active pipe leaks)
  - **Pest Intrusion** (droppings, bait traps, drywall chew holes)
  - **Electrical Safety** (missing cover plates, burnt sockets, exposed wires)
  - **Structural Concerns** (cracks, window locks, fire alarms)
- Structured Pydantic validation mapping output to urgency levels and tenant repair requests.

### 3. Comprehensive Safety Report & PDF Export (`views/report_view.py`)
- Overall risk severity banner (Low, Medium, High, Critical).
- Detailed hazard breakdown cards specifying:
  - Exact visual location within photo
  - Plain-English defect description
  - Health and habitability impact
  - Actionable tenant recommendation & urgency
- Filter hazards by category or risk level.
- Reviewed photo evidence gallery.
- **One-click Download PDF**: Generates an elegant, executive assessment dossier with numbered canvas, tables, and legal disclaimers via ReportLab.

### 4. Grounded Lease Document Review & RAG (`views/lease_view.py`)
- Upload residential lease agreements (.pdf) or click **"Test with Sample Lease"** to load the bundled 2026 agreement.
- Extracts clean text page-by-page with PyMuPDF, chunks with LangChain, and indexes in ChromaDB.
- Interactive question answering grounded strictly in lease text (no hallucinations):
  - Pre-built quick queries (Security deposit return, Landlord right of entry, Mold/repair duties, Early termination, Pets, Late fees).
  - Risk assessment badge (Favorable, Standard, Warning, Red Flag).
  - Direct clause citations citing exact page numbers and quotes.

### 5. Practical Rental Safety Checklist (`views/checklist_view.py`)
- 26-point in-person walkthrough inspection checklist across 7 critical systems:
  - Electrical Safety
  - Plumbing & Water Flow
  - Ventilation & Air Quality
  - Pests & Rodents
  - Water Damage & Mold
  - Locks & Physical Security
  - Fire & Life Safety
- Interactive state-preserved checkboxes with completion percentage.
- One-click Download of Checklist Notes (`.txt`) to email landlords or attach to move-in forms.

### 6. About & Legal Disclaimers (`views/about_view.py`)
- Complete mission briefing, system architecture, and local-first privacy guarantees.
- Comprehensive legal and technical disclaimers clarifying that AI results are preliminary educational aids and do not constitute certified physical inspections or legal counsel.

---

## 💻 Installation & Setup Guide

### Prerequisites
1. **Python 3.10+** (Python 3.14 compatible).
2. **Ollama** installed on your system ([Download Ollama](https://ollama.com/download)).

### Step 1: Clone or Navigate to the Workspace
```bash
cd "c:\Users\DELL\OneDrive\Desktop\RentLens"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Start Ollama & Download Models
Make sure the Ollama daemon is running:
```bash
ollama serve
```

In another terminal, download the recommended models:
```bash
# Pull the fast local vision model (1.7GB)
ollama pull moondream

# Pull the text model for lease RAG
ollama pull gemma3:1b

# (Optional) For high-end GPUs, pull Llama 3.2 Vision:
# ollama pull llama3.2-vision
```

### Step 4: Launch RentLens AI
```bash
python -m streamlit run app.py
```
Open your browser to:
👉 **`http://localhost:8501`**

---

## 🧪 Running the Verification Test Suite

RentLens AI includes an automated smoke test suite that verifies Pydantic schemas, ReportLab PDF generation, Ollama connectivity, PyMuPDF extraction, and ChromaDB vector search:

```bash
python -u tests/smoke_test.py
```

Expected output:
```text
[1/5] Testing Pydantic models...
  [OK] Models OK: SMOKE-01 Medium
[2/5] Testing PDF Report generation with ReportLab...
  [OK] PDF generated: 3962 bytes
[3/5] Testing Ollama connection & model inspection...
  [OK] Ollama status: Ollama online (2 models found)
  [OK] Installed models: ['moondream:latest', 'gemma3:1b']
[4/5] Testing PyMuPDF lease extraction & LangChain chunking...
  [OK] Extracted 2 pages, split into 8 chunks
[5/5] Testing ChromaDB vector indexing and keyword retrieval...
  [OK] Indexed into collection 'smoke_test_coll', retrieved 2 relevant chunks

ALL 5 SUBSYSTEM TESTS PASSED SUCCESSFULLY! :)
```

---

## 🔒 Privacy & Safety Guarantee

- **Zero Cloud APIs**: No photographs, addresses, or lease documents are uploaded to third-party services.
- **Local Vectors**: ChromaDB and ONNX embeddings operate locally on your machine.
- **File Sanitization**: Uploaded buffers are held in memory during the session and never exposed publicly.

---

## ⚠️ Disclaimer
*RentLens AI is an educational decision-support tool. Photographic visual analysis cannot detect hidden wall cavity moisture, internal electrical faults, or unexposed defects. Contract interpretations do not establish legal counsel. Prospective tenants should independently verify all conditions and consult licensed professionals.*
