#!/usr/bin/env python3
"""CLI for az-diagram-autogen."""
import argparse
import json
import sys
import os
from pathlib import Path
from .generator import generate_diagram


def main():
    parser = argparse.ArgumentParser(
        description="Generate interactive Azure architecture diagrams",
        prog="az-diagram-autogen"
    )
    parser.add_argument("-s", "--services", help="Services JSON (string or file path)")
    parser.add_argument("-c", "--connections", help="Connections JSON (string or file path)")
    parser.add_argument("-t", "--title", default="Azure Architecture", help="Diagram title")
    parser.add_argument("-o", "--output", default="azure-architecture.html", help="Output HTML file")
    parser.add_argument("--vnet-info", default="", help="VNet CIDR info")
    parser.add_argument("--hierarchy", default="", help="Subscription/RG hierarchy JSON")
    parser.add_argument("--reference", action="store_true", help="Print REFERENCE.md (skill integration guide)")

    args = parser.parse_args()

    if args.reference:
        ref_path = Path(__file__).parent / "REFERENCE.md"
        content = ref_path.read_text(encoding="utf-8")
        sys.stdout.buffer.write(content.encode("utf-8", errors="replace"))
        return

    if not args.services or not args.connections:
        parser.error("-s/--services and -c/--connections are required (use --reference for guide)")

    services = _load_json(args.services, "services")
    connections = _load_json(args.connections, "connections")
    hierarchy = None
    if args.hierarchy:
        hierarchy = _load_json(args.hierarchy, "hierarchy")

    services = _normalize_services(services)
    connections = _normalize_connections(connections)

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


def _normalize_services(services):
    """Normalize service fields for tolerance."""
    for svc in services:
        if isinstance(svc.get("details"), str):
            svc["details"] = [svc["details"]]
        if isinstance(svc.get("private"), str):
            svc["private"] = bool(svc["private"])
    return services


def _normalize_connections(connections):
    """Normalize connection fields for tolerance."""
    for conn in connections:
        if "type" not in conn:
            conn["type"] = "default"
    return connections


if __name__ == "__main__":
    main()
