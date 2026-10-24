from database import update_issue_status
from duplicate_detector import find_possible_duplicates
from budget_optimizer import optimize_repair_budget
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

# --- CivicFix Smart City Theme ---
st.markdown("""
<style>
    /* Main application */
    .stApp {
        background: linear-gradient(135deg, #0B1220 0%, #111C32 100%);
        color: #F1F5F9;
    }

    /* General text visibility */
    .stApp,
    .stApp p,
    .stApp label,
    .stApp span,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"] {
        color: #E2E8F0;
    }

    h1, h2, h3, h4 {
        color: #F8FAFC !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #080F1D;
        border-right: 1px solid #263650;
    }

    [data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #17243A;
        border: 1px solid #2B3D58;
        padding: 18px;
        border-radius: 14px;
    }

    [data-testid="stMetricLabel"] {
        color: #CBD5E1 !important;
    }

    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #4ADE80 !important;
    }

    /* Inputs */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #17243A;
        color: #F8FAFC;
        border-color: #475569;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: #1687F8;
        color: #FFFFFF !important;
        border: 1px solid #1687F8;
        border-radius: 9px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #F59E0B;
        color: #111827 !important;
        border-color: #F59E0B;
    }

    /* Dataframes and tables */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background: #111C32 !important;
        border: 1px solid #334155;
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {
        color: #E2E8F0;
    }

    /* Links */
    .stApp a {
        color: #38BDF8 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #111C32;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #CBD5E1;
    }

    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #38BDF8 !important;
    }

    /* Dividers */
    hr {
        border-color: #334155;
    }
</style>
""", unsafe_allow_html=True)


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
    if not issue_name.strip() or not location_name.strip():
        st.sidebar.error("Enter both the issue title and location.")

    else:
        # Generate an ID higher than existing CF issue IDs.
        existing_numbers = [
            int(str(issue_id)[2:])
            for issue_id in issues["id"].tolist()
            if str(issue_id).startswith("CF")
            and str(issue_id)[2:].isdigit()
        ]

        next_number = max(existing_numbers, default=0) + 1

        new_issue = {
            "id": f"CF{next_number:03d}",
            "issue": issue_name.strip(),
            "location": location_name.strip(),
            "category": category_name,
            "severity": severity_value,
            "people_affected": int(people_value),
            "risk": risk_value,
            "repair_cost": float(cost_value),
            "days_waiting": 0,
            "status": "Open",
        }

        # Check for likely duplicates before saving.
        possible_duplicates = find_possible_duplicates(
            new_issue,
            issues,
        )

        if possible_duplicates:
            st.sidebar.warning(
                "Duplicate detected! This complaint was not saved."
            )
            st.sidebar.dataframe(
                pd.DataFrame(possible_duplicates),
                hide_index=True,
            )

        else:
            # The database performs a second duplicate check.
            saved = save_issue(new_issue)

            if saved:
                st.sidebar.success(
                    "Issue submitted and saved successfully!"
                )
                st.rerun()
            else:
                st.sidebar.warning(
                    "This complaint already exists and was not saved."
                )

# Sidebar navigation and filters.
st.sidebar.title("CivicFix Navigation")


page = st.sidebar.radio(
    "Choose a page",
    [
        "Dashboard",
        "Issue Explorer",
        "Infrastructure Network",
        "Manage Issues",
        "Budget Optimizer",
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
        "Explore connections between reported civic issues "
        "and infrastructure locations. Example relationships "
        "between issues are hypothetical."
    )

    import matplotlib.pyplot as plt
    import networkx as nx

    if graph.number_of_nodes() == 0:
        st.info("No network data is available yet.")
    else:
        fig, ax = plt.subplots(figsize=(16, 10))

        pos = nx.spring_layout(
            graph,
            seed=42,
            k=2.0,
            iterations=100,
        )

        node_colors = []
        for node in graph.nodes():
            if str(node).startswith("CF"):
                node_colors.append("tomato")
            else:
                node_colors.append("skyblue")

        nx.draw_networkx(
            graph,
            pos,
            ax=ax,
            with_labels=True,
            node_color=node_colors,
            node_size=1400,
            font_size=9,
            font_weight="bold",
            edge_color="gray",
            width=1.5,
        )

        edge_labels = {
            (source, target): attributes.get(
                "relationship", "connected"
            )
            for source, target, attributes in graph.edges(data=True)
        }

        nx.draw_networkx_edge_labels(
            graph,
            pos,
            edge_labels=edge_labels,
            ax=ax,
            font_size=7,
        )

        ax.set_axis_off()
        st.pyplot(fig)
        plt.close(fig)

        st.caption(
            "Red nodes represent issue IDs; blue nodes represent "
            "locations. Relationship labels describe the connections."
        )

    st.subheader("Connection Details")

    graph_data = [
        {
            "Source": str(source),
            "Relationship": attributes.get("relationship", "connected"),
            "Connected To": str(target),
        }
        for source, target, attributes in graph.edges(data=True)
    ]

    if graph_data:
        st.dataframe(
            pd.DataFrame(graph_data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No connections to display.")

    col1, col2 = st.columns(2)
    col1.metric("Graph Nodes", graph.number_of_nodes())
    col2.metric("Graph Connections", graph.number_of_edges())

# About.

elif page == "Manage Issues":
    st.header("Manage Civic Issues")
    st.write("Update the progress of reported complaints.")

    if issues.empty:
        st.info("No issues available.")
    else:
        selected_id = st.selectbox(
            "Select issue",
            issues["id"].tolist(),
            key="manage_issue_id",
        )

        selected_issue = issues[
            issues["id"] == selected_id
        ].iloc[0]

        st.write("**Issue:**", selected_issue["issue"])
        st.write("**Location:**", selected_issue["location"])
        st.write("**Current status:**", selected_issue["status"])

        statuses = ["Open", "In Progress", "Resolved"]

        current_status = selected_issue["status"]
        default_index = (
            statuses.index(current_status)
            if current_status in statuses
            else 0
        )

        new_status = st.selectbox(
            "New status",
            statuses,
            index=default_index,
        )

        if st.button("Save Status"):
            if selected_id in saved_issues["id"].values:
                update_issue_status(selected_id, new_status)
                st.success("Status updated successfully!")
                st.rerun()
            else:
                st.warning(
                    "This is a sample issue. Status updates are "
                    "available only for saved database complaints."
                )

elif page == "Budget Optimizer":
    st.header("Municipal Repair Budget Optimizer")

    st.write(
        "Select a budget to find a combination of repairs "
        "with the highest combined priority score."
    )

    budget = st.number_input(
        "Available repair budget (₹)",
        min_value=0,
        value=20000,
        step=1000,
    )

    if st.button("Optimize Repairs"):
        selected, total_cost = optimize_repair_budget(
            ranked_issues,
            budget,
        )

        if selected.empty:
            st.warning(
                "No eligible repairs fit within this budget."
            )
        else:
            st.subheader("Recommended Repairs")

            st.dataframe(
                selected[
                    ["id", "issue", "location",
                     "repair_cost", "priority_score"]
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.metric(
                "Total Estimated Cost",
                f"₹{total_cost:,.0f}",
            )

            st.metric(
                "Remaining Budget",
                f"₹{budget - total_cost:,.0f}",
            )

            st.metric(
                "Repairs Selected",
                len(selected),
            )

            st.caption(
                "This is a prototype recommendation. "
                "Safety-critical emergencies should be handled "
                "according to emergency procedures, regardless "
                "of the optimization score."
            )

elif page == "About":
    st.header("About CivicFix")

    st.write(
        "CivicFix organizes public infrastructure complaints, "
        "estimates repair priorities, and tracks issue progress."
    )

    st.markdown("""
    **Current features**
    - Civic issue dashboard
    - Weighted repair-priority scoring
    - Category filtering
    - Complaint submission
    - SQLite storage for submitted complaints
    - Issue status management
    - Infrastructure relationship modeling
    """)
