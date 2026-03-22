// ============================================================
// App Service Plan + Web App
// ============================================================

param location string
param appServicePlanName string = 'asp-${uniqueString(resourceGroup().id)}'
param webAppName string = 'webapp-${uniqueString(resourceGroup().id)}'
param skuName string = 'B1'
param linuxFxVersion string = 'DOTNETCORE|8.0'
param keyVaultUri string = ''

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: skuName
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2024-04-01' = {
  name: webAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      appSettings: [
        {
          name: 'KEY_VAULT_URI'
          value: keyVaultUri
        }
      ]
    }
  }
}

output appServiceId string = webApp.id
output defaultHostName string = webApp.properties.defaultHostName
output webAppName string = webApp.name
output principalId string = webApp.identity.principalId
