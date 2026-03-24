# Phase 0: 기존 리소스 스캐너

이 파일은 Phase 0의 상세 지침이다. 사용자가 기존 Azure 리소스 분석을 요청하면(Path B) 이 파일을 읽고 따른다.

스캔 결과를 아키텍처 다이어그램으로 시각화하고, 이후 사용자의 자연어 수정 요청을 Phase 1로 연결한다.

---

## Step 1: Azure 로그인 + 스캔 범위 선택

### 1-A: Azure 로그인 확인

```powershell
az account show 2>&1
```

- 로그인 되어 있으면 → Step 1-B로 이동
- 로그인 안 되어 있으면 → 사용자에게 `az login` 실행 요청

### 1-B: 구독 선택 (복수 선택 가능)

```powershell
az account list --output json
```

구독 목록에서 `ask_user` 선택지로 제공. **복수 구독 선택 가능:**
```
ask_user({
  question: "분석할 Azure 구독을 선택해주세요. (복수 선택 시 하나씩 추가할 수 있습니다)",
  choices: [
    "sub-002 (현재 기본 구독) (Recommended)",
    "sub-001",
    "위 구독 모두 분석"
  ]
})
```

- 단일 구독 선택 → 해당 구독만 스캔
- "모두 분석" 선택 → 전체 구독 스캔
- 사용자가 추가 구독을 원하면 → 다시 ask_user로 추가

### 1-C: 스캔 범위 선택 (복수 RG 선택 가능)

```
ask_user({
  question: "어떤 범위의 Azure 리소스를 분석할까요?",
  choices: [
    "특정 리소스 그룹 지정 (Recommended)",
    "여러 리소스 그룹 선택",
    "현재 구독의 모든 리소스 그룹"
  ]
})
```

- **특정 RG** → RG 목록에서 선택 또는 직접 입력
- **여러 RG** → ask_user를 반복하여 RG를 하나씩 추가. "이제 됐어"라고 하면 종료.
  또는 사용자가 쉼표 구분으로 여러 개 입력 가능 (예: `rg-prod, rg-dev, rg-network`)
- **전체 구독** → `az group list` → 전체 RG 스캔 (리소스 많으면 시간 소요 경고)

**복수 구독 + 복수 RG 조합 가능:**
- 구독 A의 rg-prod + 구독 B의 rg-network → 둘 다 스캔하여 하나의 다이어그램에 표시

---

## 다이어그램 계층 구조 — 복수 구독/RG 표시

**단일 구독 + 단일 RG**: 기존과 동일 (VNet 경계선만)
**복수 RG (같은 구독)**: RG별 점선 경계 표시
**복수 구독**: Subscription > RG 2단계 경계 표시

다이어그램 JSON에 계층 정보를 전달한다:

**services JSON에 `subscription`과 `resourceGroup` 필드 추가:**
```json
{
  "id": "foundry",
  "name": "foundry-xxx",
  "type": "ai_foundry",
  "subscription": "sub-002",
  "resourceGroup": "rg-prod",
  "details": [...]
}
```

**`--hierarchy` 파라미터로 계층 정보 전달:**
```
--hierarchy '[{"subscription":"sub-002","resourceGroups":["rg-prod","rg-dev"]},{"subscription":"sub-001","resourceGroups":["rg-network"]}]'
```

다이어그램 스크립트는 이 정보를 기반으로:
- 복수 RG → 각 RG를 Cluster 점선 경계로 표현 (라벨: RG 이름)
- 복수 구독 → 구독별 큰 경계 안에 RG 경계를 중첩
- VNet 경계는 해당 VNet이 속한 RG 안에 표시

---

## Step 2: 리소스 스캔

**🚨 az CLI 출력 원칙:**
- az CLI 출력은 **항상 파일로 저장** 후 `view`로 읽는다. 터미널에 직접 출력하면 잘릴 수 있다.
- 한 번의 PowerShell 호출에 **az 명령 3개 이하**만 묶는다. 많이 묶으면 타임아웃 발생.
- `--query` JMESPath로 필요한 필드만 추출하여 출력 크기를 줄인다.

```powershell
# ✅ 올바른 방법 — 파일로 저장 후 읽기
az resource list -g "<RG>" --query "[].{name:name,type:type,kind:kind,location:location}" -o json | Set-Content -Path "$outDir\resources.json"

# ❌ 잘못된 방법 — 터미널에 직접 출력 (잘릴 수 있음)
az resource list -g "<RG>" -o json
```

### 2-A: 리소스 목록 조회

```powershell
$outDir = "<session-files>\azure-scan"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

# 1차: 기본 리소스 목록 (이름, 타입, kind, 위치)
az resource list -g "<RG>" --query "[].{name:name,type:type,kind:kind,location:location,id:id}" -o json | Set-Content "$outDir\resources.json"
```

### 2-B: 리소스 타입별 상세 조회

**명령을 2-3개씩 묶어서 실행한다. 한 번에 전부 돌리지 않는다.**

```powershell
# 묶음 1: 네트워크 (VNet, PE, NSG)
az network vnet list -g "<RG>" --query "[].{name:name,addressSpace:addressSpace.addressPrefixes,subnets:subnets[].{name:name,prefix:addressPrefix,pePolicy:privateEndpointNetworkPolicies}}" -o json | Set-Content "$outDir\vnets.json"
az network private-endpoint list -g "<RG>" --query "[].{name:name,subnetId:subnet.id,targetId:privateLinkServiceConnections[0].privateLinkServiceId,groupIds:privateLinkServiceConnections[0].groupIds,state:provisioningState}" -o json | Set-Content "$outDir\pe.json"
az network nsg list -g "<RG>" --query "[].{name:name,location:location,subnets:subnets[].id,nics:networkInterfaces[].id}" -o json | Set-Content "$outDir\nsg.json"

# 묶음 2: AI 서비스
az cognitiveservices account list -g "<RG>" --query "[].{name:name,kind:kind,sku:sku.name,endpoint:properties.endpoint,publicAccess:properties.publicNetworkAccess,location:location}" -o json | Set-Content "$outDir\cognitive.json"
az search service list -g "<RG>" --query "[].{name:name,sku:sku.name,publicAccess:properties.publicNetworkAccess,semanticSearch:properties.semanticSearch,location:location}" -o json 2>$null | Set-Content "$outDir\search.json"

# 묶음 3: 컴퓨트 + 스토리지
az vm list -g "<RG>" --query "[].{name:name,size:hardwareProfile.vmSize,os:storageProfile.osDisk.osType,location:location,nicIds:networkProfile.networkInterfaces[].id}" -o json | Set-Content "$outDir\vms.json"
az storage account list -g "<RG>" --query "[].{name:name,sku:sku.name,kind:kind,hns:properties.isHnsEnabled,publicAccess:properties.publicNetworkAccess,location:location}" -o json | Set-Content "$outDir\storage.json"
az keyvault list -g "<RG>" --query "[].{name:name,location:location}" -o json 2>$null | Set-Content "$outDir\keyvault.json"
```

### 2-C: 모델 배포 조회 (Cognitive Services가 있는 경우)

```powershell
# 각 Cognitive Services 리소스의 모델 배포 조회
az cognitiveservices account deployment list --name "<NAME>" -g "<RG>" --query "[].{name:name,model:properties.model.name,version:properties.model.version,sku:sku.name}" -o json | Set-Content "$outDir\<NAME>-deployments.json"
```

### 2-D: NIC + Public IP 조회 (VM이 있는 경우)

```powershell
az network nic list -g "<RG>" --query "[].{name:name,subnetId:ipConfigurations[0].subnet.id,privateIp:ipConfigurations[0].privateIPAddress,publicIpId:ipConfigurations[0].publicIPAddress.id}" -o json | Set-Content "$outDir\nics.json"
az network public-ip list -g "<RG>" --query "[].{name:name,ip:ipAddress,sku:sku.name}" -o json | Set-Content "$outDir\public-ips.json"
```

VNet에서:
- `addressSpace.addressPrefixes` → CIDR
- `subnets[].name`, `subnets[].addressPrefix` → 서브넷 정보
- `subnets[].privateEndpointNetworkPolicies` → PE 정책

---

## Step 3: 리소스 간 관계 추론

스캔한 리소스들의 **관계(connections)**를 자동으로 추론하여 다이어그램의 connections JSON을 구성한다.

### 관계 추론 규칙

**🚨 연결선이 부족하면 다이어그램이 의미 없다. 최대한 많은 관계를 추론한다.**

#### 확정 추론 (리소스 ID/속성에서 직접 확인 가능)

| 관계 유형 | 추론 방법 | connection type |
|---|---|---|
| PE → 서비스 | PE의 `privateLinkServiceId`에서 서비스 ID 추출 | `private` |
| PE → VNet | PE의 `subnet.id`에서 VNet 추출 | (VNet 경계선으로 표현) |
| Foundry → Project | `accounts/projects`의 부모 리소스 | `api` |
| VM → NIC → Subnet | NIC의 `subnet.id`에서 VNet/Subnet 추론 | (VNet 경계선) |
| NSG → Subnet | NSG의 `subnets[].id`에서 연결된 서브넷 확인 | `network` |
| NSG → NIC | NSG의 `networkInterfaces[].id`에서 연결된 VM 확인 | `network` |
| NIC → Public IP | NIC의 `publicIPAddress.id`에서 PIP 확인 | (details에 포함) |
| Databricks → VNet | workspace의 VNet injection 설정 | (VNet 경계선) |

#### 합리적 추론 (같은 RG 내 서비스 간 일반적 패턴)

| 관계 유형 | 추론 조건 | connection type |
|---|---|---|
| Foundry → AI Search | 같은 RG에 둘 다 있으면 RAG 연결 추론 | `api` (label: "RAG Search") |
| Foundry → Storage | 같은 RG에 둘 다 있으면 데이터 연결 추론 | `data` (label: "Data") |
| AI Search → Storage | 같은 RG에 둘 다 있으면 인덱싱 연결 추론 | `data` (label: "Indexing") |
| 서비스 → Key Vault | 같은 RG에 Key Vault가 있으면 시크릿 관리 추론 | `security` (label: "Secrets") |
| VM → Foundry/Search | 같은 RG에 VM + AI 서비스가 있으면 API 호출 추론 | `api` (label: "API") |
| DI → Foundry | 같은 RG에 Document Intelligence + Foundry가 있으면 OCR/추출 연결 추론 | `api` (label: "OCR/Extract") |
| ADF → Storage | 같은 RG에 ADF + Storage가 있으면 데이터 파이프라인 추론 | `data` (label: "Pipeline") |
| ADF → SQL | 같은 RG에 ADF + SQL이 있으면 데이터 소스 추론 | `data` (label: "Source") |
| Databricks → Storage | 같은 RG에 둘 다 있으면 데이터 레이크 연결 추론 | `data` (label: "Data Lake") |

#### 추론 후 사용자 확인

추론된 연결 목록을 사용자에게 보여주고 확인받는다:
```
> **⏳ 리소스 간 관계를 추론했습니다** — 아래가 맞는지 확인해주세요.

추론된 연결:
- Foundry → AI Search (RAG Search)
- Foundry → Storage (Data)
- VM → Foundry (API 호출)
- Document Intelligence → Foundry (OCR/Extract)

맞나요? 추가하거나 빼고 싶은 연결이 있으면 말씀해주세요.
```

#### 추론 불가능한 관계

위 규칙으로 추론되지 않는 연결이 있을 수 있다. 사용자가 추가 연결을 자유 입력할 수 있다.

### 모델 배포 조회 (Foundry 리소스가 있는 경우)

```powershell
az cognitiveservices account deployment list --name "<FOUNDRY_NAME>" -g "<RG>" --query "[].{name:name,model:properties.model.name,version:properties.model.version,sku:sku.name}" -o json
```

각 deployment의 모델명, 버전, SKU를 Foundry 노드의 details에 추가.

---

## Step 4: services/connections JSON 변환

스캔 결과를 `az-diagram-autogen` 패키지의 입력 형식으로 변환한다.

### 리소스 타입 → 다이어그램 type 매핑

| Azure 리소스 타입 | 다이어그램 type |
|---|---|
| `Microsoft.CognitiveServices/accounts` (kind: AIServices) | `ai_foundry` |
| `Microsoft.CognitiveServices/accounts` (kind: OpenAI) | `openai` |
| `Microsoft.CognitiveServices/accounts` (kind: FormRecognizer) | `document_intelligence` |
| `Microsoft.CognitiveServices/accounts` (kind: TextAnalytics, etc.) | `ai_foundry` (기본) |
| `Microsoft.CognitiveServices/accounts/projects` | `ai_foundry` |
| `Microsoft.Search/searchServices` | `search` |
| `Microsoft.Storage/storageAccounts` | `storage` |
| `Microsoft.KeyVault/vaults` | `keyvault` |
| `Microsoft.Databricks/workspaces` | `databricks` |
| `Microsoft.Sql/servers` | `sql_server` |
| `Microsoft.Sql/servers/databases` | `sql_database` |
| `Microsoft.DocumentDB/databaseAccounts` | `cosmos_db` |
| `Microsoft.Web/sites` | `app_service` |
| `Microsoft.ContainerService/managedClusters` | `aks` |
| `Microsoft.Web/sites` (kind: functionapp) | `function_app` |
| `Microsoft.Synapse/workspaces` | `synapse` |
| `Microsoft.Fabric/capacities` | `fabric` |
| `Microsoft.DataFactory/factories` | `adf` |
| `Microsoft.Compute/virtualMachines` | `vm` |
| `Microsoft.Network/privateEndpoints` | `pe` |
| `Microsoft.Network/virtualNetworks` | (VNet 경계선으로 표현 — services에 넣지 않음) |
| `Microsoft.Network/networkSecurityGroups` | `nsg` |
| `Microsoft.Network/bastionHosts` | `bastion` |
| `Microsoft.OperationalInsights/workspaces` | `log_analytics` |
| `Microsoft.Insights/components` | `app_insights` |
| 기타 | `default` |

### services JSON 구성 규칙

```json
{
  "id": "리소스 이름 (소문자, 특수문자 제거)",
  "name": "실제 리소스 이름",
  "type": "위 매핑 테이블에서 결정",
  "sku": "실제 SKU (있으면)",
  "private": true/false,  // PE가 연결되어 있으면 true
  "details": ["속성1", "속성2", ...]
}
```

**details에 포함할 정보:**
- 엔드포인트 URL
- SKU/티어 상세
- kind (AIServices, OpenAI 등)
- 모델 배포 목록 (Foundry)
- 주요 속성 (isHnsEnabled, semanticSearch 등)
- 리전

### VNet 정보 → `--vnet-info` 파라미터

VNet이 발견되면 `--vnet-info`로 경계선 라벨에 표시:
```
--vnet-info "10.0.0.0/16 | pe-subnet: 10.0.1.0/24 | <region>"
```

### PE 노드 생성

PE가 발견되면 각 PE를 별도 노드로 추가하고, 대응하는 서비스와 `private` 타입으로 연결:
```json
{"id": "pe_<서비스id>", "name": "PE: <서비스명>", "type": "pe", "details": ["groupId: <groupId>", "<상태>"]}
```

---

## Step 5: 다이어그램 생성 + 사용자에게 제시

다이어그램 파일명: `<project-name>/00_arch_current.html`

프로젝트 이름은 스캔한 RG 이름을 기본값으로 사용:
```
ask_user({
  question: "프로젝트 이름을 정해주세요. (스캔 결과 저장 폴더명)",
  choices: ["<RG-이름>", "azure-analysis"]
})
```

다이어그램 생성 후 보고:
```
## 현재 Azure 아키텍처

[인터랙티브 다이어그램 — 00_arch_current.html]

스캔된 리소스 (N개):
[리소스 타입별 요약 테이블]

여기서 무엇을 변경하고 싶으세요?
- 🔧 성능 개선 ("느려", "처리량 늘려줘")
- 💰 비용 최적화 ("비용 줄여", "싸게 해줘")
- 🔒 보안 강화 ("PE 추가", "퍼블릭 접근 막아줘")
- 🌐 네트워크 변경 ("VNet 분리", "Bastion 추가")
- ➕ 리소스 추가/제거 ("VM 추가", "이거 삭제")
- 📊 모니터링 ("로그 설정", "알람 추가")
- 🤔 진단 ("이 아키텍처 괜찮아?", "뭐가 잘못됐어?")
- 또는 아무것도 안 하고 다이어그램만 받기
```

---

## Step 6: 수정 대화 → Phase 1 연결

사용자가 수정을 요청하면 Phase 1 (phase1-advisor.md)로 연결한다.
**Path B 진입점**으로, 기존 스캔 결과를 기준선으로 사용한다.

### 자연어 수정 요청 처리 — 역질문 패턴

사용자의 모호한 요청을 구체화하기 위해 역질문한다:

**🔧 성능**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "느려" / "응답이 오래 걸려" | "어떤 서비스가 느린가요? SKU를 올릴까요, 리전을 바꿀까요?" |
| "처리량을 늘리고 싶어" | "어떤 서비스의 처리량을 늘릴까요? 스케일아웃? DTU/RU 증가?" |
| "AI Search 인덱싱이 느려" | "파티션을 추가할까요? SKU를 S2로 올릴까요?" |

**💰 비용**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "비용 줄이고 싶어" | "어떤 서비스의 비용을 줄일까요? SKU 다운그레이드? 미사용 리소스 정리?" |
| "이거 얼마나 나와?" | MS Docs에서 가격 정보를 조회하여 현재 SKU 기준 예상 비용 안내 |
| "개발 환경이니까 싸게" | "Free/Basic 티어로 전환할까요? 어떤 서비스들을?" |

**🔒 보안**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "보안 강화해줘" | "PE가 없는 서비스에 PE를 추가할까요? RBAC을 확인할까요? publicNetworkAccess를 비활성화할까요?" |
| "퍼블릭 접근 막아줘" | "모든 서비스에 PE + publicNetworkAccess: Disabled를 적용할까요?" |
| "키 관리 해줘" | "Key Vault를 추가하고 Managed Identity로 연결할까요?" |

**🌐 네트워크**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "PE 추가해줘" | "어떤 서비스에? 전체에 일괄 추가할까요?" |
| "VNet 분리해줘" | "어떤 서브넷을 분리할까요? NSG도 추가할까요?" |
| "Bastion 넣어줘" | "VM 접근용 Azure Bastion을 추가합니다. 서브넷 CIDR을 지정해주세요." |

**➕ 리소스 추가/제거**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "VM 추가해줘" | "몇 대? 어떤 SKU? 같은 VNet에? OS는?" |
| "Fabric 추가해줘" | "어떤 SKU? admin 이메일은?" |
| "이거 지워줘" | "정말로 [리소스명]을 제거할까요? 연결된 PE도 함께 제거됩니다." |

**📊 모니터링/운영**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "로그 보고 싶어" | "Log Analytics Workspace를 추가하고 Diagnostic Settings를 연결할까요?" |
| "알람 설정해줘" | "어떤 메트릭에 대한 알람인가요? CPU? 에러율? 응답시간?" |
| "Application Insights 붙여줘" | "어떤 서비스에 연결할까요? App Service? Function App?" |

**🔄 마이그레이션/변경**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "리전 바꿔줘" | "어떤 리전으로? 모든 서비스가 해당 리전에서 사용 가능한지 확인하겠습니다." |
| "SQL을 Cosmos로 바꿔줘" | "Cosmos DB API 타입은? (SQL/MongoDB/Cassandra) 데이터 마이그레이션 가이드도 제공합니다." |
| "Foundry를 Hub로 바꿔줘" | "ML 훈련/오픈소스 모델이 필요한 경우에만 Hub가 적합합니다. 용도를 확인할게요." |

**🤔 진단/질문**

| 사용자 요청 | 역질문 예시 |
|---|---|
| "뭐가 잘못됐어?" | 현재 설정 분석 (publicNetworkAccess 열림, PE 미연결, SKU 부적정 등) 후 개선점 제시 |
| "이 아키텍처 괜찮아?" | Well-Architected Framework 기준으로 리뷰 (보안, 안정성, 성능, 비용, 운영) |
| "PE가 제대로 연결됐어?" | `az network private-endpoint show`로 연결 상태 확인 후 보고 |
| "다이어그램만 줘" | Phase 1로 넘어가지 않고, 00_arch_current.html 경로를 안내하고 종료 |

수정 사항이 확정되면:
1. Phase 1의 Delta Confirmation Rule 적용
2. 팩트 체크 (MS Docs 교차 검증)
3. 업데이트된 다이어그램 생성 (01_arch_diagram_draft.html)
4. 사용자 확정 → Phase 2~4 진행

---

## 스캔 성능 최적화

- 리소스가 50개 이상이면 사용자에게 경고: "리소스가 많아 스캔에 시간이 걸릴 수 있습니다."
- `az resource list`를 먼저 실행하여 리소스 수를 파악한 후, 상세 조회를 진행
- 주요 서비스(Foundry, Search, Storage, KeyVault, VNet, PE)를 우선 조회하고, 나머지는 `az resource show`로 기본 정보만 수집
- 진행 상황을 사용자에게 안내:
  > **⏳ 리소스를 스캔하고 있습니다** — N개 리소스 중 M개 완료

---

## 지원하지 않는 리소스 처리

다이어그램 type 매핑에 없는 리소스 타입은:
- `default` 타입으로 표시 (물음표 아이콘)
- 리소스 이름과 타입을 details에 포함
- 사용자에게 표시는 하되, 관계 추론은 시도하지 않는다
