"""
Shared utility helpers used across the platform.
Keep this file dependency-light and deterministic.
"""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict


# ============================
# TIME UTILITIES
# ============================

def utc_now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def epoch_ms() -> int:
    """Return current time in milliseconds since epoch."""
    return int(time.time() * 1000)


# ============================
# ID GENERATION
# ============================

def generate_case_id(prefix: str = "CASE") -> str:
    """
    Generate a readable, collision-resistant case ID.

    Example:
        CASE-1700000000000-a3f9c2
    """
    short_uuid = uuid.uuid4().hex[:6]
    return f"{prefix}-{epoch_ms()}-{short_uuid}"


# ============================
# JSON HELPERS
# ============================

def json_dumps_safe(obj: Any) -> str:
    """
    Serialize object to JSON safely.
    Converts non-serializable objects to string.
    """
    return json.dumps(obj, default=str, ensure_ascii=False)


def json_loads_safe(data: str | None) -> Dict[str, Any]:
    """
    Safely load JSON string into dict.
    Returns empty dict if input is None or invalid.
    """
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}


# ============================
# VALIDATION HELPERS
# ============================

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value to a given range."""
    return max(min_value, min(value, max_value))


def is_probability(value: float) -> bool:
    """Check if value is a valid probability."""
    return 0.0 <= value <= 1.0


# ============================
# SAFETY / ASSERTIONS
# ============================

def require(condition: bool, message: str):
    """
    Raise a ValueError if condition is False.
    Used for defensive programming.
    """
    if not condition:
        raise ValueError(message)
