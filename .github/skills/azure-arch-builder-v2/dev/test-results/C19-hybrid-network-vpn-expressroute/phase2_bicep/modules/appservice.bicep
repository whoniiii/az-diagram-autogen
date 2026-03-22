// ============================================================
// App Service — VNet Integration (Spoke)
// ============================================================

param location string
param projectPrefix string
param appSubnetId string

var appServicePlanName = 'asp-${projectPrefix}-${uniqueString(resourceGroup().id)}'
var appServiceName = 'app-${projectPrefix}-${uniqueString(resourceGroup().id)}'

resource appServicePlan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'P1v3'
    tier: 'PremiumV3'
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
    virtualNetworkSubnetId: appSubnetId
    siteConfig: {
      minTlsVersion: '1.2'
      vnetRouteAllEnabled: true
    }
  }
}

output appServiceId string = appService.id
output appServiceName string = appService.name
output appServicePrincipalId string = appService.identity.principalId
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
