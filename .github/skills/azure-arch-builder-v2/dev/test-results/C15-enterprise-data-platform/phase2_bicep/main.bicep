// ============================================================
// Enterprise Data Platform — main.bicep
// Fabric + Databricks + ADLS Gen2 + Data Factory + SQL + KV
// ============================================================

targetScope = 'resourceGroup'

param location string
param projectPrefix string
param vnetAddressPrefix string = '10.0.0.0/16'
param peSubnetPrefix string = '10.0.1.0/24'
param fabricAdminEmail string

@secure()
param sqlAdminPassword string = newGuid()

param sqlAdminLogin string = 'sqladmin'
param aadAdminLogin string = 'aad-admin'
param aadAdminObjectId string
param aadAdminTenantId string = subscription().tenantId

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

// ── Fabric Capacity ───────────────────────────────────────
module fabric './modules/fabric.bicep' = {
  name: 'deploy-fabric'
  params: {
    location: location
    adminEmail: fabricAdminEmail
  }
}

// ── Databricks ────────────────────────────────────────────
module databricks './modules/databricks.bicep' = {
  name: 'deploy-databricks'
  params: {
    location: location
    projectPrefix: projectPrefix
  }
}

// ── Data Factory ──────────────────────────────────────────
module dataFactory './modules/datafactory.bicep' = {
  name: 'deploy-datafactory'
  params: {
    location: location
  }
}

// ── Private Endpoints ─────────────────────────────────────
module privateEndpoints './modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    storageId: storage.outputs.storageAccountId
    keyVaultId: keyVault.outputs.keyVaultId
    sqlServerId: sql.outputs.sqlServerId
    databricksId: databricks.outputs.databricksId
    dataFactoryId: dataFactory.outputs.dataFactoryId
  }
}

// ── 출력 ──────────────────────────────────────────────────
output storageAccountName string = storage.outputs.storageAccountName
output keyVaultName string = keyVault.outputs.keyVaultName
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output fabricCapacityId string = fabric.outputs.fabricCapacityId
output databricksUrl string = databricks.outputs.databricksUrl
output dataFactoryName string = dataFactory.outputs.dataFactoryName
