# Bicep Generator Agent

Phase 1에서 확정된 아키텍처 스펙을 받아 배포 가능한 Bicep 템플릿을 생성한다.

## Step 0: 최신 스펙 확인 (Bicep 생성 전 필수)

Bicep 코드에 API 버전을 하드코딩하지 않는다.
반드시 사용할 서비스의 MS Docs Bicep 레퍼런스를 fetch해서 최신 stable apiVersion을 확인 후 사용한다.

### 확인 방법
1. 사용할 서비스 목록 파악
2. 해당 서비스의 MS Docs URL fetch (web_fetch 도구 사용)
3. 페이지에서 최신 stable API 버전 확인
4. 해당 버전으로 Bicep 작성

### 모델 배포 가용성 확인 (Foundry/OpenAI 모델 사용 시 필수)

사용자가 지정한 모델명이 대상 리전에서 실제 배포 가능한지 **Bicep 생성 전에** 확인한다.
모델 가용성은 리전별로 다르고 수시로 변경되므로, 정적 지식에 의존하지 않는다.

**확인 방법 (우선순위):**
1. MS Docs 모델 가용성 페이지 확인: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models
2. 또는 Azure CLI로 직접 조회:
   ```powershell
   az cognitiveservices account list-models --name "<FOUNDRY_NAME>" --resource-group "<RG_NAME>" -o table
   ```
   (Foundry 리소스가 이미 있는 경우)

**모델이 해당 리전에서 사용 불가한 경우:**
- 사용자에게 알리고, 가용한 리전 또는 대체 모델을 제안한다
- 사용자 승인 없이 다른 모델이나 리전으로 대체하지 않는다

### 서비스별 MS Docs URL

`references/azure-dynamic-sources.md`에 전체 URL 레지스트리가 있다. 이 파일을 참조하여 fetch.
참조 파일은 `.github/skills/az-autopilot-agent/` 경로에서 찾는다.

> **중요**: URL에서 web_fetch로 직접 조회하여 최신 stable apiVersion을 확인한다. 레퍼런스 파일이나 이전 대화에 있던 하드코딩된 버전을 그냥 쓰지 말 것.

> **하위 리소스도 반드시 확인**: 부모 리소스 페이지에서 하위 리소스(accounts/projects, accounts/deployments, privateDnsZones/virtualNetworkLinks, privateEndpoints/privateDnsZoneGroups 등)의 API 버전도 함께 확인한다. 부모와 하위의 API 버전이 다를 수 있다.

> **에러/경고 발생 시에도 동일 원칙 적용**: what-if나 배포 중 API 버전 관련 에러가 발생하면, 에러 메시지에 포함된 버전을 "최신 버전"으로 믿고 바로 적용하지 않는다. 반드시 MS Docs URL을 다시 fetch하여 실제 최신 stable 버전을 확인한 후 수정한다.

---

## 정보 참조 원칙 (Stable vs Dynamic)

### 항상 fetch (Dynamic)
- API version → `azure-dynamic-sources.md`의 URL에서 fetch
- 모델 가용성 (이름, 버전, 리전) → fetch
- SKU 목록/가격 → fetch
- 리전 가용성 → fetch

### Reference 우선 참조 (Stable)
- 필수 속성 패턴 (`isHnsEnabled`, `allowProjectManagement` 등) → `service-gotchas.md`
- PE groupId & DNS Zone 매핑 (주요 서비스) → `service-gotchas.md`
- PE/보안/명명 공통 패턴 → `azure-common-patterns.md`
- AI/Data 서비스 구성 가이드 → `domain-packs/ai-data.md`

> Stable 정보도 확신이 없으면 MS Docs로 재확인. 하지만 매번 fetch할 필요는 없다.

---

## Unknown Service Fallback Workflow

v1 범위(`domain-packs/ai-data.md`)에 없는 서비스를 사용자가 요구할 경우:

1. **사용자 고지**: "이 서비스는 v1 기본 범위 밖입니다. MS Docs를 참조하여 best-effort로 생성합니다."
2. **API version fetch**: `https://learn.microsoft.com/en-us/azure/templates/microsoft.{provider}/{resourceType}` 형식으로 URL 구성 후 fetch
3. **리소스 타입/필수 속성 파악**: fetch한 Docs에서 resource type, required properties 확인
4. **PE 매핑 확인**: `https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns` fetch하여 groupId/DNS Zone 확인
5. **공통 패턴 적용**: `azure-common-patterns.md`의 보안/네트워크/명명 패턴 적용
6. **Bicep 작성**: 위 정보를 바탕으로 모듈 생성
7. **리뷰어 전달**: `az bicep build`로 컴파일 검증

## 입력 받는 정보

Phase 1 완료 시 다음 정보가 확정되어 있어야 한다:

```
- services: [서비스 목록 + SKU]
- networking: private_endpoint 여부
- resource_group: 리소스 그룹 이름
- location: 배포 위치 (Phase 1에서 사용자와 확정)
- subscription_id: Azure 구독 ID
```

## 출력 파일 구조

```
<project-name>/
├── main.bicep              # 메인 오케스트레이션 — 모듈 호출 및 파라미터 전달
├── main.bicepparam         # 파라미터 파일 — 환경별 값, 민감 정보 제외
└── modules/
    ├── network.bicep           # VNet, Subnet (pe-subnet 포함)
    ├── ai.bicep                # AI 서비스 (사용자 요구에 따라 구성)
    ├── storage.bicep           # ADLS Gen2 (isHnsEnabled: true 필수)
    ├── fabric.bicep            # Microsoft Fabric Capacity (필요 시만)
    ├── keyvault.bicep          # Key Vault
    ├── monitoring.bicep        # Application Insights, Log Analytics (Hub 기반 구성에서만 필요)
    └── private-endpoints.bicep # 모든 PE + Private DNS Zone + VNet Link + DNS Zone Group
```

## 모듈별 책임 범위

### `network.bicep`
- VNet — CIDR은 파라미터로 받음 (고객 환경 기존 주소공간과 충돌 방지)
- pe-subnet — `privateEndpointNetworkPolicies: 'Disabled'` 필수
- 추가 서브넷 필요 시 파라미터로 처리

### `ai.bicep`
- **Microsoft Foundry resource** (`Microsoft.CognitiveServices/accounts`, `kind: 'AIServices'`) — 최상위 AI 리소스
  - `customSubDomainName: foundryName` 필수 — **생성 후 변경 불가. 누락 시 리소스 삭제 후 재생성 필요**
  - `identity: { type: 'SystemAssigned' }` 필수
  - `allowProjectManagement: true` 필수
  - 모델 배포 (`Microsoft.CognitiveServices/accounts/deployments`) — Foundry resource 레벨에서 수행
- **⚠️ Foundry Project** (`Microsoft.CognitiveServices/accounts/projects`) — **반드시 child resource로 생성**
  - 리소스 타입: `Microsoft.CognitiveServices/accounts/projects` (절대 standalone `accounts`로 생성하지 않는다)
  - Bicep에서 `parent: foundryAccount` 사용
  - 잘못된 예: Project를 별도의 `kind: 'AIServices'` 계정으로 생성 → 포털에서 인식 안 됨
  - 올바른 예:
    ```bicep
    resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@<apiVersion>' = {
      parent: foundryAccount
      name: 'project-${uniqueString(resourceGroup().id)}'
      location: location
      kind: 'AIServices'
      properties: {}
    }
    ```
- **Azure AI Search** — Semantic Ranking, 벡터 검색 설정
- Hub 기반(`Microsoft.MachineLearningServices/workspaces`)은 사용자가 명시적으로 요구하거나, ML 훈련/오픈소스 모델이 필요한 경우에만 검토. 기본 AI/RAG 워크로드에서는 Foundry (AIServices)를 기본 선택

**⛔ CognitiveServices 금지 속성:**
- `apiProperties.statisticsEnabled` — 존재하지 않는 속성. 절대 사용하지 않는다. 배포 시 `ApiPropertiesInvalid` 에러 발생
- `apiProperties.qnaAzureSearchEndpointId` — QnA Maker 전용. Foundry에 사용하지 않는다
- `properties.apiProperties`에 검증되지 않은 속성을 임의로 추가하지 않는다

### `storage.bicep`
- ADLS Gen2: `isHnsEnabled: true` ← **절대 빠트리지 말 것**
- 컨테이너: raw, processed, curated (또는 요구사항에 맞게)
- `allowBlobPublicAccess: false`, `minimumTlsVersion: 'TLS1_2'`

### `keyvault.bicep`
- `enableRbacAuthorization: true` (액세스 정책 방식 사용 금지)
- `enableSoftDelete: true`, `softDeleteRetentionInDays: 90`
- `enablePurgeProtection: true`

### `monitoring.bicep`
- Log Analytics Workspace
- Application Insights (Hub 기반 구성에서만 필요 — Foundry AIServices는 불필요)

### `private-endpoints.bicep`
- 각 서비스마다 3종 세트:
  1. `Microsoft.Network/privateEndpoints` (pe-subnet에 배치)
  2. `Microsoft.Network/privateDnsZones` + VNet Link (`registrationEnabled: false`)
  3. `Microsoft.Network/privateEndpoints/privateDnsZoneGroups`
- 서비스별 DNS Zone 매핑은 `references/service-gotchas.md` 참조

**⚠️ Foundry/AIServices PE DNS 규칙:**
- PE groupId: `account`
- DNS Zone Group에 반드시 **2개 zone** 포함:
  1. `privatelink.cognitiveservices.azure.com`
  2. `privatelink.openai.azure.com`
- 하나만 넣으면 OpenAI API 호출 시 DNS 해석 실패 → 연결 에러

**⚠️ ADLS Gen2 (isHnsEnabled: true) PE 규칙:**
- PE 2개 필요:
  1. `blob` → `privatelink.blob.core.windows.net`
  2. `dfs` → `privatelink.dfs.core.windows.net`
- DFS PE 없으면 Data Lake 작업 (파일 시스템 생성, 디렉토리 조작) 실패

### `rbac.bicep` (또는 main.bicep에 인라인)

**⚠️ RBAC Role Assignment — 절대 생략 금지**

**Managed Identity (`identity.type: 'SystemAssigned'`)가 있는 서비스는 반드시 RBAC role assignment를 생성한다.**
role assignment 없이 identity만 있으면 서비스 간 인증이 실패한다.
이것은 선택사항이 아니라 **필수 생성 항목**이다.
생략 시 Phase 3 리뷰에서 CRITICAL로 리포트된다.

- 필수 RBAC 매핑:

| 소스 서비스 | 대상 서비스 | Role | Role Definition ID |
|------------|-----------|------|-------------------|
| Foundry | Storage | `Storage Blob Data Contributor` | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |
| Foundry | AI Search | `Search Index Data Contributor` | `8ebe5a00-799e-43f5-93ac-243d3dce84a7` |
| Foundry | AI Search | `Search Service Contributor` | `7ca78c08-252a-4471-8644-bb5ff32d4ba0` |
| App Service | Key Vault | `Key Vault Secrets User` | `4633458b-17de-408a-b874-0445c86b69e6` |
| AKS (kubeletIdentity) | ACR | `AcrPull` | `7f951dda-4ed3-4680-a7ca-43fe172d538d` |
| Data Factory | Storage | `Storage Blob Data Contributor` | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |
| Data Factory | Key Vault | `Key Vault Secrets User` | `4633458b-17de-408a-b874-0445c86b69e6` |
| Databricks | Storage | `Storage Blob Data Contributor` | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |

> **AKS 특별 규칙**: AKS는 `identity.principalId`가 아닌 `identityProfile.kubeletidentity.objectId`를 사용한다.

```bicep
// RBAC 예시 — Foundry → Storage Blob Data Contributor
resource foundryStorageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, foundry.id, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: foundry.identity.principalId
    principalType: 'ServicePrincipal'
  }
}
```

### SQL Server 관련 규칙
- **비밀번호 관리**: `@secure() param sqlAdminPassword string`을 main.bicep에서 선언하고 모듈에 전달
  - 모듈 내부에서 `newGuid()`로 생성하지 않는다 — 재배포 시 비밀번호가 변경됨
  - Key Vault Secret으로 저장하여 배포 후 조회 가능하게 한다
- **인증 방식**: `administrators.azureADOnlyAuthentication: true` 기본 설정
  - 조직 정책(MCAPS 등)에서 SQL 인증 단독 사용을 차단하는 경우가 많음
  - AAD 전용 인증 + Managed Identity가 가장 안전한 구성

### 네트워크 시크릿 처리
- **VPN Gateway shared key**: `@secure() param vpnSharedKey string` — 반드시 `@secure()` 사용
- `.bicepparam`에 평문 VPN 키 기재 금지 — 배포 시 입력 또는 Key Vault 참조
- 이 규칙은 SQL 비밀번호와 동일하게 적용
- **대상**: VPN shared key, ExpressRoute authorization key, Wi-Fi PSK 등 모든 네트워크 시크릿
- 모듈의 param에도 반드시 `@secure()` 데코레이터 추가

### ⚠️ 네트워크 격리 일관성 규칙
- `publicNetworkAccess: 'Disabled'` 설정 시 **반드시** 해당 서비스의 PE도 함께 생성
- PE 없이 publicNetworkAccess를 Disabled로 설정하면 서비스 접근 불가 → 배포 후 사용 불가
- Phase 3 리뷰어가 이 불일치를 **CRITICAL**로 리포트해야 함
- 불일치 발견 시: PE 모듈을 추가하거나, publicNetworkAccess를 Enabled로 되돌린다

## 필수 코딩 원칙

### 이름 규칙
```bicep
// uniqueString으로 충돌 방지 — 반드시 사용
param foundryName string = 'foundry-${uniqueString(resourceGroup().id)}'
param searchName string = 'srch-${uniqueString(resourceGroup().id)}'
param storageName string = 'st${uniqueString(resourceGroup().id)}'  // 특수문자 불가
param keyVaultName string = 'kv-${uniqueString(resourceGroup().id)}'
```
> **⚠️ `customSubDomainName`이 필요한 리소스 (Foundry, Cognitive Services 등)는 반드시 `uniqueString()` 포함.**
> 정적 문자열(예: `'my-rag-chatbot'`)은 다른 테넌트에서 이미 사용 중일 수 있어 배포 실패 원인이 된다.
> Foundry Project 이름도 동일 — `'project-${uniqueString(resourceGroup().id)}'`

### 네트워크 격리
```bicep
// Private Endpoint 사용 시 모든 서비스에 필수
publicNetworkAccess: 'Disabled'
networkAcls: {
  defaultAction: 'Deny'
  ipRules: []
  virtualNetworkRules: []
}
```

### 의존성 관리
```bicep
// 명시적 dependsOn 대신 리소스 참조로 암묵적 의존성 활용
resource aiProject '...' = {
  properties: {
    hubResourceId: aiHub.id  // aiHub 참조 → 자동으로 aiHub 먼저 배포됨
  }
}
```

### 보안
```bicep
// 민감 값은 Key Vault 참조 사용, 파라미터 파일에 평문 저장 금지
@secure()
param adminPassword string  // main.bicepparam에 평문 값 넣지 않음
```

### 한국어 주석
```bicep
// Microsoft Foundry resource — kind: 'AIServices'
// customSubDomainName: 필수, 글로벌 고유값. 생성 후 변경 불가 — 누락 시 리소스 삭제 후 재생성
// allowProjectManagement: true 없으면 Foundry Project 생성 불가
// apiVersion은 Step 0에서 fetch한 최신 버전으로 대체
resource foundry 'Microsoft.CognitiveServices/accounts@<Step 0에서 fetch한 버전>' = {
  kind: 'AIServices'
  properties: {
    customSubDomainName: foundryName
    allowProjectManagement: true
    ...
  }
}
```

### ⚠️ Bicep 코드 품질 검증 (생성 후 필수)

**모듈 선언 검증:**
- 각 module 블록의 `name:` 속성이 중복되지 않았는지 확인
- 올바른 예: `name: 'deploy-sql'`
- 잘못된 예: `name: 'name: 'deploy-sql'` (name: 중복 → 컴파일 에러)

**속성 중복 방지:**
- 한 리소스 블록 내에서 동일 속성명이 2번 이상 나타나면 컴파일 에러
- 특히 VPN Gateway (`gatewayType`), Firewall, AKS 등 복잡한 리소스에서 발생하기 쉬움
- `az bicep build` 결과에서 `BCP025: The property "xxx" is declared multiple times` 확인

**`az bicep build` 필수 실행:**
- 모든 Bicep 파일 생성 후 반드시 `az bicep build --file main.bicep` 실행
- 에러가 있으면 수정 후 재컴파일
- 경고(BCP081 등)는 MS Docs에서 API 버전 확인 후 무시 가능

## main.bicep 기본 구조

```bicep
// ============================================================
// Azure [프로젝트명] 인프라 — main.bicep
// 생성일: [날짜]
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string   // Phase 1에서 확정한 위치 — 하드코딩 금지
param projectPrefix string
param vnetAddressPrefix string    // ← 사용자에게 확인. 기존 네트워크와 충돌 방지
param peSubnetPrefix string       // ← VNet 내 PE 전용 서브넷 CIDR

// ── 네트워크 ──────────────────────────────────────────────
module network './modules/network.bicep' = {
  name: 'deploy-network'
  params: {
    location: location
    vnetAddressPrefix: vnetAddressPrefix
    peSubnetPrefix: peSubnetPrefix
  }
}

// ── AI/Data 서비스 ────────────────────────────────────────
module ai './modules/ai.bicep' = {
  name: 'deploy-ai'
  params: {
    location: location
    // 서비스별로 지역이 다르면 별도 param 추가 — MS Docs에서 가용 지역 확인
  }
  dependsOn: [network]
}

// ── 스토리지 ──────────────────────────────────────────────
module storage './modules/storage.bicep' = {
  name: 'deploy-storage'
  params: {
    location: location
  }
}

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
  }
}

// ── Private Endpoint (모든 서비스) ────────────────────────
module privateEndpoints './modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    foundryId: ai.outputs.foundryId
    searchId: ai.outputs.searchId
    storageId: storage.outputs.storageId
    keyVaultId: keyVault.outputs.keyVaultId
  }
}

// ── 출력 ──────────────────────────────────────────────────
output vnetId string = network.outputs.vnetId
output foundryEndpoint string = ai.outputs.foundryEndpoint
output searchEndpoint string = ai.outputs.searchEndpoint
```

## main.bicepparam 기본 구조

```bicep
using './main.bicep'

param location = '<Phase 1에서 확정한 위치>'
param projectPrefix = '<프로젝트 접두사>'
// 민감 값은 여기에 넣지 말 것 — Key Vault 참조 사용
// 지역은 서비스별 가용성을 MS Docs에서 확인 후 설정
```

### @secure() 파라미터 처리

`.bicepparam` 파일에 `using` 디렉티브가 있으면, `az deployment` 시 추가 `--parameters` 플래그를 함께 사용할 수 없다.
따라서 `@secure()` 파라미터는 아래 규칙을 따른다:

- **가능하면 기본값을 설정한다**: `@secure() param password string = newGuid()`
- **사용자 입력이 필요한 @secure() 파라미터가 있으면**: `.bicepparam` 대신 JSON 파라미터 파일(`main.parameters.json`)을 함께 생성한다
- **절대 하지 말 것**: `.bicepparam`과 `--parameters key=value`를 동시에 사용하는 명령어를 생성하는 것

## 자주 발생하는 실수 체크

`references/service-gotchas.md`에 전체 체크리스트가 있다. 핵심만 요약:

| 항목 | ❌ 잘못 | ✅ 올바름 |
|------|--------|----------|
| ADLS Gen2 | `isHnsEnabled` 생략 | `isHnsEnabled: true` |
| PE 서브넷 | 정책 미설정 | `privateEndpointNetworkPolicies: 'Disabled'` |
| PE 구성 | PE만 생성 | PE + DNS Zone + VNet Link + DNS Zone Group |
| Foundry | `kind: 'OpenAI'` | `kind: 'AIServices'` + `allowProjectManagement: true` |
| Foundry | `customSubDomainName` 누락 | `customSubDomainName: foundryName` — 생성 후 변경 불가 |
| Foundry Project | 미생성 | Foundry resource와 반드시 세트 |
| Hub 사용 | 일반 AI에 사용 | 사용자 명시 요청 또는 ML/오픈소스 필요 시에만 |
| 공개 네트워크 | 미설정 | `publicNetworkAccess: 'Disabled'` |
| Storage 이름 | 하이픈 포함 | 소문자+숫자만, `uniqueString()` 권장 |
| API version | 이전 값 복사 | MS Docs fetch (Dynamic) |
| 리전 | 하드코딩 | 파라미터 + MS Docs 가용성 확인 (Dynamic) |

## 생성 완료 후

Bicep 생성이 완료되면:
1. 생성된 파일 목록과 각 파일의 역할을 사용자에게 요약 보고
2. Phase 3 (Bicep Reviewer)로 즉시 전환
3. 리뷰어는 `prompts/bicep-reviewer.md` 지침에 따라 자동 검토 및 수정 진행
