# Phase 1: 아키텍처 어드바이저

이 파일은 Phase 1의 상세 지침이다. SKILL.md에서 Phase 1로 진입하면 이 파일을 읽고 따른다.
Path A(신규 설계) 또는 Path B(Phase 0 스캔 후 수정)에서 모두 사용된다.

---

## Path B에서 진입한 경우 (기존 리소스 분석 후)

Phase 0에서 스캔한 현재 아키텍처 다이어그램(00_arch_current.html)이 이미 있다.
이 경우 1-1의 프로젝트 이름/서비스 목록 확인을 건너뛰고, 바로 수정 대화로 진입한다:

1. "여기서 뭘 바꾸고 싶으세요?" — 사용자 자연어 요청
2. Delta Confirmation Rule 적용 — 변경 사항의 미확정 필수 항목 확인
3. 팩트 체크 — MS Docs 교차 검증
4. 업데이트된 다이어그램 생성 (01_arch_diagram_draft.html)
5. 확정 후 Phase 2로 진행

---

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

**🚨🚨🚨 [HARD GATE] 스펙 수집 완료 → 다이어그램 생성 필수 🚨🚨🚨**

**모든 확정 항목이 채워진 직후, 아래를 반드시 수행한다. 이 단계를 건너뛰면 Phase 1은 미완료다.**

1. 확정된 서비스 목록을 기반으로 **services JSON + connections JSON**을 구성한다
2. 내장 `az_diagram_autogen` 모듈을 사용하여 **`<project-name>/01_arch_diagram_draft.html`** 을 생성한다
3. `Start-Process`로 브라우저에서 자동으로 연다
4. 아래 **보고 형식**으로 사용자에게 다이어그램을 보여준다
5. 사용자가 다이어그램을 확인하고 **수정 요청이 없을 때만** Phase 2 전환을 묻는다

**절대 하지 말 것:**
- ❌ 다이어그램을 생성하지 않고 "아키텍처가 확정되었습니다. 다음 단계로 진행할까요?"를 묻는 것
- ❌ 다이어그램 생성을 Phase 2 이후로 미루는 것
- ❌ "다이어그램은 나중에 만들겠습니다"라고 말하는 것
- ❌ 스펙 수집 완료만으로 "아키텍처 확정"이라고 판단하는 것

**검증 조건**: `01_arch_diagram_draft.html` 파일이 생성되지 않은 상태에서 Phase 2 진입은 불가하다.

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

스킬에 내장된 **`az_diagram_autogen`** 모듈을 사용하여 인터랙티브 HTML 다이어그램을 만든다.
`pip install` 없이 스킬 폴더 내의 모듈을 직접 import하므로, 네트워크 연결이나 패키지 설치가 불필요하다.
605+ Azure 공식 아이콘이 내장되어 있다.

**다이어그램 파일명 규칙:**

모든 다이어그램은 Bicep 프로젝트 폴더(`<project-name>/`) 안에 생성한다.
각 단계별로 번호를 붙여 체계적으로 관리하며, 이전 단계 파일은 덮어쓰지 않는다.

| 단계 | 파일명 | 생성 시점 |
|------|--------|-----------|
| Phase 1 설계 초안 | `01_arch_diagram_draft.html` | 아키텍처 설계 확정 시 |
| Phase 4 What-if 프리뷰 | `02_arch_diagram_preview.html` | What-if 검증 후 |
| Phase 4 배포 결과 | `03_arch_diagram_result.html` | 실제 배포 완료 후 |

**내장 모듈 경로 탐색 + Python 경로 탐색:**

**🚨 Python 경로 + 내장 모듈 경로는 Phase 1 프리로드에서 1회 확인하고, 이후 모든 다이어그램 생성에서 재사용한다. 매번 재탐색하지 않는다.**

```powershell
# ─── Step 1: Python 경로 탐색 ───
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

# ─── Step 2: 내장 모듈 경로 탐색 (pip install 불필요) ───
# 1순위: 프로젝트 로컬 스킬 폴더
$SkillDir = Get-ChildItem -Path ".github\skills\az-autopilot-agent-core" -Filter "__init__.py" -Recurse -ErrorAction SilentlyContinue |
  Where-Object { $_.Directory.Name -eq 'az_diagram_autogen' } |
  Select-Object -First 1 -ExpandProperty DirectoryName |
  Split-Path -Parent
# 2순위: 글로벌 스킬 폴더
if (-not $SkillDir) {
  $SkillDir = Get-ChildItem -Path "$env:USERPROFILE\.copilot\skills\az-autopilot-agent-core" -Filter "__init__.py" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Directory.Name -eq 'az_diagram_autogen' } |
    Select-Object -First 1 -ExpandProperty DirectoryName |
    Split-Path -Parent
}

# ─── Step 3: 다이어그램 생성 (CLI 방식 — PYTHONPATH에 스킬 폴더 추가) ───
$OutputFile = "<project-name>\01_arch_diagram_draft.html"
$env:PYTHONPATH = $SkillDir

& $PythonCmd -m az_diagram_autogen `
  --services '<services_JSON>' `
  --connections '<connections_JSON>' `
  --title "아키텍처 제목" `
  --vnet-info "10.0.0.0/16 | pe-subnet: 10.0.1.0/24" `
  --output $OutputFile

# 생성 후 자동으로 브라우저에서 열기
Start-Process $OutputFile
```

**Python API 방식도 사용 가능 (대안):**

JSON이 매우 큰 경우 CLI 인자 길이 제한을 피하기 위해 Python API를 직접 호출할 수 있다.
`sys.path`에 스킬 폴더를 추가하여 내장 모듈을 import한다:

```python
import sys, os
# 스킬 폴더를 Python path에 추가 (pip install 없이 내장 모듈 사용)
skill_dir = r"<스킬 폴더 절대경로>"  # Step 2에서 찾은 $SkillDir 값
sys.path.insert(0, skill_dir)

from az_diagram_autogen import generate_diagram

services = [...]   # services JSON
connections = [...] # connections JSON

html = generate_diagram(
    services=services,
    connections=connections,
    title="아키텍처 제목",
    vnet_info="10.0.0.0/16 | pe-subnet: 10.0.1.0/24",
    hierarchy=None  # 복수 구독/RG일 때만 사용
)

with open("<project-name>/01_arch_diagram_draft.html", "w", encoding="utf-8") as f:
    f.write(html)
```

**🔹 CLI vs Python API 선택 기준:**

| 상황 | 방법 | 이유 |
|------|------|------|
| 서비스 10개 이하 | CLI (`PYTHONPATH=$SkillDir python -m az_diagram_autogen`) | 간단하고 빠름 |
| 서비스 10개 초과 또는 hierarchy 사용 | Python API (sys.path 추가) | CLI 인자 길이 제한 회피 |
| 복수 구독/RG 다이어그램 | Python API + `hierarchy` 파라미터 | 계층 구조 표현 |

**지원되는 서비스 타입 전체 목록:**

스킬 내장 REFERENCE.md에서 확인 가능: `az_diagram_autogen/REFERENCE.md`
또는 CLI: `$env:PYTHONPATH = $SkillDir; & $PythonCmd -m az_diagram_autogen --reference`

> **다이어그램 생성 순서**: (1) Python 경로 확인 → (2) 내장 모듈 경로 확인 → (3) services/connections JSON 구성 → (4) 실행. Python이 없으면 JSON 구성 전에 사용자에게 설치를 안내한다. JSON을 다 만들고 Python이 없어서 실패하는 낭비를 방지한다.

> **🚨 다이어그램 자동 오픈 (예외 없음)**: 내장 `az_diagram_autogen`으로 HTML 파일을 생성하면 **어떤 상황이든 반드시** 브라우저에서 자동으로 연다. 이유를 불문하고, 다이어그램이 (재)생성되면 무조건 `Start-Process` 명령을 실행한다. 다이어그램 생성과 브라우저 오픈은 항상 하나의 PowerShell 명령 블록 안에서 함께 실행한다.
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

사용 가능한 type 값: `ai_foundry`, `ai_hub`, `openai`, `search`, `ai_search`, `storage`, `adls`, `keyvault`, `kv`, `fabric`, `vm`, `bastion`, `vpn`, `vpn_gateway`, `adf`, `data_factory`, `pe`, `databricks`, `sql_server`, `sql_database`, `cosmos_db`, `app_service`, `appservice`, `app`, `aks`, `function_app`, `synapse`, `log_analytics`, `app_insights`, `appinsights`, `monitor`, `nsg`, `acr`, `container_registry`, `document_intelligence`, `form_recognizer`, `cdn`, `event_hub`, `redis`, `devops`, `app_gateway`, `iot_hub`, `stream_analytics`, `front_door`, `firewall`, `jumpbox`, `user` 등 (`python -m az_diagram_autogen --reference`로 전체 목록 확인. 목록에 없는 type은 fuzzy matching으로 시도 후 default 아이콘으로 표시)

**Private Endpoint 사용 시 — PE 노드 추가 필수:**

Private Endpoint가 포함된 아키텍처라면, 각 서비스마다 PE 노드를 services JSON에 반드시 추가하고 connections에도 연결을 넣어야 다이어그램에 표시된다.

```json
// 각 서비스에 대응하는 PE 노드 추가
{"id": "pe_서비스ID", "name": "PE: 서비스명", "type": "pe", "details": ["groupId: 해당그룹ID"]}

// connections에 서비스 → PE 연결 추가
{"from": "서비스ID", "to": "pe_서비스ID", "label": "", "type": "private"}
```

**🚨🚨🚨 PE 연결과 비즈니스 로직 연결은 별개다 — 둘 다 반드시 포함해야 한다 🚨🚨🚨**

PE 연결(`"type": "private"`)은 네트워크 격리를 표현한다. 하지만 이것만으로는 서비스 간 **실제 데이터 흐름/API 호출**이 다이어그램에 보이지 않는다.

**반드시 두 종류의 연결을 모두 포함한다:**

1. **비즈니스 로직 연결** — 서비스 간 실제 데이터 흐름 (api, data, security 타입)
2. **PE 연결** — 서비스 ↔ PE 간 네트워크 격리 (private 타입)

```json
// ✅ 올바른 예시 — Function App → Foundry
// 1) 비즈니스 로직: Function App이 Foundry를 호출하여 채팅/임베딩 수행
{"from": "func_app", "to": "foundry", "label": "RAG 채팅 + 임베딩", "type": "api"}
// 2) PE 연결: Foundry의 Private Endpoint
{"from": "foundry", "to": "pe_foundry", "label": "", "type": "private"}

// ❌ 잘못된 예시 — PE 연결만 있고 비즈니스 로직 연결이 없음
{"from": "foundry", "to": "pe_foundry", "label": "", "type": "private"}
// → 다이어그램에서 Function App과 Foundry 사이에 연결선이 없어 아키텍처 흐름이 보이지 않음
```

**절대 하지 말 것:**
- PE 연결만 만들고 비즈니스 로직 연결을 생략하는 것
- 비즈니스 로직 연결의 `from`/`to`를 PE 노드로 연결하는 것 (PE가 아닌 **실제 서비스 ID**를 사용)
- "PE가 있으니 연결선이 보일 것"이라고 가정하는 것

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

**🚨 Phase 2 전환 전제 조건 — 아래 모두 충족해야만 이 질문을 할 수 있다:**

1. `01_arch_diagram_draft.html`이 내장 `az_diagram_autogen` 모듈로 **생성 완료**됨
2. 다이어그램이 **브라우저에서 열리고** 보고 형식으로 **사용자에게 표시**됨
3. 사용자가 다이어그램을 확인하고 **수정 요청이 없거나**, 수정 반영 후 **최종 확정**됨

**위 조건이 하나라도 미충족이면 Phase 2로 넘어가지 않는다.**
다이어그램이 아직 없으면 **지금 즉시 생성한다** — 섹션 1-2의 절차를 따른다.

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

## 🚨 Phase 1 완료 체크리스트 — Phase 2 진입 전 필수 확인

Phase 1을 떠나기 전 아래 항목을 **모두** 확인한다. 하나라도 미완료면 Phase 2로 넘어가지 않는다.

| # | 항목 | 검증 방법 |
|---|------|----------|
| 1 | 모든 필수 스펙 확정 | 프로젝트명, 서비스, SKU, 리전, 네트워크 방식이 모두 확정됨 |
| 2 | 팩트 체크 완료 | MS Docs 교차 검증이 수행됨 |
| 3 | **다이어그램 생성됨** | 내장 `az_diagram_autogen` 모듈로 `01_arch_diagram_draft.html` 파일이 생성됨 |
| 4 | **사용자가 다이어그램 확인** | 브라우저 자동 오픈 + 보고 형식으로 표시 완료 |
| 5 | 사용자 최종 승인 | 다이어그램 확인 후 "다음 단계로 진행" 선택 |

**⚠️ 3, 4번이 미완료 상태에서 5번을 묻지 않는다.** 다이어그램이 없는데 "진행할까요?"를 물으면 사용자는 뭘 확정했는지 시각적으로 확인할 수 없다.

---

## Phase 2 연결: Bicep 생성 에이전트

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

## Phase 3 연결: Bicep 리뷰 에이전트

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
