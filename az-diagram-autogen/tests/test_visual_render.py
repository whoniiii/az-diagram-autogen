"""Visual rendering tests — generates HTML diagrams, captures PNG screenshots,
and produces a markdown report for human review.

Run:
    cd az-diagram-autogen
    python -m pytest tests/test_visual_render.py -v -s

Output:
    tests/test_output/YYYYMMDD_HHMMSS/
    ├── 01_fabric_foundry.html / .png
    ├── 02_pe_network.html / .png
    ├── 03_arm_types.html / .png
    ├── 04_full_architecture.html / .png
    ├── 05_all_service_types.html / .png
    └── RENDER_REPORT.md

    tests/test_output/latest → symlink/copy to most recent run
"""
import os
import shutil
import unittest
from datetime import datetime
from az_diagram_autogen.generator import generate_html, SERVICE_ICONS

_BASE_OUTPUT = os.path.join(os.path.dirname(__file__), "test_output")
_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = os.path.join(_BASE_OUTPUT, _TIMESTAMP)

# ── Scenario definitions ──────────────────────────────────────────────
SCENARIOS = {
    "01_fabric_foundry": {
        "title": "Fabric + AI Foundry Icon Test",
        "desc": "Fabric은 주황색 다이아몬드, AI Foundry는 보라색 AI Studio 아이콘이어야 합니다.",
        "services": [
            {"id": "fabric", "name": "Fabric Capacity", "type": "fabric", "sku": "F2"},
            {"id": "foundry", "name": "AI Foundry", "type": "ai_foundry", "sku": "S0"},
            {"id": "openai", "name": "Azure OpenAI", "type": "openai"},
            {"id": "storage", "name": "Storage Account", "type": "storage"},
        ],
        "connections": [
            {"from": "foundry", "to": "openai", "label": "Model Deployment", "type": "api"},
            {"from": "foundry", "to": "storage", "label": "Data", "type": "data"},
            {"from": "fabric", "to": "storage", "label": "Lakehouse", "type": "data"},
        ],
    },
    "02_pe_network": {
        "title": "Private Endpoint Rendering Test",
        "desc": "PE 노드는 상단에 보라색 작은 배지로 렌더링되어야 합니다.",
        "services": [
            {"id": "vnet", "name": "Hub VNet", "type": "vnet", "details": ["10.0.0.0/16"]},
            {"id": "adf", "name": "Data Factory", "type": "adf"},
            {"id": "kv", "name": "Key Vault", "type": "keyvault"},
            {"id": "pe_adf", "name": "PE-ADF", "type": "pe"},
            {"id": "pe_kv", "name": "PE-KV", "type": "pe"},
        ],
        "connections": [
            {"from": "adf", "to": "pe_adf", "label": "Private Link", "type": "private"},
            {"from": "kv", "to": "pe_kv", "label": "Private Link", "type": "private"},
            {"from": "adf", "to": "kv", "label": "Secrets", "type": "security"},
        ],
        "vnet_info": "10.0.0.0/16",
    },
    "03_arm_types": {
        "title": "ARM Resource Type Normalization Test",
        "desc": "Azure ARM 리소스 이름이 정규 타입으로 변환되어 올바른 아이콘/색상으로 렌더링됩니다.",
        "services": [
            {"id": "s1", "name": "Storage Acct", "type": "storage_accounts"},
            {"id": "s2", "name": "Data Factory", "type": "data_factories"},
            {"id": "s3", "name": "Virtual Network", "type": "virtual_networks"},
            {"id": "s4", "name": "Key Vault", "type": "key_vaults"},
            {"id": "s5", "name": "AKS Cluster", "type": "kubernetes_services"},
            {"id": "s6", "name": "Cognitive Svc", "type": "cognitive_services"},
            {"id": "s7", "name": "Fabric Cap", "type": "fabric_capacities"},
            {"id": "s8", "name": "Redis Cache", "type": "cache_redis"},
        ],
        "connections": [
            {"from": "s2", "to": "s1", "label": "Read/Write", "type": "data"},
            {"from": "s5", "to": "s6", "label": "AI Call", "type": "api"},
            {"from": "s7", "to": "s1", "label": "Lakehouse", "type": "data"},
        ],
    },
    "04_full_architecture": {
        "title": "Full Architecture — Fabric Data Platform",
        "desc": "실제 배포된 Fabric Data Platform 아키텍처 시뮬레이션 (PE 포함).",
        "services": [
            {"id": "vnet", "name": "fdp-vnet", "type": "vnet",
             "details": ["10.0.0.0/16"], "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "fabric", "name": "fdp-fabric", "type": "fabric",
             "sku": "F2", "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "foundry", "name": "foundry-abc", "type": "ai_foundry",
             "sku": "S0", "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "adf", "name": "fdp-adf", "type": "adf",
             "subscription": "sub-1", "resourceGroup": "rg-fabric"},
            {"id": "pe_foundry", "name": "PE-Foundry", "type": "pe"},
            {"id": "pe_adf", "name": "PE-ADF", "type": "pe"},
        ],
        "connections": [
            {"from": "adf", "to": "fabric", "label": "ETL Pipeline", "type": "data"},
            {"from": "adf", "to": "foundry", "label": "AI Enrichment", "type": "api"},
            {"from": "foundry", "to": "pe_foundry", "label": "Private Link", "type": "private"},
            {"from": "adf", "to": "pe_adf", "label": "Private Link", "type": "private"},
        ],
        "vnet_info": "10.0.0.0/16",
        "hierarchy": [{"subscription": "sub-1", "resourceGroups": ["rg-fabric"]}],
    },
    "05_all_service_types": {
        "title": "All Registered Service Types",
        "desc": "SERVICE_ICONS에 등록된 모든 서비스 타입의 아이콘/색상 렌더링 확인.",
        "services": [],  # populated dynamically
        "connections": [],
    },
    "06_hub_spoke_network": {
        "title": "Hub-Spoke Network Topology",
        "desc": "Hub VNet + Spoke VNet + Firewall + VPN Gateway + NSG 네트워크 토폴로지.",
        "services": [
            {"id": "hub", "name": "Hub VNet", "type": "vnet", "details": ["10.0.0.0/16"]},
            {"id": "spoke1", "name": "Spoke-App VNet", "type": "vnet", "details": ["10.1.0.0/16"]},
            {"id": "spoke2", "name": "Spoke-Data VNet", "type": "vnet", "details": ["10.2.0.0/16"]},
            {"id": "fw", "name": "Azure Firewall", "type": "firewall"},
            {"id": "vpn", "name": "VPN Gateway", "type": "vpn_gateway"},
            {"id": "nsg1", "name": "App NSG", "type": "nsg"},
            {"id": "nsg2", "name": "Data NSG", "type": "nsg"},
            {"id": "lb", "name": "Load Balancer", "type": "load_balancer"},
        ],
        "connections": [
            {"from": "hub", "to": "spoke1", "label": "Peering", "type": "network"},
            {"from": "hub", "to": "spoke2", "label": "Peering", "type": "network"},
            {"from": "fw", "to": "hub", "label": "Protect", "type": "security"},
            {"from": "vpn", "to": "hub", "label": "On-Prem", "type": "network"},
            {"from": "lb", "to": "spoke1", "label": "Distribute", "type": "network"},
        ],
        "vnet_info": "10.0.0.0/16",
    },
    "07_data_pipeline": {
        "title": "Data Pipeline (ADF + Databricks + SQL)",
        "desc": "ADF → Databricks → SQL Database + Storage 데이터 파이프라인 아키텍처.",
        "services": [
            {"id": "adf", "name": "Data Factory", "type": "adf"},
            {"id": "dbx", "name": "Databricks", "type": "databricks"},
            {"id": "storage", "name": "ADLS Gen2", "type": "storage"},
            {"id": "sql", "name": "SQL Database", "type": "sql_database"},
            {"id": "synapse", "name": "Synapse Analytics", "type": "synapse"},
            {"id": "kv", "name": "Key Vault", "type": "keyvault"},
        ],
        "connections": [
            {"from": "adf", "to": "storage", "label": "Ingest", "type": "data"},
            {"from": "adf", "to": "dbx", "label": "Transform", "type": "data"},
            {"from": "dbx", "to": "storage", "label": "Read/Write", "type": "data"},
            {"from": "dbx", "to": "sql", "label": "Load", "type": "data"},
            {"from": "synapse", "to": "storage", "label": "Query", "type": "data"},
            {"from": "adf", "to": "kv", "label": "Secrets", "type": "security"},
        ],
    },
    "08_microservices_aks": {
        "title": "Microservices on AKS",
        "desc": "AKS + ACR + Redis + Service Bus + App Gateway 마이크로서비스 아키텍처.",
        "services": [
            {"id": "aks", "name": "AKS Cluster", "type": "aks"},
            {"id": "acr", "name": "Container Registry", "type": "acr"},
            {"id": "redis", "name": "Redis Cache", "type": "redis"},
            {"id": "sb", "name": "Service Bus", "type": "service_bus"},
            {"id": "appgw", "name": "App Gateway", "type": "app_gateway"},
            {"id": "cosmos", "name": "Cosmos DB", "type": "cosmos_db"},
            {"id": "monitor", "name": "Monitor", "type": "monitor"},
            {"id": "appi", "name": "App Insights", "type": "appinsights"},
        ],
        "connections": [
            {"from": "appgw", "to": "aks", "label": "Ingress", "type": "network"},
            {"from": "aks", "to": "acr", "label": "Pull Images", "type": "api"},
            {"from": "aks", "to": "redis", "label": "Cache", "type": "data"},
            {"from": "aks", "to": "sb", "label": "Messages", "type": "data"},
            {"from": "aks", "to": "cosmos", "label": "Persist", "type": "data"},
            {"from": "aks", "to": "appi", "label": "Telemetry", "type": "api"},
        ],
    },
    "09_security_stack": {
        "title": "Security Stack",
        "desc": "Key Vault + Firewall + NSG + WAF + Sentinel + Managed Identity 보안 아키텍처.",
        "services": [
            {"id": "kv", "name": "Key Vault", "type": "keyvault"},
            {"id": "fw", "name": "Azure Firewall", "type": "firewall"},
            {"id": "nsg", "name": "NSG", "type": "nsg"},
            {"id": "waf", "name": "WAF", "type": "waf"},
            {"id": "sentinel", "name": "Sentinel", "type": "sentinel"},
            {"id": "la", "name": "Log Analytics", "type": "log_analytics"},
            {"id": "mi", "name": "Managed Identity", "type": "managed_identity"},
            {"id": "dns", "name": "Private DNS", "type": "dns"},
        ],
        "connections": [
            {"from": "sentinel", "to": "la", "label": "Analyze", "type": "data"},
            {"from": "fw", "to": "la", "label": "Logs", "type": "data"},
            {"from": "nsg", "to": "la", "label": "Flow Logs", "type": "data"},
            {"from": "mi", "to": "kv", "label": "Access", "type": "security"},
            {"from": "waf", "to": "fw", "label": "Filter", "type": "security"},
        ],
    },
    "10_iot_architecture": {
        "title": "IoT Architecture",
        "desc": "IoT Hub + Event Hub + Stream Analytics + Cosmos DB + Function App IoT 아키텍처.",
        "services": [
            {"id": "iot", "name": "IoT Hub", "type": "iot_hub"},
            {"id": "eh", "name": "Event Hub", "type": "event_hub"},
            {"id": "sa", "name": "Stream Analytics", "type": "stream_analytics"},
            {"id": "cosmos", "name": "Cosmos DB", "type": "cosmos_db"},
            {"id": "func", "name": "Function App", "type": "function_app"},
            {"id": "storage", "name": "Storage", "type": "storage"},
            {"id": "pbi", "name": "Power BI", "type": "power_bi"},
            {"id": "appi", "name": "App Insights", "type": "appinsights"},
        ],
        "connections": [
            {"from": "iot", "to": "eh", "label": "Telemetry", "type": "data"},
            {"from": "eh", "to": "sa", "label": "Stream", "type": "data"},
            {"from": "sa", "to": "cosmos", "label": "Store", "type": "data"},
            {"from": "sa", "to": "storage", "label": "Archive", "type": "data"},
            {"from": "func", "to": "cosmos", "label": "Process", "type": "api"},
            {"from": "cosmos", "to": "pbi", "label": "Visualize", "type": "data"},
            {"from": "func", "to": "appi", "label": "Monitor", "type": "api"},
        ],
    },
}


def _build_all_types_scenario():
    """Populate scenario 05 with every SERVICE_ICONS entry."""
    seen = set()
    services = []
    for svc_type in SERVICE_ICONS:
        if svc_type == "default":
            continue
        if svc_type in seen:
            continue
        seen.add(svc_type)
        services.append({
            "id": f"svc-{svc_type}",
            "name": svc_type.replace("_", " ").title(),
            "type": svc_type,
        })
    SCENARIOS["05_all_service_types"]["services"] = services


class TestVisualRender(unittest.TestCase):
    """Generate HTML for each scenario and capture PNG screenshots."""

    @classmethod
    def setUpClass(cls):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        _build_all_types_scenario()

        # Generate all HTML files first
        cls.generated = {}
        for name, scenario in SCENARIOS.items():
            html = generate_html(
                scenario["services"],
                scenario["connections"],
                title=scenario["title"],
                vnet_info=scenario.get("vnet_info", ""),
                hierarchy=scenario.get("hierarchy"),
            )
            html_path = os.path.join(OUTPUT_DIR, f"{name}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            cls.generated[name] = html_path

        # Capture PNGs via Playwright
        cls.screenshots = {}
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 1080})
                for name, html_path in cls.generated.items():
                    file_url = "file:///" + html_path.replace("\\", "/")
                    page.goto(file_url)
                    # Wait for rendering to complete
                    page.wait_for_timeout(2000)
                    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
                    page.screenshot(path=png_path, full_page=True)
                    cls.screenshots[name] = png_path
                browser.close()
            cls.playwright_ok = True
        except Exception as e:
            cls.playwright_ok = False
            cls.playwright_error = str(e)

        # Generate markdown report
        cls._generate_report()

        # Update "latest" pointer
        latest = os.path.join(_BASE_OUTPUT, "latest")
        if os.path.isdir(latest) and not os.path.islink(latest):
            shutil.rmtree(latest)
        elif os.path.islink(latest) or os.path.exists(latest):
            os.remove(latest)
        try:
            os.symlink(OUTPUT_DIR, latest, target_is_directory=True)
        except OSError:
            # Windows non-admin: fall back to writing a redirect file
            with open(latest + ".txt", "w", encoding="utf-8") as f:
                f.write(OUTPUT_DIR)

    @classmethod
    def _generate_report(cls):
        lines = [
            f"# 🧪 Diagram Visual Render Report",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Run folder**: `{_TIMESTAMP}`  ",
            f"**Scenarios**: {len(SCENARIOS)}  ",
            f"**Playwright**: {'✅ OK' if cls.playwright_ok else '❌ ' + getattr(cls, 'playwright_error', 'unknown')}",
            f"",
            f"---",
            f"",
        ]
        for name, scenario in SCENARIOS.items():
            lines.append(f"## {scenario['title']}")
            lines.append(f"")
            lines.append(f"> {scenario['desc']}")
            lines.append(f"")
            svc_count = len(scenario["services"])
            conn_count = len(scenario["connections"])
            pe_count = sum(1 for s in scenario["services"] if s.get("type") == "pe")
            lines.append(f"- Services: **{svc_count}** (PE: {pe_count})")
            lines.append(f"- Connections: **{conn_count}**")
            lines.append(f"")
            if name in cls.screenshots and os.path.exists(cls.screenshots[name]):
                lines.append(f"![{name}]({name}.png)")
            else:
                lines.append(f"⚠️ PNG not generated — check Playwright installation")
            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        report_path = os.path.join(OUTPUT_DIR, "RENDER_REPORT.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        cls.report_path = report_path

    # ── Test methods ──

    def test_all_html_files_generated(self):
        for name in SCENARIOS:
            path = self.generated.get(name)
            self.assertIsNotNone(path, f"HTML not generated for {name}")
            self.assertTrue(os.path.exists(path), f"HTML file missing: {path}")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("<!DOCTYPE html>", content)

    def test_all_png_screenshots_captured(self):
        if not self.playwright_ok:
            self.skipTest(f"Playwright unavailable: {self.playwright_error}")
        for name in SCENARIOS:
            path = self.screenshots.get(name)
            self.assertIsNotNone(path, f"PNG not captured for {name}")
            self.assertTrue(os.path.exists(path), f"PNG file missing: {path}")
            size = os.path.getsize(path)
            self.assertGreater(size, 1000, f"PNG too small ({size}B) for {name}")

    def test_report_generated(self):
        self.assertTrue(os.path.exists(self.report_path))
        with open(self.report_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("# 🧪 Diagram Visual Render Report", content)
        for name in SCENARIOS:
            self.assertIn(name, content)

    def test_fabric_foundry_icons_distinct(self):
        """Fabric and Foundry should render with different colors."""
        path = self.generated.get("01_fabric_foundry")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        self.assertIn("#E8740C", html)  # Fabric orange
        self.assertIn("#0078D4", html)  # Foundry blue

    def test_pe_nodes_render_as_pe_type(self):
        path = self.generated.get("02_pe_network")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        self.assertEqual(html.count('"type": "pe"'), 2)

    def test_arm_types_normalized(self):
        path = self.generated.get("03_arm_types")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        self.assertIn('"type": "storage"', html)
        self.assertIn('"type": "adf"', html)
        self.assertIn('"type": "vnet"', html)
        self.assertIn('"type": "keyvault"', html)
        self.assertIn('"type": "aks"', html)
        self.assertIn('"type": "ai_foundry"', html)
        self.assertIn('"type": "fabric"', html)
        self.assertIn('"type": "redis"', html)


if __name__ == "__main__":
    unittest.main()
