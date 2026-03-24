// ============================================================
// 네트워크 모듈 — VNet + PE 서브넷
// ============================================================

param location string
param vnetAddressPrefix string
param peSubnetPrefix string
param projectPrefix string

resource vnet 'Microsoft.Network/virtualNetworks@2025-05-01' = {
  name: 'vnet-${projectPrefix}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [vnetAddressPrefix]
    }
    subnets: [
      {
        name: 'snet-pe'
        properties: {
          addressPrefix: peSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
        }
      }
    ]
  }
}

output vnetId string = vnet.id
output peSubnetId string = vnet.properties.subnets[0].id
