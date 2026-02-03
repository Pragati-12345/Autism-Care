"""
Therapy Planning Module.

Generates explainable, conservative therapy recommendations
based on screening risk tier and evidence.

All plans MUST be reviewed and approved by a clinician.
"""

from typing import Dict, List

from src.utils import require


# ============================
# THERAPY TEMPLATES
# ============================

THERAPY_TEMPLATES = {
    "SPEECH": {
        "description": "Speech and language development therapy",
        "goals": [
            "Increase functional vocalizations",
            "Improve receptive language",
            "Encourage imitation of sounds and words"
        ]
    },
    "OT": {
        "description": "Occupational therapy for sensory and motor integration",
        "goals": [
            "Improve fine motor coordination",
            "Reduce sensory aversions",
            "Enhance self-regulation skills"
        ]
    },
    "SOCIAL": {
        "description": "Social interaction and joint attention therapy",
        "goals": [
            "Increase joint attention episodes",
            "Improve eye contact duration",
            "Encourage turn-taking behaviors"
        ]
    }
}


# ============================
# PLAN GENERATION
# ============================

def generate_therapy_plan(
    risk_level: str,
    screening_evidence: Dict
) -> Dict:
    """
    Generate a personalized therapy plan based on risk tier.
    """

    require(
        risk_level in {"LOW", "MEDIUM", "HIGH"},
        f"Invalid risk level: {risk_level}"
    )

    plan: Dict[str, Dict] = {}

    # LOW RISK: monitoring + light intervention
    if risk_level == "LOW":
        plan["MONITORING"] = {
            "frequency_per_week": 1,
            "notes": "Continue monitoring development; encourage play-based learning.",
            "goals": [
                "Maintain developmental trajectory",
                "Monitor emerging communication skills"
            ]
        }

    # MEDIUM RISK: targeted early intervention
    elif risk_level == "MEDIUM":
        plan["SPEECH"] = {
            "frequency_per_week": 2,
            "goals": THERAPY_TEMPLATES["SPEECH"]["goals"]
        }
        plan["SOCIAL"] = {
            "frequency_per_week": 2,
            "goals": THERAPY_TEMPLATES["SOCIAL"]["goals"]
        }

    # HIGH RISK: multi-domain intensive support
    elif risk_level == "HIGH":
        plan["SPEECH"] = {
            "frequency_per_week": 3,
            "goals": THERAPY_TEMPLATES["SPEECH"]["goals"]
        }
        plan["OT"] = {
            "frequency_per_week": 2,
            "goals": THERAPY_TEMPLATES["OT"]["goals"]
        }
        plan["SOCIAL"] = {
            "frequency_per_week": 3,
            "goals": THERAPY_TEMPLATES["SOCIAL"]["goals"]
        }

    # Add explainability metadata
    return {
        "risk_level": risk_level,
        "therapy_plan": plan,
        "explainability": {
            "basis": "Plan generated from screening risk tier and top contributing behavioral signals.",
            "note": "Final therapy plan must be approved and adapted by a clinician."
        }
    }


# ============================
# PLAN REVIEW UTILITIES
# ============================

def summarize_plan(plan: Dict) -> List[str]:
    """
    Generate a human-readable summary for clinicians.
    """

    summary = []

    for domain, details in plan.get("therapy_plan", {}).items():
        freq = details.get("frequency_per_week", "?")
        summary.append(f"{domain}: {freq} session(s)/week")

    return summary
