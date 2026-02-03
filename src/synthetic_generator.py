"""
Grounded Synthetic Data Generator for Autism Care Trajectories.

This module generates synthetic but realistic longitudinal data
for developmental progress, grounded in population-level assumptions.

NO real patient data is used or recreated.
"""

import random
import numpy as np
from typing import Dict, List


# ============================
# GLOBAL CONSTRAINTS
# ============================

# Progress score is normalized [0, 100]
MIN_PROGRESS = 0.0
MAX_PROGRESS = 100.0

# Weekly noise scale by age group (younger children show more variability)
AGE_NOISE = {
    "infant": 2.5,     # < 24 months
    "toddler": 2.0,    # 24–36 months
    "child": 1.5       # > 36 months
}

# Diminishing returns factor
DIMINISHING_RETURN_FACTOR = 0.015


# ============================
# HELPERS
# ============================

def _age_group(age_months: int) -> str:
    if age_months < 24:
        return "infant"
    elif age_months < 36:
        return "toddler"
    return "child"


def _clamp(value: float) -> float:
    return max(MIN_PROGRESS, min(MAX_PROGRESS, value))


# ============================
# CORE GENERATOR
# ============================

def generate_child_profile(seed: int = None) -> Dict:
    """
    Generate a synthetic child profile.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    age_months = random.randint(12, 60)

    return {
        "age_months": age_months,
        "baseline_progress": random.uniform(5, 25),
        "therapy_intensity": random.choice([1, 2, 3]),  # sessions per week
        "adherence": random.uniform(0.6, 0.95)
    }


def generate_longitudinal_progress(
    profile: Dict,
    weeks: int = 16,
    intervention_change_week: int = None,
    new_therapy_intensity: int = None
) -> List[Dict]:
    """
    Generate weekly progress trajectory for a child.
    Optionally simulates therapy change.
    """

    age_grp = _age_group(profile["age_months"])
    noise_scale = AGE_NOISE[age_grp]

    progress = profile["baseline_progress"]
    therapy_intensity = profile["therapy_intensity"]
    adherence = profile["adherence"]

    trajectory = []

    for week in range(1, weeks + 1):

        # Simulate therapy adjustment
        if intervention_change_week and week == intervention_change_week:
            therapy_intensity = new_therapy_intensity or therapy_intensity

        # Core growth function
        base_gain = therapy_intensity * adherence * 2.5

        # Diminishing returns as progress increases
        diminishing = 1 - (progress * DIMINISHING_RETURN_FACTOR)

        # Random developmental noise
        noise = np.random.normal(0, noise_scale)

        weekly_gain = base_gain * diminishing + noise

        # Plateau effect
        if weekly_gain < 0.3:
            weekly_gain *= 0.5

        progress = _clamp(progress + weekly_gain)

        trajectory.append({
            "week": week,
            "progress_score": round(progress, 2),
            "therapy_intensity": therapy_intensity,
            "adherence": round(adherence, 2)
        })

    return trajectory


# ============================
# COHORT GENERATION
# ============================

def generate_synthetic_cohort(
    size: int = 50,
    weeks: int = 16,
    seed: int = 42
) -> List[Dict]:
    """
    Generate a cohort of synthetic children with longitudinal data.
    """

    random.seed(seed)
    np.random.seed(seed)

    cohort = []

    for i in range(size):
        profile = generate_child_profile(seed + i)
        trajectory = generate_longitudinal_progress(profile, weeks)

        cohort.append({
            "child_id": f"SYNTH-{i+1}",
            "profile": profile,
            "trajectory": trajectory
        })

    return cohort
