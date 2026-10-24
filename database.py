
import sqlite3
import pandas as pd

DB_NAME = "civicfix.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id TEXT PRIMARY KEY,
                issue TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                severity INTEGER NOT NULL,
                people_affected INTEGER NOT NULL,
                risk INTEGER NOT NULL,
                repair_cost REAL NOT NULL,
                days_waiting INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'Open'
            )
        """)


def save_issue(issue):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO issues (
                id, issue, location, category, severity,
                people_affected, risk, repair_cost,
                days_waiting, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                issue = excluded.issue,
                location = excluded.location,
                category = excluded.category,
                severity = excluded.severity,
                people_affected = excluded.people_affected,
                risk = excluded.risk,
                repair_cost = excluded.repair_cost,
                days_waiting = excluded.days_waiting,
                status = excluded.status
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


def load_saved_issues():
    initialize_database()

    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM issues ORDER BY id",
            conn,
        )

def update_issue_status(issue_id, new_status):
    allowed_statuses = ["Open", "In Progress", "Resolved"]

    if new_status not in allowed_statuses:
        raise ValueError("Invalid issue status")

    with get_connection() as conn:
        conn.execute(
            "UPDATE issues SET status = ? WHERE id = ?",
            (new_status, issue_id),
        )
