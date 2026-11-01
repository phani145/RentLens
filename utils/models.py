"""
RentLens AI - Data Models and Validation Schemas.
Utilizes Pydantic for strict structured output validation and type safety.
"""

from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class HazardCategory(str, Enum):
    MOLD = "Mold & Mildew"
    WATER_DAMAGE = "Water Damage"
    PESTS = "Pests & Infestation"
    ELECTRICAL = "Electrical Hazard"
    STRUCTURAL = "Structural & Physical"
    FIRE_SAFETY = "Fire Safety"
    VENTILATION = "Ventilation & Air Quality"
    LOCKS_SECURITY = "Locks & Security"
    PLUMBING = "Plumbing Defect"
    OTHER = "General Safety Hazard"


class HazardItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the hazard item")
    title: str = Field(..., description="Short descriptive title of the hazard")
    category: str = Field(..., description="Hazard category name")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Assessed risk level")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    location_in_image: str = Field(..., description="Visual location of the detected hazard in the photograph")
    description: str = Field(..., description="Detailed observation of the visible hazard")
    potential_consequences: str = Field(..., description="Potential health, safety, or legal impacts for the renter")
    tenant_recommendation: str = Field(..., description="Actionable recommendation for the tenant")
    urgency: str = Field(default="Prior to signing lease", description="Urgency of resolution")


class ImageInspectionResult(BaseModel):
    image_filename: str = Field(..., description="Name of the evaluated image file")
    overall_risk: RiskLevel = Field(default=RiskLevel.LOW, description="Aggregated risk level for this image")
    hazards: List[HazardItem] = Field(default_factory=list, description="List of detected hazard items")
    safe_observations: List[str] = Field(default_factory=list, description="Positive or clean aspects observed")
    visual_clarity: str = Field(default="Good", description="Quality and lighting assessment of the photograph")
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Visual assessment only; does not replace invasive testing.",
            "Sub-surface moisture, behind-wall wiring, and internal pipe condition cannot be verified via photo."
        ],
        description="Limitations of visual inspection"
    )


class FullInspectionReport(BaseModel):
    report_id: str
    property_name: str
    created_at: str
    images_evaluated_count: int
    overall_property_risk: RiskLevel
    executive_summary: str
    all_hazards: List[HazardItem] = Field(default_factory=list)
    risk_breakdown: Dict[str, int] = Field(default_factory=dict)
    key_recommendations: List[str] = Field(default_factory=list)
    inspection_limitations: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "DISCLAIMER: RentLens AI is an educational decision-support tool powered by local artificial intelligence. "
        "It does not constitute an official municipal code inspection, certified pest inspection, structural engineering "
        "survey, or legal counsel. Prospective renters should independently verify all conditions and consult licensed professionals."
    )


class LeaseClauseCitation(BaseModel):
    clause_title: str = Field(..., description="Clause or section identifier")
    page_number: Optional[int] = Field(None, description="Document page number if identified")
    excerpt: str = Field(..., description="Exact quoted text from lease")
    relevance_explanation: str = Field(..., description="How this clause applies to the renter's query")


class LeaseQAResponse(BaseModel):
    question: str
    answer: str
    risk_assessment: str = Field(
        default="Standard",
        description="Evaluation of terms: 'Favorable', 'Standard / Neutral', 'Warning / Tenant Disadvantage', or 'Red Flag'"
    )
    citations: List[LeaseClauseCitation] = Field(default_factory=list)
    actionable_tenant_advice: str
    grounded_in_document: bool = True
