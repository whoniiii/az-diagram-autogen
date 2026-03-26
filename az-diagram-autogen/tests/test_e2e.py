"""End-to-end diagram generation tests.

Tests complete diagram flows with realistic Azure architectures.
"""
import unittest
from az_diagram_autogen.generator import generate_html, get_service_info, SERVICE_ICONS


class TestAllServiceTypesRender(unittest.TestCase):
    """Every type in SERVICE_ICONS should produce valid HTML without crashing."""

    def test_every_service_type_produces_html(self):
        errors = []
        for svc_type in SERVICE_ICONS:
            try:
                services = [{"id": f"test-{svc_type}", "name": f"Test {svc_type}", "type": svc_type}]
                html = generate_html(services, [], title=f"Test {svc_type}")
                if "<!DOCTYPE html>" not in html:
                    errors.append(f"{svc_type}: missing DOCTYPE")
            except Exception as e:
                errors.append(f"{svc_type}: {e}")
        self.assertEqual(errors, [], f"Failed types:\n" + "\n".join(errors))


class TestRealisticArchitecture(unittest.TestCase):
    """Test with a realistic Fabric Data Platform architecture."""

    def setUp(self):
        self.services = [
            {"id": "vnet", "name": "fdp-vnet", "type": "vnet",
             "details": ["10.0.0.0/16"], "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "fabric", "name": "fdp-fabric", "type": "fabric",
             "sku": "F2", "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "foundry", "name": "foundry-abc", "type": "ai_foundry",
             "sku": "S0", "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "adf", "name": "fdp-adf-abc", "type": "adf",
             "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "pe_foundry", "name": "PE-Foundry", "type": "pe"},
            {"id": "pe_adf", "name": "PE-ADF", "type": "pe"},
        ]
        self.connections = [
            {"from": "adf", "to": "fabric", "label": "ETL Pipeline", "type": "data"},
            {"from": "adf", "to": "foundry", "label": "AI Enrichment", "type": "api"},
            {"from": "foundry", "to": "pe_foundry", "label": "Private Link", "type": "private"},
            {"from": "adf", "to": "pe_adf", "label": "Private Link", "type": "private"},
        ]
        self.hierarchy = [
            {"subscription": "sub-1", "resourceGroups": ["rg-fabric"]}
        ]

    def test_full_diagram_generates(self):
        html = generate_html(
            self.services, self.connections,
            title="Fabric Data Platform",
            vnet_info="10.0.0.0/16",
            hierarchy=self.hierarchy,
        )
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Fabric Data Platform", html)

    def test_all_service_names_present(self):
        html = generate_html(self.services, self.connections, title="Test")
        for svc in self.services:
            self.assertIn(svc["name"], html,
                          f"Service '{svc['name']}' missing from output")

    def test_pe_nodes_typed_correctly(self):
        html = generate_html(self.services, self.connections, title="Test")
        self.assertEqual(html.count('"type": "pe"'), 2)

    def test_fabric_color_in_output(self):
        html = generate_html(self.services, self.connections, title="Test")
        self.assertIn("#E8740C", html)  # Fabric orange

    def test_vnet_info_in_output(self):
        html = generate_html(
            self.services, self.connections, title="Test", vnet_info="10.0.0.0/16"
        )
        self.assertIn("10.0.0.0/16", html)


class TestArmTypeRealWorld(unittest.TestCase):
    """Simulate real-world ARM resource types from az resource list."""

    def test_arm_types_render_correctly(self):
        """Types as they might come from Azure Resource Manager."""
        services = [
            {"id": "s1", "name": "My Storage", "type": "storage_accounts"},
            {"id": "s2", "name": "My ADF", "type": "data_factories"},
            {"id": "s3", "name": "My VNet", "type": "virtual_networks"},
            {"id": "s4", "name": "My KV", "type": "key_vaults"},
            {"id": "s5", "name": "My AKS", "type": "kubernetes_services"},
            {"id": "s6", "name": "My Foundry", "type": "cognitive_services"},
            {"id": "s7", "name": "My Fabric", "type": "fabric_capacities"},
            {"id": "pe1", "name": "PE-1", "type": "private_endpoints"},
        ]
        html = generate_html(services, [], title="ARM Types")
        self.assertIn("<!DOCTYPE html>", html)
        # Verify normalization happened
        self.assertIn('"type": "storage"', html)
        self.assertIn('"type": "adf"', html)
        self.assertIn('"type": "vnet"', html)
        self.assertIn('"type": "keyvault"', html)
        self.assertIn('"type": "aks"', html)
        self.assertIn('"type": "ai_foundry"', html)
        self.assertIn('"type": "fabric"', html)
        self.assertIn('"type": "pe"', html)


class TestConnectionStyles(unittest.TestCase):
    """Connection type styling should work."""

    def test_all_connection_types(self):
        services = [
            {"id": "s1", "name": "A", "type": "storage"},
            {"id": "s2", "name": "B", "type": "adf"},
        ]
        for conn_type in ["api", "data", "security", "private", "network", "default"]:
            connections = [
                {"from": "s1", "to": "s2", "label": f"test-{conn_type}", "type": conn_type}
            ]
            html = generate_html(services, connections, title="Conn Test")
            self.assertIn(f"test-{conn_type}", html)


class TestEdgeCases(unittest.TestCase):
    """Edge cases that shouldn't crash the generator."""

    def test_empty_services(self):
        html = generate_html([], [], title="Empty")
        self.assertIn("<!DOCTYPE html>", html)

    def test_unknown_service_type(self):
        services = [{"id": "x", "name": "Unknown", "type": "totally_unknown_xyz"}]
        html = generate_html(services, [], title="Unknown")
        self.assertIn("<!DOCTYPE html>", html)

    def test_missing_type_field(self):
        services = [{"id": "x", "name": "No Type"}]
        html = generate_html(services, [], title="No Type")
        self.assertIn("<!DOCTYPE html>", html)

    def test_unicode_names(self):
        services = [{"id": "x", "name": "저장소 테스트", "type": "storage"}]
        html = generate_html(services, [], title="유니코드 테스트")
        self.assertIn("저장소 테스트", html)

    def test_special_chars_in_details(self):
        services = [
            {"id": "x", "name": "Test", "type": "storage",
             "details": ["Size: 100GB", "Tier: 'Hot'", 'Key: "value"']}
        ]
        html = generate_html(services, [], title="Details Test")
        self.assertIn("<!DOCTYPE html>", html)


if __name__ == "__main__":
    unittest.main()
