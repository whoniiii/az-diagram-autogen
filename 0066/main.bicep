targetScope = 'resourceGroup'

// ──────────────────────────────────────
// 파라미터
// ──────────────────────────────────────

@description('프로젝트 이름 (리소스 이름 접두사)')
param projectName string = '0066'

@description('Azure 리전')
param location string = 'koreacentral'

@description('환경 구분')
@allowed(['dev', 'stg', 'prd'])
param env string = 'dev'

@description('VNet 주소 공간')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('PE 서브넷 주소 공간')
param peSubnetPrefix string = '10.0.1.0/24'

// ──────────────────────────────────────
// 모듈 호출
// ──────────────────────────────────────

module network 'modules/network.bicep' = {
  name: 'deploy-network'
  params: {
    projectName: projectName
    location: location
    env: env
    vnetAddressPrefix: vnetAddressPrefix
    peSubnetPrefix: peSubnetPrefix
  }
}

module storage 'modules/storage.bicep' = {
  name: 'deploy-storage'
  params: {
    projectName: projectName
    location: location
    env: env
  }
}

module keyVault 'modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    projectName: projectName
    location: location
    env: env
    tenantId: subscription().tenantId
  }
}

module search 'modules/search.bicep' = {
  name: 'deploy-search'
  params: {
    projectName: projectName
    location: location
    env: env
  }
}

module foundry 'modules/foundry.bicep' = {
  name: 'deploy-foundry'
  params: {
    projectName: projectName
    location: location
    env: env
  }
}

module privateEndpoints 'modules/private-endpoints.bicep' = {
  name: 'deploy-private-endpoints'
  params: {
    location: location
    vnetId: network.outputs.vnetId
    peSubnetId: network.outputs.peSubnetId
    foundryId: foundry.outputs.foundryId
    searchId: search.outputs.searchId
    storageId: storage.outputs.storageId
    keyVaultId: keyVault.outputs.keyVaultId
  }
}

// ──────────────────────────────────────
// 출력
// ──────────────────────────────────────

output foundryName string = foundry.outputs.foundryName
output foundryEndpoint string = foundry.outputs.foundryEndpoint
output searchName string = search.outputs.searchName
output storageName string = storage.outputs.storageName
output keyVaultName string = keyVault.outputs.keyVaultName
output vnetName string = network.outputs.vnetName
