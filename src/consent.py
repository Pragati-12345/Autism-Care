"""
Consent and safety enforcement module.

This module acts as a gatekeeper to ensure that:
- All sensitive actions are consent-protected
- Defaults are conservative
- Pediatric data safety is enforced

NO model or data operation should bypass this module.
"""

from typing import Dict

from src.db import save_consent, get_consents
from src.utils import require


# ============================
# CONSENT TYPES
# ============================

CONSENT_TYPES = {
    "QUESTIONNAIRE": "Consent to use questionnaire responses",
    "VIDEO": "Consent to process home videos",
    "LONGITUDINAL": "Consent for longitudinal progress tracking",
    "RESEARCH": "Consent to use anonymized data for research"
}


# ============================
# CONSENT MANAGEMENT
# ============================

def grant_consent(case_id: str, consent_type: str):
    require(
        consent_type in CONSENT_TYPES,
        f"Invalid consent type: {consent_type}"
    )
    save_consent(case_id, consent_type, True)


def revoke_consent(case_id: str, consent_type: str):
    require(
        consent_type in CONSENT_TYPES,
        f"Invalid consent type: {consent_type}"
    )
    save_consent(case_id, consent_type, False)


def get_consent_status(case_id: str) -> Dict[str, bool]:
    """
    Returns consent status for all consent types.
    Missing consents default to False.
    """
    existing = get_consents(case_id)
    return {
        consent_type: existing.get(consent_type, False)
        for consent_type in CONSENT_TYPES
    }


# ============================
# SAFETY CHECKS
# ============================

def require_consent(case_id: str, consent_type: str):
    """
    Enforce consent before sensitive operations.
    Raises ValueError if consent is missing.
    """
    consents = get_consent_status(case_id)
    require(
        consents.get(consent_type, False),
        f"Consent required for action: {CONSENT_TYPES.get(consent_type, consent_type)}"
    )
