<p align="center">
  <img src="https://raw.githubusercontent.com/whoniiii/az-diagram-autogen/main/docs/images/logo.svg" width="120" alt="az-diagram-autogen logo">
</p>

<h1 align="center">az-diagram-autogen</h1>

<p align="center">
  <strong>Azure architecture diagram engine for AI coding agent skills</strong>
</p>

<p align="center">
Generate interactive HTML/PNG diagrams of Azure architectures from JSON.<br>
Built for <a href="https://agentskills.io">Agent Skills</a> — works with GitHub Copilot, Claude Code, and compatible AI coding agents.<br>
Also usable standalone via CLI or Python API.
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
  <a href="#-use-in-your-skill">Use in Your Skill</a> •
  <a href="#-what-it-looks-like">Screenshots</a> •
  <a href="#-features">Features</a> •
  <a href="#%EF%B8%8F-cli-reference">CLI</a> •
  <a href="#-python-api">Python API</a>
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

## 🔧 Use in Your Skill

This package is built for **AI coding agent skills** — GitHub Copilot, Claude Code, and any [Agent Skills](https://agentskills.io)-compatible tool.

### 📋 Copy the block below into your SKILL.md:

> **Required**: Include this in your skill's `SKILL.md`. The agent will read `--reference` to learn the full JSON schema and service type list.

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
This prints the full service type list, JSON schema, and usage.
**Read this reference before generating diagrams. Follow the exact type values and JSON format.**

### Generate
```
az-diagram-autogen \
  --services '<services JSON or file path>' \
  --connections '<connections JSON or file path>' \
  --title '<diagram title>' \
  --output '<output file path>' \
  -f '<format: html|png|both>' \
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

> The bundled `REFERENCE.md` contains the complete service type list (72 types), JSON schema, connection types, and hierarchy format. The agent reads it via `--reference` so you don't need to list types in your SKILL.md.

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| **636 Azure Icons** | Official Microsoft Azure icons, Base64-encoded — works offline |
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

## 🖥️ CLI Reference

```
az-diagram-autogen [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--services` | `-s` | *(required)* | Services JSON — inline string or file path |
| `--connections` | `-c` | *(required)* | Connections JSON — inline string or file path |
| `--title` | `-t` | `"Azure Architecture"` | Diagram title |
| `--output` | `-o` | `"azure-architecture.html"` | Output file path |
| `--format` | `-f` | `html` | Output format: `html`, `png`, or `both` (html+png) |
| `--vnet-info` | | `""` | VNet CIDR label for boundary |
| `--hierarchy` | | `""` | Subscription/RG hierarchy JSON |
| `--reference` | | | Print skill integration reference |

**Output formats:**
```bash
# HTML only (default) — interactive, self-contained
az-diagram-autogen -s svc.json -c conn.json -o arch.html

# PNG only — static image (requires puppeteer: npm i puppeteer)
az-diagram-autogen -s svc.json -c conn.json -o arch -f png

# Both HTML + PNG
az-diagram-autogen -s svc.json -c conn.json -o arch -f both
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

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit PRs.

```bash
git clone https://github.com/whoniiii/az-diagram-autogen.git
cd az-diagram-autogen
pip install -e .
pytest tests/ -v
```

---

## 📄 License

MIT © [Jeonghoon Lee](https://github.com/whoniiii)
