# azure-arch-builder

> Design Azure AI/Data infrastructure in natural language and deploy automatically — a GitHub Copilot CLI skill.

**[한국어 README](README.ko.md)**

Say *"Create AI Search and Foundry with private endpoints"* and the skill will guide you through architecture design, generate Bicep code, review it, and deploy to Azure — all through conversation.

---

## 🔄 What It Does

```
You: "Build me a RAG chatbot with Foundry and AI Search"
       ↓
Phase 1: 🎨 Interactive architecture design + diagram
       ↓
Phase 2: 🔧 Bicep code generation (auto)
       ↓
Phase 3: ✅ Code review + compilation check (auto)
       ↓
Phase 4: 🚀 What-if → Preview diagram → Azure deployment
```

**Optimized services:** Microsoft Foundry, Azure OpenAI, AI Search, ADLS Gen2, Key Vault, Microsoft Fabric, Azure Data Factory, VNet/Private Endpoint, AML/AI Hub

**Other Azure services:** Also supported — automatically looked up from MS Docs and generated

---

## ⚙️ Prerequisites

| Tool | Required | Install |
|------|----------|---------|
| **GitHub Copilot CLI** | ✅ | [Install guide](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) |
| **Azure CLI** | ✅ (for deployment) | `winget install Microsoft.AzureCLI` |
| **Python 3** | ✅ (for diagrams) | `winget install Python.Python.3.12` |

> Azure CLI login (`az login`) is only checked when you proceed to deployment — not during design.

### 🤖 Recommended Models

This skill involves complex multi-phase orchestration with 800+ lines of instructions. Model choice matters.

| | Models | Notes |
|---|---|---|
| ✅ **Recommended** | Claude Sonnet 4.5 / 4.6 | Best cost-performance balance |
| 🏆 **Best** | Claude Opus 4.5 / 4.6 | Most reliable instruction following |
| ⚠️ **Minimum** | Claude Sonnet 4, GPT-5.1+ | May occasionally skip steps |
| ❌ **Not recommended** | Haiku, Mini | Too many instructions to follow reliably |

---

## 📦 Installation

### Project skill (this project only)

```powershell
# From your project root
git clone <repo-url> .github/skills/azure-arch-builder
```

```
your-project/
└── .github/
    └── skills/
        └── azure-arch-builder/
            ├── SKILL.md
            ├── prompts/
            ├── references/
            └── scripts/
```

### Personal skill (all projects)

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.copilot\skills" -Force
git clone <repo-url> "$env:USERPROFILE\.copilot\skills\azure-arch-builder"
```

### Verify

```
copilot /skills
```

You should see `azure-arch-builder` in the skill list.

---

## 🚀 Usage

Start GitHub Copilot CLI in your project folder:

```powershell
cd your-project
copilot
```

Then just describe what you want:

```
"Build a RAG chatbot with Foundry, AI Search, and ADLS Gen2"
"Create a data platform with Fabric and ADF, private endpoints included"
"Deploy Azure AI infrastructure with GPT-4o and embedding model"
```

The skill activates automatically for Azure infrastructure requests.

### Step-by-step flow

**🎨 1. Architecture Design (Phase 1)**
- Asks project name, services, SKUs, region, networking
- Fetches latest info from MS Docs (models, SKUs, availability)
- Generates interactive HTML architecture diagram
- Iterates until you confirm

**🔧 2. Bicep Generation (Phase 2)**
- Creates modular Bicep templates (`main.bicep` + `modules/`)
- Fetches latest API versions from MS Docs
- Applies security best practices (Private Endpoint, RBAC, etc.)

**✅ 3. Code Review (Phase 3)**
- Runs `az bicep build` for compilation check
- Reviews against checklist (Foundry Project, PE 3-set, HNS, etc.)
- Auto-fixes issues and re-compiles

**🚀 4. Deployment (Phase 4)**
- What-if validation (no actual changes)
- Preview diagram based on What-if results
- User confirmation → actual deployment
- Final diagram with deployed resource details

### 📂 Output structure

```
<project-name>/
├── 01_arch_diagram_draft.html      ← Design diagram
├── 02_arch_diagram_preview.html    ← What-if preview
├── 03_arch_diagram_result.html     ← Deployment result
├── main.bicep
├── main.bicepparam
└── modules/
    ├── network.bicep
    ├── foundry.bicep
    ├── search.bicep
    ├── storage.bicep
    ├── keyvault.bicep
    └── private-endpoints.bicep
```

---

## 🌐 Language Support

The skill automatically detects your language and responds accordingly. All user-facing output (questions, progress messages, reports, Bicep comments) adapts to your language.

---

## ✨ Key Features

- 🔍 **Live MS Docs verification** — API versions, model availability, SKU options fetched in real-time
- 🔒 **Security by default** — Private Endpoint, RBAC, no secrets in parameter files
- 🎨 **Interactive design** — Iterative architecture refinement with visual diagrams
- 👤 **Step-by-step approval** — User confirmation at every major step
- 🔄 **Cross-verification** — Critical facts checked against multiple MS Docs sources
- ⚡ **Parallel preloading** — Next-step info loaded while waiting for user input

---

## License

MIT
