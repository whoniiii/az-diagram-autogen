# GHCP001 — Project Instructions for GitHub Copilot

## 프로젝트 개요

Azure 인프라 자동화를 위한 GitHub Copilot CLI 스킬 생태계.
자연어로 Azure 아키텍처를 설계 → 다이어그램 생성 → Bicep 코드 생성 → 배포까지 자동화한다.

## 핵심 컴포넌트 (3개)

| 컴포넌트 | 경로 | 역할 |
|---|---|---|
| **az-diagram-autogen** | `az-diagram-autogen/` | 다이어그램 생성 엔진 (핵심 Python 패키지). PyPI 배포용. |
| **az-autopilot-agent** | `.github/skills/az-autopilot-agent/` | **외부 사용자용** 스킬. `pip install az-diagram-autogen`으로 설치하여 사용. |
| **az-autopilot-agent-core** | `.github/skills/az-autopilot-agent-core/` | **내부 사용자용** 스킬. az-diagram-autogen을 내장(embedded)하여 pip 없이 사용. |

## ⚠️ 수정 시 반드시 3곳 동시 반영

코드 수정 요청이 오면 **반드시 아래 3곳을 모두 업데이트**해야 한다:

### 1. 다이어그램 엔진 수정 (`generator.py`, `icons.py` 등)
```
az-diagram-autogen/az_diagram_autogen/generator.py          ← 소스 원본 (PyPI 배포 + v3용)
.github/skills/az-autopilot-agent-core/az_diagram_autogen/generator.py  ← v4 내장 복사본
```
→ 소스 원본을 수정한 뒤 v4에 복사 (`Copy-Item`)

### 2. 스킬 프롬프트 수정 (`phase1-advisor.md`, `bicep-generator.md` 등)
```
.github/skills/az-autopilot-agent/prompts/   ← v3 (외부용)
.github/skills/az-autopilot-agent-core/prompts/   ← v4 (내부용)
```
→ 두 곳 모두 동일하게 수정 (v3는 pip install 방식, v4는 PYTHONPATH 방식 — Section 1-2만 다름)

### 3. 참조 문서 수정 (`references/`)
```
.github/skills/az-autopilot-agent/references/
.github/skills/az-autopilot-agent-core/references/
```
→ 두 곳 모두 동일하게 수정

## v3 vs v4 차이점

| | v3 (외부용) | v4 (내부용) |
|---|---|---|
| 대상 | 외부 사용자 (공개 배포) | 내부 사용자 (사내 배포) |
| 다이어그램 엔진 | `pip install az-diagram-autogen` | 스킬 폴더에 내장 (`az_diagram_autogen/`) |
| 크기 | ~155KB (패키지 별도) | ~2.2MB (icons.py 포함) |
| 네트워크 | pip 설치 시 필요 | 오프라인 가능 |
| phase1-advisor.md Section 1-2 | pip install + `python -m az_diagram_autogen` | `PYTHONPATH=$SkillDir` + `python -m az_diagram_autogen` |

## 레거시 버전

v1, v2는 삭제됨. v3/v4로 완전 대체.

## 기술 환경

- **Python**: `C:\Users\jeonghoonlee\AppData\Local\Programs\Python\Python314\python.exe`
  - ⚠️ `Get-Command python` 사용 금지 (Windows Store alias 위험)
- **PyPI 패키지**: `az-diagram-autogen` (현재 v0.1.2)
- **Git**: master 브랜치

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
│       ├── az-autopilot-agent/   ← 외부용 스킬 (pip)
│       │   ├── SKILL.md
│       │   ├── prompts/
│       │   └── references/
│       ├── az-autopilot-agent-core/   ← 내부용 스킬 (embedded)
│       │   ├── SKILL.md
│       │   ├── az_diagram_autogen/  ← 내장 복사본
│       │   ├── prompts/
│       │   └── references/
│       └── revealjs-presentation-builder/
└── .gitignore
```
