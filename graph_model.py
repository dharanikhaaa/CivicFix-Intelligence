
import networkx as nx


def build_infrastructure_graph(issues):
    """Build a graph connecting civic issues to locations."""
    graph = nx.Graph()

    # Add issue and location nodes.
    for _, issue in issues.iterrows():
        issue_id = str(issue["id"])
        location = " ".join(
            str(issue["location"]).strip().lower().split()
        )

        graph.add_node(issue_id, node_type="issue")
        graph.add_node(location, node_type="location")

        graph.add_edge(
            issue_id,
            location,
            relationship="reported_at",
        )

    # Add hypothetical relationships between nearby issues.
    issue_nodes = [
        node
        for node, attributes in graph.nodes(data=True)
        if attributes.get("node_type") == "issue"
    ]

    for i in range(len(issue_nodes) - 1):
        graph.add_edge(
            issue_nodes[i],
            issue_nodes[i + 1],
            relationship="related_issue",
        )

    return graph


def get_related_issues(graph, issue_id):
    """Return neighboring nodes connected to an issue."""
    if issue_id not in graph:
        return []

    return list(graph.neighbors(issue_id))
