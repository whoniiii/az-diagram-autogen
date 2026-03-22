// ============================================================
// RBAC Role Assignments — Foundry → Storage, Foundry → Search
// ============================================================

param foundryPrincipalId string
param storageAccountId string
param searchId string

// Foundry → Storage: Storage Blob Data Contributor
resource foundryStorageRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccountId, foundryPrincipalId, 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: foundryPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Foundry → Search: Search Index Data Contributor
resource foundrySearchIndexRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchId, foundryPrincipalId, '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
    principalId: foundryPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Foundry → Search: Search Service Contributor
resource foundrySearchServiceRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(searchId, foundryPrincipalId, '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
    principalId: foundryPrincipalId
    principalType: 'ServicePrincipal'
  }
}
