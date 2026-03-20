# azure-arch-builder

> Azure AI/Data 인프라를 자연어로 설계하고 자동 배포까지 이어주는 GitHub Copilot CLI 스킬

**[English README](README.md)**

"AI Search랑 Foundry 만들고 싶어" 라고 말하면, 대화를 통해 아키텍처를 확정하고 Bicep 코드 생성부터 실제 Azure 배포까지 자동으로 진행합니다.

---

## 🔄 워크플로우

```
사용자: "RAG 챗봇 만들어줘"
       ↓
Phase 1: 🎨 대화형 아키텍처 설계 + 다이어그램
       ↓
Phase 2: 🔧 Bicep 코드 자동 생성
       ↓
Phase 3: ✅ 코드 리뷰 + 컴파일 검증 (자동)
       ↓
Phase 4: 🚀 What-if → 프리뷰 다이어그램 → Azure 배포
```

**최적화 서비스:** Microsoft Foundry, Azure OpenAI, AI Search, ADLS Gen2, Key Vault, Microsoft Fabric, Azure Data Factory, VNet/Private Endpoint, AML/AI Hub

**기타 Azure 서비스:** 모두 지원 — MS Docs를 자동 조회하여 생성

---

## ⚙️ 사전 요구사항

| 도구 | 필수 | 설치 방법 |
|------|------|----------|
| **GitHub Copilot CLI** | ✅ | [설치 가이드](https://docs.github.com/copilot/concepts/agents/about-copilot-cli) |
| **Azure CLI** | ✅ (배포 시) | `winget install Microsoft.AzureCLI` |
| **Python 3** | ✅ (다이어그램용) | `winget install Python.Python.3.12` |

> Azure CLI 로그인(`az login`)은 배포 진행 시에만 확인합니다. 설계 단계에서는 불필요합니다.

### 🤖 권장 모델

이 스킬은 800줄 이상의 지침으로 구성된 복잡한 멀티 페이즈 오케스트레이션입니다. 모델 선택이 중요합니다.

| | 모델 | 비고 |
|---|---|---|
| ✅ **권장** | Claude Sonnet 4.5 / 4.6 | 비용 대비 최적 |
| 🏆 **최상** | Claude Opus 4.5 / 4.6 | 가장 안정적인 지침 수행 |
| ⚠️ **최소** | Claude Sonnet 4, GPT-5.1+ | 간혹 단계를 건너뛸 수 있음 |
| ❌ **비추** | Haiku, Mini 계열 | 지침이 너무 많아 누락 다수 |

---

## 📦 설치

### 프로젝트 스킬 (현재 프로젝트만)

```powershell
# 프로젝트 루트에서 실행
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

### 개인 스킬 (모든 프로젝트에서 사용)

```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.copilot\skills" -Force
git clone <repo-url> "$env:USERPROFILE\.copilot\skills\azure-arch-builder"
```

### 설치 확인

```
copilot /skills
```

`azure-arch-builder`가 목록에 표시되면 설치 완료입니다.

---

## 🚀 사용법

프로젝트 폴더에서 GitHub Copilot CLI를 실행합니다:

```powershell
cd your-project
copilot
```

원하는 Azure 인프라를 자연어로 요청하세요:

```
"AI Search랑 Microsoft Foundry 만들어줘, private endpoint 포함해서"
"RAG 챗봇 아키텍처 구성해줘"
"Fabric이랑 ADF로 데이터 플랫폼 만들어줘"
"Azure에 데이터 레이크하우스 올려줘"
```

Azure 인프라 관련 요청을 하면 스킬이 자동으로 발동됩니다.

### 단계별 진행

**🎨 1. 아키텍처 설계 (Phase 1)**
- 프로젝트 이름, 서비스, SKU, 리전, 네트워킹 확인
- MS Docs에서 최신 정보 조회 (모델, SKU, 가용성)
- 인터랙티브 HTML 아키텍처 다이어그램 생성
- 사용자 확정까지 반복 수정

**🔧 2. Bicep 생성 (Phase 2)**
- 모듈형 Bicep 템플릿 생성 (`main.bicep` + `modules/`)
- MS Docs에서 최신 API 버전 조회
- 보안 모범사례 자동 적용 (Private Endpoint, RBAC 등)

**✅ 3. 코드 리뷰 (Phase 3)**
- `az bicep build`로 컴파일 검증
- 체크리스트 기반 리뷰 (Foundry Project, PE 3종 세트, HNS 등)
- 문제 자동 수정 후 재컴파일

**🚀 4. 배포 (Phase 4)**
- What-if 검증 (실제 변경 없음)
- What-if 결과 기반 프리뷰 다이어그램
- 사용자 확인 → 실제 배포
- 배포 결과 기반 최종 다이어그램

### 📂 출력 구조

```
<project-name>/
├── 01_arch_diagram_draft.html      ← 설계 다이어그램
├── 02_arch_diagram_preview.html    ← What-if 프리뷰
├── 03_arch_diagram_result.html     ← 배포 결과
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

## 🌐 언어 지원

사용자의 첫 메시지 언어를 자동 감지하여 해당 언어로 응답합니다.
질문, 진행 안내, 보고서, Bicep 주석 등 모든 사용자 대면 텍스트가 자동으로 언어에 맞춰집니다.

---

## ✨ 주요 특징

- 🔍 **MS Docs 실시간 검증** — API 버전, 모델 가용성, SKU 옵션을 실시간으로 조회
- 🔒 **보안 기본 적용** — Private Endpoint, RBAC, 파라미터 파일에 시크릿 저장 금지
- 🎨 **대화형 설계** — 시각적 다이어그램과 함께 아키텍처를 반복 수정
- 👤 **단계별 승인** — 모든 주요 단계에서 사용자 확인 후 진행
- 🔄 **교차 검증** — 핵심 정보를 여러 MS Docs 소스에서 이중 확인
- ⚡ **병렬 프리로드** — 사용자 입력 대기 시간에 다음 단계 정보 미리 로딩

---

## 라이선스

MIT
