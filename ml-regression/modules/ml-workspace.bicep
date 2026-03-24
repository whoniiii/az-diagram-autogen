// ============================================================
// Azure Machine Learning Workspace — 모델 학습 + 서빙
// ============================================================

param location string
param projectPrefix string
param storageId string
param keyVaultId string
param appInsightsId string

var workspaceName = 'mlw-${projectPrefix}-${uniqueString(resourceGroup().id)}'

resource mlWorkspace 'Microsoft.MachineLearningServices/workspaces@2025-12-01' = {
  name: workspaceName
  location: location
  identity: { type: 'SystemAssigned' }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  properties: {
    friendlyName: 'ML Regression Workspace'
    storageAccount: storageId
    keyVault: keyVaultId
    applicationInsights: appInsightsId
    publicNetworkAccess: 'Disabled'
    managedNetwork: {
      isolationMode: 'AllowInternetOutbound'
    }
  }
}

output workspaceId string = mlWorkspace.id
output workspaceName string = mlWorkspace.name
output workspacePrincipalId string = mlWorkspace.identity.principalId
