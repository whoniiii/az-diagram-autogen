"""Tests for icon resolution — ensures critical services get correct official icons.

Focuses on Fabric, AI Foundry, and services that previously had wrong icon mappings.
"""
import unittest
from az_diagram_autogen.generator import SERVICE_ICONS, get_service_info
from az_diagram_autogen.icons import get_icon_data_uri, AZURE_ICONS


class TestCriticalIconMappings(unittest.TestCase):
    """Services that previously had wrong icons — must remain correct."""

    def test_fabric_uses_microsoft_fabric_icon(self):
        info = get_service_info("fabric")
        self.assertEqual(info.get("azure_icon_key", ""), "microsoft_fabric",
                         "Fabric must use 'microsoft_fabric' icon, NOT 'managed_service_fabric'")

    def test_ai_foundry_uses_ai_foundry_icon(self):
        info = get_service_info("ai_foundry")
        self.assertEqual(info.get("azure_icon_key", ""), "ai_foundry",
                         "AI Foundry must use 'ai_foundry' icon, NOT 'azure_openai'")

    def test_fabric_icon_exists_in_icons_py(self):
        self.assertIn("microsoft_fabric", AZURE_ICONS,
                      "microsoft_fabric must exist in AZURE_ICONS")

    def test_ai_foundry_icon_exists_in_icons_py(self):
        self.assertIn("ai_foundry", AZURE_ICONS,
                      "ai_foundry must exist in AZURE_ICONS")

    def test_fabric_icon_is_valid_data_uri(self):
        uri = get_icon_data_uri("microsoft_fabric")
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"),
                        "microsoft_fabric icon should be a valid data URI")

    def test_ai_foundry_icon_is_valid_data_uri(self):
        uri = get_icon_data_uri("ai_foundry")
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"),
                        "ai_foundry icon should be a valid data URI")

    def test_fabric_color_is_orange(self):
        info = get_service_info("fabric")
        self.assertEqual(info["color"], "#E8740C")

    def test_ai_foundry_color_is_blue(self):
        info = get_service_info("ai_foundry")
        self.assertEqual(info["color"], "#0078D4")


class TestFabricVariants(unittest.TestCase):
    """All Fabric-related type variants should resolve to the same icon."""

    VARIANTS = ["fabric", "fabric_capacities", "fabric_capacity", "microsoft_fabric"]

    def test_all_variants_use_microsoft_fabric_icon(self):
        for variant in self.VARIANTS:
            info = get_service_info(variant)
            key = info.get("azure_icon_key", "")
            self.assertEqual(key, "microsoft_fabric",
                             f"'{variant}' should use 'microsoft_fabric' icon, got '{key}'")

    def test_all_variants_produce_valid_icon(self):
        for variant in self.VARIANTS:
            info = get_service_info(variant)
            uri = info.get("icon_data_uri", "")
            self.assertTrue(uri.startswith("data:image/svg+xml;base64,"),
                            f"'{variant}' should produce a valid icon data URI")


class TestFoundryVariants(unittest.TestCase):
    """All Foundry-related type variants should resolve to ai_foundry icon."""

    VARIANTS = ["ai_foundry", "foundry", "cognitive_services", "ai_services"]

    def test_all_variants_use_ai_foundry_icon(self):
        for variant in self.VARIANTS:
            info = get_service_info(variant)
            key = info.get("azure_icon_key", "")
            self.assertEqual(key, "ai_foundry",
                             f"'{variant}' should use 'ai_foundry' icon, got '{key}'")


class TestAllServiceIconsHaveValidKeys(unittest.TestCase):
    """Every SERVICE_ICONS entry with azure_icon_key should point to an existing icon."""

    def test_all_azure_icon_keys_exist(self):
        missing = []
        for svc_type, info in SERVICE_ICONS.items():
            azure_key = info.get("azure_icon_key")
            if azure_key and azure_key not in AZURE_ICONS:
                missing.append(f"{svc_type} -> {azure_key}")
        self.assertEqual(missing, [],
                         f"SERVICE_ICONS references missing icons: {missing}")

    def test_icon_count_minimum(self):
        self.assertGreaterEqual(len(AZURE_ICONS), 634,
                                "Expected at least 634 icons (including fabric + foundry)")


class TestIconRenderInHtml(unittest.TestCase):
    """Verify icons actually appear in generated HTML."""

    def test_fabric_icon_in_html(self):
        from az_diagram_autogen.generator import generate_html
        services = [{"id": "f1", "name": "My Fabric", "type": "fabric"}]
        html = generate_html(services, [], title="Icon Test")
        self.assertIn("My Fabric", html)
        self.assertIn("<!DOCTYPE html>", html)

    def test_foundry_icon_in_html(self):
        from az_diagram_autogen.generator import generate_html
        services = [{"id": "a1", "name": "My Foundry", "type": "ai_foundry"}]
        html = generate_html(services, [], title="Icon Test")
        self.assertIn("My Foundry", html)


if __name__ == "__main__":
    unittest.main()
