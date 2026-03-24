// ============================================================
// Azure ML Regression 인프라 — main.bicep
// 리그레이션 모델 학습 + Managed Online Endpoint 서빙
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string
param projectPrefix string
param vnetAddressPrefix string
param peSubnetPrefix string

// ── 네트워크 ──────────────────────────────────────────────
module network './modules/network.bicep' = {
  name: 'deploy-network'
  params: {
    location: location
    projectPrefix: projectPrefix
    vnetAddressPrefix: vnetAddressPrefix
    peSubnetPrefix: peSubnetPrefix
  }
}

// ── 스토리지 ──────────────────────────────────────────────
module storage './modules/storage.bicep' = {
  name: 'deploy-storage'
  params: {
    location: location
    projectPrefix: projectPrefix
  }
}

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
    projectPrefix: projectPrefix
    tenantId: tenant().tenantId
  }
}

// ── 모니터링 ──────────────────────────────────────────────
module monitoring './modules/monitoring.bicep' = {
  name: 'deploy-monitoring'
  params: {
    location: location
    projectPrefix: projectPrefix
  }
}

// ── Azure ML Workspace ────────────────────────────────────
module mlWorkspace './modules/ml-workspace.bicep' = {
  name: 'deploy-ml-workspace'
  params: {
    location: location
    projectPrefix: projectPrefix
    storageId: storage.outputs.storageId
    keyVaultId: keyVault.outputs.keyVaultId
    appInsightsId: monitoring.outputs.appInsightsId
  }
}

// ── Private Endpoints ─────────────────────────────────────
module privateEndpoints './modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    workspaceId: mlWorkspace.outputs.workspaceId
    storageId: storage.outputs.storageId
    keyVaultId: keyVault.outputs.keyVaultId
  }
}

// ── RBAC — AML Workspace → Storage (Storage Blob Data Contributor) ──
resource mlStorageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, projectPrefix, 'ml-storage-blob-contributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: mlWorkspace.outputs.workspacePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── RBAC — AML Workspace → Key Vault (Key Vault Administrator) ──
resource mlKeyVaultRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, projectPrefix, 'ml-keyvault-admin')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '00482a5a-887f-4fb3-b363-3b7fe8e74483')
    principalId: mlWorkspace.outputs.workspacePrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ── 출력 ──────────────────────────────────────────────────
output vnetId string = network.outputs.vnetId
output mlWorkspaceName string = mlWorkspace.outputs.workspaceName
output storageName string = storage.outputs.storageName
output keyVaultName string = keyVault.outputs.keyVaultName
