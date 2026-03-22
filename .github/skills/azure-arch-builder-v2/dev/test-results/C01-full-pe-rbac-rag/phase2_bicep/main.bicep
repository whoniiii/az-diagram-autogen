// ============================================================
// Enterprise RAG Chatbot Infrastructure — main.bicep
// Full PE + RBAC Chain: Foundry, AI Search, ADLS Gen2, KV
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string
param projectPrefix string
param vnetAddressPrefix string = '10.0.0.0/16'
param peSubnetPrefix string = '10.0.1.0/24'

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

// ── Monitoring ────────────────────────────────────────────
module monitoring './modules/monitoring.bicep' = {
  name: 'deploy-monitoring'
  params: {
    location: location
    projectPrefix: projectPrefix
  }
}

// ── Storage (ADLS Gen2) ───────────────────────────────────
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

// ── AI Search ─────────────────────────────────────────────
module search './modules/search.bicep' = {
  name: 'deploy-search'
  params: {
    location: location
  }
}

// ── AI Foundry (Hub + Project) ────────────────────────────
module foundry './modules/foundry.bicep' = {
  name: 'deploy-foundry'
  params: {
    location: location
    storageAccountId: storage.outputs.storageAccountId
    keyVaultId: keyVault.outputs.keyVaultId
    searchId: search.outputs.searchId
  }
}

// ── Private Endpoints ─────────────────────────────────────
module privateEndpoints './modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    foundryId: foundry.outputs.foundryId
    searchId: search.outputs.searchId
    storageId: storage.outputs.storageAccountId
    keyVaultId: keyVault.outputs.keyVaultId
  }
}

// ── RBAC ──────────────────────────────────────────────────
module rbac './modules/rbac.bicep' = {
  name: 'deploy-rbac'
  params: {
    foundryPrincipalId: foundry.outputs.foundryPrincipalId
    storageAccountId: storage.outputs.storageAccountId
    searchId: search.outputs.searchId
  }
}

// ── 출력 ──────────────────────────────────────────────────
output vnetId string = network.outputs.vnetId
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output searchEndpoint string = search.outputs.searchEndpoint
output storageAccountName string = storage.outputs.storageAccountName
output keyVaultName string = keyVault.outputs.keyVaultName
