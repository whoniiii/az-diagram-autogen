---
name: azure-arch-builder-v2
description: >
  Azure 인프라를 자연어로 설계하거나, 기존 Azure 리소스를 분석하여
  아키텍처 다이어그램을 자동 생성하고, 대화로 수정한 뒤 Bicep 배포까지 진행한다.

  반드시 이 스킬을 사용해야 하는 경우:
  - "Azure에 X 만들어줘", "RAG 아키텍처 구성해줘" (신규 설계)
  - "현재 Azure 인프라 분석해줘", "rg-xxx 리소스 다이어그램 그려줘" (기존 분석)
  - "Foundry가 느려", "비용 줄이고 싶어", "보안 강화해줘" (자연어 수정)
  - Azure 리소스 배포, Bicep 템플릿 생성, IaC 코드 생성
  - Microsoft Foundry, AI Search, OpenAI, Fabric, ADLS Gen2, Databricks 등 모든 Azure 서비스
---

# Azure Architecture Builder v2

자연어로 Azure 인프라를 설계하거나, 기존 리소스를 분석하여 아키텍처를 시각화하고 수정·배포까지 이어주는 파이프라인.

## 사용자 언어 자동 감지

**🚨 사용자의 첫 메시지 언어를 감지하여, 이후 모든 응답을 해당 언어로 제공한다. 이것은 최우선 원칙이다.**

- 사용자가 한국어로 요청하면 → 한국어로 응답
- 사용자가 영어로 요청하면 → **영어로 응답** (ask_user, 진행 안내, 보고서, Bicep 주석 모두 영어)
- 이 문서의 지침과 예시는 한국어로 작성되어 있지만, **사용자에게 보이는 모든 출력은 사용자의 언어에 맞춘다**

**⚠️ 이 문서의 한국어 예시를 그대로 사용자에게 보여주지 않는다.**
구조만 참고하고, 텍스트는 사용자 언어로 번역하여 사용한다.

## 도구 사용 안내 (GHCP 환경)

| 기능 | 도구명 | 참고 |
|------|--------|------|
| URL 내용 가져오기 | `web_fetch` | MS Docs 조회 등 |
| 웹 검색 | `web_search` | URL 탐색 |
| 사용자 질문 | `ask_user` | `choices`는 반드시 문자열 배열 |
| 서브에이전트 | `task` | explore/task/general-purpose |
| 셸 명령 실행 | `powershell` | Windows PowerShell |

> 모든 서브에이전트(explore/task/general-purpose)는 `web_fetch`와 `web_search`를 사용할 수 없다.
> MS Docs 조회가 필요한 팩트 체크는 **메인 에이전트가 직접** 수행한다.

## 외부 도구 경로 탐색

`az`, `python`, `bicep` 등은 PATH에 없는 경우가 흔하다.
**Phase 시작 전 1회 탐색하고 캐시한다. 매번 재탐색하지 않는다.**

> **⚠️ `Get-Command python`은 사용하지 않는다** — Windows Store alias 위험.
> 파일 시스템 직접 탐색(`$env:LOCALAPPDATA\Programs\Python`)을 1순위로 한다.

az CLI 경로:
```powershell
$azCmd = $null
if (Get-Command az -ErrorAction SilentlyContinue) { $azCmd = 'az' }
if (-not $azCmd) {
  $azExe = Get-ChildItem -Path "$env:ProgramFiles\Microsoft SDKs\Azure\CLI2\wbin", "$env:LOCALAPPDATA\Programs\Azure CLI\wbin" -Filter "az.cmd" -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
  if ($azExe) { $azCmd = $azExe }
}
```

Python 경로: `prompts/phase1-advisor.md`의 다이어그램 생성 섹션 참조.

## 진행 상황 안내 필수

블록인용 + 이모지 + 볼드 형식:
```markdown
> **⏳ [동작]** — [이유]
> **✅ [완료]** — [결과]
> **⚠️ [경고]** — [내용]
> **❌ [실패]** — [원인]
```

## 병렬 프리로드 원칙

`ask_user`로 사용자 입력을 기다리는 동안, 다음 단계에서 필요한 정보를 병렬로 미리 로딩한다.

| ask_user 질문 | 동시에 프리로드할 것 |
|---|---|
| 프로젝트 이름 / 스캔 범위 | reference 파일, MS Docs, Python 경로 탐색 |
| 모델/SKU 선택 | 다음 질문 선택지용 MS Docs |
| 아키텍처 확정 | `az account show/list`, `az group list` |
| 구독 선택 | `az group list` |

---

## Path 분기 — 사용자 요청에 따라 자동 판별

### Path A: 신규 설계 (New Build)

**트리거**: "만들어줘", "구성해줘", "deploy", "create", "build" 등
```
Phase 1 (prompts/phase1-advisor.md) — 대화형 아키텍처 설계 + 다이어그램
    ↓
Phase 2 (prompts/bicep-generator.md) — Bicep 코드 생성
    ↓
Phase 3 (prompts/bicep-reviewer.md) — 코드 리뷰 + 컴파일 검증
    ↓
Phase 4 (prompts/phase4-deployer.md) — validate → what-if → 배포
```

### Path B: 기존 분석 + 수정 (Analyze & Modify)

**트리거**: "분석해줘", "현재 리소스", "analyze", "scan", "다이어그램 그려줘", "인프라 보여줘" 등
```
Phase 0 (prompts/phase0-scanner.md) — 기존 리소스 스캔 + 다이어그램
    ↓
수정 대화 — "여기서 뭘 바꾸고 싶으세요?" (자연어 수정 요청 → 역질문)
    ↓
Phase 1 (prompts/phase1-advisor.md) — 수정 사항 확정 + 다이어그램 업데이트
    ↓
Phase 2~4 — 동일
```

### Path 판별이 모호한 경우

사용자에게 직접 묻는다:
```
ask_user({
  question: "어떤 작업을 하시겠습니까?",
  choices: [
    "새로운 Azure 아키텍처 설계 (Recommended)",
    "기존 Azure 리소스 분석 + 수정"
  ]
})
```

---

## Phase 전환 규칙

- 각 Phase는 해당 `prompts/*.md` 파일의 지침을 읽고 따른다
- Phase 전환 시 사용자에게 반드시 다음 단계를 안내한다
- Phase를 건너뛰지 않는다 (특히 Phase 3 → Phase 4 사이의 what-if)
- 배포 완료 후 수정 요청 → Phase 0가 아닌 Phase 1로 복귀 (Delta Confirmation Rule)

## v1 Scope & Fallback

### 최적화 서비스
Microsoft Foundry, Azure OpenAI, AI Search, ADLS Gen2, Key Vault, Microsoft Fabric, Azure Data Factory, VNet/Private Endpoint, AML/AI Hub

### 기타 Azure 서비스
모두 지원 — MS Docs를 자동 조회하여 동일한 품질 기준으로 생성한다.
**사용자에게 "범위 밖", "best-effort" 같은 불안감을 주는 메시지를 보내지 않는다.**

### Stable vs Dynamic 정보 처리

| 구분 | 처리 방법 | 예시 |
|------|----------|------|
| **Stable** | Reference 파일 우선 참조 | `isHnsEnabled: true`, PE 3종 세트 |
| **Dynamic** | **항상 MS Docs fetch** | API version, 모델 가용성, SKU, region |

## 빠른 참조

| 파일 | 역할 |
|------|------|
| `prompts/phase0-scanner.md` | 기존 리소스 스캔 + 관계 추론 + 다이어그램 |
| `prompts/phase1-advisor.md` | 대화형 아키텍처 설계 + 팩트 체크 |
| `prompts/bicep-generator.md` | Bicep 코드 생성 규칙 |
| `prompts/bicep-reviewer.md` | 코드 리뷰 체크리스트 |
| `prompts/phase4-deployer.md` | validate → what-if → 배포 |
| `references/service-gotchas.md` | 필수 속성, PE 매핑 |
| `references/azure-dynamic-sources.md` | MS Docs URL 레지스트리 |
| `references/azure-common-patterns.md` | PE/보안/명명 패턴 |
| `references/domain-packs/ai-data.md` | AI/Data 서비스 가이드 |
