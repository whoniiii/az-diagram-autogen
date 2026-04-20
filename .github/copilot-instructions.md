# GHCP001 — Project Instructions for GitHub Copilot

## 프로젝트 개요

Azure 인프라 자동화를 위한 GitHub Copilot CLI 스킬 생태계.
자연어로 Azure 아키텍처를 설계 → 다이어그램 생성 → Bicep 코드 생성 → 배포까지 자동화한다.

## 핵심 컴포넌트 (2개)

| 컴포넌트 | 경로 | 역할 | 배포 대상 |
|---|---|---|---|
| **az-diagram-autogen** | `az_diagram_autogen/` | 다이어그램 생성 엔진 (핵심 Python 패키지) | **PyPI** (`pip install az-diagram-autogen`) |
| **azure-architecture-autopilot** | `.github/skills/azure-architecture-autopilot/` | awesome-copilot 기여용 (EN) 스킬. 엔진 내장 + 표준 구조(scripts/references/ 플랫) | **github/awesome-copilot** (fork → PR to `staged`) |

> 💡 둘은 같은 repo(`whoniiii/az-diagram-autogen`, `master` 브랜치)의 서로 다른 폴더지만, **배포 파이프라인은 완전히 독립**:
> - `az_diagram_autogen/` → `twine upload` → PyPI
> - `.github/skills/azure-architecture-autopilot/` → `awesome-copilot-contributor` 에이전트 워크플로우 → github/awesome-copilot PR

> ℹ️ KR 스킬 (`azure-architecture-autopilot-kr`, `azure-architecture-autopilot-pip-kr`)은 로컬에만 존재하며 git 추적 대상이 아님.

## ⚠️ 수정 시 반드시 2곳 동시 반영

**스킬 프롬프트/참조 문서/엔진 수정 요청이 오면 반드시 아래 2곳을 모두 업데이트해야 한다:**

| # | 경로 | 설명 |
|---|------|------|
| 1 | `az_diagram_autogen/` | 소스 원본 (PyPI 패키지). 상대 import (`from .icons`) |
| 2 | `.github/skills/azure-architecture-autopilot/` | awesome-copilot 기여용 (EN). 절대 import (`from icons`) |

### 2곳 차이점

| 항목 | az_diagram_autogen (Source) | azure-architecture-autopilot (EN) |
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
   az_diagram_autogen/generator.py                       ← 소스 원본 (상대 import)
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

## 🛡️ 다이어그램 회귀 방지 (generator.py 반복 개선 시 필수)

### 배경
`generator.py` 의 엣지 라우팅/레이아웃을 반복 개선하다 `overlap=0` 같은 **숫자 지표는 유지되지만 시각적으로 점점 나빠지는 회귀 루프**가 실제로 발생했다 (2026-04-15 사건). 따라서 반복 개선 작업에는 반드시 **명시적 baseline + 다중 지표 비교 + 조기 중단 규칙**이 적용돼야 한다.

### 에이전트: `diagram-quality-guardian`
이 목적을 전담하는 에이전트 — `.github/agents/diagram-quality-guardian.agent.md`

**사용 시점 (메인 에이전트의 역할)**:
- 사용자가 "엣지 라우팅 개선", "레이아웃 튜닝", "generator.py 반복 수정" 같은 **반복 개선 작업**을 요청하면 **작업 시작 전에 사용자에게 `/agent diagram-quality-guardian` 호출을 제안한다**.
- 에이전트는 자동 발동되지 않음 — 사용자가 `/agent` 로 직접 선택해야 함.
- 제안 문구 예시: "반복 개선 중 회귀를 방지하려면 먼저 `/agent` → `diagram-quality-guardian` 을 호출해 현재 상태를 baseline 으로 고정하는 걸 권장합니다."

### Baseline 디렉터리
```
baselines/           ← repo 루트 (gitignored)
├── current-best/    ← 사용자 승인된 gold 상태 (3개 케이스 HTML+PNG+meta.json)
├── working/         ← 비교용 임시
└── .attempts        ← 연속 회귀 카운터
```

> ℹ️ baseline 은 **전부 local-only** (`.gitignore` 에 `baselines/` 추가됨). git 추적하지 않는다. 회귀 방지는 세션 내 품질 보호가 목적이며, 영속 gold 가 필요하면 commit SHA 를 `meta.json` 에 기록한다.

### 반복 개선 체크리스트
메인 에이전트가 generator.py 를 고칠 때 지켜야 할 원칙:

1. **작업 전 baseline 확인** — `baselines/current-best/` 가 비어있으면 먼저 guardian 으로 snapshot.
2. **숫자만 보고 개선 판단 금지** — overlap count 가 0으로 유지돼도 edge-to-euclidean ratio 또는 시각 PNG 가 나빠지면 회귀.
3. **사용자 PNG 육안 승인 전에 baseline 교체 금지** — 지표가 모두 개선돼도 promote 는 사용자 확인 후.
4. **연속 5회 회귀 시 중단** — guardian `.attempts` 가 5 도달하면 접근법 재검토. rubber-duck 에이전트 호출 고려.
5. **각 시도는 stash 단위로** — 즉시 롤백 가능하도록 각 iteration 을 `git stash` 또는 커밋으로 격리.
6. **2곳 동기화 잊지 말 것** — `az_diagram_autogen/` 수정 후 `.github/skills/azure-architecture-autopilot/scripts/` 에도 반영 (import 만 `from .icons` → `from icons`).

### 판정 기준 (요약)
| 상황 | 판정 |
|---|---|
| Overlap count 증가 | 🔴 REGRESSION (즉시 롤백) |
| worst ratio +5% 초과 | 🔴 REGRESSION |
| avg ratio +5% 초과 | 🟡 BORDERLINE (사용자 확인) |
| PNG diff > 15% | 🟡 VISUAL CHECK 강제 |
| 모두 개선 또는 tie | 🟢 사용자 승인 후 promote |

## ⚠️ Git 커밋 규칙

**자동 커밋 금지** — 사용자가 명시적으로 "커밋해" 라고 요청할 때만 커밋한다. 수정 후 자동으로 `git commit`을 실행하지 않는다.

## 🧪 테스트 규칙

**코드 수정 후 반드시 테스트를 실행한다.**

```powershell
cd az_diagram_autogen
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
├── az_diagram_autogen/              ← PyPI 패키지 소스 (tracked)
│   ├── generator.py                 ← 핵심 HTML 다이어그램 생성기
│   ├── icons.py                     ← Azure 공식 아이콘 (SVG base64, ~2MB)
│   ├── cli.py                       ← CLI 인터페이스
│   └── REFERENCE.md                 ← 서비스 타입 레퍼런스
├── pyproject.toml                   ← PyPI 패키지 메타 (name = az-diagram-autogen)
├── tests/                           ← pytest 스위트 (gitignored; 결과 출력)
├── baselines/                       ← 다이어그램 회귀 방지 baseline (gitignored, local-only)
├── .github/
│   ├── copilot-instructions.md      ← 이 파일
│   ├── agents/                      ← GHCP 에이전트 (diagram-tester, diagram-quality-guardian, awesome-copilot-contributor)
│   └── skills/
│       └── azure-architecture-autopilot/  ← awesome-copilot 기여용 (EN, flat)
│           ├── SKILL.md
│           ├── scripts/                 ← 다이어그램 엔진 (플랫, 절대 import)
│           ├── references/              ← 프롬프트 + 참조 문서 (플랫)
│           └── assets/                  ← 스크린샷 이미지
└── .gitignore
```
