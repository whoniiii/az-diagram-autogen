// ============================================================
// Azure Basic RAG Chatbot 인프라 — main.bicep
// Scenario 1-1: Basic RAG (Default)
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string = resourceGroup().location

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

// ── 출력 ──────────────────────────────────────────────────
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output foundryName string = foundry.outputs.foundryName
output searchEndpoint string = search.outputs.searchEndpoint
output searchName string = search.outputs.searchName
output storageAccountName string = storage.outputs.storageAccountName
output keyVaultUri string = keyVault.outputs.keyVaultUri
