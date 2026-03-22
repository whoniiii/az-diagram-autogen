// ============================================================
// AKS Microservices Platform — main.bicep
// AKS + ACR + Redis + SQL + KV + Application Gateway
// ============================================================

targetScope = 'resourceGroup'

param location string
param projectPrefix string
param vnetAddressPrefix string = '10.0.0.0/16'
param aksSubnetPrefix string = '10.0.0.0/22'
param appGwSubnetPrefix string = '10.0.4.0/24'
param peSubnetPrefix string = '10.0.5.0/24'

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
    aksSubnetPrefix: aksSubnetPrefix
    appGwSubnetPrefix: appGwSubnetPrefix
    peSubnetPrefix: peSubnetPrefix
  }
}

// ── ACR ───────────────────────────────────────────────────
module acr './modules/acr.bicep' = {
  name: 'deploy-acr'
  params: {
    location: location
  }
}

// ── AKS ───────────────────────────────────────────────────
module aks './modules/aks.bicep' = {
  name: 'deploy-aks'
  params: {
    location: location
    projectPrefix: projectPrefix
    aksSubnetId: network.outputs.aksSubnetId
    appGwId: appGateway.outputs.appGwId
  }
}

// ── Redis ─────────────────────────────────────────────────
module redis './modules/redis.bicep' = {
  name: 'deploy-redis'
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

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
  }
}

// ── Application Gateway ───────────────────────────────────
module appGateway './modules/appgateway.bicep' = {
  name: 'deploy-appgateway'
  params: {
    location: location
    projectPrefix: projectPrefix
    appGwSubnetId: network.outputs.appGwSubnetId
  }
}

// ── 출력 ──────────────────────────────────────────────────
output aksClusterName string = aks.outputs.aksClusterName
output acrLoginServer string = acr.outputs.acrLoginServer
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output keyVaultName string = keyVault.outputs.keyVaultName
