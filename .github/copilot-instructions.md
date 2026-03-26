# GHCP001 — Project Instructions for GitHub Copilot

## 프로젝트 개요

Azure 인프라 자동화를 위한 GitHub Copilot CLI 스킬 생태계.
자연어로 Azure 아키텍처를 설계 → 다이어그램 생성 → Bicep 코드 생성 → 배포까지 자동화한다.

## 핵심 컴포넌트 (2개)

| 컴포넌트 | 경로 | 역할 |
|---|---|---|
| **az-diagram-autogen** | `az-diagram-autogen/` | 다이어그램 생성 엔진 (핵심 Python 패키지). PyPI 배포용. |
| **azure-architecture-autopilot** | `.github/skills/azure-architecture-autopilot/` | **awesome-copilot 기여용 (EN)** 스킬. 엔진 내장 + awesome-copilot 표준 구조(scripts/references/ 플랫). |

> ℹ️ KR 스킬 (`azure-architecture-autopilot-kr`, `azure-architecture-autopilot-pip-kr`)은 로컬에만 존재하며 git 추적 대상이 아님.

## ⚠️ 수정 시 반드시 2곳 동시 반영

**스킬 프롬프트/참조 문서/엔진 수정 요청이 오면 반드시 아래 2곳을 모두 업데이트해야 한다:**

| # | 경로 | 설명 |
|---|------|------|
| 1 | `az-diagram-autogen/` | 소스 원본 (PyPI 패키지). 상대 import (`from .icons`) |
| 2 | `.github/skills/azure-architecture-autopilot/` | awesome-copilot 기여용 (EN). 절대 import (`from icons`) |

### 2곳 차이점

| 항목 | az-diagram-autogen (Source) | azure-architecture-autopilot (EN) |
|------|---------------------------|-----------------------------------|
| 언어 | — (라이브러리) | **영어** |
| 다이어그램 엔진 | `az_diagram_autogen/` (패키지) | `scripts/` 에 플랫 내장 |
| import 방식 | `from .icons import` (상대) | `from icons import` (절대) |
| 프롬프트 | 없음 | `references/` (플랫, prompts 통합) |
| 참조 문서 | 없음 | `references/` (플랫, domain-packs 통합) |
| 실행 방식 | `python -m az_diagram_autogen` | `python scripts/cli.py` |

### 수정 규칙

1. **프롬프트/참조 문서 수정** (Phase 흐름, 질문 로직, 보고 형식 등)
   - `.github/skills/azure-architecture-autopilot/references/` 만 수정

2. **다이어그램 엔진 수정** (`generator.py`, `icons.py` 등)
   ```
   az-diagram-autogen/az_diagram_autogen/generator.py   ← 소스 원본 (상대 import)
   .github/skills/azure-architecture-autopilot/scripts/  ← EN 플랫 복사본 (절대 import)
   ```
   → 소스 원본 수정 → EN에 복사 (import만 `from .icons` → `from icons` 변경)

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

## 🧪 테스트 규칙

**코드 수정 후 반드시 테스트를 실행한다.**

```powershell
cd az-diagram-autogen
& "C:\Users\jeonghoonlee\AppData\Local\Programs\Python\Python314\python.exe" -m pytest tests/ -v --tb=short
```

### 테스트 스위트 (67 tests)

| 파일 | 역할 | 주요 검증 |
|---|---|---|
| `test_type_normalization.py` | 타입 정규화 | 95개 alias → canonical, ARM 이름 매핑, 대소문자/하이픈 |
| `test_icon_resolution.py` | 아이콘 매핑 | Fabric/Foundry 아이콘, azure_icon_key 유효성 |
| `test_pe_detection.py` | PE 렌더링 | PE 타입 변환, 보라색 색상, 카운트 |
| `test_e2e.py` | E2E 다이어그램 | 전체 서비스 렌더링, 실제 아키텍처, 엣지케이스 |
| `test_visual_render.py` | 시각 검증 | HTML→PNG 렌더링, 5개 시나리오, RENDER_REPORT.md 생성 |
| `test_cross_sync.py` | 2곳 동기화 | source↔EN generator.py/icons.py 일치 검증 |
| `test_generator.py` | 기본 생성 | HTML 출력, 타이틀, hierarchy |
| `test_icons.py` | 아이콘 DB | 636개 아이콘 존재, 검색, 정규화 |
| `test_cli.py` | CLI | JSON 로딩, 파일 출력 |

### 수정 시 테스트 추가 기준

- **새 서비스 타입 추가** → `test_type_normalization.py`에 alias 추가
- **새 아이콘 추가** → `test_icon_resolution.py`에 키 검증 추가
- **generator.py 로직 변경** → `test_e2e.py`에 시나리오 추가
- **source↔EN 동기화 후** → `test_cross_sync.py` 자동 검증됨

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
│       └── azure-architecture-autopilot/  ← awesome-copilot 기여용 (EN, flat)
│           ├── SKILL.md
│           ├── scripts/                 ← 다이어그램 엔진 (플랫)
│           ├── references/              ← 프롬프트 + 참조 문서 (플랫)
│           └── assets/                  ← 스크린샷 이미지
└── .gitignore
```
