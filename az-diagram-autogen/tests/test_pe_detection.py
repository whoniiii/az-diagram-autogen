"""Tests for PE (Private Endpoint) detection and rendering.

PE nodes must be type "pe" in the output JS for correct purple rendering.
"""
import unittest
from az_diagram_autogen.generator import generate_html, get_service_info


class TestPeTypeDetection(unittest.TestCase):
    """PE type variants must all normalize to 'pe' in output."""

    PE_VARIANTS = ["pe", "private_endpoints", "private_endpoint",
                   "Private_Endpoints", "PRIVATE_ENDPOINTS"]

    def test_pe_variants_normalize_in_html(self):
        for variant in self.PE_VARIANTS:
            services = [
                {"id": "svc1", "name": "ADF", "type": "adf"},
                {"id": "pe1", "name": "PE-ADF", "type": variant},
            ]
            html = generate_html(services, [], title="PE Test")
            self.assertIn('"type": "pe"', html,
                          f"Variant '{variant}' should normalize to 'pe' in output")

    def test_pe_color_is_purple(self):
        info = get_service_info("pe")
        self.assertEqual(info["color"], "#5C2D91")
        self.assertEqual(info["bg"], "#F3EEF9")

    def test_pe_category_is_network(self):
        info = get_service_info("pe")
        self.assertEqual(info["category"], "Network")


class TestPeCountInHtml(unittest.TestCase):
    """PE count should be correctly calculated for layout."""

    def test_pe_count_with_mixed_services(self):
        services = [
            {"id": "s1", "name": "ADF", "type": "adf"},
            {"id": "s2", "name": "Storage", "type": "storage"},
            {"id": "pe1", "name": "PE-ADF", "type": "pe"},
            {"id": "pe2", "name": "PE-Storage", "type": "private_endpoints"},
        ]
        html = generate_html(services, [], title="PE Count Test")
        # Both PE nodes should be type "pe"
        self.assertEqual(html.count('"type": "pe"'), 2)

    def test_no_pe_when_none_present(self):
        services = [
            {"id": "s1", "name": "ADF", "type": "adf"},
            {"id": "s2", "name": "Storage", "type": "storage"},
        ]
        html = generate_html(services, [], title="No PE Test")
        self.assertNotIn('"type": "pe"', html)


class TestPeConnectionDirection(unittest.TestCase):
    """Connections from service → PE should work correctly."""

    def test_service_to_pe_connection(self):
        services = [
            {"id": "adf", "name": "ADF", "type": "adf"},
            {"id": "pe_adf", "name": "PE-ADF", "type": "pe"},
        ]
        connections = [
            {"from": "adf", "to": "pe_adf", "label": "Private Link", "type": "private"},
        ]
        html = generate_html(services, connections, title="PE Connection Test")
        self.assertIn("Private Link", html)
        self.assertIn("pe_adf", html)


if __name__ == "__main__":
    unittest.main()
