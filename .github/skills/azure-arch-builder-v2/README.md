# azure-arch-builder v2

> Design Azure infrastructure in natural language — or scan existing resources, visualize the architecture, and modify it through conversation.

**[한국어 README](README.ko.md)**

---

## 🔄 What It Does

```
Path A: "Build me a RAG chatbot"
         ↓
  🎨 Phase 1 → 🔧 Phase 2 → ✅ Phase 3 → 🚀 Phase 4

Path B: "Analyze my current Azure resources"
         ↓
  🔍 Phase 0 (Scan) → 🎨 Phase 1 (Modify) → 🔧→✅→🚀
```

| Phase | Name | Description |
|-------|------|-------------|
| **0** | 🔍 Resource Scanner | Scan existing Azure resources → auto-generate architecture diagram |
| **1** | 🎨 Architecture Advisor | Interactive design or modification through conversation |
| **2** | 🔧 Bicep Generator | Auto-generate modular Bicep templates |
| **3** | ✅ Code Reviewer | Compile check + security/best-practice review |
| **4** | 🚀 Deployer | Validate → What-if → Preview diagram → Deploy |

**All Azure services supported** — optimized for AI/Data services, others auto-looked up from MS Docs.

---

## ⚙️ Prerequisites

| Tool | Required | Install |
|------|----------|---------|
| **GitHub Copilot CLI** | ✅ | [Install guide](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) |
| **Azure CLI** | ✅ | `winget install Microsoft.AzureCLI` |
| **Python 3** | ✅ (diagrams) | `winget install Python.Python.3.12` |

### 🤖 Recommended Models

| | Models | Notes |
|---|---|---|
| ✅ **Recommended** | Claude Sonnet 4.5 / 4.6 | Best cost-performance |
| 🏆 **Best** | Claude Opus 4.5 / 4.6 | Most reliable |
| ⚠️ **Minimum** | Claude Sonnet 4, GPT-5.1+ | May skip steps |

---

## 📦 Installation

```powershell
# Project skill
git clone <repo-url> .github/skills/azure-arch-builder-v2

# Personal skill (all projects)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.copilot\skills" -Force
git clone <repo-url> "$env:USERPROFILE\.copilot\skills\azure-arch-builder-v2"
```

Verify: `copilot /skills`

---

## 🚀 Usage

### Path A: Build new infrastructure

```
"Build a RAG chatbot with Foundry and AI Search"
"Create a data platform with Databricks and ADLS Gen2"
"Deploy Fabric + ADF pipeline with private endpoints"
```

### Path B: Analyze & modify existing resources

```
"Analyze my current Azure infrastructure"
"Scan rg-production and show me the architecture"
"What resources are in my subscription?"
```

Then modify with natural language:
```
"Add 3 VMs to this architecture"
"The Foundry endpoint is slow — what can I do?"
"Reduce costs — downgrade AI Search to Basic"
"Add private endpoints to all services"
```

### 📂 Output structure

```
<project-name>/
├── 00_arch_current.html        ← Scanned architecture (Path B)
├── 01_arch_diagram_draft.html  ← Design diagram
├── 02_arch_diagram_preview.html ← What-if preview
├── 03_arch_diagram_result.html  ← Deployment result
├── main.bicep
├── main.bicepparam
└── modules/
    └── *.bicep
```

---

## 🌐 Language Support

Auto-detects your language. All output adapts — English, Korean, or any language.

---

## ✨ Key Features

- 🔍 **Resource scanning** — Analyze existing Azure resources and auto-generate architecture diagrams
- 💬 **Natural language modification** — "It's slow", "reduce costs", "add security" → guided resolution
- 📊 **Live MS Docs verification** — API versions, SKUs, model availability fetched in real-time
- 🔒 **Security by default** — Private Endpoint, RBAC, no secrets in files
- 🎨 **Interactive diagrams** — Clickable, draggable HTML architecture visualization
- ⚡ **Parallel preloading** — Next-step info loaded while waiting for input

---

## 📁 Architecture

```
SKILL.md (Router ~160 lines)
├── prompts/phase0-scanner.md      ← Existing resource scan
├── prompts/phase1-advisor.md      ← Architecture design/modify
├── prompts/bicep-generator.md     ← Bicep generation
├── prompts/bicep-reviewer.md      ← Code review
├── prompts/phase4-deployer.md     ← Deployment pipeline
├── references/                    ← Service patterns, PE mappings
└── scripts/generate_html_diagram.py
```

SKILL.md is a lightweight router. All phase logic lives in `prompts/`.

---

## License

MIT
