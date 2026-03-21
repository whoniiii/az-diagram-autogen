#!/usr/bin/env python3
"""
Azure Architecture Diagram Generator v2 — using mingrammer/diagrams library.
Generates PNG architecture diagrams with official Azure icons.

Same CLI interface as generate_html_diagram.py (v1) for compatibility.

Prerequisites:
  pip install diagrams
  winget install Graphviz (or choco install graphviz)

Usage:
  python generate_html_diagram_v2.py \
    --services '[{"id":"svc1","name":"Name","type":"search","sku":"S1","private":true,"details":["detail1"]}]' \
    --connections '[{"from":"svc1","to":"svc2","label":"desc","type":"api"}]' \
    --title "Architecture Title" \
    --output "architecture.png"
"""

import argparse
import json
import sys
import os

try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.azure.ml import CognitiveServices
    from diagrams.azure.aimachinelearning import CognitiveSearch, AzureOpenai
    from diagrams.azure.compute import VM, AKS, AppServices as ComputeAppServices
    from diagrams.azure.database import CosmosDb, SQLServers, SQLDatabases, DataFactory
    from diagrams.azure.network import VirtualNetworks, Firewall, ApplicationGateway
    from diagrams.azure.security import KeyVaults
    from diagrams.azure.storage import DataLakeStorage
    from diagrams.azure.analytics import Databricks, AzureSynapseAnalytics, DataFactories
    from diagrams.azure.ml import MachineLearningServiceWorkspaces
    from diagrams.azure.web import AppServices
    from diagrams.azure.monitor import ApplicationInsights, LogAnalyticsWorkspaces
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}", file=sys.stderr)
    print("Install with: pip install diagrams", file=sys.stderr)
    print("Also need Graphviz: winget install Graphviz", file=sys.stderr)
    sys.exit(1)


# Service type → diagrams node class mapping
NODE_MAP = {
    "ai_foundry":     CognitiveServices,
    "ai_hub":         MachineLearningServiceWorkspaces,
    "openai":         AzureOpenai,
    "search":         CognitiveSearch,
    "storage":        DataLakeStorage,
    "keyvault":       KeyVaults,
    "fabric":         AzureSynapseAnalytics,
    "vm":             VM,
    "databricks":     Databricks,
    "sql_server":     SQLServers,
    "sql_database":   SQLDatabases,
    "cosmos_db":      CosmosDb,
    "app_service":    AppServices,
    "aks":            AKS,
    "function_app":   AppServices,
    "synapse":        AzureSynapseAnalytics,
    "adf":            DataFactories,
    "pe":             Firewall,     # no PE icon, use Firewall as proxy
    "vnet":           VirtualNetworks,
    "nsg":            Firewall,
    "bastion":        ApplicationGateway,
    "log_analytics":  LogAnalyticsWorkspaces,
    "app_insights":   ApplicationInsights,
    "default":        CognitiveServices,
}

# Connection type → Edge style
EDGE_STYLES = {
    "api":      {"color": "#0078D4", "style": "solid"},
    "data":     {"color": "#0F9D58", "style": "solid"},
    "security": {"color": "#E8A000", "style": "dashed"},
    "private":  {"color": "#5C2D91", "style": "dashed"},
    "network":  {"color": "#5C2D91", "style": "dotted"},
    "default":  {"color": "#999999", "style": "solid"},
}

# Category grouping
CATEGORY_MAP = {
    "ai_foundry": "AI", "ai_hub": "AI", "openai": "AI", "search": "AI",
    "storage": "Data", "fabric": "Data", "databricks": "Data",
    "sql_server": "Data", "sql_database": "Data", "cosmos_db": "Data",
    "synapse": "Data", "adf": "Data",
    "keyvault": "Security",
    "vm": "Compute", "aks": "Compute", "app_service": "Compute", "function_app": "Compute",
    "pe": "Network", "vnet": "Network", "nsg": "Network", "bastion": "Network",
    "log_analytics": "Monitoring", "app_insights": "Monitoring",
}


def get_node_class(svc_type: str):
    t = svc_type.lower().replace("-", "_").replace(" ", "_")
    return NODE_MAP.get(t, NODE_MAP["default"])


def get_category(svc_type: str) -> str:
    t = svc_type.lower().replace("-", "_").replace(" ", "_")
    return CATEGORY_MAP.get(t, "Azure")


def build_label(svc: dict) -> str:
    """Build a concise label for the node."""
    name = svc.get("name", svc["id"])
    sku = svc.get("sku", "")
    # Truncate long names
    if len(name) > 25:
        name = name[:22] + "..."
    if sku:
        return f"{name}\n({sku})"
    return name


def generate_diagram(services: list, connections: list, title: str, output: str, vnet_info: str = ""):
    """Generate a PNG diagram using the diagrams library."""

    # Separate PE nodes from service nodes
    pe_nodes = [s for s in services if s.get("type", "default") == "pe"]
    svc_nodes = [s for s in services if s.get("type", "default") != "pe" and s.get("type", "default") != "vnet"]
    vnet_nodes = [s for s in services if s.get("type", "default") == "vnet"]

    # Group services by category
    categories = {}
    for svc in svc_nodes:
        cat = get_category(svc.get("type", "default"))
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(svc)

    # Determine output format from extension
    out_base = os.path.splitext(output)[0]
    out_format = os.path.splitext(output)[1].lstrip(".") or "png"
    if out_format not in ("png", "svg", "pdf", "jpg"):
        out_format = "png"

    # Build diagram
    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "ranksep": "1.0",
        "nodesep": "0.8",
    }

    node_refs = {}  # id → diagrams node reference

    vnet_label = f"Virtual Network ({vnet_info})" if vnet_info else "Virtual Network"
    has_private = any(s.get("private", False) for s in svc_nodes) or len(pe_nodes) > 0

    with Diagram(title, filename=out_base, outformat=out_format, show=False,
                 direction="TB", graph_attr=graph_attr):

        if has_private:
            # Wrap everything in VNet cluster
            with Cluster(vnet_label, graph_attr={"style": "dashed", "color": "#5C2D91", "bgcolor": "#f8f7ff"}):

                # PE cluster
                if pe_nodes:
                    with Cluster("Private Endpoints", graph_attr={"style": "dashed", "color": "#d4b8ff", "bgcolor": "#f3eef9"}):
                        for pe in pe_nodes:
                            node_cls = get_node_class("pe")
                            label = build_label(pe)
                            node_refs[pe["id"]] = node_cls(label)

                # Service clusters by category
                for cat, svcs in categories.items():
                    with Cluster(cat, graph_attr={"style": "rounded", "color": "#e1dfdd", "bgcolor": "white"}):
                        for svc in svcs:
                            node_cls = get_node_class(svc.get("type", "default"))
                            label = build_label(svc)
                            node_refs[svc["id"]] = node_cls(label)
        else:
            # No VNet — flat layout with category clusters
            for cat, svcs in categories.items():
                with Cluster(cat, graph_attr={"style": "rounded", "color": "#e1dfdd", "bgcolor": "white"}):
                    for svc in svcs:
                        node_cls = get_node_class(svc.get("type", "default"))
                        label = build_label(svc)
                        node_refs[svc["id"]] = node_cls(label)

        # Draw connections
        for conn in connections:
            from_id = conn.get("from", "")
            to_id = conn.get("to", "")
            if from_id not in node_refs or to_id not in node_refs:
                continue

            conn_type = conn.get("type", "default")
            style = EDGE_STYLES.get(conn_type, EDGE_STYLES["default"])
            label = conn.get("label", "")

            node_refs[from_id] >> Edge(
                label=label,
                color=style["color"],
                style=style["style"],
            ) >> node_refs[to_id]

    actual_output = f"{out_base}.{out_format}"
    return actual_output


def main():
    parser = argparse.ArgumentParser(description="Azure Architecture Diagram Generator v2 (diagrams library)")
    parser.add_argument("--services", type=str, required=True)
    parser.add_argument("--connections", type=str, required=True)
    parser.add_argument("--title", type=str, default="Azure Architecture")
    parser.add_argument("--output", type=str, default="architecture.png")
    parser.add_argument("--vnet-info", type=str, default="",
                        help="VNet details for the boundary label")
    args = parser.parse_args()

    try:
        services = json.loads(args.services)
        connections = json.loads(args.connections)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Check Graphviz availability
    import shutil
    if not shutil.which("dot"):
        # Try common Windows paths
        gv_paths = [
            r"C:\Program Files\Graphviz\bin",
            r"C:\Program Files (x86)\Graphviz\bin",
        ]
        found = False
        for p in gv_paths:
            dot_path = os.path.join(p, "dot.exe")
            if os.path.exists(dot_path):
                os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")
                found = True
                break
        if not found:
            print("ERROR: Graphviz not found. Install with: winget install Graphviz", file=sys.stderr)
            sys.exit(1)

    output = generate_diagram(services, connections, args.title, args.output, args.vnet_info)
    print(f"SUCCESS: Diagram saved to {output}")


if __name__ == "__main__":
    main()
