// ============================================================
// VNet + PE Subnet — 프라이빗 엔드포인트용 네트워크
// ============================================================

param location string
param vnetName string = 'vnet-${uniqueString(resourceGroup().id)}'
param vnetAddressPrefix string = '10.0.0.0/16'
param peSubnetPrefix string = '10.0.1.0/24'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        vnetAddressPrefix
      ]
    }
    subnets: [
      {
        name: 'pe-subnet'
        properties: {
          addressPrefix: peSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output vnetName string = vnet.name
output peSubnetId string = vnet.properties.subnets[0].id
