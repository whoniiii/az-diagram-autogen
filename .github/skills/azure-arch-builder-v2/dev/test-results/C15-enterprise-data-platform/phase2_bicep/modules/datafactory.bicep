// ============================================================
// Azure Data Factory — Managed VNet Integration Runtime
// ============================================================

param location string

var dataFactoryName = 'adf-${uniqueString(resourceGroup().id)}'

resource dataFactory 'Microsoft.DataFactory/factories@2018-06-01' = {
  name: dataFactoryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publicNetworkAccess: 'Disabled'
  }
}

output dataFactoryId string = dataFactory.id
output dataFactoryName string = dataFactory.name
