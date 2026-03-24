# Phase 4: 배포 에이전트

이 파일은 Phase 4의 상세 지침이다. Phase 3(코드 리뷰) 완료 후 사용자가 배포를 승인하면 이 파일을 읽고 따른다.

---

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

조회 결과에서 리소스명, 타입, SKU, 엔드포인트를 추출하여 내장 `az_diagram_autogen` 모듈로 최종 다이어그램을 생성한다.
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
