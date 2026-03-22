// ============================================================
// App Service — Managed Identity + KV Reference
// ============================================================

param location string
param projectPrefix string
param keyVaultUri string

var appServicePlanName = 'asp-${projectPrefix}-${uniqueString(resourceGroup().id)}'
var appServiceName = 'app-${projectPrefix}-${uniqueString(resourceGroup().id)}'

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: false
  }
}

resource appService 'Microsoft.Web/sites@2024-04-01' = {
  name: appServiceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
      appSettings: [
        {
          name: 'KEY_VAULT_URI'
          value: keyVaultUri
        }
      ]
    }
  }
}

output appServiceId string = appService.id
output appServiceName string = appService.name
output appServicePrincipalId string = appService.identity.principalId
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
