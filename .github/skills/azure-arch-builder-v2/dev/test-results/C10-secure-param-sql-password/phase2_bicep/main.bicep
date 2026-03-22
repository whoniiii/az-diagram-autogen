// ============================================================
// App Service + SQL + Key Vault — @secure() Password Pattern
// SQL 비밀번호: @secure() param, KV에 저장, AAD-only Auth
// ============================================================

targetScope = 'resourceGroup'

param location string
param projectPrefix string

@secure()
param sqlAdminPassword string = newGuid()

param sqlAdminLogin string = 'sqladmin'
param aadAdminLogin string = 'aad-admin'
param aadAdminObjectId string
param aadAdminTenantId string = subscription().tenantId

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
    sqlAdminPassword: sqlAdminPassword
  }
}

// ── SQL ───────────────────────────────────────────────────
module sql './modules/sql.bicep' = {
  name: 'deploy-sql'
  params: {
    location: location
    sqlAdminLogin: sqlAdminLogin
    sqlAdminPassword: sqlAdminPassword
    aadAdminLogin: aadAdminLogin
    aadAdminObjectId: aadAdminObjectId
    aadAdminTenantId: aadAdminTenantId
  }
}

// ── App Service ───────────────────────────────────────────
module appService './modules/appservice.bicep' = {
  name: 'deploy-appservice'
  params: {
    location: location
    projectPrefix: projectPrefix
    keyVaultUri: keyVault.outputs.keyVaultUri
  }
}

// ── RBAC: App Service → Key Vault Secrets User ────────────
module rbac './modules/rbac.bicep' = {
  name: 'deploy-rbac'
  params: {
    keyVaultName: keyVault.outputs.keyVaultName
    appServicePrincipalId: appService.outputs.appServicePrincipalId
  }
}

// ── 출력 ──────────────────────────────────────────────────
output appServiceUrl string = appService.outputs.appServiceUrl
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output keyVaultName string = keyVault.outputs.keyVaultName
