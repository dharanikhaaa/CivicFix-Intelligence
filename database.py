
import streamlit as st
import pandas as pd
import psycopg


def get_connection():
    """Connect to the Supabase PostgreSQL database."""
    database_url = st.secrets["SUPABASE_DB_URL"]
    return psycopg.connect(database_url)


def initialize_database():
    """Create the issues table if it does not exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS public.issues (
                id TEXT PRIMARY KEY,
                issue TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                severity INTEGER NOT NULL,
                people_affected INTEGER NOT NULL,
                risk INTEGER NOT NULL,
                repair_cost DOUBLE PRECISION NOT NULL,
                days_waiting INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'Open'
            )
        """)


def save_issue(issue):
    """Save a complaint, rejecting duplicate reports."""
    initialize_database()

    with get_connection() as conn:
        duplicate = conn.execute("""
            SELECT 1
            FROM public.issues
            WHERE LOWER(TRIM(issue)) = LOWER(TRIM(%s))
              AND LOWER(TRIM(location)) = LOWER(TRIM(%s))
              AND LOWER(TRIM(category)) = LOWER(TRIM(%s))
            LIMIT 1
        """, (
            issue["issue"],
            issue["location"],
            issue["category"],
        )).fetchone()

        if duplicate:
            return False

        conn.execute("""
            INSERT INTO public.issues (
                id, issue, location, category, severity,
                people_affected, risk, repair_cost,
                days_waiting, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            issue["id"],
            issue["issue"],
            issue["location"],
            issue["category"],
            issue["severity"],
            issue["people_affected"],
            issue["risk"],
            issue["repair_cost"],
            issue["days_waiting"],
            issue["status"],
        ))

        saved = conn.execute(
            "SELECT 1 FROM public.issues WHERE id = %s",
            (issue["id"],),
        ).fetchone()

        return saved is not None


def load_saved_issues():
    """Load complaints from Supabase into a DataFrame."""
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM public.issues
            ORDER BY id
        """).fetchall()

        columns = [
            "id", "issue", "location", "category", "severity",
            "people_affected", "risk", "repair_cost",
            "days_waiting", "status",
        ]

        return pd.DataFrame(rows, columns=columns)


def update_issue_status(issue_id, new_status):
    """Update a complaint's status."""
    allowed_statuses = ["Open", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid issue status")

    with get_connection() as conn:
        conn.execute("""
            UPDATE public.issues
            SET status = %s
            WHERE id = %s
        """, (new_status, issue_id))
