# Skill Test Fix Report

Generated: 2026-03-22 12:05
Test Framework: `dev/test_skill.py`
Tested Scenarios: 7 (Phase 1 all 7, Phase 2-4 for 3 representative)

## Summary

| Scenario | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Diagram | Overall |
|----------|---------|---------|---------|---------|---------|---------|
| 1-1-basic-rag-default | PASS | PASS | FAIL | FAIL | PASS* | **FAIL** |
| 1-2-basic-rag-korea | PASS | — | — | — | PASS* | Phase 1 OK |
| 1-3-basic-rag-auto | PASS | — | — | — | PASS* | Phase 1 OK |
| 2-1-private-rag-default | PASS | PASS | FAIL | FAIL | PASS* | **FAIL** |
| 2-2-private-rag-custom-vnet | PASS | — | — | — | PASS* | Phase 1 OK |
| 3-1-webapp-basic | PASS | PASS | WARN | FAIL† | PASS | **WARN** |
| 3-2-webapp-add-cache | PASS | — | — | — | PASS | Phase 1 OK |

- `*` = Diagram renders but AI Search shows "?" icon (missing `ai_search` alias)
- `†` = Policy violation (org-specific, not a Bicep code issue)

---

## Issues Found (8)

### 1. [CRITICAL] Diagram: `ai_search` type not recognized

- **Affected**: All RAG scenarios (1-1, 1-2, 1-3, 2-1, 2-2)
- **Symptom**: AI Search node shows "?" icon and falls into "Azure" category instead of "AI"
- **Root Cause**: `SERVICE_ICONS` in `generate_html_diagram.py` has key `"search"` (line 51) but NOT `"ai_search"`. The skill's Phase 1 output uses type `"ai_search"`.
- **Fix File**: `scripts/generate_html_diagram.py`
- **Fix**: Add `"ai_search"` as an alias entry pointing to the same config as `"search"`:
  ```python
  # After line 55 (closing of "search" entry), add:
  "ai_search": {
      "icon_svg": '<circle cx="20" cy="20" r="12" fill="none" stroke="#0078D4" stroke-width="3.5"/><line x1="29" y1="29" x2="40" y2="40" stroke="#0078D4" stroke-width="3.5" stroke-linecap="round"/><circle cx="20" cy="20" r="5" fill="#0078D4" opacity="0.3"/>',
      "color": "#0078D4", "bg": "#E8F4FD", "category": "AI",
      "azure_icon_key": "cognitive_search"
  },
  ```
- **Also add to TYPE_LABELS** (around line 1445): `'ai_search': 'AI Search'`

### 2. [CRITICAL] Bicep: Foundry Project uses wrong resource type

- **Affected**: 1-1, 2-1 (all RAG scenarios)
- **Symptom**: Foundry Project created as standalone `Microsoft.CognitiveServices/accounts` with `kind: 'AIServices'`
- **Root Cause**: Sub-agent generated Project as a separate top-level resource instead of child resource
- **Fix File**: `prompts/bicep-generator.md`
- **Fix**: Add explicit rule:
  ```markdown
  ### Foundry Hub + Project 패턴
  - Foundry Hub: `Microsoft.CognitiveServices/accounts` (kind: 'AIServices')
  - Foundry Project: `Microsoft.CognitiveServices/accounts/projects` (자식 리소스)
  - Project는 반드시 Hub의 child resource로 생성한다
  - `parent: foundryAccount` 사용
  - Hub에 `allowProjectManagement: true` 속성 필수
  ```

### 3. [CRITICAL] Bicep: Project name not globally unique

- **Affected**: 1-1, 2-1 (all RAG scenarios)
- **Symptom**: `projectName = 'my-rag-chatbot'` (static string, no uniqueString)
- **Root Cause**: customSubDomainName requires global uniqueness but static name used
- **Fix File**: `prompts/bicep-generator.md`
- **Fix**: Add rule:
  ```markdown
  ### 명명 규칙
  - `customSubDomainName`이 필요한 리소스는 반드시 `uniqueString(resourceGroup().id)` 포함
  - 예: `'foundry-${uniqueString(resourceGroup().id)}'`
  ```

### 4. [CRITICAL] Bicep: `statisticsEnabled` invalid API property

- **Affected**: 1-1, 2-1 (all Foundry scenarios)
- **Symptom**: `az deployment group validate` fails with `ApiPropertiesInvalid`
- **Root Cause**: `apiProperties.statisticsEnabled` is not a valid property for CognitiveServices
- **Fix File**: `prompts/bicep-generator.md`
- **Fix**: Add to Foundry generation rules:
  ```markdown
  ### CognitiveServices 금지 속성
  - `apiProperties.statisticsEnabled` — 존재하지 않는 속성. 절대 사용하지 않는다
  - `apiProperties.qnaAzureSearchEndpointId` — QnA Maker 전용. Foundry에 사용하지 않는다
  ```

### 5. [CRITICAL] Bicep: PE DNS Zone missing for OpenAI endpoint

- **Affected**: 2-1 (Private RAG)
- **Symptom**: OpenAI DNS Zone created but not linked to Foundry PE's DNS Zone Group
- **Root Cause**: Foundry PE needs BOTH `privatelink.cognitiveservices.azure.com` AND `privatelink.openai.azure.com` in DNS Zone Group
- **Fix File**: `prompts/bicep-generator.md` or `references/service-gotchas.md`
- **Fix**: Add PE DNS rule:
  ```markdown
  ### Foundry/AIServices PE DNS 규칙
  - PE groupId: `account`
  - DNS Zone Group에 반드시 2개 zone 포함:
    1. `privatelink.cognitiveservices.azure.com`
    2. `privatelink.openai.azure.com`
  - 하나만 넣으면 OpenAI API 호출 시 DNS 해석 실패
  ```

### 6. [WARNING] Bicep: ADLS Gen2 missing DFS private endpoint

- **Affected**: 2-1 (Private RAG)
- **Symptom**: Only blob PE created, no DFS PE
- **Root Cause**: ADLS Gen2 (isHnsEnabled=true) uses DFS endpoint for Data Lake operations
- **Fix File**: `references/service-gotchas.md`
- **Fix**: Add to Storage PE section:
  ```markdown
  ### Storage Account PE (ADLS Gen2)
  - isHnsEnabled: true인 경우 PE 2개 필요:
    1. `blob` → `privatelink.blob.core.windows.net`
    2. `dfs` → `privatelink.dfs.core.windows.net`
  - DFS PE 없으면 Data Lake 작업 (파일 시스템 생성, 디렉토리 조작) 실패
  ```

### 7. [WARNING] Bicep: No RBAC role assignments between services

- **Affected**: All scenarios (1-1, 2-1, 3-1)
- **Symptom**: Services have SystemAssigned identity but no role assignments
- **Root Cause**: Bicep generator doesn't generate `Microsoft.Authorization/roleAssignments`
- **Fix File**: `prompts/bicep-generator.md`
- **Fix**: Add RBAC generation rule:
  ```markdown
  ### RBAC Role Assignment 필수 생성
  서비스 간 연결이 있으면 해당 role assignment도 Bicep에 포함:
  - Foundry → Storage: `Storage Blob Data Contributor`
  - Foundry → Search: `Search Index Data Contributor`
  - App Service → Key Vault: `Key Vault Secrets User`
  - App Service → SQL: connection string 또는 Managed Identity 인증
  ```

### 8. [WARNING] Bicep: SQL admin password lifecycle issue

- **Affected**: 3-1 (Web App)
- **Symptom**: `newGuid()` generates new password on every deployment, never stored
- **Root Cause**: Password generated inside module, not passed from main.bicep or stored in KV
- **Fix File**: `prompts/bicep-generator.md`
- **Fix**: Add SQL password rule:
  ```markdown
  ### SQL Server 비밀번호 관리
  - `@secure() param sqlAdminPassword string`을 main.bicep에서 선언
  - Key Vault Secret으로 저장 (배포 후 조회 가능하도록)
  - `newGuid()`를 모듈 내부에서 사용하지 않는다 — 재배포 시 비밀번호 변경됨
  ```

---

## Phase 4 Validate 상세

### 1-1 & 2-1 (RAG): `ApiPropertiesInvalid`
```
ERROR: Property 'statisticsEnabled' has not been defined and the schema
does not allow additional properties. Path 'apiProperties.statisticsEnabled'.
```

### 3-1 (Web App): `RequestDisallowedByPolicy`
```
ERROR: Resource 'sql-xxx' was disallowed by policy.
Policy: AzureSQL_WithoutAzureADOnlyAuthentication_Deny
```
→ 이 에러는 조직 정책(MCAPS)에 의한 것. SQL Server에 `azureADOnlyAuthentication: true` 설정 필요.
→ `prompts/bicep-generator.md`에 추가 권장:
```markdown
### SQL Server 인증
- 기본적으로 `administrators.azureADOnlyAuthentication: true` 설정
- 조직 정책에서 SQL 인증 단독 사용을 차단하는 경우 많음
```

---

## 다이어그램 검증 결과

| Scenario | 서비스 렌더링 | 아이콘 | 연결선 | VNet | 비고 |
|----------|-------------|--------|--------|------|------|
| 1-1 | 5/5 | 4/5 | 6/6 | N/A | AI Search "?" 아이콘 |
| 1-2 | 5/5 | 4/5 | 6/6 | N/A | AI Search "?" 아이콘 |
| 1-3 | 5/5 | 4/5 | 6/6 | N/A | AI Search "?" 아이콘 |
| 2-1 | 8/8 | 7/8 | 7/7 | ✅ 10.0.0.0/16 | AI Search "?" 아이콘 |
| 2-2 | 8/8 | 7/8 | 7/7 | ✅ 10.1.0.0/16 | AI Search "?" 아이콘 |
| 3-1 | 3/3 | 3/3 | 2/2 | N/A | 완벽 |
| 3-2 | 4/4 | 4/4 | 3/3 | N/A | 완벽 |

---

## 수정 우선순위

| 순위 | Issue # | 심각도 | 수정 대상 파일 |
|------|---------|--------|--------------|
| 1 | #1 | CRITICAL | `scripts/generate_html_diagram.py` |
| 2 | #4 | CRITICAL | `prompts/bicep-generator.md` |
| 3 | #2 | CRITICAL | `prompts/bicep-generator.md` |
| 4 | #3 | CRITICAL | `prompts/bicep-generator.md` |
| 5 | #5 | CRITICAL | `prompts/bicep-generator.md` or `references/service-gotchas.md` |
| 6 | #7 | WARNING | `prompts/bicep-generator.md` |
| 7 | #6 | WARNING | `references/service-gotchas.md` |
| 8 | #8 | WARNING | `prompts/bicep-generator.md` |
