// ============================================================
// Spoke VNet — App Subnet + Data Subnet
// ============================================================

param location string
param projectPrefix string
param spokeVnetAddressPrefix string
param appSubnetPrefix string
param dataSubnetPrefix string

resource spokeVnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'vnet-spoke-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [spokeVnetAddressPrefix]
    }
    subnets: [
      {
        name: 'snet-app'
        properties: {
          addressPrefix: appSubnetPrefix
          delegations: [
            {
              name: 'delegation-appservice'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: 'snet-data'
        properties: {
          addressPrefix: dataSubnetPrefix
        }
      }
    ]
  }
}

output spokeVnetId string = spokeVnet.id
output spokeVnetName string = spokeVnet.name
output appSubnetId string = spokeVnet.properties.subnets[0].id
output dataSubnetId string = spokeVnet.properties.subnets[1].id
