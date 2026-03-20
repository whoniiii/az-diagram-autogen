# Contributing to azure-arch-builder

Thank you for your interest in contributing! This guide will help you understand the project structure and how to make changes.

## 📁 Project Structure

```
azure-arch-builder/
├── SKILL.md                    # Main orchestration — 4-phase pipeline
├── prompts/
│   ├── bicep-generator.md      # Phase 2: Bicep generation instructions
│   └── bicep-reviewer.md       # Phase 3: Code review checklist
├── references/
│   ├── azure-common-patterns.md        # PE/security/naming patterns
│   ├── azure-dynamic-sources.md        # MS Docs URL registry
│   ├── architecture-guidance-sources.md # Architecture guidance sources
│   ├── service-gotchas.md              # Required properties, common mistakes
│   └── domain-packs/
│       └── ai-data.md                  # AI/Data service configuration guide
├── scripts/
│   └── generate_html_diagram.py        # Interactive HTML diagram generator
├── README.md                   # English README
└── README.ko.md                # Korean README
```

## 🌐 About the Korean Instructions

The internal instruction files (SKILL.md, prompts/, references/) are written in **Korean**. This is intentional:

- **LLMs understand Korean instructions perfectly** and respond in whatever language the user speaks
- The skill has a **language auto-detection** feature — all user-facing output adapts to the user's language
- These instructions have been **extensively tested and tuned** in Korean; translating risks breaking proven behavior
- The primary developer maintains the project in Korean for speed and accuracy

**You don't need to read Korean to contribute.** The structure and flow are consistent across files, and the README provides a complete overview in English.

## 🔧 How to Contribute

### Adding a new service type icon (diagram)

Edit `scripts/generate_html_diagram.py` → `SERVICE_ICONS` dictionary:

```python
"your_service": {
    "icon_svg": '<...SVG markup...>',
    "color": "#HEX",
    "bg": "#HEX",
    "category": "Category"
},
```

### Adding a new reference pattern

Add to the appropriate file in `references/`:
- **Service-specific gotchas** → `service-gotchas.md`
- **Common patterns (PE, security, naming)** → `azure-common-patterns.md`
- **MS Docs URL patterns** → `azure-dynamic-sources.md`
- **AI/Data service configs** → `domain-packs/ai-data.md`

### Modifying phase behavior

- **Phase 1 (Architecture Design)** → `SKILL.md` sections 1-1 through 1-3
- **Phase 2 (Bicep Generation)** → `prompts/bicep-generator.md`
- **Phase 3 (Code Review)** → `prompts/bicep-reviewer.md`
- **Phase 4 (Deployment)** → `SKILL.md` Phase 4 section

### Running evals

Test cases are in `dev/evals.json` (15 scenarios). Run them manually by starting a Copilot CLI session and providing each eval prompt.

## ⚠️ Important Guidelines

- **Do not hardcode** API versions, SKU lists, or region availability — these are fetched from MS Docs at runtime
- **Do not remove** the `ask_user` interaction points — they ensure user control at every step
- **Test after changes** — the instruction set is 2,300+ lines and tightly interconnected; small changes can have cascading effects

## 📝 Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with at least 2 eval scenarios (one v1-core, one fallback)
5. Submit a PR with a clear description of what changed and why

## License

MIT
