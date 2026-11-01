"""
RentLens AI - Storage and History Manager.
Persists inspection history and provides sample test assets.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.models import FullInspectionReport, RiskLevel, HazardItem

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "inspection_history.json")


def ensure_data_dir():
    """Creates the data storage directory if it doesn't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def load_inspection_history() -> List[Dict[str, Any]]:
    """Loads previous inspection records from disk."""
    ensure_data_dir()
    if not os.path.exists(HISTORY_FILE):
        # Return default starter demonstrations if no history yet
        return get_default_demo_history()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return get_default_demo_history()


def save_inspection_to_history(report: FullInspectionReport) -> bool:
    """Saves a new inspection report to local history."""
    ensure_data_dir()
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    report_dict = report.model_dump()
    # Prepend new report to top
    history.insert(0, report_dict)
    # Keep up to 25 historical records
    history = history[:25]

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        return True
    except Exception:
        return False


def get_default_demo_history() -> List[Dict[str, Any]]:
    """Starter demonstration inspections to populate dashboard on fresh launch."""
    return [
        {
            "report_id": "RL-2026-9041",
            "property_name": "Apt 4B - Oakwood Manor",
            "created_at": "2026-10-28 14:15",
            "images_evaluated_count": 4,
            "overall_property_risk": "Medium",
            "executive_summary": "Inspection identified localized drywall water staining underneath the primary bathroom vanity and missing smoke detector bracket in hallway.",
            "all_hazards": [
                {
                    "id": "haz-demo-1",
                    "title": "Sub-sink Drywall Moisture Discoloration",
                    "category": "Water Damage",
                    "risk_level": "Medium",
                    "confidence": 0.88,
                    "location_in_image": "Behind P-trap plumbing fitting",
                    "description": "Dark brown staining and visible paper swelling on gypsum board beneath shutoff valves.",
                    "potential_consequences": "Indicates historical or active slow valve weeping; risk of fungal growth if unaddressed.",
                    "tenant_recommendation": "Demand plumber pressure test and moisture meter check before lease signing.",
                    "urgency": "Prior to signing lease"
                },
                {
                    "id": "haz-demo-2",
                    "title": "Unmounted Smoke Alarm Fitting",
                    "category": "Fire Safety",
                    "risk_level": "High",
                    "confidence": 0.94,
                    "location_in_image": "Ceiling fixture adjacent to bedroom corridor",
                    "description": "Alarm mounting ring present with bare 120V quick-connect wires; unit itself is absent.",
                    "potential_consequences": "Violation of municipal residential fire code; extreme life safety risk during sleep hours.",
                    "tenant_recommendation": "Require landlord install functional hardwired dual-sensor detector immediately.",
                    "urgency": "Immediate"
                }
            ],
            "risk_breakdown": {"High": 1, "Medium": 1, "Low": 0},
            "key_recommendations": [
                "Require certified plumber sign-off on vanity valve shutoffs.",
                "Obtain confirmation of installed and tested smoke alarms before moving furniture."
            ],
            "inspection_limitations": ["Visual review of provided photographs."]
        },
        {
            "report_id": "RL-2026-8812",
            "property_name": "Unit 12 - Cedar Ridge Lofts",
            "created_at": "2026-10-15 09:30",
            "images_evaluated_count": 6,
            "overall_property_risk": "Low",
            "executive_summary": "Property in good overall condition. Minor surface scuffs on kitchen baseboards and slightly loose bedroom deadbolt strike plate.",
            "all_hazards": [
                {
                    "id": "haz-demo-3",
                    "title": "Loose Exterior Deadbolt Strike Plate",
                    "category": "Locks & Security",
                    "risk_level": "Low",
                    "confidence": 0.82,
                    "location_in_image": "Front entry door jamb",
                    "description": "Strike plate screw slightly backed out causing minor door wobble when latched.",
                    "potential_consequences": "Minor security vulnerability if door is forced.",
                    "tenant_recommendation": "Request 3-inch security screws installed into stud before move-in.",
                    "urgency": "Prior to signing lease"
                }
            ],
            "risk_breakdown": {"High": 0, "Medium": 0, "Low": 1},
            "key_recommendations": ["Tighten and reinforce door hardware."],
            "inspection_limitations": ["Visual inspection of entry doors and living areas."]
        }
    ]
