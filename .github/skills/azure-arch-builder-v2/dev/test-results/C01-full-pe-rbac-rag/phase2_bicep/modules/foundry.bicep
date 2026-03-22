// ============================================================
// AI Foundry (AIServices) + Foundry Project
// customSubDomainName: 필수, 글로벌 고유값 — 생성 후 변경 불가
// allowProjectManagement: true — Project 생성에 필수
// ============================================================

param location string
param storageAccountId string
param keyVaultId string
param searchId string

var foundryName = 'foundry-${uniqueString(resourceGroup().id)}'

resource foundryAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: foundryName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: foundryName
    allowProjectManagement: true
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

// Foundry Project — 반드시 child resource로 생성
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2024-10-01' = {
  parent: foundryAccount
  name: 'project-${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'AIServices'
  properties: {}
}

output foundryId string = foundryAccount.id
output foundryName string = foundryAccount.name
output foundryEndpoint string = foundryAccount.properties.endpoint
output foundryPrincipalId string = foundryAccount.identity.principalId
output projectId string = foundryProject.id
