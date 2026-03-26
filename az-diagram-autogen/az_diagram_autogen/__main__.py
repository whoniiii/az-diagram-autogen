"""Entry point for python -m az_diagram_autogen"""
import sys

if len(sys.argv) == 1:
    # No args — show help with reference hint
    sys.argv.append("--help")

from .cli import main
main()
