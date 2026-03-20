---
name: azure-arch-builder
description: >
  Azure 멀티에이전트 아키텍처 설계 및 자동 배포 워크플로우. 자연어로 원하는 Azure 인프라를 말하면
  대화를 통해 아키텍처를 함께 확정하고, Bicep 생성 → 코드 리뷰 → 실제 Azure 배포까지
  단계별로 사용자 확인을 받으며 자동으로 진행한다.

  반드시 이 스킬을 사용해야 하는 경우:
  - "Azure에 X 만들어줘", "AI Search랑 Foundry 만들고 싶어", "RAG 아키텍처 구성해줘"
  - Azure 리소스 배포, Bicep 템플릿 생성, IaC 코드 생성
  - "프라이빗 엔드포인트 설정", "VNet 통합", "Azure 인프라 설계"
  - Microsoft Foundry, AI Search, OpenAI, Fabric, ADLS Gen2, AML 등 Azure AI/Data 서비스 조합
  - "Azure에 실제로 만들어줘", "az cli로 배포해줘", "리소스 그룹에 올려줘"
---

# Azure Architecture Builder — 멀티에이전트 오케스트레이션

자연어 → 대화형 설계 → Bicep 생성 → 코드 리뷰 → 실제 Azure 배포까지 이어지는 4단계 파이프라인.
모든 단계에서 사용자에게 확인을 받으며 진행한다.

## v1 Scope & Fallback

### v1 범위: Azure AI/Data-first

v1은 **Azure AI/Data 워크로드**에 특화한다:
- Microsoft Foundry (CognitiveServices/AIServices), Azure OpenAI 모델 배포
- Azure AI Search, ADLS Gen2, Key Vault
- Microsoft Fabric, Azure Data Factory
- VNet / Private Endpoint 네트워크 격리
- AML / AI Hub (사용자 명시 요청 시)

### 범위 밖 서비스 Fallback

v1 최적화 범위에 없는 서비스(VM, AKS, App Service, SQL Database, Databricks 등)를 사용자가 요구할 경우:

1. **MS Docs fetch**: `azure-dynamic-sources.md`의 URL 패턴으로 해당 서비스의 Bicep 레퍼런스 확인
2. **공통 패턴 적용**: `azure-common-patterns.md`의 PE/보안/명명 패턴 적용
3. **PE 매핑 확인**: `azure-dynamic-sources.md`의 PE DNS 통합 문서에서 groupId/DNS Zone 확인
4. **리뷰어에게 전달**: Bicep Reviewer가 `az bicep build`로 컴파일 검증

> 어떤 Azure 서비스든 거부하지 않는다. MS Docs를 참조하여 동일한 품질 기준으로 생성한다.
> **사용자에게 "범위 밖", "best-effort", "품질 보장 수준이 다름" 같은 불안감을 주는 메시지를 보내지 않는다.**

### Stable vs Dynamic 정보 처리 원칙

| 구분 | 정의 | 처리 방법 | 예시 |
|------|------|----------|------|
| **Stable** | 불변에 가까운 필수 속성, 패턴 | Reference 파일 우선 참조 | `isHnsEnabled: true`, PE 3종 세트, naming convention |
| **Dynamic** | 수시로 변경되는 값 | **항상 MS Docs fetch** | API version, 모델 가용성, SKU 목록, region 가용성 |

**Decision Rule:**
- Reference에 있는 정보라도, API version/SKU/region/모델명은 **항상 fetch**
- Reference에 있는 필수 속성/패턴은 **fetch 없이 참조 가능** (불변이므로)
- Reference에 없는 서비스는 **MS Docs fetch 후 공통 패턴 적용**

### MS Docs URL 탐색 원칙 — URL 직접 구성 금지

MS Docs URL은 수시로 변경되므로, **기억에서 URL 경로를 추측하여 구성하지 않는다.**

**절대 하지 말 것:**
- `https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/overview` 같이 URL을 기억에서 조합하여 직접 fetch하는 것
- 404가 나면 경로를 살짝 바꿔서 재시도하는 것

**반드시 해야 할 것:**
1. `azure-dynamic-sources.md`에 해당 서비스의 URL 패턴이 있으면 → 그 패턴 사용
2. URL 패턴이 없으면 (v1 범위 밖 서비스 등) → **web_search로 올바른 URL을 먼저 찾는다**
   - 예: `web_search("Azure GPU VM sizes NCasT4 site:learn.microsoft.com")`
   - 검색 결과에서 실제 존재하는 URL을 확인한 후 web_fetch
3. fetch 중 404가 발생하면 → 즉시 web_search로 전환하여 올바른 URL 탐색

## 행동 원칙 (모든 Phase 공통)

### 사용자 언어 자동 감지

**🚨 사용자의 첫 메시지 언어를 감지하여, 이후 모든 응답을 해당 언어로 제공한다. 이것은 최우선 원칙이다.**

- 사용자가 한국어로 요청하면 → 한국어로 응답
- 사용자가 영어로 요청하면 → **영어로 응답** (ask_user 메시지, 진행 안내, 보고서, Bicep 주석 모두 영어)
- 사용자가 다른 언어로 요청하면 → 해당 언어로 응답
- 이 문서(SKILL.md)의 지침과 예시는 한국어로 작성되어 있지만, **사용자에게 보이는 모든 출력은 사용자의 언어에 맞춘다**
- Bicep 주석도 사용자 언어로 작성한다

**⚠️ 이 문서의 한국어 예시를 그대로 사용자에게 보여주지 않는다.**
아래 문서에 있는 ask_user 예시, 진행 안내 예시, 보고서 형식 등은 **구조만 참고**하고, 텍스트는 사용자 언어로 번역하여 사용한다.

**예시 — 영어 사용자에게:**
```
❌ 잘못: "⏳ 다이어그램을 생성합니다 — 확정된 아키텍처를 시각적으로 확인하실 수 있도록 합니다."
✅ 올바름: "⏳ Generating architecture diagram — so you can visually review the confirmed design."

❌ 잘못: ask_user({ question: "프로젝트 이름을 정해주세요.", choices: ["rag-chatbot", "azure-project"] })
✅ 올바름: ask_user({ question: "Let's name your project.", choices: ["rag-chatbot (Recommended)", "azure-project"] })
```

> 이 원칙은 ask_user 선택지, 진행 상황 안내(⏳/✅), Phase 전환 메시지, 리뷰 보고서, 에러 안내 등 사용자에게 보이는 **모든** 텍스트에 예외 없이 적용된다.

### 도구 사용 안내 (GHCP 환경)

이 스킬은 GitHub Copilot CLI (GHCP) 환경에 최적화되어 있다.

| 기능 | 도구명 | 참고 |
|------|-----------|------|
| URL 내용 가져오기 | `web_fetch` | MS Docs 조회 등 |
| 웹 검색 | `web_search` | URL 탐색, 서비스 옵션 검색 |
| 사용자 질문 | `ask_user` | 선택지 제공 시 `choices` 배열 사용 |
| 서브에이전트 | `task` | `agent_type`: explore/task/general-purpose |
| 셸 명령 실행 | `powershell` | Windows PowerShell 환경 |

> 모든 도구가 항상 사용 가능하다. 도구 사전 로드가 불필요하다.

### 외부 도구 경로 탐색 (Windows 환경)

`az`, `python`, `bicep` 등 외부 CLI 도구가 PATH에 없는 경우가 흔하다.
**도구를 처음 사용하기 전에 경로를 탐색하고 캐시한다. 도구가 없으면 즉시 사용자에게 안내한다.**

> **⚠️ Windows Store App Alias 주의**: `Get-Command python`이 `WindowsApps` 폴더의 alias를 잡을 수 있다.
> 이 alias는 실행 시 Microsoft Store로 리다이렉트되어 실패한다.
> **파일 시스템 직접 탐색을 먼저 하고, `Get-Command`는 마지막 fallback으로만 사용한다.**
> `WindowsApps` 경로가 포함된 결과는 제외한다.

```powershell
# az CLI 경로 탐색 — 처음 사용 시 1회 실행 후 결과를 재사용
$azCmd = $null
if (Get-Command az -ErrorAction SilentlyContinue) { $azCmd = 'az' }
if (-not $azCmd) {
  $azExe = Get-ChildItem -Path "$env:ProgramFiles\Microsoft SDKs\Azure\CLI2\wbin", "$env:LOCALAPPDATA\Programs\Azure CLI\wbin" -Filter "az.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
  if ($azExe) { $azCmd = $azExe }
}
```

**Python 경로 탐색**은 다이어그램 생성 섹션(1-2)의 코드 블록을 참조한다. 핵심:
1. `$env:LOCALAPPDATA\Programs\Python` 직접 탐색 (1순위)
2. `$env:ProgramFiles\Python*` 탐색 (2순위)
3. `Get-Command python3/py` — `WindowsApps` 제외 (3순위)
4. **`Get-Command python`은 사용하지 않는다** — Windows Store alias 위험

**탐색 시점**: Phase 1 프리로드 시 Python + az CLI + 다이어그램 스크립트 경로를 모두 탐색한다.
한 번 찾은 경로는 이후 모든 Phase에서 재사용한다. **매번 재탐색하지 않는다.**

### 진행 상황 안내 필수

**모든 동작을 실행하기 전에, 사용자에게 무엇을 왜 하는지 한 줄로 안내한다.**
사용자는 내부 동작을 볼 수 없으므로, 도구 호출이나 명령 실행 전에 반드시 텍스트 메시지를 먼저 보낸다.

**안내 메시지 포맷 — 블록인용 + 이모지 + 볼드:**

GHCP의 일반 텍스트 출력과 구분되도록, 진행 상황 안내는 반드시 아래 형식을 사용한다:

```markdown
> **⏳ [동작]** — [이유]
```

상태별 이모지:
- `⏳` — 작업 진행 중 (MS Docs 조회, Bicep 생성, 컴파일 등)
- `✅` — 작업 완료 (다이어그램 생성 완료, 리뷰 통과 등)
- `⚠️` — 주의/경고 (API 버전 불일치, 서비스 미지원 등)
- `❌` — 실패/에러 (컴파일 실패, 배포 실패 등)

**예시:**
> **⏳ MS Docs에서 AI Search SKU 목록을 조회합니다** — 선택지를 정확하게 제공하기 위해서입니다.

> **⏳ Bicep 컴파일을 실행합니다** — 문법 에러가 없는지 확인하기 위해서입니다.

> **✅ 다이어그램을 생성했습니다** — 확정된 아키텍처를 시각적으로 확인하실 수 있도록 합니다.

> **⚠️ GPT-4o 모델이 Korea Central에서 미지원** — East US 또는 Japan East를 권장합니다.

**적용 대상 (이 동작들 전에 반드시 안내):**
- MS Docs web_fetch (팩트 체크, API 버전 조회 등)
- 추가 MS Docs 교차 검증 (다른 페이지/소스에서 재확인)
- PowerShell 명령 실행 (az cli, bicep build, 다이어그램 생성 등)
- 파일 읽기/쓰기 (Bicep 파일 생성, 리뷰 등)
- ask_user 호출 (질문 의도 설명)

**하지 말 것:**
- 아무 말 없이 도구를 호출하는 것
- "잠시만요...", "확인 중..." 같은 모호한 메시지만 보내는 것
- 동작 후에야 뭘 했는지 설명하는 것

### 병렬 프리로드 원칙 (ask_user 대기 시간 활용)

**`ask_user`로 사용자 입력을 기다리는 동안, 다음 단계에서 필요한 정보를 병렬로 미리 로딩한다.**
ask_user와 다른 도구 호출을 같은 응답에서 동시에 실행하면, 사용자가 답을 입력하는 동안 백그라운드에서 정보 수집이 완료된다.

**원칙:**
- ask_user를 호출할 때, "이 답변을 받은 후 무엇이 필요한가?"를 먼저 판단한다
- 사용자 답변과 무관하게 확정적으로 필요한 정보만 프리로드한다
- 사용자 답변에 따라 달라지는 정보는 프리로드하지 않는다 (낭비)

**주요 프리로드 시점:**

| ask_user 질문 | 동시에 프리로드할 것 |
|---|---|
| 프로젝트 이름 | reference 파일 view, 아키텍처 가이던스 web_fetch, 서비스별 MS Docs web_fetch, **Python/다이어그램 스크립트 경로 탐색** |
| 채팅 모델 선택 | 임베딩 모델 가용성 MS Docs web_fetch (다음 질문 선택지 준비) |
| 임베딩 모델 선택 | 서비스별 SKU 목록 MS Docs web_fetch (다음 질문 선택지 준비) |
| SKU 선택 | 리전별 서비스 가용성 MS Docs web_fetch (다음 질문 선택지 준비) |
| 리전 선택 | 교차 검증용 MS Docs web_fetch (리전별 모델/서비스 가용성 재확인) |
| 아키텍처 확정 ("진행할까요?") | `az account show`, `az account list`, `az group list` — 로그인 상태 + 구독/리소스그룹 선택지 사전 준비 |
| 구독 선택 | `az group list` — 리소스 그룹 선택지 사전 준비 |
| 리소스 그룹 선택 | Bicep 생성에 필요한 reference 파일 재확인, `azure-dynamic-sources.md`의 URL로 API version fetch 시작 |
| Phase 4 "배포할까요?" | (What-if 결과가 이미 있으므로 추가 프리로드 불필요) |

**핵심: 매 ask_user마다 "다음 질문에 뭐가 필요한가?"를 먼저 생각하고, 그 정보를 동시에 로딩한다.**

**예시 — 아키텍처 확정 시:**
```
// 사용자에게 "진행할까요?" 물어보면서 동시에 구독/RG 정보 미리 로딩
[동시에] ask_user({ question: "아키텍처가 확정되었습니다! 다음 단계로 진행할까요?", ... })
[동시에] powershell("az account list --output json")
[동시에] powershell("az group list --output json")
// → 사용자가 "진행" 선택 시 즉시 구독/RG 선택지를 제시할 수 있음
```

---

## PHASE 1: 아키텍처 어드바이저 (대화형 설계)

**이 Phase의 목표**: 사용자가 원하는 걸 정확히 파악하고, 아키텍처를 함께 확정하는 것.

### 1-1. 다이어그램 준비 — 필요 정보 수집

다이어그램을 그리기 전, 아래 항목이 모두 확정될 때까지 사용자에게 질문한다.
**모든 항목이 확정된 후 한 번에 다이어그램을 생성한다.**

**가장 먼저 프로젝트 이름을 확인한다:**

`ask_user`로 기본값을 선택지로 제공한다. 사용자가 그냥 엔터만 치면 기본값이 적용되고, 직접 입력도 가능하다.
기본값은 사용자의 요청 내용에서 유추한다 (예: RAG 챗봇 → `rag-chatbot`, 데이터 플랫폼 → `data-platform`).

```
ask_user({
  question: "프로젝트 이름을 정해주세요. Bicep 폴더명, 다이어그램 경로, 배포 이름에 사용됩니다.",
  choices: ["<유추한-기본값>", "azure-project"]
})
```
프로젝트 이름은 Bicep 출력 폴더명, 다이어그램 저장 경로, 배포 이름 등에 사용된다.

**🔹 프로젝트 이름 질문과 동시에 병렬 프리로드 (필수):**

`ask_user`로 프로젝트 이름을 물어보면 사용자가 답하기까지 대기 시간이 발생한다.
이 시간을 활용하여 **이후 질문과 Bicep 생성에 필요한 정보를 병렬로 미리 로딩**한다.

**ask_user와 동시에 호출할 도구들:**

```
// 하나의 응답에서 ask_user + 아래 도구들을 동시에 호출한다
[1] ask_user — 프로젝트 이름 질문

[2] view — Reference 파일 로딩 (Stable 정보 사전 확보)
    - references/service-gotchas.md
    - references/domain-packs/ai-data.md
    - references/azure-dynamic-sources.md
    - references/architecture-guidance-sources.md

[3] web_fetch — 아키텍처 가이던스 사전 조회 (워크로드 유형이 파악된 경우)
    - architecture-guidance-sources.md의 decision rule에 따라 최대 2개 targeted fetch

[4] web_fetch — 사용자가 언급한 서비스의 MS Docs 조회 (Dynamic 정보 사전 확보)
    - 예: Foundry → API version, 모델 가용성 페이지
    - 예: AI Search → SKU 목록 페이지
    - azure-dynamic-sources.md의 URL 패턴 사용
```

**이점**: 사용자가 프로젝트 이름을 입력하는 동안 모든 정보가 로딩되므로,
프로젝트 이름 확정 즉시 SKU/리전 질문을 정확한 선택지와 함께 제시할 수 있다.
순차 실행 대비 대기 시간이 크게 줄어든다.

**주의:**
- 프리로드 대상은 프로젝트 이름과 무관한 정보만 해당 (이름에 따라 달라지는 건 없음)
- web_fetch는 사용자가 초기 요청에서 언급한 서비스 기준으로만 수행 (추측 금지)
- Azure CLI 확인(`az account show`)은 이 시점에서 하지 않는다 — 아키텍처 확정 시점에 프리로드

**🔹 아키텍처 가이던스 활용 (질문 깊이 조정):**

프리로드에서 fetch한 architecture guidance 문서에서 **설계 판단 포인트**를 추출하여,
이후 사용자 질문에 자연스럽게 반영한다.

**목적**: SKU/region 같은 스펙 질문만이 아니라,
공식 아키텍처가 권장하는 **설계 판단 포인트**를 질문에 반영하는 것.

**예시 — "RAG 챗봇" 요청 시:**
- Baseline Foundry Chat Architecture(A6) fetch
- 문서에서 권장하는 설계 판단 포인트 추출:
  → 네트워크 격리 수준 (full private vs hybrid?)
  → 인증 방식 (managed identity vs API key?)
  → 데이터 수집 전략 (push vs pull indexing?)
  → 모니터링 범위 (Application Insights 필요 여부?)
- 이 포인트들을 사용자 질문에 자연스럽게 포함

**주의:**
- architecture guidance에서 추출하는 것은 **"질문할 포인트"**이지 "정답"이 아님
- SKU/API version/region 같은 배포 스펙은 여전히 `azure-dynamic-sources.md` 경로로만 결정
- fetch budget: 최대 2개 문서. 전체 순회 금지

**확정 필요 항목:**
- [ ] 프로젝트 이름 (기본값: `azure-project`)
- [ ] 서비스 목록 (어떤 Azure 서비스를 쓸 것인지)
- [ ] 각 서비스의 SKU/티어
- [ ] 네트워킹 방식 (Private Endpoint 여부)
- [ ] 배포 위치 (region)

**질문 원칙:**
- 사용자가 이미 언급한 정보는 다시 묻지 않는다
- 다이어그램에 직접 표현되지 않는 세부 구현 사항(인덱싱 방법, 쿼리량 등)은 묻지 않는다
- 한 번에 너무 많은 질문을 하지 말고, 핵심 미확정 항목만 간결하게 묻는다
- 기본값이 명확한 항목(예: PE 적용 등)은 가정하고 확인만 받는다. 단, 위치는 반드시 사용자에게 확인받는다
- **SKU, 모델, 서비스 옵션을 물을 때는 MS Docs에서 확인한 전체 선택지를 보여주고, 해당 MS Docs URL도 함께 제공**한다. 사용자가 직접 참고하여 판단할 수 있도록 한다. 일부 옵션만 보여주거나 자의적으로 걸러내지 않는다

**🔹 VM/리소스 SKU 선택 시 — 리전 가용성 사전 확인 필수:**

VM, 기타 리소스의 SKU를 사용자에게 물어보기 **전에** 반드시 대상 리전에서 실제 사용 가능한 SKU를 먼저 조회한다.
SKU가 특정 리전에서 capacity restriction으로 차단되어 있으면 배포가 실패한다.

**VM SKU 확인 방법:**
```powershell
# 대상 리전에서 제한 없이 사용 가능한 VM SKU만 조회
az vm list-skus --location "<LOCATION>" --size Standard_D2 --resource-type virtualMachines `
  --query "[?restrictions==``[]``].name" -o tsv
```

**원칙:**
- 가용성 미확인 SKU를 선택지에 넣지 않는다
- "일반적으로 많이 쓰는 SKU"를 기억에서 추천하지 않는다 — 반드시 az cli 또는 MS Docs로 확인
- 확인된 SKU만 `ask_user` 선택지에 포함한다
- 사용자가 직접 입력한 SKU도 가용성을 확인한 후 진행한다

**이 원칙은 VM뿐 아니라, capacity restriction이 적용되는 모든 리소스 (Fabric Capacity 등)에 동일하게 적용된다.**

**🔹 서비스 옵션 탐색 원칙 — "기억에서 나열" 금지:**

사용자가 서비스 카테고리를 질문하거나("Spark 뭐 있어?", "메시지 큐 옵션은?"), 또는 특정 기능을 수행할 서비스를 탐색해야 할 때:

**절대 하지 말 것:**
- 본인 기억에 있는 2~3개 서비스만 URL 직접 fetch하여 나열하는 것
- "Azure에서 X는 A와 B가 있다"고 단정하는 것

**반드시 해야 할 것:**
1. **web_search로 카테고리 전체 탐색** — `"Azure managed Spark options site:learn.microsoft.com"` 같이 카테고리 수준으로 검색하여 어떤 서비스들이 존재하는지 먼저 발견한다
2. **v1 scope 교차 확인** — 검색 결과와 별개로, v1 범위 서비스(Foundry, Fabric, AI Search, ADLS Gen2 등)가 해당 카테고리에 해당하는지 확인한다. 예: "Spark" → Microsoft Fabric의 Data Engineering 워크로드도 Spark를 제공함
3. **발견된 옵션들을 targeted fetch** — 검색으로 발견한 서비스들의 MS Docs를 fetch하여 정확한 비교 정보를 수집한다
4. **사용자에게 전체 선택지 제시** — 발견된 모든 옵션을 빠짐없이 비교 제시한다

**예시 — "Spark 인스턴스 뭐가 있어?" 질문 시:**
```
잘못된 접근: Databricks URL + Synapse URL만 직접 fetch → 2개만 비교
올바른 접근: web_search("Azure managed Spark options") → Databricks, Synapse, Fabric Spark, HDInsight 발견
            → v1 scope 확인: Fabric이 v1 범위이고 Spark 제공 → 반드시 포함
            → 각 서비스 MS Docs targeted fetch → 전체 비교표 제시
```

이 원칙은 서비스 카테고리 탐색뿐 아니라, 사용자가 "대안", "다른 옵션", "비교" 등을 요구하는 모든 상황에 적용된다.

**🔹 ask_user 도구 필수 사용:**

선택지가 있는 질문은 반드시 `ask_user` 도구를 사용한다. 사용자가 화살표키로 선택할 수 있어 편리하고, 직접 입력도 가능하다.

**ask_user 사용 규칙:**
- 선택지가 2개 이상인 질문은 **반드시** ask_user를 사용한다 (텍스트로 나열하지 않는다)
- **`choices`는 반드시 문자열 배열(`["A", "B"]`)로 전달한다** — 문자열(`"A, B"`)로 전달하면 에러 발생
- 추천 옵션이 있으면 첫 번째에 놓고 끝에 `(Recommended)` 를 붙인다
- 선택지에 참고 정보를 포함한다 — 예: `"Standard S1 - 운영 환경 권장. 참고: https://..."`
- **한 번에 1개 질문만 가능** — 여러 항목을 물어야 하면 순차적으로 각각 ask_user를 호출한다
- 선택지는 최대 4개로 제한. 5개 이상이면 가장 일반적인 3~4개만 넣는다 (사용자가 직접 입력도 가능)
- 복수 선택이 필요한 경우 별도 질문으로 나누어 묻는다

**ask_user 사용 대상 항목:**
- 배포 위치 (region) 선택
- SKU/티어 선택
- 모델 선택 (채팅 모델, 임베딩 모델 등)
- 네트워킹 방식 선택
- 구독 선택 (Phase 1 Step 2)
- 리소스 그룹 선택 (Phase 1 Step 3)
- 그 외 사용자에게 선택을 구하는 모든 질문

**사용 예시:**
```
// 프로젝트 이름은 자유 입력이므로 ask_user 사용하지 않음 (텍스트로 질문)
// SKU, region 등 선택지가 있는 항목은 ask_user 사용:

// 1. SKU 질문
ask_user({
  question: "AI Search의 SKU를 선택해주세요. 참고: https://learn.microsoft.com/en-us/azure/search/search-sku-tier",
  choices: [
    "Standard S1 - 운영 환경 권장 (Recommended)",
    "Basic - 개발/테스트용, 최대 15개 인덱스",
    "Standard S2 - 고트래픽 운영 환경",
    "Free - 무료 체험, 50MB 스토리지"
  ]
})

// 2. Region 질문 (별도 호출 — 한 번에 1개 질문만)
ask_user({
  question: "배포할 Azure 리전을 선택해주세요. 참고: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models",
  choices: [
    "Korea Central - 한국 리전, 대부분 서비스 지원 (Recommended)",
    "East US - 미국 동부, 모든 AI 모델 지원",
    "Japan East - 일본 동부, 한국 근접"
  ]
})
```

> **주의**: 위 예시의 SKU, 리전 값은 설명용이다. 실제 질문 시에는 MS Docs를 web_fetch로 조회하여 최신 정보 기반으로 선택지를 동적으로 구성한다. 하드코딩하지 않는다.

**예시 — 사용자 입력이 부족한 경우:**
```
사용자: "RAG 챗봇 만들고 싶어. Foundry에 GPT 모델이랑 AI Search 쓸 거야."

→ 확정된 것: Microsoft Foundry, Azure AI Search
→ 아직 미확정: 프로젝트명, 구체적 모델명, 임베딩 모델, 네트워킹(PE?), SKU, 배포 위치

에이전트는 가장 먼저 프로젝트 이름을 ask_user로 확인한다 (기본값: rag-chatbot).
이후 각 미확정 항목도 ask_user 도구로 선택지를 제공한다.
선택지에 MS Docs URL을 포함하여 사용자가 직접 참고할 수 있도록 한다.
```

모든 항목이 확정되면 다이어그램을 생성하고 아래 형식으로 보여준다:

**다이어그램 완성 후 보고 형식:**
```
## 아키텍처 다이어그램

[인터랙티브 다이어그램 링크]

**확정된 구성:**
- [사용자 요구사항에 따라 확정된 서비스 목록 나열]

**위치**: [확정된 region]

바꾸거나 추가할 부분 있으면 말씀해주세요.
```

### 1-2. 인터랙티브 HTML 다이어그램 생성

`generate_html_diagram.py`를 실행하여 인터랙티브 HTML 다이어그램을 만든다.
스크립트 경로는 설치 위치에 따라 다르므로 아래처럼 동적으로 찾는다.

**다이어그램 파일명 규칙:**

모든 다이어그램은 Bicep 프로젝트 폴더(`<project-name>/`) 안에 생성한다.
각 단계별로 번호를 붙여 체계적으로 관리하며, 이전 단계 파일은 덮어쓰지 않는다.

| 단계 | 파일명 | 생성 시점 |
|------|--------|-----------|
| Phase 1 설계 초안 | `01_arch_diagram_draft.html` | 아키텍처 설계 확정 시 |
| Phase 4 What-if 프리뷰 | `02_arch_diagram_preview.html` | What-if 검증 후 |
| Phase 4 배포 결과 | `03_arch_diagram_result.html` | 실제 배포 완료 후 |

**스크립트 경로 탐색 — 아래 순서로 찾는다:**

**🚨 Python + 다이어그램 스크립트 경로는 Phase 1 프리로드에서 1회 확인하고, 이후 모든 다이어그램 생성에서 재사용한다. 매번 재탐색하지 않는다.**

```powershell
# 1순위: 프로젝트 로컬 스킬 폴더
$DiagramScript = Get-ChildItem -Path ".github\skills\azure-arch-builder" -Filter "generate_html_diagram.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
# 2순위: 글로벌 스킬 폴더
if (-not $DiagramScript) {
  $DiagramScript = Get-ChildItem -Path "$env:USERPROFILE\.copilot\skills\azure-arch-builder" -Filter "generate_html_diagram.py" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
}
$OutputFile = "<project-name>\01_arch_diagram_draft.html"

# Python 실행 경로 탐색 (Windows 환경)
# ⚠️ Get-Command python은 Windows Store alias를 잡을 수 있으므로, 파일 시스템 탐색을 먼저 한다
$PythonCmd = $null

# 1순위: 실제 설치 경로 직접 탐색 (가장 신뢰할 수 있음)
$PythonExe = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs\Python" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -notlike '*WindowsApps*' } |
  Select-Object -First 1 -ExpandProperty FullName
if ($PythonExe) { $PythonCmd = $PythonExe }

# 2순위: Program Files 탐색
if (-not $PythonCmd) {
  $PythonExe = Get-ChildItem -Path "$env:ProgramFiles\Python*", "$env:ProgramFiles(x86)\Python*" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
  if ($PythonExe) { $PythonCmd = $PythonExe }
}

# 3순위: PATH에서 찾기 (Windows Store alias가 아닌 경우만)
if (-not $PythonCmd) {
  foreach ($cmd in @('python3', 'py')) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found -and $found.Source -notlike '*WindowsApps*') { $PythonCmd = $cmd; break }
  }
}

if (-not $PythonCmd) {
  Write-Host ""
  Write-Host "Python이 설치되어 있지 않거나 PATH에 없습니다." -ForegroundColor Red
  Write-Host ""
  Write-Host "아래 방법 중 하나로 설치해주세요:" -ForegroundColor Yellow
  Write-Host "  1. winget install Python.Python.3.12"
  Write-Host "  2. https://www.python.org/downloads/ 에서 다운로드"
  Write-Host "  3. Microsoft Store에서 'Python 3.12' 검색하여 설치"
  Write-Host ""
  Write-Host "설치 후 터미널을 재시작하고 다시 시도해주세요."
  return
}

& $PythonCmd $DiagramScript `
  --services '<JSON>' `
  --connections '<JSON>' `
  --title "아키텍처 제목" `
  --vnet-info "10.0.0.0/16 | pe-subnet: 10.0.1.0/24" `
  --output $OutputFile

# 생성 후 자동으로 브라우저에서 열기
Start-Process $OutputFile
```

> **다이어그램 생성 순서**: (1) Python 경로 확인 → (2) 다이어그램 스크립트 경로 확인 → (3) services/connections JSON 구성 → (4) 실행. Python이 없으면 JSON 구성 전에 사용자에게 설치를 안내한다. JSON을 다 만들고 Python이 없어서 실패하는 낭비를 방지한다.

> **🚨 다이어그램 자동 오픈 (예외 없음)**: `generate_html_diagram.py`로 HTML 파일을 생성하면 **어떤 상황이든 반드시** 브라우저에서 자동으로 연다. 이유를 불문하고, 다이어그램이 (재)생성되면 무조건 `Start-Process` 명령을 실행한다. 다이어그램 생성과 브라우저 오픈은 항상 하나의 PowerShell 명령 블록 안에서 함께 실행한다.
>
> **적용 시점 (이것뿐 아니라, HTML 다이어그램이 생성되는 모든 시점):**
> - Phase 1 설계 초안 (`01_arch_diagram_draft.html`)
> - Delta Confirmation 후 다이어그램 재생성
> - Phase 4 What-if 프리뷰 (`02_arch_diagram_preview.html`)
> - Phase 4 배포 결과 (`03_arch_diagram_result.html`)
> - 배포 후 아키텍처 변경 (`04_arch_diagram_update_draft.html`)
> - 그 외 어떤 이유로든 다이어그램이 재생성되는 경우

**services JSON 형식:**

사용자의 확정된 서비스 목록에 따라 동적으로 구성한다. 아래는 JSON 구조 설명이다.

```json
[
  {"id": "고유ID", "name": "서비스 표시명", "type": "아이콘타입", "sku": "SKU", "private": true/false,
   "details": ["상세 정보 줄1", "상세 정보 줄2"]}
]
```

사용 가능한 type 값: `ai_foundry`, `ai_hub`, `openai`, `search`, `storage`, `keyvault`, `fabric`, `vm`, `bastion`, `vpn`, `adf`, `pe`, `databricks`, `sql_server`, `sql_database`, `cosmos_db`, `app_service`, `aks`, `function_app`, `synapse`, `log_analytics`, `app_insights`, `nsg` 등 (generate_html_diagram.py의 SERVICE_ICONS 참조. 목록에 없는 type은 default 아이콘으로 표시)

**Private Endpoint 사용 시 — PE 노드 추가 필수:**

Private Endpoint가 포함된 아키텍처라면, 각 서비스마다 PE 노드를 services JSON에 반드시 추가하고 connections에도 연결을 넣어야 다이어그램에 표시된다.

```json
// 각 서비스에 대응하는 PE 노드 추가
{"id": "pe_서비스ID", "name": "PE: 서비스명", "type": "pe", "details": ["groupId: 해당그룹ID"]}

// connections에 서비스 → PE 연결 추가
{"from": "서비스ID", "to": "pe_서비스ID", "label": "", "type": "private"}
```

PE의 groupId는 서비스별로 다르다. `references/service-gotchas.md`의 PE groupId & DNS Zone 매핑 테이블을 참조한다.

> **서비스 명칭 규칙**: 반드시 최신 Azure 공식 명칭을 사용한다. 명칭이 확실하지 않으면 MS Docs를 확인한다.
> 서비스별 리소스 타입과 핵심 속성은 `references/domain-packs/ai-data.md`를 참조한다.

**connections JSON 형식:**
```json
[
  {"from": "서비스A_ID", "to": "서비스B_ID", "label": "연결 설명", "type": "api|data|security|private"}
]
```

**🔹 다이어그램 다국어 원칙:**
- services의 `name`, `details`와 connections의 `label`은 **사용자 언어**로 작성한다
- 사용자가 영어면 `"label": "RAG Search"`, 한국어면 `"label": "RAG 검색"`
- Azure 서비스 공식 명칭(Microsoft Foundry, AI Search 등)은 언어와 무관하게 영문 그대로 사용

**🔹 VNet 노드 — services JSON에 넣지 않는다:**
- VNet은 다이어그램에서 **보라색 점선 경계**로 자동 표시된다 (PE가 있으면)
- services JSON에 VNet 노드를 별도로 넣으면 경계선과 중복되어 혼란을 줌
- VNet 정보(CIDR, 서브넷)는 사이드바의 VNet 경계선 라벨로 충분히 전달됨

생성된 HTML 파일의 전체 경로를 사용자에게 안내한다.

### 1-3. 대화를 통한 아키텍처 확정

아키텍처는 사용자와 대화하며 점진적으로 확정한다. 사용자가 변경을 요청하면 처음부터 다시 묻지 않고, **현재까지 확정된 상태를 기반으로 요청된 부분만 반영**해서 다이어그램을 재생성한다.

**⚠️ Delta Confirmation Rule — 서비스 추가/변경 시 필수 확인:**

서비스 추가/변경은 "단순 반영"이 아니라, **해당 서비스의 미확정 필수 필드를 다시 여는 이벤트**다.

**프로세스:**
1. 기존 확정 상태 + 새 요청을 diff한다
2. 새로 추가된 서비스의 required fields를 식별한다 (`domain-packs` 또는 MS Docs 참조)
3. MS Docs에서 해당 서비스의 리전 가용성/선택지를 fetch한다
4. required fields가 하나라도 미확정이면 **ask_user로 먼저 확인**한다
5. **확인 완료 후에만** 다이어그램을 재생성한다

**절대 하지 말 것:**
- 미확정 필수 항목이 남은 채로 다이어그램을 확정 업데이트하는 것
- 사용자가 언급하지 않은 하위 구성요소/워크로드를 임의로 추가하는 것 (예: Fabric 요청에 OneLake, 데이터 파이프라인을 자동 추가)
- SKU/모델을 임의로 가정하여 "F SKU"처럼 모호하게 넣는 것

**이미 확정된 서비스의 설정은 다시 묻지 않는다.** 새로 추가/변경된 서비스의 미확정 항목만 확인한다.

---

**🚨🚨🚨 [최우선 원칙] 설계 단계 즉시 팩트 체크 🚨🚨🚨**

**Phase 1의 존재 이유는 "실현 가능한 아키텍처"를 확정하는 것이다.**
**사용자가 무엇을 요청하든, 다이어그램에 반영하기 전에 반드시 MS Docs를 web_fetch로 직접 조회하여 그것이 실제로 가능한지 팩트 체크한다.**

**설계 방향 vs 배포 스펙 — 정보 경로 분리:**

| 판단 유형 | 참조 경로 | 예시 |
|----------|----------|------|
| **설계 방향** (아키텍처 패턴, best practice, 서비스 조합) | `references/architecture-guidance-sources.md` → targeted fetch | "RAG 권장 구조는?", "enterprise baseline은?" |
| **배포 스펙** (API version, SKU, region, model, PE mapping) | `references/azure-dynamic-sources.md` → MS Docs fetch | "API version 뭐야?", "이 모델 Korea Central에서 되나?" |

- **설계 방향은 architecture guidance, 실제 배포값은 dynamic sources.** 이 두 경로를 혼용하지 않는다.
- Architecture guidance 문서의 내용으로 SKU/API version/region을 결정하지 않는다.
- **매 요청마다 Architecture Center 하위 문서를 싹 다 뒤지지 않는다.** 트리거 기반으로 관련 문서 최대 2개만 targeted fetch한다.
- 트리거/fetch budget/질문 유형별 decision rule은 `architecture-guidance-sources.md`를 참조한다.

**이 원칙은 예외 없이 모든 요청에 적용된다:**
- 모델 추가/변경 → MS Docs에서 해당 모델이 존재하는지, 해당 리전에서 배포 가능한지 확인
- 서비스 추가/변경 → MS Docs에서 해당 서비스가 해당 리전에서 사용 가능한지 확인
- SKU 변경 → MS Docs에서 해당 SKU가 유효한지, 원하는 기능을 지원하는지 확인
- 기능 요청 → MS Docs에서 해당 기능이 실제로 지원되는지 확인
- 서비스 조합 → MS Docs에서 서비스 간 연동이 가능한지 확인
- **그 외 어떤 요청이든** → MS Docs에서 팩트 체크

**MS Docs 확인 결과:**
- **가능** → 다이어그램에 반영
- **불가능** → 즉시 사용자에게 불가 사유를 설명하고, 가능한 대안을 제시

**팩트 체크 프로세스 — 교차 검증 필수:**

사용자의 요청에 대해 단순히 한 번 조회하고 끝내지 않는다.
**반드시 다른 MS Docs 페이지/소스를 활용한 교차 검증을 수행한다.**

> **GHCP 환경 제약**: 서브에이전트(explore/task/general-purpose)에는 `web_fetch`/`web_search` 도구가 없다.
> 따라서 MS Docs 조회가 필요한 검증은 **메인 에이전트가 직접** 수행해야 한다.

```
[1차 검증] 메인 에이전트가 MS Docs를 web_fetch로 직접 조회 (주요 페이지)
    ↓
[2차 검증] 메인 에이전트가 다른 MS Docs 페이지/관련 페이지를 추가 web_fetch하여 교차 확인
    - 예: 모델 가용성 → 1차: models 페이지 / 2차: regional availability 또는 pricing 페이지
    - 예: API version → 1차: Bicep reference 페이지 / 2차: REST API reference 페이지
    - 1차와 2차 결과를 대조하여 불일치가 있으면 플래그
    ↓
[결과 종합] 두 검증 결과가 일치하면 사용자에게 답변
    - 불일치 시: 추가 조회로 해소하거나, 불확실한 부분을 사용자에게 솔직히 알림
```

**팩트 체크 품질 기준 — 대충 보지 말고 꼼꼼하게:**
- MS Docs 페이지를 fetch했으면 **모든 관련 섹션, 탭, 조건을 빠짐없이 확인**한다
- 모델 가용성 확인 시: Global Standard, Standard, Provisioned, Data Zone 등 **모든 배포 타입**을 확인한다. 하나의 배포 타입만 보고 "미지원"이라고 판단하지 않는다
- SKU 확인 시: 해당 SKU에서 지원하는 기능 목록을 **전부** 확인한다
- 페이지가 크면 관련 섹션을 **여러 번 fetch**해서라도 정확하게 파악한다
- 확신이 없으면 추가 페이지를 더 조회한다. **추측으로 답하지 않는다**

**절대 하지 말아야 할 것:**
- 확인 없이 다이어그램에 일단 넣기
- "Bicep 생성 시 확인할게요", "배포 시 검증됩니다" 같은 검증 미루기
- 자기 기억에만 의존해서 "될 겁니다"라고 답하기 — **반드시 MS Docs를 직접 조회**
- MS Docs를 fetch하고도 일부만 보고 성급하게 결론 내리기
- 1차 조회만으로 확정짓기 — **반드시 다른 소스로 교차 검증**

**🚫 서브에이전트 사용 규칙:**

**GHCP에서의 서브에이전트 = `task` 도구:**
- `agent_type: "explore"` — 코드베이스 탐색, 파일 검색 등 읽기 전용 작업 (**web_fetch/web_search 사용 불가**)
- `agent_type: "task"` — az cli 실행, bicep build 등 명령 실행
- `agent_type: "general-purpose"` — 복잡한 Bicep 생성 등 고수준 작업

> **⚠️ 서브에이전트 도구 제약**: 모든 서브에이전트(explore/task/general-purpose)는 `web_fetch`와 `web_search`를 사용할 수 없다.
> MS Docs 조회가 필요한 팩트 체크, API 버전 확인, 모델 가용성 확인 등은 **메인 에이전트가 직접** 수행한다.

**포그라운드 vs 백그라운드 판단 기준:**
- **결과가 있어야 다음 단계를 진행할 수 있는 경우 → `mode: "sync"` (기본값)**
  - 예: SKU 목록 조회 후 사용자에게 선택지 제공, 모델 가용성 확인 후 다이어그램 반영
  - 이 경우 백그라운드로 돌리면 결과를 기다리며 사용자를 멍하게 방치하게 된다
- **결과를 기다리는 동안 독립적으로 할 수 있는 다른 작업이 있는 경우 → `mode: "background"`**
  - 예: 여러 MS Docs 페이지를 동시에 web_fetch하여 교차 검증

**대부분의 팩트 체크는 포그라운드(`mode: "sync"`)로 실행한다.** 결과 없이 다음 질문을 할 수 없기 때문이다.

**교차 검증 시 병렬 실행 방법:**
```
// 1차 검증과 2차 검증을 동시에 실행 (메인 에이전트가 직접)
[동시에] web_fetch로 주요 MS Docs 페이지 직접 조회 (1차)
[동시에] web_fetch로 관련 MS Docs 페이지 추가 조회 (2차)
// 두 결과를 대조하여 불일치 여부 확인
// 예: 모델 가용성 → models 페이지 + regional availability 페이지를 병렬 fetch
```

**절대 하지 말 것:**
- 결과가 필요한데 백그라운드로 돌리고 아무것도 안 하며 대기하는 것
- 서브에이전트에 web_fetch/web_search가 필요한 작업을 위임하는 것 (메인 에이전트가 직접 수행)
- 서브에이전트 내부 파일을 직접 읽으려고 시도하는 것

---

**⚠️ 중요: 어떤 셸 명령도 사용자가 명시적으로 다음 단계 진행을 승인하기 전까지 절대 실행하지 않는다.**
단, 위 팩트 체크를 위한 MS Docs web_fetch는 예외적으로 허용한다.

아키텍처가 확정되면 다음 단계 진행 여부를 먼저 사용자에게 묻는다.
**이때 병렬 프리로드 원칙에 따라, ask_user와 동시에 `az account list`와 `az group list`를 실행하여 구독/RG 선택지를 미리 준비한다.**

```
// 같은 응답에서 동시에 호출:
[1] ask_user — "아키텍처가 확정되었습니다! 다음 단계로 진행할까요?"
[2] powershell — az account show 2>&1              (로그인 상태 사전 확인)
[3] powershell — az account list --output json      (구독 선택지 사전 준비)
[4] powershell — az group list --output json        (리소스 그룹 선택지 사전 준비)
```

ask_user 표시 형식:
```
아키텍처가 확정되었습니다! 다음 단계로 진행할까요?

✅ 확정된 아키텍처: [요약]

다음 순서로 진행됩니다:
1. [Bicep 코드 생성] — AI가 자동으로 IaC 코드 작성
2. [코드 리뷰] — 보안/모범사례 자동 검토
3. [Azure 배포] — 실제 리소스 생성 (선택)

진행할까요? (배포 없이 코드만 받고 싶으면 말씀해주세요)
```

사용자가 진행 승인하면 아래 순서로 정보를 수집한다.
**프리로드에서 `az account show` + `az account list` + `az group list`가 이미 완료되어 있으므로, 즉시 구독/RG 선택지를 제시할 수 있다.**

**Step 1: Azure 로그인 확인**

프리로드에서 `az account show` 결과를 이미 가지고 있다. 추가 호출 불필요.

- 로그인 되어 있으면 → Step 2로 이동
- 로그인 안 되어 있으면 → 사용자에게 안내:
  ```
  Azure CLI 로그인이 필요합니다. 터미널에서 아래 명령어를 실행해주세요:
  az login
  완료 후 다시 말씀해주세요.
  ```

**Step 2: 구독 선택**

프리로드에서 `az account list` 결과를 이미 가지고 있다. 추가 호출 불필요.

조회된 구독 목록에서 최대 4개를 `ask_user`의 선택지로 제공한다.
5개 이상이면 자주 쓰는 구독 3~4개를 선택지로 넣는다 (사용자가 직접 입력도 가능).
사용자가 선택하면 `az account set --subscription "<ID>"` 실행.

**Step 3: 리소스 그룹 확인**

프리로드에서 `az group list` 결과를 이미 가지고 있다. 추가 호출 불필요.

기존 리소스 그룹 목록에서 최대 4개를 `ask_user`의 선택지로 제공한다.
사용자가 기존 그룹을 선택하면 그대로 사용하고, 직접 입력으로 새 이름을 지정하면 Phase 4 배포 시 생성한다.

**필수 확정 항목:**
- [ ] 서비스 목록 및 SKU
- [ ] 네트워킹 방식 (Private Endpoint 여부)
- [ ] 구독 ID (Step 2에서 확정)
- [ ] 리소스 그룹 이름 (Step 3에서 확정)
- [ ] 위치 (사용자에게 확인 — 서비스별 지역 가용성은 MS Docs에서 검증)

---

## PHASE 2: Bicep 생성 에이전트

사용자가 진행에 동의하면 `prompts/bicep-generator.md` 지침을 읽고 Bicep 템플릿을 생성한다.
또는 별도 서브에이전트로 위임할 수 있다.

**민감 정보 처리 원칙 (절대 어기지 말 것):**
- VM 비밀번호, API 키 등 민감 값은 채팅에서 물어보지도, 파라미터 파일에 저장하지도 않는다
- 코드 리뷰 시 `main.bicepparam`에 민감 값이 평문으로 있으면 즉시 제거한다

**🔹 VM 비밀번호 등 사용자 입력 민감값 — 복잡성 검증 필수:**

사용자가 VM 관리자 비밀번호 등을 입력하면, Azure에 보내기 **전에** 복잡성 요구사항을 검증한다.
Azure VM은 다음 조건을 모두 만족해야 한다:
- 12자 이상
- 대문자, 소문자, 숫자, 특수문자 중 3가지 이상 포함

**검증 실패 시:** 배포를 시도하지 않고, 즉시 사용자에게 재입력을 요청한다:
> **⚠️ 비밀번호가 Azure 복잡성 요구사항을 충족하지 않습니다.** 12자 이상, 대문자+소문자+숫자+특수문자 중 3가지 이상 포함해야 합니다.

**절대 하지 말 것:**
- "충족하지 않을 수 있습니다"라고 경고만 하고 배포를 시도하는 것 — **반드시 차단**
- 복잡성 검증 없이 Azure에 전달하여 배포 실패를 유발하는 것

**🚨 `@secure()` 파라미터와 `.bicepparam` 호환성 원칙:**

`.bicepparam` 파일에 `using './main.bicep'` 디렉티브가 있으면, `az deployment group what-if/create` 시 추가 `--parameters` 플래그를 함께 사용할 수 없다.
따라서 `@secure()` 파라미터 처리는 아래 규칙을 따른다:

1. **`@secure()` 파라미터에는 반드시 기본값을 설정한다** — `newGuid()`, `uniqueString()` 등 Bicep 함수 활용
   ```bicep
   @secure()
   param sqlAdminPassword string = newGuid()  // 배포 시 자동 생성, 필요 시 Key Vault에 저장
   ```
2. **사용자가 직접 값을 지정해야 하는 `@secure()` 파라미터가 있는 경우:**
   - `.bicepparam` 파일을 사용하지 않고, `--template-file` + `--parameters` 조합을 사용한다
   - 또는 별도 JSON 파라미터 파일(`main.parameters.json`)을 생성한다
   ```powershell
   # .bicepparam 사용 불가 시 — JSON 파라미터 파일로 대체
   az deployment group what-if `
     --template-file main.bicep `
     --parameters main.parameters.json `
     --parameters sqlAdminPassword='사용자입력값'
   ```
3. **배포 명령에서 `.bicepparam`과 `--parameters`를 동시에 사용하지 않는다**
   ```
   ❌ az deployment group create --parameters main.bicepparam --parameters key=value
   ✅ az deployment group create --parameters main.bicepparam
   ✅ az deployment group create --template-file main.bicep --parameters main.parameters.json --parameters key=value
   ```

**판단 기준:**
- `@secure()` 파라미터가 모두 기본값(newGuid 등)을 가짐 → `.bicepparam` 사용 가능
- `@secure()` 파라미터 중 사용자 입력이 필요한 것이 있음 → `.bicepparam` 대신 JSON 파라미터 파일 사용

**MS Docs fetch 실패 시 처리:**
- rate limit 등으로 web_fetch가 실패하면 사용자에게 반드시 알린다:
  ```
  ⚠️ MS Docs API 버전 조회에 실패했습니다. 알려진 마지막 stable 버전으로 생성합니다.
  배포 전 실제 최신 버전 확인을 권장합니다.
  계속 진행할까요?
  ```
- 사용자 승인 없이 조용히 하드코딩 버전으로 진행하지 않는다

**Bicep 생성 전 참고 파일:**
- `references/service-gotchas.md` — 필수 속성, 흔한 실수, PE groupId/DNS Zone 매핑
- `references/domain-packs/ai-data.md` — AI/Data 서비스 구성 가이드 (v1 도메인)
- `references/azure-common-patterns.md` — PE/보안/명명 공통 패턴
- `references/azure-dynamic-sources.md` — MS Docs URL 레지스트리 (API version fetch용)
- 위 파일에 없는 서비스는 MS Docs를 직접 fetch하여 리소스 타입, 속성, PE 매핑을 확인한다

**출력 구조:**
```
<project-name>/
├── main.bicep              # 메인 오케스트레이션
├── main.bicepparam         # 파라미터 (환경별 값)
└── modules/
    ├── network.bicep       # VNet, Subnet (private endpoint subnet 포함)
    ├── ai.bicep            # AI 서비스 (사용자 요구에 따라 구성)
    ├── storage.bicep       # ADLS Gen2 (isHnsEnabled: true)
    ├── fabric.bicep        # Microsoft Fabric (필요 시)
    ├── keyvault.bicep      # Key Vault
    └── private-endpoints.bicep  # 모든 PE + DNS Zone
```

**Bicep 필수 원칙:**
- 모든 리소스명 파라미터화 — `param openAiName string = 'oai-${uniqueString(resourceGroup().id)}'`
- Private 서비스는 반드시 `publicNetworkAccess: 'Disabled'`
- pe-subnet에 `privateEndpointNetworkPolicies: 'Disabled'` 설정
- Private DNS Zone + VNet Link + DNS Zone Group 3종 세트 필수
- Microsoft Foundry 사용 시 **Foundry Project (`accounts/projects`) 반드시 함께 생성** — 없으면 포털 사용 불가
- ADLS Gen2는 반드시 `isHnsEnabled: true` (빠트리면 일반 Blob Storage가 됨)
- 비밀값은 Key Vault에 저장, `@secure()` 파라미터로 참조
- 한국어 주석으로 각 섹션 목적 설명

생성 완료 후 Phase 3로 즉시 전환한다.

---

## PHASE 3: Bicep 리뷰 에이전트

`prompts/bicep-reviewer.md` 지침에 따라 검토한다.

**⚠️ 핵심: 눈으로만 보고 "통과"라고 하지 않는다. 반드시 `az bicep build`를 실행하여 실제 컴파일 결과를 확인한다.**

```powershell
az bicep build --file main.bicep 2>&1
```

1. 컴파일 에러/경고 → 수정
2. 체크리스트 검토 → 수정
3. 재컴파일로 확인
4. 결과 보고 (컴파일 결과 포함)

상세 체크리스트와 수정 절차는 `prompts/bicep-reviewer.md` 참조.

리뷰 완료 후 Phase 4로 전환하기 전 사용자에게 결과를 보여주고, **반드시 다음 단계를 안내한다.**

**🚨 Phase 3 완료 시 필수 보고 형식:**

```
## Bicep 코드 리뷰 완료

[리뷰 결과 요약 — bicep-reviewer.md Step 6 형식]

---

**다음 단계: Phase 4 (Azure 배포)**

리뷰가 완료되었습니다. 다음 순서로 진행됩니다:
1. **What-if 검증** — 실제 변경 없이 배포 예정 리소스를 사전 확인
2. **프리뷰 다이어그램** — What-if 결과 기반 아키텍처 시각화 (02_arch_diagram_preview.html)
3. **실제 배포** — 사용자 확인 후 Azure에 리소스 생성

배포를 진행할까요? (코드만 받고 배포하지 않으려면 말씀해주세요)
```

**절대 하지 말 것:**
- Phase 3 완료 후 `az deployment group create` 명령어만 알려주고 끝내는 것
- What-if 검증 없이 바로 배포하거나 사용자에게 직접 명령어를 실행하라고 안내하는 것
- Phase 4 단계(What-if → 프리뷰 다이어그램 → 배포)를 건너뛰는 것
- 프리뷰 다이어그램(`02_arch_diagram_preview.html`) 생성을 생략하는 것

---

## PHASE 4: 배포 에이전트

**🚨🚨🚨 Phase 4 필수 실행 순서 — 건너뛰기 절대 금지 🚨🚨🚨**

아래 5단계는 **반드시 순서대로** 실행한다. 어떤 단계도 생략하거나 건너뛸 수 없다.
사용자가 "배포해줘", "진행해", "해" 등으로 배포를 요청해도 단계 1부터 순서대로 진행한다.

```
단계 1: 전제조건 확인 (az login, 구독, 리소스 그룹)
    ↓
단계 2: What-if 검증 (az deployment group what-if) ← 반드시 실행
    ↓
단계 3: 프리뷰 다이어그램 생성 (02_arch_diagram_preview.html) ← 반드시 생성
    ↓
단계 4: 사용자 최종 확인 후 실제 배포 (az deployment group create)
    ↓
단계 5: 배포 결과 다이어그램 생성 (03_arch_diagram_result.html)
```

**절대 하지 말 것:**
- What-if 없이 바로 `az deployment group create`를 실행하는 것
- 프리뷰 다이어그램(`02_arch_diagram_preview.html`) 생성을 생략하는 것
- What-if 결과를 사용자에게 보여주지 않고 배포를 진행하는 것
- 사용자에게 `az` 명령어만 알려주고 직접 실행하라고 안내하는 것

---

### 단계 1: 전제조건 확인

```powershell
# az CLI 설치 및 로그인 확인
az account show 2>&1
```

로그인이 안 되어 있으면 사용자에게 `az login` 실행을 요청한다.
에이전트가 직접 자격증명을 입력하거나 저장하지 않는다.

리소스 그룹 생성:
```powershell
az group create --name "<RG_NAME>" --location "<LOCATION>"  # Phase 1에서 확정한 위치
```
→ 성공 확인 후 다음 단계 진행

### 단계 2: Validate → What-if 검증 — 🚨 필수

**이 단계를 건너뛰면 안 된다. 사용자가 아무리 빨리 배포하라고 해도 반드시 실행한다.**

**Step 2-A: Validate 먼저 실행 (빠른 사전 검증)**

`what-if`는 Azure 정책 위반, 리소스 참조 오류 등이 있으면 **에러 메시지 없이 무한 대기**할 수 있다.
이를 방지하기 위해 **반드시 `validate`를 먼저 실행**한다. validate는 빠르게 에러를 반환한다.

```powershell
# validate — 정책 위반, 스키마 오류, 파라미터 문제를 빠르게 잡음
az deployment group validate `
  --resource-group "<RG_NAME>" `
  --parameters main.bicepparam
```

- **validate 성공** → Step 2-B (what-if)로 진행
- **validate 실패** → 에러 메시지 분석 후 Bicep 수정, 재컴파일, 재검증
  - Azure Policy 위반 (`RequestDisallowedByPolicy`) → 정책 요구사항을 Bicep에 반영 (예: `azureADOnlyAuthentication: true`)
  - 스키마 오류 → API version/속성 수정
  - 파라미터 오류 → 파라미터 파일 수정

**Step 2-B: What-if 실행**

validate 통과 후 what-if를 실행한다.

**파라미터 전달 방식 선택:**
- `@secure()` 파라미터가 모두 기본값을 가지고 있으면 → `.bicepparam` 사용
- `@secure()` 파라미터에 사용자 입력이 필요하면 → `--template-file` + JSON 파라미터 파일 사용

```powershell
# 방법 1: .bicepparam 사용 (@secure() 파라미터가 모두 기본값인 경우)
az deployment group what-if `
  --resource-group "<RG_NAME>" `
  --parameters main.bicepparam

# 방법 2: JSON 파라미터 파일 사용 (@secure() 파라미터에 사용자 입력이 필요한 경우)
az deployment group what-if `
  --resource-group "<RG_NAME>" `
  --template-file main.bicep `
  --parameters main.parameters.json `
  --parameters secureParam='값'
```
→ What-if 결과를 요약해서 사용자에게 보여준다.

**⏱️ What-if 실행 방법 및 타임아웃 처리:**

What-if는 Azure 서버 측에서 리소스 검증을 수행하므로, 서비스/리전에 따라 시간이 걸릴 수 있다.
**반드시 `initial_wait: 300` (5분)으로 실행한다.** 5분 안에 완료되지 않으면 자동으로 타임아웃된다.

```powershell
# powershell 도구 호출 시 반드시 initial_wait: 300 설정
# mode: "sync", initial_wait: 300
az deployment group what-if `
  --resource-group "<RG_NAME>" `
  --parameters main.bicepparam
```

**5분 내 완료** → 정상 진행 (결과 요약 → 프리뷰 다이어그램 → 배포 확인)

**5분 내 미완료 (타임아웃)** → 즉시 `stop_powershell`로 중지하고 사용자에게 선택지 제공:

```
ask_user({
  question: "What-if 검증이 5분 내에 완료되지 않았습니다. Azure 서버 응답이 지연되고 있습니다. 어떻게 할까요?",
  choices: [
    "다시 시도 (Recommended)",
    "What-if 건너뛰고 바로 배포"
  ]
})
```

**"다시 시도" 선택 시:** 동일한 명령을 `initial_wait: 300`으로 재실행한다. 최대 2회까지 재시도.
**"What-if 건너뛰고 바로 배포" 선택 시:**
- 프리뷰 다이어그램은 Phase 1 초안 기반으로 생성한다
- 사용자에게 리스크를 안내한다:
  > **⚠️ What-if 검증 없이 배포합니다.** 예상치 못한 리소스 변경이 발생할 수 있습니다. 배포 후 Azure Portal에서 반드시 확인해주세요.

**절대 하지 말 것:**
- `initial_wait`을 설정하지 않고 실행하여 끝없이 대기하는 것
- 에이전트가 임의로 "what-if는 선택 단계"라고 판단하여 건너뛰는 것
- 타임아웃 시 사용자에게 묻지 않고 자동으로 배포로 전환하는 것
- "배포가 더 빠릅니다" 같은 이유로 what-if를 스킵하는 것

### 단계 3: What-if 결과 기반 프리뷰 다이어그램 — 🚨 필수

**이 단계를 건너뛰면 안 된다. What-if가 성공하면 반드시 프리뷰 다이어그램을 생성한다.**

What-if 결과에서 실제 배포 예정 리소스 목록(리소스명, 타입, 위치, 수량)으로 다이어그램을 재생성한다.
Phase 1에서 그린 초안(`01_arch_diagram_draft.html`)은 그대로 두고, 프리뷰를 `02_arch_diagram_preview.html`로 생성한다.
초안은 언제든 다시 열어볼 수 있다.

```
## 배포 예정 아키텍처 (What-if 기반)

[인터랙티브 다이어그램 링크 — 02_arch_diagram_preview.html]
(설계 초안: 01_arch_diagram_draft.html)

생성될 리소스 (N개):
[What-if 결과 요약 테이블]

이 리소스들을 배포할까요? (예/아니오)
```

사용자가 확인하면 단계 4로 진행한다. **프리뷰 다이어그램 없이 배포로 넘어가지 않는다.**

### 단계 4: 실제 배포

사용자가 프리뷰 다이어그램과 What-if 결과를 확인하고 배포를 승인한 경우에만 실행한다.
**What-if에서 사용한 것과 동일한 파라미터 전달 방식을 사용한다.**

```powershell
$deployName = "deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# 방법 1: .bicepparam 사용
az deployment group create `
  --resource-group "<RG_NAME>" `
  --parameters main.bicepparam `
  --name $deployName `
  2>&1 | Tee-Object -FilePath deployment.log

# 방법 2: JSON 파라미터 파일 사용
az deployment group create `
  --resource-group "<RG_NAME>" `
  --template-file main.bicep `
  --parameters main.parameters.json `
  --name $deployName `
  2>&1 | Tee-Object -FilePath deployment.log
```

배포 중 진행 상황을 주기적으로 모니터링:
```powershell
az deployment group show `
  --resource-group "<RG_NAME>" `
  --name "<DEPLOYMENT_NAME>" `
  --query "{status:properties.provisioningState, duration:properties.duration}" `
  -o table
```

### 배포 실패 시 처리

배포가 실패하면 일부 리소스가 'Failed' 상태로 남을 수 있다. 이 상태에서 재배포하면 `AccountIsNotSucceeded` 같은 에러가 발생한다.

**⚠️ 리소스 삭제는 파괴적 명령이다. 반드시 사용자에게 상황을 설명하고 승인을 받은 후 실행한다.**

```
배포 중 [리소스명]이 실패했습니다.
재배포하려면 실패한 리소스를 먼저 삭제해야 합니다.

삭제 후 재배포할까요? (예/아니오)
```

사용자가 승인하면 실패한 리소스를 삭제하고 재배포한다.

**🔹 Soft-deleted 리소스 처리 (재배포 차단 방지):**

배포 실패 후 리소스 그룹을 삭제하면, Cognitive Services(Foundry), Key Vault 등은 **soft-delete 상태**로 남는다.
같은 이름으로 재배포하면 `FlagMustBeSetForRestore`, `Conflict` 에러가 발생한다.

**재배포 전 반드시 확인:**
```powershell
# Soft-deleted Cognitive Services 확인
az cognitiveservices account list-deleted -o table

# Soft-deleted Key Vault 확인
az keyvault list-deleted -o table
```

**처리 방법 (사용자에게 선택지 제공):**
```
ask_user({
  question: "이전 배포에서 soft-deleted 리소스가 발견되었습니다. 어떻게 처리할까요?",
  choices: [
    "purge 후 재배포 (Recommended) - 깨끗하게 삭제 후 새로 생성",
    "restore 모드로 재배포 - 기존 리소스 복구"
  ]
})
```

**주의 — `enablePurgeProtection: true`인 Key Vault:**
- purge 불가 (보존 기간 만료까지 대기 필요)
- 같은 이름으로 재생성 불가
- **해결: Key Vault 이름을 변경**하여 재배포 (예: `uniqueString()` 시드에 타임스탬프 추가)
- 사용자에게 상황을 설명하고 이름 변경을 안내한다

### 단계 5: 배포 완료 — 실제 리소스 기반 다이어그램 생성 및 보고

배포가 완료되면 실제 배포된 리소스를 조회하여 최종 아키텍처 다이어그램을 생성한다.

**Step 1: 배포된 리소스 조회**
```powershell
az resource list --resource-group "<RG_NAME>" --output json
```

**Step 2: 실제 리소스 기반 다이어그램 생성**

조회 결과에서 리소스명, 타입, SKU, 엔드포인트를 추출하여 `generate_html_diagram.py`로 최종 다이어그램을 생성한다.
이전 다이어그램을 덮어쓰지 않도록 파일명에 주의한다:
- `01_arch_diagram_draft.html` — 설계 초안 (유지)
- `02_arch_diagram_preview.html` — What-if 프리뷰 (유지)
- `03_arch_diagram_result.html` — 배포 결과 최종본

다이어그램의 services JSON은 실제 배포된 리소스 정보로 채운다:
- `name`: 실제 리소스 이름 (예: `foundry-duru57kxgqzxs`)
- `sku`: 실제 SKU
- `details`: 엔드포인트, 위치 등 실제 값

**Step 3: 보고**
```
## 배포 완료!

[인터랙티브 아키텍처 다이어그램 — 03_arch_diagram_result.html]
(설계 초안: 01_arch_diagram_draft.html | What-if 프리뷰: 02_arch_diagram_preview.html)

생성된 리소스 (N개):
[실제 배포 결과에서 리소스명, 타입, 엔드포인트를 동적으로 추출하여 나열]

## 다음 단계
1. Azure Portal에서 리소스 확인
2. Private Endpoint 연결 상태 확인
3. 필요 시 추가 구성 안내

## 정리 명령어 (필요 시)
az group delete --name <RG_NAME> --yes --no-wait
```

---

### 배포 완료 후 아키텍처 변경 요청 처리

**배포가 완료된 상태에서 사용자가 리소스 추가/변경/삭제를 요청하면, Bicep/배포로 바로 가지 않는다.**
반드시 Phase 1로 돌아가 아키텍처를 먼저 업데이트한다.

**프로세스:**

1. **사용자 의도 확인** — 기존 배포된 아키텍처에 추가하는 것인지 먼저 묻는다:
   ```
   현재 배포된 아키텍처에 VM을 추가하시겠습니까?
   기존 구성: [배포된 서비스 요약]
   ```

2. **Phase 1 복귀 — Delta Confirmation Rule 적용**
   - 기존 배포 결과(`03_arch_diagram_result.html`)를 현재 상태 기준선으로 사용
   - 새 서비스의 required fields 확인 (SKU, 네트워킹, region 가용성 등)
   - ask_user로 미확정 항목 확인
   - 팩트 체크 (MS Docs fetch + 교차 검증)

3. **업데이트된 아키텍처 다이어그램 생성**
   - 기존 배포 리소스 + 새 리소스를 합쳐서 `04_arch_diagram_update_draft.html` 생성
   - 사용자에게 보여주고 확정 받기:
   ```
   ## 업데이트된 아키텍처

   [인터랙티브 다이어그램 — 04_arch_diagram_update_draft.html]
   (이전 배포 결과: 03_arch_diagram_result.html)

   **변경 사항:**
   - 추가: [새 서비스 목록]
   - 제거: [제거된 서비스 목록] (있을 경우)

   이 구성으로 진행할까요?
   ```

4. **확정 후 Phase 2 → 3 → 4 순서대로 진행**
   - 기존 Bicep에 incremental로 새 리소스 모듈 추가
   - 리뷰 → What-if → 배포 (incremental deployment)

**절대 하지 말 것:**
- 배포 완료 후 변경 요청에 아키텍처 다이어그램 업데이트 없이 바로 Bicep 생성으로 넘어가는 것
- 기존 배포 상태를 무시하고 새 리소스만 단독으로 만드는 것
- 사용자에게 "기존 아키텍처에 추가할지" 확인하지 않고 진행하는 것

---

## 빠른 참조

### 기본값

- **위치**: Phase 1에서 사용자와 확정. 서비스별 지역 가용성은 MS Docs에서 반드시 확인
- **네트워킹**: Private Endpoint 기본 적용
- **VNet CIDR**: 파라미터로 사용자에게 확인 (고객 환경 기존 주소공간 충돌 방지). 기본 제안: `10.0.0.0/16`, pe-subnet: `10.0.1.0/24`

### 참조 파일 (Stable vs Dynamic 분리 구조)

| 파일 | 역할 | 정보 성격 |
|------|------|----------|
| `references/azure-common-patterns.md` | PE/보안/명명 등 공통 패턴 | Stable |
| `references/azure-dynamic-sources.md` | MS Docs URL 레지스트리 (값 아닌 출처만) | Dynamic source |
| `references/architecture-guidance-sources.md` | 공식 아키텍처 가이던스 source registry (설계 방향 판단용) | Source registry |
| `references/service-gotchas.md` | 비직관적 필수 속성, 흔한 실수, PE 매핑 | Stable |
| `references/domain-packs/ai-data.md` | AI/Data 서비스 구성 가이드 (v1 도메인) | Stable + Decision Rules |
| `prompts/bicep-generator.md` | Bicep 생성 규칙 + Fallback workflow | |
| `prompts/bicep-reviewer.md` | 코드 리뷰 체크리스트 + 하드코딩 감지 | |

> **원칙**: Stable 정보는 reference 우선 참조. Dynamic 정보(API version, SKU, region, 모델)는 항상 MS Docs fetch.
