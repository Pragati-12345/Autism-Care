"""
Developmental Trajectory Forecasting Engine (DTFE).

Provides probabilistic forecasting of developmental progress
using longitudinal time-series data.

This module supports:
- Short-term forecasts
- Plateau risk detection
- What-if therapy simulations

DTFE outputs are advisory and require clinician interpretation.
"""

from typing import Dict, List

import numpy as np

from src.config import DTFE_MIN_WEEKS_FOR_FORECAST
from src.utils import require, clamp


# ============================
# CORE FORECASTING
# ============================

def forecast_progress(
    timeseries: List[Dict],
    forecast_weeks: int = 8
) -> Dict:
    """
    Forecast future developmental progress.

    Uses linear trend extrapolation with uncertainty bounds.
    """

    require(
        len(timeseries) >= DTFE_MIN_WEEKS_FOR_FORECAST,
        "Insufficient data for forecasting."
    )

    weeks = np.array([p["week"] for p in timeseries])
    scores = np.array([p["progress_score"] for p in timeseries])

    # Linear trend fit
    coeffs = np.polyfit(weeks, scores, 1)
    slope, intercept = coeffs

    future_weeks = np.arange(
        weeks[-1] + 1,
        weeks[-1] + forecast_weeks + 1
    )

    mean_forecast = slope * future_weeks + intercept

    # Uncertainty estimation
    residuals = scores - (slope * weeks + intercept)
    std = np.std(residuals) if len(residuals) > 1 else 2.0

    lower = mean_forecast - 1.96 * std
    upper = mean_forecast + 1.96 * std

    return {
        "forecast_weeks": forecast_weeks,
        "trend_slope": round(float(slope), 3),
        "mean_forecast": [
            round(clamp(v, 0, 100), 2) for v in mean_forecast
        ],
        "confidence_interval": {
            "lower": [
                round(clamp(v, 0, 100), 2) for v in lower
            ],
            "upper": [
                round(clamp(v, 0, 100), 2) for v in upper
            ]
        },
        "interpretation": (
            "Forecast represents probabilistic trajectory guidance "
            "based on recent progress trends."
        )
    }


# ============================
# PLATEAU RISK ANALYSIS
# ============================

def detect_plateau_risk(timeseries: List[Dict]) -> Dict:
    """
    Detect risk of developmental plateau.
    """

    require(
        len(timeseries) >= DTFE_MIN_WEEKS_FOR_FORECAST,
        "Insufficient data for plateau analysis."
    )

    weeks = np.array([p["week"] for p in timeseries])
    scores = np.array([p["progress_score"] for p in timeseries])

    slope = np.polyfit(weeks, scores, 1)[0]

    plateau = slope < 0.5

    return {
        "plateau_risk": plateau,
        "trend_slope": round(float(slope), 3),
        "message": (
            "Potential plateau detected. Consider reviewing therapy intensity."
            if plateau else
            "Progress trend appears on track."
        )
    }


# ============================
# WHAT-IF SIMULATION
# ============================

def simulate_therapy_adjustment(
    timeseries: List[Dict],
    intensity_multiplier: float = 1.2
) -> Dict:
    """
    Simulate effect of therapy intensity change.

    intensity_multiplier > 1 increases therapy
    intensity_multiplier < 1 decreases therapy
    """

    require(
        intensity_multiplier > 0,
        "Intensity multiplier must be positive."
    )

    base_forecast = forecast_progress(timeseries)

    adjusted_mean = [
        clamp(v * intensity_multiplier, 0, 100)
        for v in base_forecast["mean_forecast"]
    ]

    return {
        "intensity_multiplier": intensity_multiplier,
        "adjusted_forecast": [
            round(v, 2) for v in adjusted_mean
        ],
        "interpretation": (
            "Simulated outcome assuming proportional change "
            "in therapy intensity. Requires clinician judgment."
        )
    }


# ============================
# DTFE ORCHESTRATOR
# ============================

def run_dtfe(
    timeseries: List[Dict]
) -> Dict:
    """
    Run full DTFE analysis pipeline.
    """

    forecast = forecast_progress(timeseries)
    plateau = detect_plateau_risk(timeseries)

    return {
        "forecast": forecast,
        "plateau_analysis": plateau,
        "what_if_examples": {
            "+20% therapy": simulate_therapy_adjustment(timeseries, 1.2),
            "-20% therapy": simulate_therapy_adjustment(timeseries, 0.8)
        },
        "clinical_note": (
            "DTFE outputs are advisory and must be reviewed "
            "by a qualified clinician before any changes."
        )
    }
