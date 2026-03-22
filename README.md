<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/logo.svg" width="120" alt="az-diagram-autogen logo">
</p>

<h1 align="center">az-diagram-autogen</h1>

<p align="center">
  <strong>Interactive Azure architecture diagrams from JSON — with 605 official Azure icons</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/az-diagram-autogen/"><img src="https://img.shields.io/pypi/v/az-diagram-autogen?color=blue&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/az-diagram-autogen/"><img src="https://img.shields.io/pypi/pyversions/az-diagram-autogen" alt="Python"></a>
  <a href="https://github.com/whoniiii/az-diagram-autogen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/whoniiii/az-diagram-autogen" alt="License"></a>
  <a href="https://pypi.org/project/az-diagram-autogen/"><img src="https://img.shields.io/pypi/dm/az-diagram-autogen?color=green" alt="Downloads"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-cli-reference">CLI</a> •
  <a href="#-python-api">Python API</a> •
  <a href="#-supported-types">Service Types</a>
</p>

---

## 🎨 What It Looks Like

### Basic RAG Chatbot
<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/basic_rag.png" width="100%" alt="Basic RAG Chatbot Architecture">
</p>

### Multi-Subscription Landing Zone
<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/landing_zone.png" width="100%" alt="Azure Landing Zone Architecture">
</p>

### Private RAG with VNet & PE
<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/private_rag.png" width="100%" alt="Private RAG Architecture">
</p>

---

## 🚀 Quick Start

```bash
pip install az-diagram-autogen
```

**Generate your first diagram in 10 seconds:**

```bash
# Create a simple JSON file
cat > my-arch.json << 'EOF'
{
  "title": "My RAG App",
  "services": [
    {"id": "foundry", "name": "AI Foundry", "type": "ai_foundry", "sku": "S0"},
    {"id": "search", "name": "AI Search", "type": "ai_search", "sku": "S1"},
    {"id": "storage", "name": "ADLS Gen2", "type": "storage"},
    {"id": "kv", "name": "Key Vault", "type": "keyvault"}
  ],
  "connections": [
    {"from": "foundry", "to": "search", "label": "RAG Query", "type": "api"},
    {"from": "search", "to": "storage", "label": "Indexing", "type": "data"},
    {"from": "foundry", "to": "kv", "label": "Secrets", "type": "security"}
  ]
}
EOF

# Generate the diagram
az-diagram-autogen -s my-arch.json -c my-arch.json -o my-arch.html

# Open in browser 🎉
```

> **Output is a single self-contained HTML file** — no server, no dependencies, just open it.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **605 Azure Icons** | Official Microsoft Azure icons, Base64-encoded — works offline |
| 🖱️ **Interactive** | Drag-and-drop nodes, pan & zoom, click for details |
| 🔒 **Private Endpoints** | Visualize PE connections with dedicated group |
| 🌐 **VNet Boundaries** | Purple dashed boundaries with CIDR labels |
| 📦 **Multi-Sub/RG** | Nested subscription → resource group hierarchy |
| 🎨 **Auto-Layout** | Smart category-based or RG-based grouping |
| 📊 **Sidebar** | Resource details panel with SKU, tags, connection legend |
| 📄 **Self-Contained** | Single HTML file — share via email, Slack, Teams |
| 🐍 **Dual Interface** | CLI tool + Python API |
| 0️⃣ **Zero Dependencies** | Pure Python, no external packages required |

---

## 📋 Examples

### 1. Basic — RAG Chatbot

```bash
az-diagram-autogen -s examples/basic_rag.json -o rag.html
```

### 2. With VNet & Private Endpoints

```bash
az-diagram-autogen \
  -s examples/private_rag.json \
  --vnet-info "10.0.0.0/16 | pe-subnet: 10.0.1.0/24" \
  -o private-rag.html
```

### 3. Multi-Subscription Landing Zone

```bash
az-diagram-autogen \
  -s examples/landing_zone.json \
  -o landing-zone.html
```

> See the [`examples/`](examples/) directory for ready-to-use JSON files.

---

## 💻 CLI Reference

```
az-diagram-autogen [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--services` | `-s` | *(required)* | Services JSON — inline string or file path |
| `--connections` | `-c` | *(required)* | Connections JSON — inline string or file path |
| `--title` | `-t` | `"Azure Architecture"` | Diagram title |
| `--output` | `-o` | `"azure-architecture.html"` | Output HTML file path |
| `--vnet-info` | | `""` | VNet CIDR label for boundary |
| `--hierarchy` | | `""` | Subscription/RG hierarchy JSON |

**Supports both inline JSON and file paths:**
```bash
# Inline JSON
az-diagram-autogen -s '[{"id":"s1",...}]' -c '[...]'

# File path (auto-detected)
az-diagram-autogen -s services.json -c connections.json
```

---

## 🐍 Python API

```python
from az_diagram_autogen import generate_diagram

html = generate_diagram(
    services=[
        {"id": "foundry", "name": "AI Foundry", "type": "ai_foundry", "sku": "S0"},
        {"id": "search", "name": "AI Search", "type": "ai_search", "sku": "S1"},
    ],
    connections=[
        {"from": "foundry", "to": "search", "label": "RAG Query", "type": "api"},
    ],
    title="My Architecture",
    vnet_info="10.0.0.0/16 | pe-subnet: 10.0.1.0/24",
    hierarchy=[{"subscription": "prod-sub", "resourceGroups": ["rg-ai", "rg-data"]}],
)

with open("output.html", "w") as f:
    f.write(html)
```

### Search Azure Icons

```python
from az_diagram_autogen import search_icons

for key, name, category in search_icons("storage"):
    print(f"  {key}: {name} ({category})")
# storage_accounts: Storage Accounts (Storage)
# storage_accounts_classic: Storage Accounts (Classic) (Storage)
# ...
```

---

## 📐 JSON Schema

### Service Object

```jsonc
{
  "id": "unique-kebab-case",       // Required — unique identifier
  "name": "Display Name",          // Required — shown on node
  "type": "ai_foundry",            // Required — determines icon & category
  "sku": "S0",                     // Optional — shown under name
  "private": false,                // Optional — marks as PE-connected
  "details": ["GPT-4o", "..."],    // Optional — shown in sidebar
  "subscription": "sub-name",      // Optional — for multi-sub diagrams
  "resourceGroup": "rg-name"       // Optional — for multi-RG diagrams
}
```

### Connection Object

```jsonc
{
  "from": "service-id",            // Required — source service ID
  "to": "service-id",              // Required — target service ID
  "label": "RAG Query",            // Optional — shown on line
  "type": "api"                    // Optional — api|data|security|private|network|default
}
```

### Connection Types & Colors

| Type | Color | Style | Use For |
|------|-------|-------|---------|
| `api` | 🔵 Blue | Solid | API calls, queries |
| `data` | 🟢 Green | Solid | Data flow, indexing |
| `security` | 🟡 Orange | Dashed | Secrets, auth |
| `private` | 🟣 Purple | Dashed | Private endpoint |
| `network` | ⚫ Gray | Solid | Network routing |
| `default` | ⚫ Gray | Solid | Other |

---

## 🏗️ Supported Types

<details>
<summary><strong>30+ Azure service types</strong> (click to expand)</summary>

| Type | Label | Category | Icon |
|------|-------|----------|------|
| `ai_foundry` | AI Foundry | AI | ☁️ |
| `ai_search` / `search` | AI Search | AI | 🔍 |
| `document_intelligence` | Doc Intelligence | AI | 📄 |
| `storage` | Storage | Data | 📦 |
| `cosmos_db` | Cosmos DB | Data | 🌍 |
| `sql_database` | SQL Database | Data | 🗃️ |
| `databricks` | Databricks | Data | 🧱 |
| `data_factory` / `adf` | Data Factory | Data | ➡️ |
| `fabric` | Fabric | Data | 🔷 |
| `redis` | Redis Cache | Data | ⚡ |
| `stream_analytics` | Stream Analytics | Data | 📊 |
| `keyvault` | Key Vault | Security | 🔑 |
| `app_service` | App Service | Compute | 🌐 |
| `function_app` | Function App | Compute | ⚡ |
| `aks` | AKS | Compute | ☸️ |
| `acr` | Container Registry | Compute | 📦 |
| `vm` | Virtual Machine | Compute | 🖥️ |
| `firewall` | Firewall | Network | 🔥 |
| `bastion` | Bastion | Network | 🏰 |
| `vpn_gateway` | VPN Gateway | Network | 🔗 |
| `app_gateway` | App Gateway | Network | 🚪 |
| `front_door` | Front Door | Network | 🚀 |
| `cdn` | CDN | Network | 🌍 |
| `nsg` | NSG | Network | 🛡️ |
| `iot_hub` | IoT Hub | IoT | 📡 |
| `event_hub` | Event Hub | Integration | ⚡ |
| `log_analytics` | Log Analytics | Monitor | 📈 |
| `app_insights` | App Insights | Monitor | 📊 |
| `devops` | Azure DevOps | DevOps | 🔄 |

> Unrecognized types render with a default "?" icon — all Azure services work.

</details>

---

## 🔧 For GHCP Skill Developers

This package is designed as a **rendering engine for GitHub Copilot CLI skills**. When building a skill that designs Azure architectures, add the following to your `SKILL.md` to integrate diagram generation.

### Step 1: Add to SKILL.md

Copy this block into your skill's diagram generation instructions:

````markdown
### 다이어그램 생성

아키텍처 설계가 확정되면 아래 명령으로 인터랙티브 다이어그램을 생성한다.

```powershell
# Python 경로 탐색 (Windows Store alias 방지 — Get-Command python 사용 금지)
$pyPath = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
if (-not $pyPath) { $pyPath = "python" }

# 다이어그램 생성
& $pyPath -m az_diagram_autogen.cli `
  --services '<services JSON>' `
  --connections '<connections JSON>' `
  --title '<프로젝트명> Architecture' `
  --output '<project-folder>/01_arch_diagram_draft.html' `
  --vnet-info '<VNet CIDR 정보 (선택)>' `
  --hierarchy '<구독/RG 계층 JSON (선택)>'
```

**패키지 미설치 시**: `pip install az-diagram-autogen` 실행 후 재시도.
````

### Step 2: Generate Services & Connections JSON

Your skill's Phase 1 (Architecture Design) should produce JSON matching this schema:

```jsonc
// services — 각 Azure 리소스
[
  {
    "id": "foundry-hub",              // Required: unique kebab-case ID
    "name": "AI Foundry Hub",         // Required: display name
    "type": "ai_foundry",             // Required: must match a supported type (see table below)
    "sku": "S0",                      // Optional: shown in sidebar
    "private": true,                  // Optional: marks as PE-connected (default: false)
    "details": ["GPT-4o", "..."],     // Optional: extra info in sidebar
    "subscription": "prod-sub",       // Optional: for multi-subscription diagrams
    "resourceGroup": "rg-ai"          // Optional: for multi-RG diagrams
  }
]

// connections — 서비스 간 연결
[
  {
    "from": "foundry-hub",            // Required: source service ID
    "to": "search",                   // Required: target service ID
    "label": "RAG Query",             // Optional: line label
    "type": "api"                     // Optional: api|data|security|private|network|default
  }
]
```

### Step 3: Diagram File Naming Convention

| File | When | Description |
|------|------|-------------|
| `00_arch_current.html` | Phase 0 (Path B) | Scanned existing architecture |
| `01_arch_diagram_draft.html` | Phase 1 | Initial design draft |
| `02_arch_diagram_preview.html` | Phase 4 (pre-deploy) | What-if preview |
| `03_arch_diagram_result.html` | Phase 4 (post-deploy) | Final deployed architecture |
| `04_arch_diagram_update_draft.html` | Delta update | Post-deployment modification |

### Step 4: Hierarchy Parameter (Multi-Sub/RG)

For multi-subscription or multi-resource-group architectures, pass the `--hierarchy` parameter:

```json
[
  {"subscription": "connectivity-sub", "resourceGroups": ["rg-hub"]},
  {"subscription": "workload-sub", "resourceGroups": ["rg-ai", "rg-data", "rg-security"]}
]
```

When hierarchy is provided:
- Each service **must** have `subscription` and `resourceGroup` fields
- Layout switches from category-based to **RG-based grouping**
- Subscription boundaries render as labeled boxes containing RG boxes

### Supported Service Types (Complete List)

Your skill must use these exact `type` values:

| Type | Label | Category | Type | Label | Category |
|------|-------|----------|------|-------|----------|
| `ai_foundry` | AI Foundry | AI | `aks` | AKS | Compute |
| `ai_search` | AI Search | AI | `acr` | Container Registry | Compute |
| `search` | AI Search | AI | `vm` | Virtual Machine | Compute |
| `document_intelligence` | Doc Intelligence | AI | `firewall` | Firewall | Network |
| `storage` | Storage | Data | `bastion` | Bastion | Network |
| `cosmos_db` | Cosmos DB | Data | `vpn_gateway` | VPN Gateway | Network |
| `sql_database` | SQL Database | Data | `app_gateway` | App Gateway | Network |
| `databricks` | Databricks | Data | `front_door` | Front Door | Network |
| `data_factory` | Data Factory | Data | `cdn` | CDN | Network |
| `adf` | Data Factory | Data | `nsg` | NSG | Network |
| `fabric` | Fabric | Data | `iot_hub` | IoT Hub | IoT |
| `redis` | Redis Cache | Data | `event_hub` | Event Hub | Integration |
| `stream_analytics` | Stream Analytics | Data | `log_analytics` | Log Analytics | Monitor |
| `keyvault` | Key Vault | Security | `app_insights` | App Insights | Monitor |
| `app_service` | App Service | Compute | `devops` | Azure DevOps | DevOps |
| `function_app` | Function App | Compute | *(any other)* | *(fallback)* | Azure |

> ⚠️ Unrecognized types render with a "?" icon. Always use the exact type strings above.

### Real-World Integration Example

See the [azure-arch-builder-v2](https://github.com/whoniiii/GHCP001/.github/skills/azure-arch-builder-v2) skill for a production reference implementation.

---

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

```bash
git clone https://github.com/whoniiii/az-diagram-autogen.git
cd az-diagram-autogen
pip install -e .
python -m unittest discover -s tests
```

---

## 📄 License

MIT © [Jeonghoon Lee](https://github.com/whoniiii)
