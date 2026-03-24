# az-autopilot-agent

> Azure 인프라를 자연어로 설계하거나, 기존 리소스를 분석하여 아키텍처를 시각화하고 수정·배포까지 이어주는 GitHub Copilot CLI 스킬

**[English README](README.md)**

---

## 🆕 v3 변경점

**v3는 [`az-diagram-autogen`](https://pypi.org/project/az-diagram-autogen/) PyPI 패키지**로 다이어그램을 생성합니다.

| | v2 | v3 |
|---|---|---|
| 다이어그램 엔진 | 내장 `generate_html_diagram.py` + `icons_azure.py` (~1.9MB) | `pip install az-diagram-autogen` |
| 아이콘 수 | 스킬 폴더에 번들 | 605+ Azure 공식 아이콘 (자동 설치) |
| 업데이트 | 수동 복사 | `pip install --upgrade az-diagram-autogen` |
| 스킬 크기 | ~2MB | ~50KB (scripts 폴더 없음) |

---

## 🔄 워크플로우

```
Path A: "RAG 챗봇 만들어줘"
         ↓
  🎨 Phase 1 → 🔧 Phase 2 → ✅ Phase 3 → 🚀 Phase 4

Path B: "현재 Azure 인프라 분석해줘"
         ↓
  🔍 Phase 0 (스캔) → 🎨 Phase 1 (수정) → 🔧→✅→🚀
```

| Phase | 이름 | 설명 |
|-------|------|------|
| **0** | 🔍 리소스 스캐너 | 기존 Azure 리소스 스캔 → 아키텍처 다이어그램 자동 생성 |
| **1** | 🎨 아키텍처 어드바이저 | 대화형 설계 또는 수정 |
| **2** | 🔧 Bicep 생성기 | 모듈형 Bicep 템플릿 자동 생성 |
| **3** | ✅ 코드 리뷰어 | 컴파일 검증 + 보안/모범사례 리뷰 |
| **4** | 🚀 배포 에이전트 | Validate → What-if → 프리뷰 → 배포 |

**모든 Azure 서비스 지원** — AI/Data 서비스에 최적화, 나머지는 MS Docs 자동 조회.

---

## ⚙️ 사전 요구사항

| 도구 | 필수 | 설치 |
|------|------|------|
| **GitHub Copilot CLI** | ✅ | [설치 가이드](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) |
| **Azure CLI** | ✅ | `winget install Microsoft.AzureCLI` |
| **Python 3** | ✅ (다이어그램) | `winget install Python.Python.3.12` |

| **az-diagram-autogen** | ✅ (자동 설치) | `pip install az-diagram-autogen` |

### 🤖 권장 모델

| | 모델 | 비고 |
|---|---|---|
| ✅ **권장** | Claude Sonnet 4.5 / 4.6 | 비용 대비 최적 |
| 🏆 **최상** | Claude Opus 4.5 / 4.6 | 가장 안정적 |
| ⚠️ **최소** | Claude Sonnet 4, GPT-5.1+ | 간혹 단계 건너뜀 |

---

## 📦 설치

```powershell
# 프로젝트 스킬
git clone <repo-url> .github/skills/az-autopilot-agent

# 개인 스킬 (모든 프로젝트)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.copilot\skills" -Force
git clone <repo-url> "$env:USERPROFILE\.copilot\skills\az-autopilot-agent"

# 다이어그램 패키지 (스킬이 자동 설치하지만, 미리 설치 가능)
pip install az-diagram-autogen
```

확인: `copilot /skills`

---

## 🚀 사용법

### Path A: 새로 만들기

```
"AI Search랑 Foundry 만들어줘, PE 포함"
"Databricks + ADLS Gen2 데이터 플랫폼 구성해줘"
"RAG 챗봇 아키텍처 만들어줘"
```

### Path B: 기존 분석 + 수정

```
"현재 Azure 인프라 분석해줘"
"rg-production 리소스 그룹 스캔해서 다이어그램 그려줘"
"내 구독에 뭐가 있어?"
```

이후 자연어로 수정:
```
"VM 3대 추가해줘"
"Foundry가 느린데 어떻게 하면 돼?"
"비용 줄이고 싶어 — AI Search를 Basic으로"
"모든 서비스에 PE 추가해줘"
```

### 📂 출력 구조

```
<project-name>/
├── 00_arch_current.html         ← 스캔 결과 (Path B)
├── 01_arch_diagram_draft.html   ← 설계 다이어그램
├── 02_arch_diagram_preview.html ← What-if 프리뷰
├── 03_arch_diagram_result.html  ← 배포 결과
├── main.bicep
├── main.bicepparam
└── modules/
    └── *.bicep
```

---

## 🌐 언어 지원

사용자 언어를 자동 감지하여 모든 출력이 해당 언어로 제공됩니다.

---

## ✨ 주요 특징

- 📦 **PyPI 패키지 기반 다이어그램** — `az-diagram-autogen` 605+ Azure 공식 아이콘, PNG 내보내기
- 🔍 **리소스 스캔** — 기존 Azure 리소스를 분석하여 아키텍처 다이어그램 자동 생성
- 💬 **자연어 수정** — "느려", "비용 줄여", "보안 강화" → 역질문으로 구체화
- 📊 **MS Docs 실시간 검증** — API 버전, SKU, 모델 가용성 실시간 조회
- 🔒 **보안 기본 적용** — Private Endpoint, RBAC, 시크릿 파일 저장 금지
- 🎨 **인터랙티브 다이어그램** — 클릭, 드래그 가능한 HTML 시각화
- ⚡ **병렬 프리로드** — 사용자 입력 대기 중 다음 단계 정보 미리 로딩

---

## 📁 구조

```
SKILL.md (라우터 ~160줄)
├── prompts/phase0-scanner.md      ← 기존 리소스 스캔
├── prompts/phase1-advisor.md      ← 아키텍처 설계/수정
├── prompts/bicep-generator.md     ← Bicep 생성
├── prompts/bicep-reviewer.md      ← 코드 리뷰
├── prompts/phase4-deployer.md     ← 배포 파이프라인
└── references/                    ← 서비스 패턴, PE 매핑
```

SKILL.md는 경량 라우터. 모든 Phase 로직은 `prompts/`에.

**`scripts/` 폴더 없음** — 다이어그램은 `az-diagram-autogen` PyPI 패키지로 생성.

---

## 라이선스

MIT
