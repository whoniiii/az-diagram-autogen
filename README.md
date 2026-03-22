<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/logo.svg" width="120" alt="az-diagram-autogen logo">
</p>

<h1 align="center">az-diagram-autogen</h1>

<p align="center">
  <strong>Interactive Azure architecture diagrams from JSON — with 605 official Azure icons</strong>
</p>

<p align="center">
Generate self-contained, interactive HTML diagrams of Azure architectures from simple JSON input.<br>
Designed as a diagram rendering engine for AI coding agent skills<br>
(GitHub Copilot, Claude Code, and <a href="https://agentskills.io">Agent Skills</a>-compatible tools) —<br>
but also works standalone via CLI or Python API.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white" alt="macOS">
  <img src="https://img.shields.io/badge/Linux-FCC624?logo=linux&logoColor=black" alt="Linux">
  <img src="https://img.shields.io/badge/WSL-4D4D4D?logo=windows-terminal&logoColor=white" alt="WSL">
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
  <a href="#%EF%B8%8F-cli-reference">CLI</a> •
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

## ▶️ Quick Start

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

## ⚡ Features

| Feature | Description |
|---------|-------------|
| **605 Azure Icons** | Official Microsoft Azure icons, Base64-encoded — works offline |
| **Interactive** | Drag-and-drop nodes, pan & zoom, click for details |
| **Private Endpoints** | Visualize PE connections with dedicated group |
| **VNet Boundaries** | Purple dashed boundaries with CIDR labels |
| **Multi-Sub/RG** | Nested subscription → resource group hierarchy |
| **Auto-Layout** | Smart category-based or RG-based grouping |
| **Sidebar** | Resource details panel with SKU, tags, connection legend |
| **Self-Contained** | Single HTML file — share via email, Slack, Teams |
| **Dual Interface** | CLI tool + Python API |
| **Zero Dependencies** | Pure Python, no external packages required |
| **Cross-Platform** | Windows, macOS, Linux, WSL — anywhere Python runs |

---

## 📌 Examples

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

## 🖥️ CLI Reference

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

## 📦 Python API

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

## 📝 JSON Schema

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

## 🧩 Supported Types

<details>
<summary><strong>30+ Azure service types</strong> (click to expand)</summary>

| Type | Label | Category |
|------|-------|----------|
| `ai_foundry` | AI Foundry | AI |
| `ai_search` / `search` | AI Search | AI |
| `document_intelligence` | Doc Intelligence | AI |
| `storage` | Storage | Data |
| `cosmos_db` | Cosmos DB | Data |
| `sql_database` | SQL Database | Data |
| `databricks` | Databricks | Data |
| `data_factory` / `adf` | Data Factory | Data |
| `fabric` | Fabric | Data |
| `redis` | Redis Cache | Data |
| `stream_analytics` | Stream Analytics | Data |
| `keyvault` | Key Vault | Security |
| `app_service` | App Service | Compute |
| `function_app` | Function App | Compute |
| `aks` | AKS | Compute |
| `acr` | Container Registry | Compute |
| `vm` | Virtual Machine | Compute |
| `firewall` | Firewall | Network |
| `bastion` | Bastion | Network |
| `vpn_gateway` | VPN Gateway | Network |
| `app_gateway` | App Gateway | Network |
| `front_door` | Front Door | Network |
| `cdn` | CDN | Network |
| `nsg` | NSG | Network |
| `iot_hub` | IoT Hub | IoT |
| `event_hub` | Event Hub | Integration |
| `log_analytics` | Log Analytics | Monitor |
| `app_insights` | App Insights | Monitor |
| `devops` | Azure DevOps | DevOps |

> Unrecognized types render with a default "?" icon — all Azure services work.

</details>

---

## 🔧 For Skill Developers (GitHub Copilot, Claude Code & Agent Skills)

This package is designed as a **rendering engine for AI coding agent skills** — works with GitHub Copilot, Claude Code, and any [Agent Skills](https://agentskills.io)-compatible tool.

### 📋 Copy the block below into your SKILL.md:

> **Required**: You must include the following block in your skill's `SKILL.md`. Without this, the skill cannot generate diagrams.

````markdown
## Diagram Generation

Use the `az-diagram-autogen` package to generate architecture diagrams.

### Install
```
pip install az-diagram-autogen
```

### Read Reference
```
az-diagram-autogen --reference
```
This command prints the full service type list, JSON schema, and usage.
**You must read this reference before generating diagrams and follow the exact type values and JSON format.**

### Generate
```
az-diagram-autogen \
  --services '<services JSON or file path>' \
  --connections '<connections JSON or file path>' \
  --title '<diagram title>' \
  --output '<output>.html' \
  --vnet-info '<VNet CIDR (optional)>' \
  --hierarchy '<subscription/RG hierarchy JSON (optional)>'
```

### Or via Python API
```python
from az_diagram_autogen import generate_diagram
html = generate_diagram(services=[...], connections=[...], title="Title")
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)
```
````

---

### JSON Schema for Services & Connections

```jsonc
// services
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

// connections
[
  {
    "from": "foundry-hub",            // Required: source service ID
    "to": "search",                   // Required: target service ID
    "label": "RAG Query",             // Optional: line label
    "type": "api"                     // Optional: api|data|security|private|network|default
  }
]
```

### Step 3: Hierarchy Parameter (Multi-Sub/RG)

For multi-subscription or multi-resource-group architectures, pass `--hierarchy`:

```json
[
  {"subscription": "connectivity-sub", "resourceGroups": ["rg-hub"]},
  {"subscription": "workload-sub", "resourceGroups": ["rg-ai", "rg-data"]}
]
```

When hierarchy is provided:
- Each service **must** have `subscription` and `resourceGroup` fields
- Layout switches from category-based to **RG-based grouping**

### Supported Service Types (Complete List)

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
