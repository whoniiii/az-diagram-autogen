// ============================================================
// Azure Bastion + Public IP
// ============================================================

param location string
param projectPrefix string
param bastionSubnetId string

resource bastionPublicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: 'pip-bastion-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource bastion 'Microsoft.Network/bastionHosts@2024-05-01' = {
  name: 'bastion-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    ipConfigurations: [
      {
        name: 'bastionIpConfig'
        properties: {
          publicIPAddress: { id: bastionPublicIp.id }
          subnet: { id: bastionSubnetId }
        }
      }
    ]
  }
}

output bastionId string = bastion.id
output bastionName string = bastion.name
