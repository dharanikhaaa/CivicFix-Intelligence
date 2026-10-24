
import pandas as pd


def load_issues():
    """Return sample public infrastructure issues."""

    issues = [
        {
            "id": "CF001",
            "issue": "Large pothole",
            "location": "Main Road",
            "category": "Road",
            "severity": 5,
            "people_affected": 120,
            "risk": 5,
            "repair_cost": 15000,
            "days_waiting": 12,
            "status": "Open",
        },
        {
            "id": "CF002",
            "issue": "Broken streetlight",
            "location": "Bus Stop",
            "category": "Lighting",
            "severity": 3,
            "people_affected": 80,
            "risk": 4,
            "repair_cost": 3000,
            "days_waiting": 7,
            "status": "Open",
        },
        {
            "id": "CF003",
            "issue": "Overflowing drain",
            "location": "Market Street",
            "category": "Drainage",
            "severity": 4,
            "people_affected": 200,
            "risk": 5,
            "repair_cost": 8000,
            "days_waiting": 5,
            "status": "Open",
        },
        {
            "id": "CF004",
            "issue": "Damaged footpath",
            "location": "School Road",
            "category": "Footpath",
            "severity": 3,
            "people_affected": 100,
            "risk": 3,
            "repair_cost": 5000,
            "days_waiting": 20,
            "status": "Open",
        },
        {
            "id": "CF005",
            "issue": "Water pipe leakage",
            "location": "Lake Road",
            "category": "Water",
            "severity": 4,
            "people_affected": 150,
            "risk": 4,
            "repair_cost": 10000,
            "days_waiting": 3,
            "status": "Open",
        },
    ]

    return pd.DataFrame(issues)
