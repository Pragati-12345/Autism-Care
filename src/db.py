"""
Database layer for the Autism Predictive Care Platform.

This module owns:
- Schema creation
- CRUD operations
- Audit logging
- JSON-safe persistence

SQLite is used for hackathon simplicity and portability.
"""

import sqlite3
from typing import Dict, Any, List, Optional

from src.config import DATABASE_PATH, ENABLE_AUDIT_LOGGING
from src.utils import utc_now_iso, json_dumps_safe, json_loads_safe


# ============================
# CONNECTION
# ============================

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================
# SCHEMA INITIALIZATION
# ============================

def init_db():
    """Create all required tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()

    # --- CASES ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            created_at TEXT,
            child_age_months INTEGER,
            notes TEXT
        )
    """)

    # --- CONSENTS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS consents (
            case_id TEXT,
            consent_type TEXT,
            granted INTEGER,
            timestamp TEXT
        )
    """)

    # --- SCREENING RESULTS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS screening_results (
            case_id TEXT,
            risk_score REAL,
            risk_level TEXT,
            evidence_json TEXT,
            created_at TEXT
        )
    """)

    # --- THERAPY PLANS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS therapy_plans (
            case_id TEXT,
            plan_json TEXT,
            approved INTEGER,
            created_at TEXT
        )
    """)

    # --- WEEKLY PROGRESS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            case_id TEXT,
            week_number INTEGER,
            progress_score REAL,
            notes TEXT,
            timestamp TEXT
        )
    """)

    # --- DTFE FORECASTS ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dtfe_forecasts (
            case_id TEXT,
            forecast_json TEXT,
            created_at TEXT
        )
    """)

    # --- AUDIT LOG ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            timestamp TEXT,
            action TEXT,
            case_id TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()


# ============================
# AUDIT LOGGING
# ============================

def log_audit(action: str, case_id: str, details: Optional[Dict[str, Any]] = None):
    if not ENABLE_AUDIT_LOGGING:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO audit_log (timestamp, action, case_id, details)
        VALUES (?, ?, ?, ?)
    """, (
        utc_now_iso(),
        action,
        case_id,
        json_dumps_safe(details or {})
    ))

    conn.commit()
    conn.close()


# ============================
# CASES
# ============================

def create_case(case_id: str, child_age_months: int, notes: str = ""):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO cases (case_id, created_at, child_age_months, notes)
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        utc_now_iso(),
        child_age_months,
        notes
    ))

    conn.commit()
    conn.close()

    log_audit("CASE_CREATED", case_id, {"age_months": child_age_months})


def list_cases() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM cases").fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================
# CONSENTS
# ============================

def save_consent(case_id: str, consent_type: str, granted: bool):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO consents (case_id, consent_type, granted, timestamp)
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        consent_type,
        int(granted),
        utc_now_iso()
    ))

    conn.commit()
    conn.close()

    log_audit("CONSENT_UPDATED", case_id, {
        "type": consent_type,
        "granted": granted
    })


def get_consents(case_id: str) -> Dict[str, bool]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT consent_type, granted
        FROM consents
        WHERE case_id = ?
    """, (case_id,)).fetchall()

    conn.close()

    return {row["consent_type"]: bool(row["granted"]) for row in rows}


# ============================
# SCREENING
# ============================

def save_screening_result(
    case_id: str,
    risk_score: float,
    risk_level: str,
    evidence: Dict[str, Any]
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO screening_results
        (case_id, risk_score, risk_level, evidence_json, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        case_id,
        risk_score,
        risk_level,
        json_dumps_safe(evidence),
        utc_now_iso()
    ))

    conn.commit()
    conn.close()

    log_audit("SCREENING_COMPLETED", case_id, {
        "risk_level": risk_level,
        "risk_score": risk_score
    })


def get_latest_screening(case_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("""
        SELECT *
        FROM screening_results
        WHERE case_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    conn.close()

    if not row:
        return None

    data = dict(row)
    data["evidence"] = json_loads_safe(data.pop("evidence_json"))
    return data


# ============================
# THERAPY PLANS
# ============================

def save_therapy_plan(case_id: str, plan: Dict[str, Any], approved: bool):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO therapy_plans
        (case_id, plan_json, approved, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        json_dumps_safe(plan),
        int(approved),
        utc_now_iso()
    ))

    conn.commit()
    conn.close()

    log_audit("THERAPY_PLAN_SAVED", case_id, {
        "approved": approved
    })


def get_latest_therapy_plan(case_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("""
        SELECT *
        FROM therapy_plans
        WHERE case_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    conn.close()

    if not row:
        return None

    data = dict(row)
    data["plan"] = json_loads_safe(data.pop("plan_json"))
    data["approved"] = bool(data["approved"])
    return data


# ============================
# PROGRESS TRACKING
# ============================

def add_progress_log(
    case_id: str,
    week_number: int,
    progress_score: float,
    notes: str = ""
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO progress_logs
        (case_id, week_number, progress_score, notes, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        case_id,
        week_number,
        progress_score,
        notes,
        utc_now_iso()
    ))

    conn.commit()
    conn.close()

    log_audit("PROGRESS_LOGGED", case_id, {
        "week": week_number,
        "score": progress_score
    })


def get_progress_history(case_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT *
        FROM progress_logs
        WHERE case_id = ?
        ORDER BY week_number ASC
    """, (case_id,)).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================
# DTFE FORECASTS
# ============================

def save_dtfe_forecast(case_id: str, forecast: Dict[str, Any]):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO dtfe_forecasts
        (case_id, forecast_json, created_at)
        VALUES (?, ?, ?)
    """, (
        case_id,
        json_dumps_safe(forecast),
        utc_now_iso()
    ))

    conn.commit()
    conn.close()

    log_audit("DTFE_FORECAST_GENERATED", case_id)


def get_latest_dtfe_forecast(case_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("""
        SELECT *
        FROM dtfe_forecasts
        WHERE case_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (case_id,)).fetchone()

    conn.close()

    if not row:
        return None

    data = dict(row)
    data["forecast"] = json_loads_safe(data.pop("forecast_json"))
    return data
