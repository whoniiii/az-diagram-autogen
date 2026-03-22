// ============================================================
// Microsoft Foundry (AIServices) — Account + Project + Model Deployments
// Private 모드: publicNetworkAccess 'Disabled'
// ============================================================

param location string
param foundryName string = 'foundry-${uniqueString(resourceGroup().id)}'
param projectName string = 'my-rag-chatbot'

// Foundry Account — kind: 'AIServices'
// customSubDomainName: 필수, 글로벌 고유값. 생성 후 변경 불가
resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
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
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      ipRules: []
      virtualNetworkRules: []
    }
    apiProperties: {
      statisticsEnabled: false
    }
  }
}

// Foundry Project — Foundry resource와 반드시 세트로 생성
resource project 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: projectName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: projectName
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      ipRules: []
      virtualNetworkRules: []
    }
  }
  dependsOn: [foundry]
}

// GPT-4o 배포 — 채팅 모델
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-4o'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
  }
}

// text-embedding-ada-002 배포 — 임베딩 모델
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'text-embedding-ada-002'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
  }
  dependsOn: [gpt4oDeployment]
}

output foundryId string = foundry.id
output foundryName string = foundry.name
output foundryEndpoint string = foundry.properties.endpoint
