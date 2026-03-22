# az-diagram-autogen

Interactive Azure architecture diagram generator with **605 official Azure icons**.

Generate self-contained HTML diagrams from JSON — with drag-and-drop, zoom, VNet boundaries, multi-subscription hierarchy, and private endpoint visualization.

## Install

```bash
pip install az-diagram-autogen
```

Or install from source:

```bash
git clone https://github.com/user/az-diagram-autogen.git
cd az-diagram-autogen
pip install -e .
```

## Quick Start

### CLI

```bash
# From JSON files
az-diagram-autogen -s services.json -c connections.json -o architecture.html

# Inline JSON
az-diagram-autogen \
  -s '[{"id":"foundry","name":"AI Foundry","type":"ai_foundry"},{"id":"search","name":"AI Search","type":"ai_search"}]' \
  -c '[{"from":"foundry","to":"search","label":"RAG Query","type":"api"}]' \
  -t "My RAG Architecture" \
  -o my-arch.html
```

### Python API

```python
from az_diagram_autogen import generate_diagram

html = generate_diagram(
    services=[
        {"id": "foundry", "name": "AI Foundry", "type": "ai_foundry", "sku": "S0"},
        {"id": "search", "name": "AI Search", "type": "ai_search", "sku": "S1"},
        {"id": "storage", "name": "ADLS Gen2", "type": "storage"},
        {"id": "keyvault", "name": "Key Vault", "type": "keyvault"},
    ],
    connections=[
        {"from": "foundry", "to": "search", "label": "RAG Query", "type": "api"},
        {"from": "search", "to": "storage", "label": "Indexing", "type": "data"},
        {"from": "foundry", "to": "keyvault", "label": "Secrets", "type": "security"},
    ],
    title="RAG Chatbot Architecture",
)

with open("rag-architecture.html", "w") as f:
    f.write(html)
```

### Search Azure Icons

```python
from az_diagram_autogen import search_icons

results = search_icons("storage")
for key, name, category in results:
    print(f"{key}: {name} ({category})")
```

## CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--services` | `-s` | (required) | Services JSON string or file path |
| `--connections` | `-c` | (required) | Connections JSON string or file path |
| `--title` | `-t` | `"Azure Architecture"` | Diagram title |
| `--output` | `-o` | `"azure-architecture.html"` | Output HTML file |
| `--vnet-info` | | `""` | VNet boundary label (e.g., `"10.0.0.0/16 \| pe-subnet: 10.0.1.0/24"`) |
| `--hierarchy` | | `""` | Subscription/RG hierarchy JSON |

## Service JSON Schema

```json
{
  "id": "unique-kebab-case",
  "name": "Display Name",
  "type": "ai_foundry",
  "sku": "S0 (optional)",
  "private": false,
  "details": ["optional detail 1", "optional detail 2"],
  "subscription": "sub-name (for multi-sub diagrams)",
  "resourceGroup": "rg-name (for multi-RG diagrams)"
}
```

## Connection JSON Schema

```json
{
  "from": "service-id",
  "to": "service-id",
  "label": "Connection Label",
  "type": "api|data|security|private|network|default"
}
```

## Supported Service Types

| Type | Label | Category |
|------|-------|----------|
| `ai_foundry` | AI Foundry | AI |
| `ai_search` / `search` | AI Search | AI |
| `storage` | Storage | Data |
| `keyvault` | Key Vault | Security |
| `app_service` | App Service | Compute |
| `sql_database` | SQL Database | Data |
| `cosmos_db` | Cosmos DB | Data |
| `redis` | Redis Cache | Data |
| `aks` | AKS | Compute |
| `acr` | Container Registry | Compute |
| `function_app` | Function App | Compute |
| `databricks` | Databricks | Data |
| `data_factory` / `adf` | Data Factory | Data |
| `fabric` | Fabric | Data |
| `vm` | Virtual Machine | Compute |
| `firewall` | Firewall | Network |
| `bastion` | Bastion | Network |
| `vpn_gateway` | VPN Gateway | Network |
| `app_gateway` | App Gateway | Network |
| `front_door` | Front Door | Network |
| `cdn` | CDN | Network |
| `iot_hub` | IoT Hub | IoT |
| `event_hub` | Event Hub | Integration |
| `stream_analytics` | Stream Analytics | Data |
| `log_analytics` | Log Analytics | Monitor |
| `app_insights` | App Insights | Monitor |
| `nsg` | NSG | Network |
| `devops` | Azure DevOps | DevOps |
| `document_intelligence` | Doc Intelligence | AI |

Any unrecognized type renders with a default "?" icon.

## Features

- **605 Azure Official Icons** — Base64-encoded SVG, no network required
- **Interactive** — Drag-and-drop nodes, pan & zoom, tooltips
- **VNet Boundaries** — Purple dashed boundary with CIDR labels
- **Private Endpoints** — Dedicated PE group with connection lines
- **Multi-Subscription/RG** — Nested hierarchy boundaries
- **Self-Contained** — Single HTML file, no dependencies
- **Category Layout** — Auto-grouped by AI, Data, Security, Compute, Network
- **RG Layout** — Resource Group-based layout when hierarchy provided
- **Sidebar** — Resource details panel with service info

## Examples

See the `examples/` directory for ready-to-use JSON files:

```bash
# Basic RAG chatbot
az-diagram-autogen -s examples/basic_rag.json -c examples/basic_rag.json -o rag.html

# From combined JSON (services + connections in one file)
python -c "
import json
from az_diagram_autogen import generate_diagram
data = json.load(open('examples/landing_zone.json'))
html = generate_diagram(**data)
open('landing_zone.html','w').write(html)
"
```

## License

MIT
