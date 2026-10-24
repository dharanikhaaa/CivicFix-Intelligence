
def calculate_priority(issues):
    """
    Calculate a priority score for each civic issue.
    Higher scores mean the issue should be considered sooner.
    """

    issues = issues.copy()

    # Normalize the values to a scale of 0 to 1.
    severity_score = issues["severity"] / 5
    people_score = issues["people_affected"] / max(
        issues["people_affected"].max(), 1
    )
    risk_score = issues["risk"] / 5
    waiting_score = issues["days_waiting"] / max(
        issues["days_waiting"].max(), 1
    )

    # Lower repair costs receive a higher affordability score.
    max_cost = max(issues["repair_cost"].max(), 1)
    affordability_score = 1 - (
        issues["repair_cost"] / max_cost
    )

    # Weighted priority score out of 100.
    issues["priority_score"] = 100 * (
        0.30 * severity_score
        + 0.25 * people_score
        + 0.25 * risk_score
        + 0.10 * waiting_score
        + 0.10 * affordability_score
    )

    # Sort the highest-priority issue first.
    issues = issues.sort_values(
        by="priority_score",
        ascending=False
    ).reset_index(drop=True)

    issues["priority_rank"] = issues.index + 1

    return issues
