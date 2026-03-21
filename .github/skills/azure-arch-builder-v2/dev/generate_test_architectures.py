#!/usr/bin/env python3
"""Generate 20 test architecture diagrams + screenshots + REPORT.md"""

import json
import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIAGRAM_SCRIPT = os.path.join(SCRIPT_DIR, "..", "scripts", "generate_html_diagram.py")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test-architectures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ARCHITECTURES = [
    # Level 1
    {
        "id": "01", "name": "Static Website", "level": 1,
        "desc": "Blob static hosting + Azure CDN",
        "services": [
            {"id":"storage","name":"Storage Account","type":"storage","sku":"Standard_LRS","details":["Static Website"]},
            {"id":"cdn","name":"Azure CDN","type":"default","details":["Global CDN"]},
        ],
        "connections": [{"from":"cdn","to":"storage","label":"Origin","type":"data"}],
    },
    {
        "id": "02", "name": "Basic Web App", "level": 1,
        "desc": "App Service + SQL Database",
        "services": [
            {"id":"app","name":"App Service","type":"app_service","sku":"B1","details":["Web App"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","sku":"S0","details":["10 DTU"]},
        ],
        "connections": [{"from":"app","to":"sql","label":"Query","type":"data"}],
    },
    {
        "id": "03", "name": "Serverless API", "level": 1,
        "desc": "Function App + Cosmos DB",
        "services": [
            {"id":"func","name":"Function App","type":"function_app","details":["Consumption"]},
            {"id":"cosmos","name":"Cosmos DB","type":"cosmos_db","sku":"Serverless","details":["SQL API"]},
        ],
        "connections": [{"from":"func","to":"cosmos","label":"CRUD","type":"data"}],
    },
    {
        "id": "04", "name": "Key Vault Pattern", "level": 1,
        "desc": "App Service + Key Vault secret reference",
        "services": [
            {"id":"app","name":"App Service","type":"app_service","details":["Managed Identity"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","details":["RBAC"]},
        ],
        "connections": [{"from":"app","to":"kv","label":"Secrets","type":"security"}],
    },
    # Level 2
    {
        "id": "05", "name": "Basic RAG Chatbot", "level": 2,
        "desc": "Foundry + AI Search + Storage + Key Vault",
        "services": [
            {"id":"foundry","name":"MS Foundry","type":"ai_foundry","sku":"S0","details":["gpt-4o","text-embedding-3-large"]},
            {"id":"search","name":"AI Search","type":"search","sku":"Standard S1","details":["Semantic"]},
            {"id":"storage","name":"ADLS Gen2","type":"storage","sku":"Standard_LRS","details":["Documents"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","details":["RBAC"]},
        ],
        "connections": [
            {"from":"foundry","to":"search","label":"RAG","type":"api"},
            {"from":"search","to":"storage","label":"Indexing","type":"data"},
            {"from":"foundry","to":"kv","label":"Secrets","type":"security"},
        ],
    },
    {
        "id": "06", "name": "Web App + Cache", "level": 2,
        "desc": "App Service + SQL + Redis + App Insights",
        "services": [
            {"id":"app","name":"App Service","type":"app_service","sku":"S1","details":["Production"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","sku":"S1","details":["50 DTU"]},
            {"id":"redis","name":"Azure Redis","type":"default","details":["Cache"]},
            {"id":"ai","name":"App Insights","type":"app_insights","details":["Monitoring"]},
        ],
        "connections": [
            {"from":"app","to":"sql","label":"Query","type":"data"},
            {"from":"app","to":"redis","label":"Cache","type":"data"},
            {"from":"app","to":"ai","label":"Telemetry","type":"api"},
        ],
    },
    {
        "id": "07", "name": "Event-Driven Processing", "level": 2,
        "desc": "Event Hub + Function App + Cosmos DB",
        "services": [
            {"id":"eh","name":"Event Hub","type":"default","sku":"Standard","details":["Stream"]},
            {"id":"func","name":"Function App","type":"function_app","details":["Consumer"]},
            {"id":"cosmos","name":"Cosmos DB","type":"cosmos_db","details":["Store"]},
            {"id":"storage","name":"Storage","type":"storage","details":["Dead Letter"]},
        ],
        "connections": [
            {"from":"eh","to":"func","label":"Events","type":"data"},
            {"from":"func","to":"cosmos","label":"Write","type":"data"},
            {"from":"func","to":"storage","label":"DLQ","type":"data"},
        ],
    },
    {
        "id": "08", "name": "CI/CD Pipeline", "level": 2,
        "desc": "DevOps + ACR + AKS",
        "services": [
            {"id":"devops","name":"Azure DevOps","type":"default","details":["Pipeline"]},
            {"id":"acr","name":"Container Registry","type":"default","details":["ACR"]},
            {"id":"aks","name":"AKS","type":"aks","sku":"Standard","details":["K8s Cluster"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","details":["Secrets"]},
        ],
        "connections": [
            {"from":"devops","to":"acr","label":"Push Image","type":"data"},
            {"from":"acr","to":"aks","label":"Deploy","type":"api"},
            {"from":"aks","to":"kv","label":"Secrets","type":"security"},
        ],
    },
    # Level 3
    {
        "id": "09", "name": "RAG Chatbot (Private)", "level": 3,
        "desc": "Full PE isolation — Foundry + Search + ADLS + KV + VNet",
        "services": [
            {"id":"foundry","name":"MS Foundry","type":"ai_foundry","sku":"S0","private":True,"details":["gpt-4o"]},
            {"id":"project","name":"Foundry Project","type":"ai_foundry","private":True,"details":["Project"]},
            {"id":"search","name":"AI Search","type":"search","sku":"S1","private":True,"details":["Semantic"]},
            {"id":"storage","name":"ADLS Gen2","type":"storage","private":True,"details":["HNS"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","private":True,"details":["RBAC"]},
            {"id":"pe1","name":"PE: Foundry","type":"pe","details":["account"]},
            {"id":"pe2","name":"PE: Search","type":"pe","details":["searchService"]},
            {"id":"pe3","name":"PE: Storage","type":"pe","details":["blob"]},
            {"id":"pe4","name":"PE: KV","type":"pe","details":["vault"]},
        ],
        "connections": [
            {"from":"foundry","to":"project","label":"parent","type":"api"},
            {"from":"foundry","to":"search","label":"RAG","type":"api"},
            {"from":"search","to":"storage","label":"Index","type":"data"},
            {"from":"foundry","to":"kv","label":"Secrets","type":"security"},
            {"from":"foundry","to":"pe1","label":"","type":"private"},
            {"from":"search","to":"pe2","label":"","type":"private"},
            {"from":"storage","to":"pe3","label":"","type":"private"},
            {"from":"kv","to":"pe4","label":"","type":"private"},
        ],
        "vnet_info": "10.0.0.0/16 | pe-subnet: 10.0.1.0/24",
    },
    {
        "id": "10", "name": "Data Lakehouse", "level": 3,
        "desc": "Databricks + ADLS Gen2 + ADF + Key Vault",
        "services": [
            {"id":"databricks","name":"Databricks","type":"databricks","sku":"Premium","details":["VNet Injection"]},
            {"id":"adls","name":"ADLS Gen2","type":"storage","sku":"Standard_LRS","details":["isHnsEnabled"]},
            {"id":"adf","name":"Data Factory","type":"adf","details":["Pipeline"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","details":["Secrets"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","sku":"S1","details":["Source"]},
        ],
        "connections": [
            {"from":"adf","to":"sql","label":"Extract","type":"data"},
            {"from":"adf","to":"adls","label":"Load","type":"data"},
            {"from":"databricks","to":"adls","label":"Transform","type":"data"},
            {"from":"databricks","to":"kv","label":"Secrets","type":"security"},
        ],
    },
    {
        "id": "11", "name": "Microservices (AKS)", "level": 3,
        "desc": "AKS + ACR + SQL + Redis + App Gateway",
        "services": [
            {"id":"agw","name":"App Gateway","type":"default","details":["WAF v2"]},
            {"id":"aks","name":"AKS","type":"aks","sku":"Standard","details":["3 nodes"]},
            {"id":"acr","name":"ACR","type":"default","details":["Premium"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","sku":"S2","details":["DTU"]},
            {"id":"redis","name":"Redis","type":"default","details":["Cache"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","details":["Secrets"]},
        ],
        "connections": [
            {"from":"agw","to":"aks","label":"Ingress","type":"api"},
            {"from":"aks","to":"sql","label":"Data","type":"data"},
            {"from":"aks","to":"redis","label":"Cache","type":"data"},
            {"from":"aks","to":"kv","label":"Secrets","type":"security"},
            {"from":"acr","to":"aks","label":"Images","type":"api"},
        ],
    },
    {
        "id": "12", "name": "IoT Solution", "level": 3,
        "desc": "IoT Hub + Stream Analytics + Cosmos + Function",
        "services": [
            {"id":"iot","name":"IoT Hub","type":"default","sku":"S1","details":["Devices"]},
            {"id":"sa","name":"Stream Analytics","type":"default","details":["Real-time"]},
            {"id":"cosmos","name":"Cosmos DB","type":"cosmos_db","details":["Hot Store"]},
            {"id":"func","name":"Function App","type":"function_app","details":["Alerts"]},
            {"id":"storage","name":"Storage","type":"storage","details":["Cold Store"]},
        ],
        "connections": [
            {"from":"iot","to":"sa","label":"Telemetry","type":"data"},
            {"from":"sa","to":"cosmos","label":"Hot Path","type":"data"},
            {"from":"sa","to":"storage","label":"Cold Path","type":"data"},
            {"from":"sa","to":"func","label":"Alerts","type":"api"},
        ],
    },
    # Level 4
    {
        "id": "13", "name": "Enterprise RAG", "level": 4,
        "desc": "Full enterprise RAG with monitoring + bastion",
        "services": [
            {"id":"foundry","name":"MS Foundry","type":"ai_foundry","sku":"S0","private":True,"subscription":"sub-prod","resourceGroup":"rg-ai","details":["gpt-4o"]},
            {"id":"search","name":"AI Search","type":"search","sku":"S1","private":True,"subscription":"sub-prod","resourceGroup":"rg-ai","details":["Semantic"]},
            {"id":"storage","name":"ADLS Gen2","type":"storage","private":True,"subscription":"sub-prod","resourceGroup":"rg-data","details":["HNS"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","private":True,"subscription":"sub-prod","resourceGroup":"rg-ai","details":["RBAC"]},
            {"id":"app","name":"App Service","type":"app_service","subscription":"sub-prod","resourceGroup":"rg-app","details":["Chat UI"]},
            {"id":"bastion","name":"Bastion","type":"bastion","subscription":"sub-prod","resourceGroup":"rg-network","details":["Admin"]},
            {"id":"log","name":"Log Analytics","type":"log_analytics","subscription":"sub-prod","resourceGroup":"rg-monitor","details":["Logs"]},
        ],
        "connections": [
            {"from":"app","to":"foundry","label":"Chat API","type":"api"},
            {"from":"foundry","to":"search","label":"RAG","type":"api"},
            {"from":"search","to":"storage","label":"Index","type":"data"},
            {"from":"foundry","to":"kv","label":"Secrets","type":"security"},
            {"from":"app","to":"log","label":"Logs","type":"api"},
        ],
        "hierarchy": [{"subscription":"sub-prod","resourceGroups":["rg-ai","rg-data","rg-app","rg-network","rg-monitor"]}],
    },
    {
        "id": "14", "name": "Data Analytics Platform", "level": 4,
        "desc": "Fabric + Databricks + ADLS + ADF + SQL",
        "services": [
            {"id":"fabric","name":"MS Fabric","type":"fabric","sku":"F4","subscription":"sub-data","resourceGroup":"rg-analytics","details":["Capacity"]},
            {"id":"databricks","name":"Databricks","type":"databricks","sku":"Premium","subscription":"sub-data","resourceGroup":"rg-analytics","details":["ML"]},
            {"id":"adls","name":"ADLS Gen2","type":"storage","subscription":"sub-data","resourceGroup":"rg-storage","details":["Data Lake"]},
            {"id":"adf","name":"Data Factory","type":"adf","subscription":"sub-data","resourceGroup":"rg-ingest","details":["ETL"]},
            {"id":"sql","name":"SQL Server","type":"sql_server","subscription":"sub-data","resourceGroup":"rg-sources","details":["Source"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","subscription":"sub-data","resourceGroup":"rg-security","details":["Secrets"]},
        ],
        "connections": [
            {"from":"adf","to":"sql","label":"Extract","type":"data"},
            {"from":"adf","to":"adls","label":"Load","type":"data"},
            {"from":"databricks","to":"adls","label":"Transform","type":"data"},
            {"from":"fabric","to":"adls","label":"Analyze","type":"data"},
            {"from":"databricks","to":"kv","label":"Secrets","type":"security"},
        ],
        "hierarchy": [{"subscription":"sub-data","resourceGroups":["rg-analytics","rg-storage","rg-ingest","rg-sources","rg-security"]}],
    },
    {
        "id": "15", "name": "Hybrid Network", "level": 4,
        "desc": "VPN + Firewall + Bastion + Hub-Spoke",
        "services": [
            {"id":"fw","name":"Azure Firewall","type":"nsg","subscription":"hub","resourceGroup":"rg-hub","details":["Central Firewall"]},
            {"id":"bastion","name":"Bastion","type":"bastion","subscription":"hub","resourceGroup":"rg-hub","details":["Admin Access"]},
            {"id":"vpn","name":"VPN Gateway","type":"default","subscription":"hub","resourceGroup":"rg-hub","details":["On-premises"]},
            {"id":"app","name":"App Service","type":"app_service","subscription":"spoke-1","resourceGroup":"rg-workload","details":["Web App"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","subscription":"spoke-1","resourceGroup":"rg-workload","details":["Data"]},
            {"id":"vm","name":"Jump VM","type":"vm","subscription":"spoke-1","resourceGroup":"rg-workload","details":["Admin"]},
        ],
        "connections": [
            {"from":"vpn","to":"fw","label":"On-prem","type":"network"},
            {"from":"fw","to":"app","label":"Allow","type":"network"},
            {"from":"bastion","to":"vm","label":"RDP/SSH","type":"network"},
            {"from":"app","to":"sql","label":"Data","type":"data"},
        ],
        "hierarchy": [
            {"subscription":"hub","resourceGroups":["rg-hub"]},
            {"subscription":"spoke-1","resourceGroups":["rg-workload"]},
        ],
    },
    {
        "id": "16", "name": "Multi-tier Web App", "level": 4,
        "desc": "App Gateway + App Service + SQL + Redis + CDN",
        "services": [
            {"id":"cdn","name":"Azure CDN","type":"default","subscription":"prod","resourceGroup":"rg-frontend","details":["Global"]},
            {"id":"agw","name":"App Gateway","type":"default","subscription":"prod","resourceGroup":"rg-frontend","details":["WAF v2"]},
            {"id":"app","name":"App Service","type":"app_service","sku":"P1v3","subscription":"prod","resourceGroup":"rg-app","details":["Web"]},
            {"id":"redis","name":"Redis Cache","type":"default","subscription":"prod","resourceGroup":"rg-app","details":["Session"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","sku":"S2","subscription":"prod","resourceGroup":"rg-data","details":["Primary"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","subscription":"prod","resourceGroup":"rg-security","details":["RBAC"]},
            {"id":"ai","name":"App Insights","type":"app_insights","subscription":"prod","resourceGroup":"rg-monitor","details":["APM"]},
        ],
        "connections": [
            {"from":"cdn","to":"agw","label":"Static","type":"data"},
            {"from":"agw","to":"app","label":"Ingress","type":"api"},
            {"from":"app","to":"redis","label":"Cache","type":"data"},
            {"from":"app","to":"sql","label":"Query","type":"data"},
            {"from":"app","to":"kv","label":"Secrets","type":"security"},
            {"from":"app","to":"ai","label":"Telemetry","type":"api"},
        ],
        "hierarchy": [{"subscription":"prod","resourceGroups":["rg-frontend","rg-app","rg-data","rg-security","rg-monitor"]}],
    },
    # Level 5
    {
        "id": "17", "name": "Azure Landing Zone", "level": 5,
        "desc": "Enterprise governance — Hub + 2 Spokes",
        "services": [
            {"id":"fw","name":"Azure Firewall","type":"nsg","subscription":"connectivity","resourceGroup":"rg-hub","details":["Premium"]},
            {"id":"bastion","name":"Bastion","type":"bastion","subscription":"connectivity","resourceGroup":"rg-hub","details":["Standard"]},
            {"id":"vpn","name":"VPN Gateway","type":"default","subscription":"connectivity","resourceGroup":"rg-hub","details":["S2S"]},
            {"id":"log","name":"Log Analytics","type":"log_analytics","subscription":"management","resourceGroup":"rg-management","details":["Central Logs"]},
            {"id":"foundry","name":"MS Foundry","type":"ai_foundry","sku":"S0","subscription":"workload-ai","resourceGroup":"rg-ai-prod","details":["AI"]},
            {"id":"search","name":"AI Search","type":"search","subscription":"workload-ai","resourceGroup":"rg-ai-prod","details":["RAG"]},
            {"id":"app","name":"App Service","type":"app_service","subscription":"workload-web","resourceGroup":"rg-web-prod","details":["Web"]},
            {"id":"sql","name":"SQL Database","type":"sql_database","subscription":"workload-web","resourceGroup":"rg-web-prod","details":["Data"]},
        ],
        "connections": [
            {"from":"vpn","to":"fw","label":"On-prem","type":"network"},
            {"from":"fw","to":"foundry","label":"Allow","type":"network"},
            {"from":"fw","to":"app","label":"Allow","type":"network"},
            {"from":"app","to":"sql","label":"Data","type":"data"},
            {"from":"foundry","to":"search","label":"RAG","type":"api"},
            {"from":"app","to":"log","label":"Logs","type":"api"},
            {"from":"foundry","to":"log","label":"Logs","type":"api"},
        ],
        "hierarchy": [
            {"subscription":"connectivity","resourceGroups":["rg-hub"]},
            {"subscription":"management","resourceGroups":["rg-management"]},
            {"subscription":"workload-ai","resourceGroups":["rg-ai-prod"]},
            {"subscription":"workload-web","resourceGroups":["rg-web-prod"]},
        ],
    },
    {
        "id": "18", "name": "Mission-Critical AKS", "level": 5,
        "desc": "Multi-region AKS + Front Door + Cosmos",
        "services": [
            {"id":"fd","name":"Front Door","type":"default","subscription":"global","resourceGroup":"rg-global","details":["Global LB"]},
            {"id":"aks1","name":"AKS (East US)","type":"aks","subscription":"region-east","resourceGroup":"rg-east","details":["Primary"]},
            {"id":"aks2","name":"AKS (West EU)","type":"aks","subscription":"region-west","resourceGroup":"rg-west","details":["Secondary"]},
            {"id":"cosmos","name":"Cosmos DB","type":"cosmos_db","subscription":"global","resourceGroup":"rg-global","details":["Multi-region"]},
            {"id":"acr","name":"ACR","type":"default","subscription":"global","resourceGroup":"rg-global","details":["Geo-replicated"]},
            {"id":"kv1","name":"KV East","type":"keyvault","subscription":"region-east","resourceGroup":"rg-east","details":["Secrets"]},
            {"id":"kv2","name":"KV West","type":"keyvault","subscription":"region-west","resourceGroup":"rg-west","details":["Secrets"]},
        ],
        "connections": [
            {"from":"fd","to":"aks1","label":"Route","type":"api"},
            {"from":"fd","to":"aks2","label":"Route","type":"api"},
            {"from":"aks1","to":"cosmos","label":"Data","type":"data"},
            {"from":"aks2","to":"cosmos","label":"Data","type":"data"},
            {"from":"acr","to":"aks1","label":"Image","type":"api"},
            {"from":"acr","to":"aks2","label":"Image","type":"api"},
            {"from":"aks1","to":"kv1","label":"Secrets","type":"security"},
            {"from":"aks2","to":"kv2","label":"Secrets","type":"security"},
        ],
        "hierarchy": [
            {"subscription":"global","resourceGroups":["rg-global"]},
            {"subscription":"region-east","resourceGroups":["rg-east"]},
            {"subscription":"region-west","resourceGroups":["rg-west"]},
        ],
    },
    {
        "id": "19", "name": "AI/ML Platform", "level": 5,
        "desc": "Full AI lifecycle — Foundry + AI Hub + AML + Databricks",
        "services": [
            {"id":"foundry","name":"MS Foundry","type":"ai_foundry","sku":"S0","subscription":"ai-platform","resourceGroup":"rg-foundry","details":["GPT-4o"]},
            {"id":"hub","name":"AI Hub","type":"default","subscription":"ai-platform","resourceGroup":"rg-ml","details":["ML Workspace"]},
            {"id":"search","name":"AI Search","type":"search","sku":"S1","subscription":"ai-platform","resourceGroup":"rg-foundry","details":["RAG"]},
            {"id":"databricks","name":"Databricks","type":"databricks","sku":"Premium","subscription":"ai-platform","resourceGroup":"rg-ml","details":["Feature Eng"]},
            {"id":"adls","name":"ADLS Gen2","type":"storage","subscription":"ai-platform","resourceGroup":"rg-data","details":["Data Lake"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","subscription":"ai-platform","resourceGroup":"rg-security","details":["RBAC"]},
            {"id":"log","name":"Log Analytics","type":"log_analytics","subscription":"ai-platform","resourceGroup":"rg-monitor","details":["Logs"]},
            {"id":"ai","name":"App Insights","type":"app_insights","subscription":"ai-platform","resourceGroup":"rg-monitor","details":["ML Metrics"]},
        ],
        "connections": [
            {"from":"foundry","to":"search","label":"RAG","type":"api"},
            {"from":"hub","to":"adls","label":"Training Data","type":"data"},
            {"from":"hub","to":"databricks","label":"Feature Store","type":"data"},
            {"from":"databricks","to":"adls","label":"ETL","type":"data"},
            {"from":"foundry","to":"kv","label":"Secrets","type":"security"},
            {"from":"hub","to":"kv","label":"Secrets","type":"security"},
            {"from":"hub","to":"log","label":"Logs","type":"api"},
            {"from":"foundry","to":"ai","label":"Metrics","type":"api"},
        ],
        "hierarchy": [{"subscription":"ai-platform","resourceGroups":["rg-foundry","rg-ml","rg-data","rg-security","rg-monitor"]}],
    },
    {
        "id": "20", "name": "Data Mesh", "level": 5,
        "desc": "Distributed data governance — Fabric + multi-domain",
        "services": [
            {"id":"fabric","name":"MS Fabric","type":"fabric","sku":"F8","subscription":"data-platform","resourceGroup":"rg-fabric","details":["Central"]},
            {"id":"adls1","name":"ADLS Sales","type":"storage","subscription":"domain-sales","resourceGroup":"rg-sales-data","details":["Sales Domain"]},
            {"id":"adls2","name":"ADLS Finance","type":"storage","subscription":"domain-finance","resourceGroup":"rg-finance-data","details":["Finance Domain"]},
            {"id":"adf1","name":"ADF Sales","type":"adf","subscription":"domain-sales","resourceGroup":"rg-sales-data","details":["Sales Pipeline"]},
            {"id":"adf2","name":"ADF Finance","type":"adf","subscription":"domain-finance","resourceGroup":"rg-finance-data","details":["Finance Pipeline"]},
            {"id":"sql1","name":"SQL Sales","type":"sql_database","subscription":"domain-sales","resourceGroup":"rg-sales-src","details":["Source"]},
            {"id":"sql2","name":"SQL Finance","type":"sql_database","subscription":"domain-finance","resourceGroup":"rg-finance-src","details":["Source"]},
            {"id":"kv","name":"Key Vault","type":"keyvault","subscription":"data-platform","resourceGroup":"rg-governance","details":["Central KV"]},
        ],
        "connections": [
            {"from":"adf1","to":"sql1","label":"Extract","type":"data"},
            {"from":"adf1","to":"adls1","label":"Load","type":"data"},
            {"from":"adf2","to":"sql2","label":"Extract","type":"data"},
            {"from":"adf2","to":"adls2","label":"Load","type":"data"},
            {"from":"fabric","to":"adls1","label":"Analyze","type":"data"},
            {"from":"fabric","to":"adls2","label":"Analyze","type":"data"},
            {"from":"fabric","to":"kv","label":"Secrets","type":"security"},
        ],
        "hierarchy": [
            {"subscription":"data-platform","resourceGroups":["rg-fabric","rg-governance"]},
            {"subscription":"domain-sales","resourceGroups":["rg-sales-data","rg-sales-src"]},
            {"subscription":"domain-finance","resourceGroups":["rg-finance-data","rg-finance-src"]},
        ],
    },
]


def main():
    python = sys.executable
    results = []

    for arch in ARCHITECTURES:
        aid = arch["id"]
        name = arch["name"]
        level = arch["level"]
        html_file = os.path.join(OUTPUT_DIR, f"{aid}-{name.lower().replace(' ', '-').replace('/', '-')}.html")
        png_file = html_file.replace(".html", ".png")

        services_json = json.dumps(arch["services"], ensure_ascii=False)
        connections_json = json.dumps(arch["connections"], ensure_ascii=False)
        title = f"[Lv{level}] {name}"

        cmd = [python, DIAGRAM_SCRIPT,
               "--services", services_json,
               "--connections", connections_json,
               "--title", title,
               "--output", html_file]

        if arch.get("vnet_info"):
            cmd += ["--vnet-info", arch["vnet_info"]]
        if arch.get("hierarchy"):
            cmd += ["--hierarchy", json.dumps(arch["hierarchy"], ensure_ascii=False)]

        print(f"[{aid}] Generating {name}...", end=" ")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"FAIL: {r.stderr[:200]}")
            results.append({"id": aid, "name": name, "level": level, "desc": arch["desc"],
                          "html": html_file, "png": None, "status": "FAIL"})
            continue

        # Screenshot with puppeteer
        ss_script = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{headless: true}});
  const page = await browser.newPage();
  await page.setViewport({{width: 1920, height: 1080}});
  await page.goto('file:///{html_file.replace(os.sep, "/")}', {{waitUntil: 'networkidle0', timeout: 10000}});
  await new Promise(r => setTimeout(r, 1500));
  await page.screenshot({{path: '{png_file.replace(os.sep, "/")}'}});
  await browser.close();
}})();
"""
        ss_file = os.path.join(os.environ["TEMP"], "ss_batch.js")
        with open(ss_file, "w") as f:
            f.write(ss_script)

        sr = subprocess.run(["node", ss_file], capture_output=True, text=True,
                          cwd=os.environ["TEMP"])
        if sr.returncode == 0 and os.path.exists(png_file):
            print("OK ✅")
            results.append({"id": aid, "name": name, "level": level, "desc": arch["desc"],
                          "html": os.path.basename(html_file),
                          "png": os.path.basename(png_file), "status": "OK"})
        else:
            print(f"Screenshot FAIL")
            results.append({"id": aid, "name": name, "level": level, "desc": arch["desc"],
                          "html": os.path.basename(html_file), "png": None, "status": "HTML_ONLY"})

    # Generate REPORT.md
    report_path = os.path.join(OUTPUT_DIR, "REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Azure Architecture Diagram Test Report\n\n")
        f.write(f"20 architectures generated — {sum(1 for r in results if r['status']=='OK')} with screenshots\n\n")
        f.write("---\n\n")

        for level in range(1, 6):
            stars = "⭐" * level
            f.write(f"## {stars} Level {level}\n\n")
            level_results = [r for r in results if r["level"] == level]
            for r in level_results:
                f.write(f"### {r['id']}. {r['name']}\n\n")
                f.write(f"**{r['desc']}**\n\n")
                if r["png"]:
                    f.write(f"![{r['name']}]({r['png']})\n\n")
                f.write(f"📄 [{r['html']}]({r['html']})\n\n")
                f.write("---\n\n")

    print(f"\n✅ REPORT.md generated at {report_path}")
    print(f"Total: {len(results)}, OK: {sum(1 for r in results if r['status']=='OK')}, "
          f"HTML Only: {sum(1 for r in results if r['status']=='HTML_ONLY')}, "
          f"Fail: {sum(1 for r in results if r['status']=='FAIL')}")


if __name__ == "__main__":
    main()
