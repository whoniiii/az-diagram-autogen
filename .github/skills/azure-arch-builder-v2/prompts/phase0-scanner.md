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

### 1-B: 구독 선택

```powershell
az account list --output json
```

구독 목록에서 최대 4개를 `ask_user` 선택지로 제공.
사용자가 선택하면 `az account set --subscription "<ID>"` 실행.

### 1-C: 스캔 범위 선택

```
ask_user({
  question: "어떤 범위의 Azure 리소스를 분석할까요?",
  choices: [
    "특정 리소스 그룹 지정 (Recommended)",
    "현재 구독의 모든 리소스 그룹",
    "여러 리소스 그룹 선택"
  ]
})
```

- **특정 RG** → RG 목록에서 선택 또는 직접 입력
- **전체 구독** → `az group list` → 전체 RG 스캔 (리소스 많으면 시간 소요 경고)
- **여러 RG** → 순차적으로 ask_user (또는 쉼표 구분 입력)

---

## Step 2: 리소스 스캔

### 2-A: 리소스 목록 조회

```powershell
# 선택된 RG의 모든 리소스 조회
az resource list --resource-group "<RG_NAME>" --output json
```

여러 RG를 스캔하는 경우 각 RG별로 실행하고 결과를 합친다.

### 2-B: 리소스 타입별 상세 조회

기본 목록에서 각 리소스의 상세 정보(SKU, 네트워킹, 속성)를 조회한다.
**모든 리소스 타입에 대해 `az resource show`를 사용하되, 주요 서비스는 전용 명령으로 더 상세한 정보를 가져온다:**

```powershell
# 범용 — 모든 리소스에 사용 가능
az resource show --ids "<RESOURCE_ID>" --output json

# 주요 서비스별 전용 명령 (더 상세한 정보)
az cognitiveservices account show --name "<NAME>" -g "<RG>" -o json
az search service show --name "<NAME>" -g "<RG>" -o json
az storage account show --name "<NAME>" -g "<RG>" -o json
az keyvault show --name "<NAME>" -g "<RG>" -o json
az network vnet show --name "<NAME>" -g "<RG>" -o json
az vm show --name "<NAME>" -g "<RG>" -o json
az sql server show --name "<NAME>" -g "<RG>" -o json
az databricks workspace show --name "<NAME>" -g "<RG>" -o json
```

### 2-C: Private Endpoint 조회

```powershell
az network private-endpoint list --resource-group "<RG_NAME>" --output json
```

PE 목록에서 각 PE의:
- `privateLinkServiceConnections[0].privateLinkServiceId` → 연결된 서비스
- `subnet.id` → 소속 VNet/Subnet
- `privateLinkServiceConnections[0].groupIds` → groupId (account, searchService, blob 등)

### 2-D: VNet/Subnet 조회

```powershell
az network vnet list --resource-group "<RG_NAME>" --output json
```

VNet에서:
- `addressSpace.addressPrefixes` → CIDR
- `subnets[].name`, `subnets[].addressPrefix` → 서브넷 정보
- `subnets[].privateEndpointNetworkPolicies` → PE 정책

---

## Step 3: 리소스 간 관계 추론

스캔한 리소스들의 **관계(connections)**를 자동으로 추론하여 다이어그램의 connections JSON을 구성한다.

### 관계 추론 규칙

| 관계 유형 | 추론 방법 | connection type |
|---|---|---|
| PE → 서비스 | PE의 `privateLinkServiceId`에서 서비스 ID 추출 | `private` |
| PE → VNet | PE의 `subnet.id`에서 VNet 추출 | (VNet 경계선으로 표현) |
| Foundry → Project | `Microsoft.CognitiveServices/accounts/projects`의 부모 | `api` |
| Foundry → 모델 배포 | `accounts/deployments` 조회 | (details에 포함) |
| AI Search → Storage | AI Search의 data source 설정 (있을 경우) | `data` |
| 서비스 → Key Vault | 같은 RG 내 Key Vault가 있으면 secrets 관리 추론 | `security` |
| Databricks → VNet | Databricks의 `vnetAddressPrefix` 확인 (VNet injection) | (VNet 경계선) |

### 모델 배포 조회 (Foundry 리소스가 있는 경우)

```powershell
az cognitiveservices account deployment list --name "<FOUNDRY_NAME>" -g "<RG>" -o json
```

각 deployment의 모델명, 버전, SKU를 Foundry 노드의 details에 추가.

### 추론 불가능한 관계

모든 관계를 자동 추론할 수는 없다. 추론되지 않는 연결은 사용자에게 묻는다:
```
ask_user({
  question: "이 서비스들 간의 관계를 알려주세요. 어떤 서비스가 어떤 서비스를 사용하나요?",
  allow_freeform: true
})
```

---

## Step 4: services/connections JSON 변환

스캔 결과를 `generate_html_diagram.py`의 입력 형식으로 변환한다.

### 리소스 타입 → 다이어그램 type 매핑

| Azure 리소스 타입 | 다이어그램 type |
|---|---|
| `Microsoft.CognitiveServices/accounts` (kind: AIServices) | `ai_foundry` |
| `Microsoft.CognitiveServices/accounts` (kind: OpenAI) | `openai` |
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
