// ============================================================
// Azure Web App 인프라 — main.bicep
// Scenario 3-1: Web App (Basic)
// ============================================================

targetScope = 'resourceGroup'

// ── 공통 파라미터 ─────────────────────────────────────────
param location string = resourceGroup().location
param sqlAdminLogin string = 'sqladmin'

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
  }
}

// ── SQL Server + Database ─────────────────────────────────
module sql './modules/sql.bicep' = {
  name: 'deploy-sql'
  params: {
    location: location
    sqlAdminLogin: sqlAdminLogin
  }
}

// ── App Service (Plan + Web App) ──────────────────────────
module appService './modules/appservice.bicep' = {
  name: 'deploy-appservice'
  params: {
    location: location
    keyVaultUri: keyVault.outputs.keyVaultUri
  }
}

// ── 출력 ──────────────────────────────────────────────────
output webAppHostName string = appService.outputs.defaultHostName
output webAppName string = appService.outputs.webAppName
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output sqlDatabaseName string = sql.outputs.sqlDatabaseName
output keyVaultUri string = keyVault.outputs.keyVaultUri
