"""
Screening and explainability module.

Provides conservative, explainable screening decision support
using questionnaire inputs and optional behavioral features.

NOT a diagnostic system.
"""

import os
import pickle
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.config import MODEL_DIR, RISK_THRESHOLDS
from src.utils import clamp, require

MODEL_PATH = MODEL_DIR / "screening_model.pkl"


# ============================
# MODEL TRAINING (BASELINE)
# ============================

def _train_baseline_model() -> Pipeline:
    """
    Train a simple, explainable baseline screening model.

    This uses synthetic-but-reasonable questionnaire data
    to bootstrap a screening model for demo purposes.
    """

    np.random.seed(42)

    n = 500

    # Synthetic questionnaire features
    data = pd.DataFrame({
        "eye_contact": np.random.binomial(1, 0.6, n),
        "response_to_name": np.random.binomial(1, 0.65, n),
        "joint_attention": np.random.binomial(1, 0.55, n),
        "gestures": np.random.binomial(1, 0.6, n),
        "sensory_sensitivity": np.random.binomial(1, 0.4, n),
        "language_delay": np.random.binomial(1, 0.35, n),
    })

    # Risk label (higher probability with multiple red flags)
    risk_score = (
        1 - data.mean(axis=1)
        + np.random.normal(0, 0.05, n)
    )
    y = (risk_score > 0.55).astype(int)

    model = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=500))
    ])

    model.fit(data, y)
    return model


def load_or_train_model() -> Pipeline:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)

    model = _train_baseline_model()
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    return model


# ============================
# RISK SCORING
# ============================

def compute_risk(
    questionnaire: Dict[str, int],
    video_features: Dict[str, float] | None = None
) -> Tuple[float, str, Dict]:
    """
    Compute risk score, tier, and evidence.

    questionnaire: binary features (0/1)
    video_features: optional behavioral signals (demo-safe)
    """

    require(
        questionnaire and isinstance(questionnaire, dict),
        "Questionnaire data is required for screening."
    )

    model = load_or_train_model()

    # Prepare input
    df = pd.DataFrame([questionnaire])

    # Ensure column order consistency
    df = df[model.feature_names_in_]

    prob = model.predict_proba(df)[0, 1]
    prob = clamp(float(prob), 0.0, 1.0)

    # Risk tiering (conservative)
    if prob <= RISK_THRESHOLDS["LOW_MAX"]:
        risk_level = "LOW"
    elif prob <= RISK_THRESHOLDS["MEDIUM_MAX"]:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Explainability (coefficient-based)
    clf = model.named_steps["clf"]
    coefs = clf.coef_[0]

    evidence = {
        "risk_probability": round(prob, 3),
        "top_contributors": sorted(
            [
                {
                    "feature": feature,
                    "value": questionnaire.get(feature, 0),
                    "weight": round(weight, 3)
                }
                for feature, weight in zip(
                    model.feature_names_in_, coefs
                )
            ],
            key=lambda x: abs(x["weight"]),
            reverse=True
        )[:3],
        "notes": "Risk tier is probabilistic and for screening support only."
    }

    # Optional video signals (annotated, not decisive)
    if video_features:
        evidence["video_signals"] = video_features

    return prob, risk_level, evidence
