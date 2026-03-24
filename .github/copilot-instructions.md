# GHCP001 — Project Instructions for GitHub Copilot

## 프로젝트 개요

Azure 인프라 자동화를 위한 GitHub Copilot CLI 스킬 생태계.
자연어로 Azure 아키텍처를 설계 → 다이어그램 생성 → Bicep 코드 생성 → 배포까지 자동화한다.

## 핵심 컴포넌트 (4개)

| 컴포넌트 | 경로 | 역할 |
|---|---|---|
| **az-diagram-autogen** | `az-diagram-autogen/` | 다이어그램 생성 엔진 (핵심 Python 패키지). PyPI 배포용. |
| **az-autopilot-agent** | `.github/skills/az-autopilot-agent/` | **외부 사용자용 (KR)** 스킬. `pip install az-diagram-autogen`으로 설치하여 사용. |
| **az-autopilot-agent-core** | `.github/skills/az-autopilot-agent-core/` | **내부 사용자용 (KR)** 스킬. az-diagram-autogen을 내장(embedded)하여 pip 없이 사용. |
| **az-autopilot-agent-core-en** | `.github/skills/az-autopilot-agent-core-en/` | **awesome-copilot 기여용 (EN)** 스킬. core와 동일하나 영문 + awesome-copilot 표준 구조(scripts/references/ 플랫). |

## ⚠️ 수정 시 반드시 3곳 동시 반영

**스킬 프롬프트/참조 문서 수정 요청이 오면 반드시 아래 3곳을 모두 업데이트해야 한다:**

| # | 경로 | 설명 | 프롬프트 위치 | 참조 문서 위치 |
|---|------|------|-------------|---------------|
| 1 | `.github/skills/az-autopilot-agent/` | 외부 사용자용 (KR). pip install 방식 | `prompts/` | `references/` |
| 2 | `.github/skills/az-autopilot-agent-core/` | 내부 사용자용 (KR). 다이어그램 엔진 내장 | `prompts/` | `references/` |
| 3 | `.github/skills/az-autopilot-agent-core-en/` | awesome-copilot 기여용 (EN). 엔진 내장 + 플랫 구조 | `references/` (prompts 포함) | `references/` |

### 3곳 차이점

| 항목 | az-autopilot-agent (v3) | az-autopilot-agent-core (v4 KR) | az-autopilot-agent-core-en (v4 EN) |
|------|------------------------|-------------------------------|-----------------------------------|
| 언어 | 한국어 | 한국어 | **영어** |
| 다이어그램 엔진 | `pip install az-diagram-autogen` | `az_diagram_autogen/` 내장 | `scripts/` 에 플랫 내장 |
| 프롬프트 경로 | `prompts/` | `prompts/` | `references/` (플랫, prompts 통합) |
| 참조 문서 경로 | `references/`, `references/domain-packs/` | `references/`, `references/domain-packs/` | `references/` (플랫, domain-packs 통합) |
| 실행 방식 | `pip install` + `python -m az_diagram_autogen` | `PYTHONPATH=$SkillDir` + `python -m az_diagram_autogen` | `python scripts/cli.py` |
| 대상 | 외부 공개 배포 | 내부(사내) 배포 | github/awesome-copilot 기여 |

### 수정 규칙

1. **프롬프트 내용 수정** (Phase 흐름, 질문 로직, 보고 형식 등)
   - 3곳 모두 동일하게 수정
   - 단, Section 1-2 (다이어그램 실행 방식)만 각각 다름 (위 표 참조)

2. **참조 문서 수정** (`service-gotchas.md`, `azure-common-patterns.md` 등)
   - 3곳 모두 동일하게 수정

3. **다이어그램 엔진 수정** (`generator.py`, `icons.py` 등)
   ```
   az-diagram-autogen/az_diagram_autogen/generator.py           ← 소스 원본 (PyPI + v3용)
   .github/skills/az-autopilot-agent-core/az_diagram_autogen/   ← v4 KR 내장 복사본
   .github/skills/az-autopilot-agent-core-en/scripts/           ← v4 EN 플랫 복사본
   ```
   → 소스 원본 수정 → v4 KR에 복사 → v4 EN에 복사 (EN은 플랫 구조 + 절대 import)

## 기술 환경

- **Python**: `C:\Users\jeonghoonlee\AppData\Local\Programs\Python\Python314\python.exe`
  - ⚠️ `Get-Command python` 사용 금지 (Windows Store alias 위험)
- **PyPI 패키지**: `az-diagram-autogen` (현재 v0.1.2)
- **Git**: master 브랜치

## ⚠️ 크로스플랫폼 요구사항

이 스킬은 **Windows, WSL, macOS** 3개 환경 모두에서 동작해야 한다.

현재 프롬프트 코드 스니펫이 Windows PowerShell에 하드코딩되어 있으므로, 수정 시 아래를 고려:

| 항목 | Windows | WSL / macOS |
|---|---|---|
| 셸 | PowerShell | bash/zsh |
| 경로 구분자 | `\` | `/` |
| Python 탐색 | `$env:LOCALAPPDATA\Programs\Python` | `which python3` |
| 환경변수 | `$env:USERPROFILE`, `$env:LOCALAPPDATA` | `$HOME` |
| 브라우저 오픈 | `Start-Process` | `open` (macOS) / `xdg-open` (Linux) |
| 파일 저장 | `Set-Content` | `>` 리다이렉트 |

**현재 상태**: 프롬프트가 Windows 전용 — 크로스플랫폼 리팩토링 필요 (phase0-scanner.md ~14건, phase1-advisor.md ~7건)

**산출물 저장 규칙**: 모든 산출물(스캔 JSON, 다이어그램 HTML, Bicep 코드)은 **cwd 아래 프로젝트 폴더**에 저장. 절대로 `~/.copilot/session-state/` 안에 저장하지 않음.

## ⚠️ Git 커밋 규칙

**자동 커밋 금지** — 사용자가 명시적으로 "커밋해" 라고 요청할 때만 커밋한다. 수정 후 자동으로 `git commit`을 실행하지 않는다.

## 파일 구조

```
GHCP001/
├── az-diagram-autogen/              ← PyPI 패키지 소스
│   ├── az_diagram_autogen/
│   │   ├── generator.py             ← 핵심 HTML 다이어그램 생성기
│   │   ├── icons.py                 ← Azure 공식 아이콘 (SVG base64, ~2MB)
│   │   ├── cli.py                   ← CLI 인터페이스
│   │   └── REFERENCE.md             ← 서비스 타입 레퍼런스
│   ├── setup.py
│   └── README.md
├── .github/
│   ├── copilot-instructions.md      ← 이 파일
│   └── skills/
│       ├── az-autopilot-agent/          ← 외부용 (KR, pip)
│       │   ├── SKILL.md
│       │   ├── prompts/
│       │   └── references/
│       ├── az-autopilot-agent-core/     ← 내부용 (KR, embedded)
│       │   ├── SKILL.md
│       │   ├── az_diagram_autogen/      ← 내장 복사본
│       │   ├── prompts/
│       │   └── references/
│       ├── az-autopilot-agent-core-en/  ← awesome-copilot 기여용 (EN, flat)
│       │   ├── SKILL.md
│       │   ├── scripts/                 ← 다이어그램 엔진 (플랫)
│       │   ├── references/              ← 프롬프트 + 참조 문서 (플랫)
│       │   └── assets/                  ← 스크린샷 이미지
│       └── revealjs-presentation-builder/
└── .gitignore
```
