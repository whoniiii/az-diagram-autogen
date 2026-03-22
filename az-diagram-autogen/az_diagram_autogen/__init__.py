"""Azure Architecture Diagram Generator - Interactive HTML diagrams with 605 official Azure icons."""

__version__ = "0.1.0"

from .generator import generate_diagram
from .icons import search_icons, get_icon_data_uri

__all__ = ["generate_diagram", "search_icons", "get_icon_data_uri"]
