
import networkx as nx


def build_infrastructure_graph(issues):
    """
    Build a graph connecting civic issues to their locations
    and related infrastructure.
    """

    graph = nx.Graph()

    for _, issue in issues.iterrows():
        issue_id = issue["id"]
        location = issue["location"]
        category = issue["category"]

        # Add the issue as a node.
        graph.add_node(
            issue_id,
            node_type="issue",
            label=issue["issue"],
            category=category,
            risk=issue["risk"],
        )

        # Add the location as a node.
        graph.add_node(
            location,
            node_type="location",
            label=location,
        )

        # Connect the issue to its location.
        graph.add_edge(
            issue_id,
            location,
            relationship="reported_at",
        )

    # Example infrastructure relationships.
    # These are hypothetical links for our prototype.
    related_infrastructure = [
        ("CF003", "CF005", "possible_shared_area"),
        ("CF001", "CF004", "nearby_road_network"),
    ]

    for source, target, relationship in related_infrastructure:
        if source in graph and target in graph:
            graph.add_edge(
                source,
                target,
                relationship=relationship,
            )

    return graph


def get_related_issues(graph, issue_id):
    """Return issues directly connected to a given issue."""

    if issue_id not in graph:
        return []

    related = []

    for neighbor in graph.neighbors(issue_id):
        if graph.nodes[neighbor].get("node_type") == "issue":
            related.append({
                "id": neighbor,
                "issue": graph.nodes[neighbor].get("label"),
                "relationship": graph.edges[issue_id, neighbor].get(
                    "relationship"
                ),
            })

    return related
