"""Tests for az_diagram_autogen.generator"""
import unittest
from az_diagram_autogen.generator import generate_diagram


SAMPLE_SERVICES = [
    {"id": "s1", "name": "Foundry", "type": "ai_foundry", "sku": "S0"},
    {"id": "s2", "name": "Storage", "type": "storage"},
]

SAMPLE_CONNECTIONS = [
    {"from": "s1", "to": "s2", "label": "Data", "type": "data"},
]


class TestGenerator(unittest.TestCase):
    def test_returns_html_string(self):
        html = generate_diagram(SAMPLE_SERVICES, SAMPLE_CONNECTIONS)
        self.assertIsInstance(html, str)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("</html>", html)

    def test_title_in_output(self):
        html = generate_diagram(SAMPLE_SERVICES, SAMPLE_CONNECTIONS, title="My Test Arch")
        self.assertIn("My Test Arch", html)

    def test_service_names_in_output(self):
        html = generate_diagram(SAMPLE_SERVICES, SAMPLE_CONNECTIONS)
        self.assertIn("Foundry", html)
        self.assertIn("Storage", html)

    def test_empty_connections(self):
        html = generate_diagram(SAMPLE_SERVICES, [])
        self.assertIn("<!DOCTYPE html>", html)

    def test_vnet_info(self):
        html = generate_diagram(SAMPLE_SERVICES, SAMPLE_CONNECTIONS, vnet_info="10.0.0.0/16")
        self.assertIn("10.0.0.0/16", html)

    def test_hierarchy(self):
        services = [
            {"id": "s1", "name": "Foundry", "type": "ai_foundry", "subscription": "sub-1", "resourceGroup": "rg-ai"},
            {"id": "s2", "name": "Storage", "type": "storage", "subscription": "sub-1", "resourceGroup": "rg-data"},
        ]
        hierarchy = [{"subscription": "sub-1", "resourceGroups": ["rg-ai", "rg-data"]}]
        html = generate_diagram(services, SAMPLE_CONNECTIONS, hierarchy=hierarchy)
        self.assertIn("sub-1", html)

    def test_all_known_types_have_icons(self):
        """Verify common types produce valid HTML (no crash)."""
        types = ["ai_foundry", "ai_search", "storage", "keyvault", "app_service",
                 "sql_database", "redis", "cosmos_db", "aks", "acr", "function_app",
                 "data_factory", "databricks", "fabric", "firewall", "bastion",
                 "vpn_gateway", "front_door", "iot_hub", "event_hub", "log_analytics",
                 "app_insights", "vm", "cdn", "stream_analytics", "devops",
                 "app_gateway", "document_intelligence", "nsg"]
        for t in types:
            services = [{"id": f"svc-{t}", "name": f"Test {t}", "type": t}]
            html = generate_diagram(services, [])
            self.assertIn("<!DOCTYPE html>", html, f"Failed for type: {t}")


if __name__ == "__main__":
    unittest.main()
