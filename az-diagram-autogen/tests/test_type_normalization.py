"""Tests for _TYPE_ALIASES normalization in generator.py.

Ensures all aliases resolve to valid canonical types that exist in SERVICE_ICONS.
"""
import unittest
from az_diagram_autogen.generator import (
    _TYPE_ALIASES, SERVICE_ICONS, get_service_info, generate_html
)


class TestTypeAliases(unittest.TestCase):
    """Every alias must map to a canonical type present in SERVICE_ICONS."""

    def test_all_aliases_resolve_to_known_types(self):
        missing = []
        for alias, canonical in _TYPE_ALIASES.items():
            if canonical not in SERVICE_ICONS:
                missing.append(f"{alias} -> {canonical}")
        self.assertEqual(missing, [], f"Aliases point to unknown types: {missing}")

    def test_alias_count_minimum(self):
        self.assertGreaterEqual(len(_TYPE_ALIASES), 90, "Expected at least 90 aliases")

    def test_no_self_referencing_aliases(self):
        """Aliases should not map to themselves (pointless)."""
        self_refs = [k for k, v in _TYPE_ALIASES.items() if k == v]
        # sentinel -> sentinel is OK (explicit identity), but flag others
        allowed_self = {"sentinel", "spring_apps"}
        unexpected = [k for k in self_refs if k not in allowed_self]
        self.assertEqual(unexpected, [], f"Self-referencing aliases: {unexpected}")


class TestNormalizationViaGetServiceInfo(unittest.TestCase):
    """get_service_info() should normalize aliases and return valid info."""

    ALIAS_SAMPLES = [
        # (input, expected_canonical)
        ("private_endpoints", "pe"),
        ("private_endpoint", "pe"),
        ("Private_Endpoints", "pe"),
        ("virtual_networks", "vnet"),
        ("data_factories", "adf"),
        ("data_factory", "adf"),
        ("storage_accounts", "storage"),
        ("fabric_capacities", "fabric"),
        ("microsoft_fabric", "fabric"),
        ("cognitive_services", "ai_foundry"),
        ("ai_services", "ai_foundry"),
        ("foundry", "ai_foundry"),
        ("azure_openai", "openai"),
        ("key_vault", "keyvault"),
        ("key_vaults", "keyvault"),
        ("kubernetes", "aks"),
        ("managed_clusters", "aks"),
        ("container_registries", "acr"),
        ("function_apps", "function_app"),
        ("functions", "function_app"),
        ("log_analytics_workspaces", "log_analytics"),
        ("application_insights", "appinsights"),
        ("redis_cache", "redis"),
        ("cosmos", "cosmos_db"),
        ("cosmosdb", "cosmos_db"),
        ("sql_databases", "sql_database"),
        ("event_hubs", "event_hub"),
        ("databricks_workspaces", "databricks"),
    ]

    def test_aliases_resolve_via_get_service_info(self):
        for alias, expected_canonical in self.ALIAS_SAMPLES:
            info = get_service_info(alias)
            expected_info = get_service_info(expected_canonical)
            self.assertEqual(
                info["color"], expected_info["color"],
                f"Alias '{alias}' should resolve to '{expected_canonical}'"
            )

    def test_hyphen_underscore_space_normalization(self):
        """All these formats should resolve identically."""
        variants = ["data-factory", "data_factory", "data factory"]
        colors = [get_service_info(v)["color"] for v in variants]
        self.assertTrue(all(c == colors[0] for c in colors))

    def test_case_insensitive(self):
        info_lower = get_service_info("storage_accounts")
        info_mixed = get_service_info("Storage_Accounts")
        self.assertEqual(info_lower["color"], info_mixed["color"])


class TestNormalizationInGenerateHtml(unittest.TestCase):
    """_norm() inside generate_html normalizes types in the output JS."""

    def test_pe_alias_produces_pe_in_output(self):
        services = [
            {"id": "svc1", "name": "ADF", "type": "adf"},
            {"id": "pe1", "name": "PE-ADF", "type": "private_endpoints"},
        ]
        html = generate_html(services, [], title="PE Test")
        # The output JS should have type "pe", not "private_endpoints"
        self.assertIn('"type": "pe"', html)

    def test_arm_type_normalized_in_output(self):
        services = [
            {"id": "s1", "name": "Storage", "type": "storage_accounts"},
        ]
        html = generate_html(services, [], title="ARM Test")
        self.assertIn('"type": "storage"', html)

    def test_fabric_alias_normalized(self):
        for variant in ["fabric_capacities", "microsoft_fabric", "fabric"]:
            services = [{"id": "f1", "name": "Fabric", "type": variant}]
            html = generate_html(services, [], title="Fabric Test")
            self.assertIn('"type": "fabric"', html, f"Failed for variant: {variant}")


class TestArmResourceTypeMapping(unittest.TestCase):
    """Azure ARM resource type names should normalize correctly."""

    ARM_MAPPING = [
        ("storage_accounts", "storage", "#0078D4"),
        ("data_factories", "adf", "#0078D4"),
        ("virtual_networks", "vnet", "#5C2D91"),
        ("private_endpoints", "pe", "#5C2D91"),
        ("key_vaults", "keyvault", "#E8A000"),
        ("cognitive_services", "ai_foundry", "#0078D4"),
        ("kubernetes_services", "aks", "#326CE5"),
        ("fabric_capacities", "fabric", "#E8740C"),
        ("firewalls", "firewall", "#E8A000"),
        ("cache_redis", "redis", "#D83B01"),
        ("container_registries", "acr", "#0078D4"),
        ("sql_databases", "sql_database", "#0078D4"),
        ("event_hubs", "event_hub", "#0078D4"),
        ("log_analytics_workspaces", "log_analytics", "#5C2D91"),
        ("application_insights", "appinsights", "#773ADC"),
        ("network_security_groups", "nsg", "#E8A000"),
    ]

    def test_arm_to_canonical_color(self):
        for arm_name, canonical, expected_color in self.ARM_MAPPING:
            info = get_service_info(arm_name)
            self.assertEqual(
                info["color"], expected_color,
                f"ARM '{arm_name}' -> '{canonical}' should be color {expected_color}"
            )


if __name__ == "__main__":
    unittest.main()
