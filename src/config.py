"""
Global configuration for the Autism Predictive Care Platform.

This module should be the ONLY place that reads environment variables.
All other modules must import from here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ============================
# APPLICATION METADATA
# ============================

APP_NAME: str = os.getenv(
    "APP_NAME", "AI-Enabled Predictive Autism Care Platform"
)

ENV: str = os.getenv("ENV", "development")

# ============================
# SECURITY (DEMO-ONLY)
# ============================

# NOTE:
# This is intentionally simple for hackathon use.
# Do NOT use this authentication scheme in production.
CLINICIAN_PASSWORD: str = os.getenv(
    "CLINICIAN_PASSWORD", "demo_clinician_123"
)

# ============================
# DATA & STORAGE PATHS
# ============================

BASE_DIR: Path = Path(__file__).resolve().parent.parent

DATA_DIR: Path = BASE_DIR / os.getenv("DATA_DIR", "data")
DATABASE_PATH: Path = BASE_DIR / os.getenv(
    "DATABASE_PATH", "data/app.db"
)
MODEL_DIR: Path = BASE_DIR / os.getenv(
    "MODEL_DIR", "data/models"
)

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ============================
# PRIVACY & SAFETY DEFAULTS
# ============================

# Raw videos should NEVER be stored by default
DELETE_RAW_VIDEO: bool = os.getenv(
    "DELETE_RAW_VIDEO", "true"
).lower() == "true"

# ============================
# MODEL & ML DEFAULTS
# ============================

# Screening risk thresholds (conservative by design)
RISK_THRESHOLDS = {
    "LOW_MAX": 0.45,
    "MEDIUM_MAX": 0.75,
}

# DTFE parameters
DTFE_MIN_WEEKS_FOR_FORECAST: int = 4
DTFE_PLATEAU_SLOPE_THRESHOLD: float = 0.4  # weekly score increase

# ============================
# UI SETTINGS
# ============================

STREAMLIT_PAGE_CONFIG = {
    "page_title": APP_NAME,
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# ============================
# LOGGING / AUDIT
# ============================

ENABLE_AUDIT_LOGGING: bool = True
