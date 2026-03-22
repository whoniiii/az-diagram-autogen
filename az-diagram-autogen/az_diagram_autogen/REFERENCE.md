# az-diagram-autogen — Skill Reference

> **This file is a reference for AI coding agent skills (GitHub Copilot, Claude Code, and [Agent Skills](https://agentskills.io)-compatible tools).**
> After `pip install az-diagram-autogen`, refer to this document to generate diagrams.

---

## Installation

```bash
pip install az-diagram-autogen
```

You can print this reference anytime with:
```bash
az-diagram-autogen --reference
```

---

## Diagram Generation Commands

### CLI

```bash
az-diagram-autogen \
  -s '<services JSON or file path>' \
  -c '<connections JSON or file path>' \
  -t '<diagram title>' \
  -o '<output file path>' \
  -f '<format: html|png|both>' \
  --vnet-info '<VNet CIDR (optional)>' \
  --hierarchy '<subscription/RG hierarchy JSON (optional)>'
```

**Output formats:**
- `html` (default) — interactive, self-contained HTML
- `png` — static image (requires `npm i puppeteer`)
- `both` — generates both HTML and PNG

### Python API

```python
from az_diagram_autogen import generate_diagram

html = generate_diagram(
    services=[...],       # List of services (see schema below)
    connections=[...],    # List of connections (see schema below)
    title="Title",
    vnet_info="10.0.0.0/16 | pe-subnet: 10.0.1.0/24",  # Optional
    hierarchy=[...]       # Optional (see below)
)

with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)
```

---

## Services JSON Schema

```json
[
  {
    "id": "unique-kebab-case-id",
    "name": "Display Name",
    "type": "Select from type list below",
    "sku": "SKU (optional)",
    "private": false,
    "details": ["Detail 1", "Detail 2"],
    "subscription": "Subscription name (for multi-sub)",
    "resourceGroup": "Resource group name (for multi-RG)"
  }
]
```

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `id` | Yes | string | Unique identifier (kebab-case, alphanumeric) |
| `name` | Yes | string | Display name shown on diagram |
| `type` | Yes | string | Service type (select from list below) |
| `sku` | | string | SKU/tier information |
| `private` | | boolean | Private Endpoint connected (default: false) |
| `details` | | string[] | Additional info shown in sidebar |
| `subscription` | | string | Subscription name (required when using hierarchy) |
| `resourceGroup` | | string | Resource group name (required when using hierarchy) |

---

## Connections JSON Schema

```json
[
  {
    "from": "source service id",
    "to": "target service id",
    "label": "Connection label",
    "type": "connection type"
  }
]
```

| Field | Required | Description |
|-------|----------|-------------|
| `from` | Yes | Source service id |
| `to` | Yes | Target service id |
| `label` | | Text displayed on the connection line |
| `type` | | Connection style (see below) |

### Connection Types

| type | Color | Style | Use For |
|------|-------|-------|---------|
| `api` | Blue | Solid | API calls, queries |
| `data` | Green | Solid | Data flow, indexing |
| `security` | Orange | Dashed | Secrets, auth |
| `private` | Purple | Dashed | Private Endpoint connections |
| `network` | Gray | Solid | Network routing |
| `default` | Gray | Solid | Other |

---

## Service Type List (Complete)

> **You must use the exact strings below.** Unrecognized values render with a "?" icon.

### AI
| type | Display Label |
|------|--------------|
| `ai_foundry` | AI Foundry |
| `ai_search` | AI Search |
| `search` | AI Search (alias) |
| `document_intelligence` | Doc Intelligence |
| `form_recognizer` | Doc Intelligence (alias) |
| `aml` | Azure ML |

### Data
| type | Display Label |
|------|--------------|
| `storage` | Storage Account |
| `adls` | ADLS Gen2 (alias) |
| `cosmos_db` | Cosmos DB |
| `sql_database` | SQL Database |
| `sql_server` | SQL Server |
| `databricks` | Databricks |
| `data_factory` | Data Factory |
| `adf` | Data Factory (alias) |
| `fabric` | Microsoft Fabric |
| `redis` | Redis Cache |
| `stream_analytics` | Stream Analytics |
| `synapse` | Synapse Analytics |

### Security
| type | Display Label |
|------|--------------|
| `keyvault` | Key Vault |

### Compute
| type | Display Label |
|------|--------------|
| `app_service` | App Service |
| `appservice` | App Service (alias) |
| `function_app` | Function App |
| `vm` | Virtual Machine |
| `aks` | AKS |
| `acr` | Container Registry |
| `container_registry` | Container Registry (alias) |

### Network
| type | Display Label |
|------|--------------|
| `firewall` | Azure Firewall |
| `bastion` | Azure Bastion |
| `vpn_gateway` | VPN Gateway |
| `app_gateway` | Application Gateway |
| `front_door` | Front Door |
| `cdn` | CDN |
| `nsg` | NSG |

### IoT
| type | Display Label |
|------|--------------|
| `iot_hub` | IoT Hub |

### Integration
| type | Display Label |
|------|--------------|
| `event_hub` | Event Hub |

### Monitoring
| type | Display Label |
|------|--------------|
| `log_analytics` | Log Analytics |
| `app_insights` | App Insights |
| `monitor` | Azure Monitor |
| `appinsights` | App Insights (alias) |

### DevOps
| type | Display Label |
|------|--------------|
| `devops` | Azure DevOps |

---

## Hierarchy (Multi-Subscription / Multi-RG)

To render subscription and resource group boundaries, use the `--hierarchy` parameter:

```json
[
  {"subscription": "connectivity-sub", "resourceGroups": ["rg-hub"]},
  {"subscription": "workload-sub", "resourceGroups": ["rg-ai", "rg-data", "rg-security"]}
]
```

**Rules when using hierarchy:**
- All services must have `subscription` and `resourceGroup` fields
- Layout automatically switches from category-based to RG-based grouping
- Rendered as nested boundaries: Subscription > Resource Group > Service nodes

---

## VNet Boundary

When VNet info is provided, a purple dashed boundary is rendered:

```
--vnet-info "10.0.0.0/16 | pe-subnet: 10.0.1.0/24"
```

VNet boundary only renders when services with `private: true` exist.

---

## Output

- **Single HTML file** — opens directly in any browser, no server needed
- 605 official Azure icons embedded as Base64 (works offline)
- Interactive: drag-and-drop, zoom, sidebar with resource details
