
def optimize_repair_budget(issues, budget):
    """
    Select repairs that maximize total priority score
    without exceeding the available budget.
    """

    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    candidates = issues[
        (issues["status"] != "Resolved")
        & (issues["repair_cost"] > 0)
        & (issues["repair_cost"] <= budget)
    ].copy()

    if candidates.empty:
        return candidates, 0.0

    # Dynamic programming: budget is measured in rupees.
    # Scale costs to whole rupees for the DP table.
    capacity = int(budget)
    dp = [0.0] * (capacity + 1)
    decisions = []

    for _, issue in candidates.iterrows():
        cost = int(issue["repair_cost"])
        score = float(issue["priority_score"])
        decisions.append((issue["id"], cost, score))

    # Store the best score attainable for each budget.
    for _, cost, score in decisions:
        for available in range(capacity, cost - 1, -1):
            dp[available] = max(
                dp[available],
                dp[available - cost] + score,
            )

    # Recover one optimal selection using a second DP table.
    n = len(decisions)
    table = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    for i, (_, cost, score) in enumerate(decisions, start=1):
        for available in range(capacity + 1):
            table[i][available] = table[i - 1][available]

            if cost <= available:
                table[i][available] = max(
                    table[i][available],
                    table[i - 1][available - cost] + score,
                )

    selected_ids = []
    available = capacity

    for i in range(n, 0, -1):
        if table[i][available] > table[i - 1][available]:
            issue_id, cost, _ = decisions[i - 1]
            selected_ids.append(issue_id)
            available -= cost

    selected = candidates[
        candidates["id"].isin(selected_ids)
    ].copy()

    selected["priority_score"] = selected["priority_score"].astype(float)

    total_cost = float(selected["repair_cost"].sum())

    return selected, total_cost
