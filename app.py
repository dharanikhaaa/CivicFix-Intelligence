from database import initialize_database, save_issue, load_saved_issues
import streamlit as st
import pandas as pd

from data import load_issues
from optimizer import calculate_priority
from graph_model import build_infrastructure_graph, get_related_issues


st.set_page_config(
    page_title="CivicFix",
    page_icon="🏙️",
    layout="wide",
)

st.title("🏙️ CivicFix")
st.subheader("Smart Public Issue Tracking and Prioritization")

st.markdown(
    "Track civic issues, identify urgent problems, "
    "and help prioritize public infrastructure repairs."
)

# Load sample data and calculate priorities.

initialize_database()

sample_issues = load_issues()
saved_issues = load_saved_issues()

issues = pd.concat(
    [sample_issues, saved_issues],
    ignore_index=True,
).drop_duplicates(subset="id", keep="last")

if "submitted_issues" in st.session_state:
    new_issues = pd.DataFrame(st.session_state.submitted_issues)
    issues = pd.concat([issues, new_issues], ignore_index=True)

ranked_issues = calculate_priority(issues)
graph = build_infrastructure_graph(issues)


# Complaint submission form
st.sidebar.divider()
st.sidebar.subheader("Report a Civic Issue")

with st.sidebar.form("report_issue_form", clear_on_submit=True):
    issue_name = st.text_input("Issue title")
    location_name = st.text_input("Location")

    category_name = st.selectbox(
        "Category",
        ["Road", "Lighting", "Drainage", "Footpath", "Water", "Other"],
    )

    severity_value = st.slider(
        "Severity",
        min_value=1,
        max_value=5,
        value=3,
    )

    people_value = st.number_input(
        "People affected",
        min_value=1,
        value=10,
    )

    risk_value = st.slider(
        "Safety risk",
        min_value=1,
        max_value=5,
        value=3,
    )

    cost_value = st.number_input(
        "Estimated repair cost (₹)",
        min_value=0,
        value=5000,
        step=500,
    )

    submitted = st.form_submit_button("Submit Issue")

    
    if submitted:
        if issue_name.strip() and location_name.strip():
            next_number = len(st.session_state.get("submitted_issues", [])) + 6

            new_issue = {
                "id": f"CF{next_number:03d}",
                "issue": issue_name.strip(),
                "location": location_name.strip(),
                "category": category_name,
                "severity": severity_value,
                "people_affected": people_value,
                "risk": risk_value,
                "repair_cost": cost_value,
                "days_waiting": 0,
                "status": "Open",
            }

            save_issue(new_issue)

            if "submitted_issues" not in st.session_state:
                st.session_state.submitted_issues = []

            st.session_state.submitted_issues.append(new_issue)
            st.sidebar.success("Issue saved permanently!")
        else:
            st.sidebar.error("Enter both the issue title and location.")


# Sidebar navigation and filters.
st.sidebar.title("CivicFix Navigation")

page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Issue Explorer",
        "Infrastructure Network",
        "About",
    ],
)

categories = ["All"] + sorted(issues["category"].unique().tolist())

selected_category = st.sidebar.selectbox(
    "Filter by category",
    categories,
)

filtered = ranked_issues.copy()

if selected_category != "All":
    filtered = filtered[
        filtered["category"] == selected_category
    ]

# Dashboard.
if page == "Dashboard":
    st.header("Civic Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Issues", len(issues))
    col2.metric(
        "Open Issues",
        len(issues[issues["status"] == "Open"]),
    )
    col3.metric(
        "High-Risk Issues",
        len(issues[issues["risk"] >= 4]),
    )
    col4.metric(
        "People Affected",
        int(issues["people_affected"].sum()),
    )

    st.divider()

    st.subheader("🚨 Repair Priority Ranking")

    display_columns = [
        "priority_rank",
        "id",
        "issue",
        "location",
        "category",
        "priority_score",
        "risk",
        "days_waiting",
    ]

    st.dataframe(
        filtered[display_columns].round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Priority scores are prototype estimates based on "
        "sample data, not official municipal decisions."
    )

    st.subheader("Issues by Category")

    category_counts = issues["category"].value_counts()
    st.bar_chart(category_counts)

# Issue Explorer.
elif page == "Issue Explorer":
    st.header("🔎 Issue Explorer")

    selected_id = st.selectbox(
        "Select a civic issue",
        filtered["id"].tolist(),
    )

    if selected_id:
        issue = issues[issues["id"] == selected_id].iloc[0]
        ranked = ranked_issues[
            ranked_issues["id"] == selected_id
        ].iloc[0]

        st.subheader(issue["issue"])

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Issue ID:**", issue["id"])
            st.write("**Location:**", issue["location"])
            st.write("**Category:**", issue["category"])
            st.write("**Status:**", issue["status"])

        with col2:
            st.metric(
                "Priority Score",
                f"{ranked['priority_score']:.2f}/100",
            )
            st.metric("Safety Risk", f"{issue['risk']}/5")
            st.metric(
                "People Affected",
                int(issue["people_affected"]),
            )

        st.write("**Estimated Repair Cost:**",
                 f"₹{issue['repair_cost']:,}")

        st.write("**Days Waiting:**", issue["days_waiting"])

        st.subheader("Related Infrastructure Issues")

        related = get_related_issues(graph, selected_id)

        if related:
            st.dataframe(
                pd.DataFrame(related),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No directly connected issues found.")

# Infrastructure Network.
elif page == "Infrastructure Network":
    st.header("🕸️ Infrastructure Network")

    st.write(
        "Explore connections between reported issues. "
        "The example relationships are hypothetical."
    )

    graph_data = []

    for source, target, attributes in graph.edges(data=True):
        graph_data.append({
            "Source": str(source),
            "Relationship": attributes.get("relationship", "connected"),
            "Connected To": str(target),
        })

    st.dataframe(
        pd.DataFrame(graph_data),
        use_container_width=True,
        hide_index=True,
    )

    st.write("**Graph nodes:**", graph.number_of_nodes())
    st.write("**Graph connections:**", graph.number_of_edges())

# About.
elif page == "About":
    st.header("About CivicFix")

    st.write(
        "CivicFix is a prototype public issue tracking system "
        "designed to organize infrastructure complaints and "
        "estimate repair priorities."
    )

    st.markdown("""
    **Current features**
    - Civic issue dashboard
    - Weighted repair-priority scoring
    - Category filtering
    - Issue details and related-issue lookup
    - Infrastructure relationship table

    **Prototype limitations**
    - Uses fictional sample data
    - Does not yet accept or store new public reports
    - Does not connect to municipal systems
    - Does not verify infrastructure relationships
    """)
