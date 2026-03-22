// ============================================================
// Hub VNet — GatewaySubnet + AzureFirewallSubnet + AzureBastionSubnet
// ============================================================

param location string
param projectPrefix string
param hubVnetAddressPrefix string
param gatewaySubnetPrefix string
param firewallSubnetPrefix string
param bastionSubnetPrefix string

resource hubVnet 'Microsoft.Network/virtualNetworks@2024-05-01' = {
  name: 'vnet-hub-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [hubVnetAddressPrefix]
    }
    subnets: [
      {
        name: 'GatewaySubnet'
        properties: {
          addressPrefix: gatewaySubnetPrefix
        }
      }
      {
        name: 'AzureFirewallSubnet'
        properties: {
          addressPrefix: firewallSubnetPrefix
        }
      }
      {
        name: 'AzureBastionSubnet'
        properties: {
          addressPrefix: bastionSubnetPrefix
        }
      }
    ]
  }
}

output hubVnetId string = hubVnet.id
output hubVnetName string = hubVnet.name
output gatewaySubnetId string = hubVnet.properties.subnets[0].id
output firewallSubnetId string = hubVnet.properties.subnets[1].id
output bastionSubnetId string = hubVnet.properties.subnets[2].id
