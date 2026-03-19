@description('프로젝트 이름')
param projectName string

@description('Azure 리전')
param location string

@description('환경')
param env string

@description('VNet 주소 공간')
param vnetAddressPrefix string

@description('PE 서브넷 주소')
param peSubnetPrefix string

var vnetName = 'vnet-${projectName}-${env}'

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: vnetName
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
output vnetName string = vnet.name
output peSubnetId string = vnet.properties.subnets[0].id
