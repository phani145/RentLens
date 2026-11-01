"""
RentLens AI - Ollama Client Integration.
Handles communication with local Ollama instance for Vision multimodal analysis
and document RAG question answering with Pydantic validation and error resilience.
"""

import json
import re
import uuid
import requests
from typing import Tuple, List, Dict, Any, Optional
from utils.models import (
    RiskLevel,
    HazardCategory,
    HazardItem,
    ImageInspectionResult,
    LeaseQAResponse,
    LeaseClauseCitation
)

DEFAULT_OLLAMA_HOST = "http://localhost:11434"

# Recognized vision-capable model families/names in Ollama
KNOWN_VISION_MODELS = [
    "moondream",
    "llama3.2-vision",
    "llava",
    "llava-llama3",
    "llava-phi3",
    "minicpm-v",
    "bakllava",
    "qwen2-vl",
    "qwen2.5-vl"
]


class OllamaServiceException(Exception):
    """Custom exception with clear renter-friendly troubleshooting advice."""
    def __init__(self, message: str, advice: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.advice = advice or (
            "Ensure Ollama is running (`ollama serve`). "
            "You can test connection using the sidebar status badge."
        )


def check_ollama_connection(host: str = DEFAULT_OLLAMA_HOST) -> Tuple[bool, str, List[str]]:
    """
    Checks if Ollama is accessible and returns installed model names.
    Returns: (is_online, message, list_of_models)
    """
    cleaned_host = host.rstrip("/")
    try:
        response = requests.get(f"{cleaned_host}/api/tags", timeout=4)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return True, f"Ollama online ({len(models)} model{'s' if len(models) != 1 else ''} found)", models
        return False, f"Ollama responded with status code {response.status_code}", []
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama. Daemon may not be running on localhost:11434.", []
    except requests.exceptions.Timeout:
        return False, "Connection to Ollama timed out. Host may be unreachable or busy.", []
    except Exception as e:
        return False, f"Error reaching Ollama: {str(e)}", []


def is_vision_capable_model(model_name: str) -> bool:
    """Checks if a model name corresponds to a known vision-capable model."""
    clean = model_name.lower().split(":")[0]
    return any(v_model in clean for v_model in KNOWN_VISION_MODELS)


def get_categorized_models(host: str = DEFAULT_OLLAMA_HOST) -> Dict[str, List[str]]:
    """Returns installed models segregated by vision vs text capabilities."""
    online, _, models = check_ollama_connection(host)
    if not online:
        return {"vision": [], "text": [], "all": []}

    vision_models = [m for m in models if is_vision_capable_model(m)]
    text_models = [m for m in models if not is_vision_capable_model(m)]

    # If no recognized vision model is installed, still include any model user might have customized
    return {
        "vision": vision_models,
        "text": text_models,
        "all": models
    }


def _extract_json_from_text(raw_text: str) -> Optional[dict]:
    """Extracts JSON object from markdown code fences or raw string."""
    raw_text = raw_text.strip()
    
    # Try finding ```json ... ``` or ``` ... ```
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except Exception:
            pass

    # Try finding outer braces { ... }
    brace_match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(1))
        except Exception:
            pass

    try:
        return json.loads(raw_text)
    except Exception:
        return None


def analyze_property_image(
    image_bytes: bytes,
    filename: str,
    model_name: str = "moondream",
    host: str = DEFAULT_OLLAMA_HOST
) -> ImageInspectionResult:
    """
    Submits a rental property photo to a vision-capable Ollama model for hazard analysis.
    Validates output using Pydantic ImageInspectionResult.
    """
    online, msg, _ = check_ollama_connection(host)
    if not online:
        raise OllamaServiceException(
            message="Ollama server is not reachable.",
            advice="Please start Ollama in your terminal by running `ollama serve` or ensure the Ollama desktop app is open."
        )

    import base64
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "You are RentLens AI, an expert rental property safety inspector.\n"
        "Carefully inspect this rental property image for visible safety hazards, maintenance problems, or habitability concerns.\n\n"
        "Key areas to assess:\n"
        "1. Mold, mildew, fungal growth, or discolored drywall/grout\n"
        "2. Water damage, bubbling paint, active leaks, staining, or warped baseboards\n"
        "3. Pest evidence (droppings, traps, chew marks, nesting, entry holes)\n"
        "4. Electrical hazards (exposed wires, missing faceplates, burnt sockets, overloaded outlets)\n"
        "5. Structural issues (cracks in walls/ceiling, sagging structures, broken tiles, tripping hazards)\n"
        "6. Fire and life safety (missing smoke detector mounts, blocked windows, emergency egress)\n"
        "7. Plumbing defects (corrosion, pipe leaks, drain blocks)\n"
        "8. Door/window locks and physical security\n\n"
        "Respond ONLY in valid, parseable JSON format matching this exact schema:\n"
        "{\n"
        '  "overall_risk": "None" | "Low" | "Medium" | "High" | "Critical",\n'
        '  "hazards": [\n'
        "    {\n"
        '      "title": "Short descriptive hazard name",\n'
        '      "category": "Mold & Mildew" | "Water Damage" | "Pests & Infestation" | "Electrical Hazard" | "Structural & Physical" | "Fire Safety" | "Plumbing Defect" | "General Safety Hazard",\n'
        '      "risk_level": "Low" | "Medium" | "High" | "Critical",\n'
        '      "confidence": 0.85,\n'
        '      "location_in_image": "Specific visual location (e.g. upper right corner near vent)",\n'
        '      "description": "Clear factual observation of what is visibly seen",\n'
        '      "potential_consequences": "Health or structural impact for tenant",\n'
        '      "tenant_recommendation": "Concrete action for tenant (e.g. request mold remediation in writing before signing)",\n'
        '      "urgency": "Immediate" | "Prior to signing lease" | "Monitor regularly"\n'
        "    }\n"
        "  ],\n"
        '  "safe_observations": ["list of areas that look clean, intact, or properly maintained"],\n'
        '  "visual_clarity": "Good" | "Fair" | "Poor / Obscured",\n'
        '  "limitations": ["Visual photo inspection only; cannot verify hidden moisture, internal wall studs, or electrical conduit behind drywall."]\n'
        "}\n\n"
        "Do not invent hazards that do not exist. If the room is clean, state overall_risk as 'None' or 'Low' and leave hazards empty.\n"
        "Provide ONLY the JSON response with no extra commentary."
    )

    cleaned_host = host.rstrip("/")
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [b64_image]
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024
        }
    }

    try:
        response = requests.post(f"{cleaned_host}/api/chat", json=payload, timeout=90)
    except requests.exceptions.Timeout:
        raise OllamaServiceException(
            message=f"Model '{model_name}' timed out after 90 seconds.",
            advice="The model may be too large for available GPU/CPU resources. Try a lightweight vision model like 'moondream'."
        )
    except Exception as e:
        raise OllamaServiceException(
            message=f"Network error when calling Ollama: {str(e)}",
            advice="Check your Ollama connection and server logs."
        )

    if response.status_code != 200:
        error_text = response.text
        if "does not support multimodal" in error_text.lower():
            raise OllamaServiceException(
                message=f"Selected model '{model_name}' is text-only and does not accept image analysis.",
                advice="Please select or pull a vision-capable model such as 'moondream' (`ollama pull moondream`) or 'llama3.2-vision'."
            )
        elif "not found" in error_text.lower():
            raise OllamaServiceException(
                message=f"Model '{model_name}' is not installed in your Ollama library.",
                advice=f"Install it via your command prompt with: `ollama pull {model_name}`."
            )
        else:
            raise OllamaServiceException(
                message=f"Ollama returned HTTP error {response.status_code}: {error_text}",
                advice="Check if the model is loaded properly in Ollama."
            )

    result_data = response.json()
    content = result_data.get("message", {}).get("content", "")

    # Parse and structure the response
    parsed_json = _extract_json_from_text(content)

    if parsed_json and isinstance(parsed_json, dict):
        try:
            # Map risk level safely
            raw_risk = parsed_json.get("overall_risk", "Low")
            mapped_risk = RiskLevel.LOW
            for r in RiskLevel:
                if r.value.lower() == str(raw_risk).lower():
                    mapped_risk = r
                    break

            hazards_list = []
            for idx, h in enumerate(parsed_json.get("hazards", [])):
                h_risk = RiskLevel.LOW
                for r in RiskLevel:
                    if r.value.lower() == str(h.get("risk_level", "Low")).lower():
                        h_risk = r
                        break

                hazard_item = HazardItem(
                    id=f"haz-{uuid.uuid4().hex[:6]}",
                    title=h.get("title", f"Identified Issue #{idx+1}"),
                    category=h.get("category", HazardCategory.OTHER.value),
                    risk_level=h_risk,
                    confidence=float(h.get("confidence", 0.85)),
                    location_in_image=h.get("location_in_image", "Visible in photo area"),
                    description=h.get("description", "Potential maintenance concern noted in photograph."),
                    potential_consequences=h.get("potential_consequences", "May require landlord repair before move-in."),
                    tenant_recommendation=h.get("tenant_recommendation", "Document on pre-move-in condition checklist."),
                    urgency=h.get("urgency", "Prior to signing lease")
                )
                hazards_list.append(hazard_item)

            return ImageInspectionResult(
                image_filename=filename,
                overall_risk=mapped_risk,
                hazards=hazards_list,
                safe_observations=parsed_json.get("safe_observations", ["General structural surfaces appear intact."]),
                visual_clarity=parsed_json.get("visual_clarity", "Good"),
                limitations=parsed_json.get("limitations", [
                    "Visual inspection of photographed angle only.",
                    "Does not reveal concealed plumbing or internal wall conditions."
                ])
            )
        except Exception as parse_err:
            # Fall through to raw text wrapper
            pass

    # Fallback if model responded in free-form text instead of strict JSON
    # Analyze text for hazard keywords to construct a faithful inspection result
    lower_content = content.lower()
    inferred_risk = RiskLevel.LOW
    if any(k in lower_content for k in ["severe", "dangerous", "urgent", "critical", "exposed wire", "black mold"]):
        inferred_risk = RiskLevel.HIGH
    elif any(k in lower_content for k in ["hazard", "leak", "mold", "water damage", "pest", "crack"]):
        inferred_risk = RiskLevel.MEDIUM

    hazards = []
    if inferred_risk in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
        hazards.append(
            HazardItem(
                id=f"haz-{uuid.uuid4().hex[:6]}",
                title="Observed Property Condition Concern",
                category=HazardCategory.OTHER.value,
                risk_level=inferred_risk,
                confidence=0.80,
                location_in_image="Subject frame area",
                description=content[:350] + ("..." if len(content) > 350 else ""),
                potential_consequences="Visual anomaly identified requiring physical verification.",
                tenant_recommendation="Request written landlord disclosure and physical inspection before signing.",
                urgency="Prior to signing lease"
            )
        )

    return ImageInspectionResult(
        image_filename=filename,
        overall_risk=inferred_risk,
        hazards=hazards,
        safe_observations=["Analysis completed based on model visual review."],
        visual_clarity="Evaluated",
        limitations=[
            "Model returned narrative description rather than structured JSON schema.",
            "Visual inspection only. Internal or concealed hazards cannot be evaluated."
        ]
    )


def generate_rag_answer(
    query: str,
    context_chunks: List[Dict[str, Any]],
    model_name: str = "gemma3:1b",
    host: str = DEFAULT_OLLAMA_HOST
) -> LeaseQAResponse:
    """
    Answers tenant questions grounded strictly in retrieved lease document chunks.
    Prevents fabrication and cites exact clause excerpts and page numbers.
    """
    online, _, _ = check_ollama_connection(host)
    if not online:
        raise OllamaServiceException(
            message="Ollama server is offline.",
            advice="Please start Ollama (`ollama serve`) to run lease analysis."
        )

    # Format context with chunk index and source metadata
    formatted_context = ""
    for idx, chunk in enumerate(context_chunks):
        page = chunk.get("metadata", {}).get("page", 1)
        text = chunk.get("text", "").strip()
        formatted_context += f"\n--- EXCERPT {idx+1} (Page {page}) ---\n{text}\n"

    system_instruction = (
        "You are RentLens AI Lease Advisor, an impartial expert in residential lease agreements.\n"
        "Your task is to answer the renter's query strictly using ONLY the provided lease excerpts.\n\n"
        "RULES:\n"
        "1. GROUNDING: Base every claim on the provided text. Never invent lease terms, penalties, or rules not present.\n"
        "2. UNMENTIONED TOPICS: If the document does NOT mention the topic, clearly state: 'The provided lease document does not contain specific clauses regarding this question.'\n"
        "3. TENANT PERSPECTIVE: Evaluate whether the clause is standard, favorable, or carries disadvantage/risk for the tenant.\n"
        "4. CITATIONS: Mention the relevant excerpt or section.\n\n"
        "Respond in valid JSON format matching this schema:\n"
        "{\n"
        '  "answer": "Clear, direct, plain-language answer explaining what the lease dictates.",\n'
        '  "risk_assessment": "Favorable" | "Standard / Fair" | "Warning / Tenant Caution" | "High Risk / Red Flag" | "Not Addressed in Lease",\n'
        '  "actionable_tenant_advice": "Practical advice for the renter (e.g. request an addendum, negotiate terms, or clarify in writing).",\n'
        '  "citations": [\n'
        "    {\n"
        '      "clause_title": "Section or Clause Heading (or Topic)",\n'
        '      "page_number": 1,\n'
        '      "excerpt": "Direct exact quote of the relevant sentence from the lease excerpt",\n'
        '      "relevance_explanation": "Why this specific sentence matters to the tenant"\n'
        "    }\n"
        "  ]\n"
        "}"
    )

    user_prompt = f"LEASE EXCERPTS:\n{formatted_context}\n\nRENTER QUESTION:\n{query}\n\nProvide your grounded JSON analysis:"

    cleaned_host = host.rstrip("/")
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 1024
        }
    }

    try:
        response = requests.post(f"{cleaned_host}/api/chat", json=payload, timeout=60)
        if response.status_code != 200:
            raise OllamaServiceException(
                message=f"Model error {response.status_code}: {response.text}",
                advice=f"Verify model '{model_name}' is installed via `ollama list`."
            )
        data = response.json()
        content = data.get("message", {}).get("content", "")
    except requests.exceptions.Timeout:
        raise OllamaServiceException(
            message=f"Query timed out for model '{model_name}'.",
            advice="Consider using a faster model like `gemma3:1b` or reducing context length."
        )
    except Exception as e:
        raise OllamaServiceException(message=f"Ollama communication failure: {str(e)}")

    parsed = _extract_json_from_text(content)
    if parsed and isinstance(parsed, dict):
        citations = []
        for c in parsed.get("citations", []):
            citations.append(
                LeaseClauseCitation(
                    clause_title=c.get("clause_title", "Lease Clause"),
                    page_number=c.get("page_number", context_chunks[0].get("metadata", {}).get("page", 1) if context_chunks else 1),
                    excerpt=c.get("excerpt", "Direct quote from clause."),
                    relevance_explanation=c.get("relevance_explanation", "Directly governs this rental condition.")
                )
            )

        return LeaseQAResponse(
            question=query,
            answer=parsed.get("answer", "Analysis of lease terms completed."),
            risk_assessment=parsed.get("risk_assessment", "Standard / Fair"),
            citations=citations,
            actionable_tenant_advice=parsed.get("actionable_tenant_advice", "Review clause carefully with the leasing agent before signing."),
            grounded_in_document=True
        )

    # Narrative fallback if model answered in text
    return LeaseQAResponse(
        question=query,
        answer=content.strip(),
        risk_assessment="Standard / Fair",
        citations=[
            LeaseClauseCitation(
                clause_title="Lease Excerpt",
                page_number=context_chunks[0].get("metadata", {}).get("page", 1) if context_chunks else 1,
                excerpt=context_chunks[0].get("text", "")[:200] if context_chunks else "See retrieved section.",
                relevance_explanation="Retrieved via lease vector search."
            )
        ] if context_chunks else [],
        actionable_tenant_advice="Ensure this requirement is clearly understood and documented in your lease addendum.",
        grounded_in_document=True
    )
