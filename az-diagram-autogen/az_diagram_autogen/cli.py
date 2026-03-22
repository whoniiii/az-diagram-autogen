#!/usr/bin/env python3
"""CLI for azure-diagram-gen."""
import argparse
import json
import sys
import os
from .generator import generate_diagram


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive Azure architecture diagrams",
        prog="azure-diagram-gen"
    )
    parser.add_argument("-s", "--services", required=True, help="Services JSON (string or file path)")
    parser.add_argument("-c", "--connections", required=True, help="Connections JSON (string or file path)")
    parser.add_argument("-t", "--title", default="Azure Architecture", help="Diagram title")
    parser.add_argument("-o", "--output", default="azure-architecture.html", help="Output HTML file")
    parser.add_argument("--vnet-info", default="", help="VNet CIDR info")
    parser.add_argument("--hierarchy", default="", help="Subscription/RG hierarchy JSON")

    args = parser.parse_args()

    # Support both inline JSON and file paths
    services = _load_json(args.services, "services")
    connections = _load_json(args.connections, "connections")
    hierarchy = None
    if args.hierarchy:
        hierarchy = _load_json(args.hierarchy, "hierarchy")

    html = generate_diagram(
        services=services,
        connections=connections,
        title=args.title,
        vnet_info=args.vnet_info,
        hierarchy=hierarchy,
    )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"SUCCESS: Diagram saved to {args.output}")


def _load_json(value, name):
    """Load JSON from string or file path."""
    if os.path.isfile(value):
        with open(value, "r", encoding="utf-8") as f:
            return json.load(f)
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON for --{name}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
