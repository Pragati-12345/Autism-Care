"""
Progress Tracking and Trend Analysis Module.

Handles weekly progress updates, normalization,
trend detection, and stagnation alerts.

Feeds clean time-series data into DTFE.
"""

from typing import Dict, List

import numpy as np

from src.utils import clamp, require
from src.config import DTFE_PLATEAU_SLOPE_THRESHOLD


# ============================
# PROGRESS NORMALIZATION
# ============================

def normalize_progress(score: float) -> float:
    """
    Normalize raw progress score to [0, 100].

    Ensures consistency across sources.
    """
    return clamp(score, 0.0, 100.0)


# ============================
# TREND COMPUTATION
# ============================

def compute_trend(progress_history: List[Dict]) -> Dict:
    """
    Compute trend statistics from weekly progress history.

    Returns:
    - slope
    - direction
    - stagnation flag
    """

    require(
        len(progress_history) >= 2,
        "At least two progress points are required for trend analysis."
    )

    weeks = np.array([p["week_number"] for p in progress_history])
    scores = np.array([normalize_progress(p["progress_score"]) for p in progress_history])

    # Linear regression slope
    slope = np.polyfit(weeks, scores, 1)[0]

    if slope > DTFE_PLATEAU_SLOPE_THRESHOLD:
        direction = "IMPROVING"
    elif slope < -DTFE_PLATEAU_SLOPE_THRESHOLD:
        direction = "REGRESSING"
    else:
        direction = "PLATEAU"

    return {
        "slope": round(float(slope), 3),
        "direction": direction,
        "plateau_risk": direction == "PLATEAU"
    }


# ============================
# ALERTING
# ============================

def needs_attention(progress_history: List[Dict]) -> bool:
    """
    Determine whether clinician review is recommended.
    """

    if len(progress_history) < 4:
        return False  # too early

    trend = compute_trend(progress_history[-4:])
    return trend["plateau_risk"] or trend["direction"] == "REGRESSING"


# ============================
# DTFE INPUT PREP
# ============================

def prepare_dtfe_timeseries(progress_history: List[Dict]) -> List[Dict]:
    """
    Prepare clean time-series input for DTFE.
    """

    return [
        {
            "week": p["week_number"],
            "progress_score": normalize_progress(p["progress_score"])
        }
        for p in progress_history
    ]
