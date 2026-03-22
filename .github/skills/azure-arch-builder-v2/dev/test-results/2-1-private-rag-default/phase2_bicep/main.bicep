// ============================================================
// Azure Private RAG Chatbot 인프라 — main.bicep
// Scenario 2-1: Private RAG (Default VNet)
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string = resourceGroup().location
param vnetAddressPrefix string = '10.0.0.0/16'
param peSubnetPrefix string = '10.0.1.0/24'

// ── 네트워크 ──────────────────────────────────────────────
module network './modules/network.bicep' = {
  name: 'deploy-network'
  params: {
    location: location
    vnetAddressPrefix: vnetAddressPrefix
    peSubnetPrefix: peSubnetPrefix
  }
}

// ── Foundry (AIServices + Project + 모델 배포) ────────────
module foundry './modules/foundry.bicep' = {
  name: 'deploy-foundry'
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

// ── Private Endpoints (모든 서비스) ───────────────────────
module privateEndpoints './modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    foundryId: foundry.outputs.foundryId
    foundryName: foundry.outputs.foundryName
    searchId: search.outputs.searchId
    searchName: search.outputs.searchName
    storageId: storage.outputs.storageId
    storageName: storage.outputs.storageAccountName
    keyVaultId: keyVault.outputs.keyVaultId
    keyVaultName: keyVault.outputs.keyVaultName
  }
}

// ── 출력 ──────────────────────────────────────────────────
output vnetId string = network.outputs.vnetId
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output foundryName string = foundry.outputs.foundryName
output searchEndpoint string = search.outputs.searchEndpoint
output searchName string = search.outputs.searchName
output storageAccountName string = storage.outputs.storageAccountName
output keyVaultUri string = keyVault.outputs.keyVaultUri
