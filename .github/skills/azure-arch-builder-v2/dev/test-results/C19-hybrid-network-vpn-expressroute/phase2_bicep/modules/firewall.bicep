// ============================================================
// Azure Firewall Premium + Firewall Policy
// ============================================================

param location string
param projectPrefix string
param firewallSubnetId string

resource firewallPublicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: 'pip-fw-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource firewallPolicy 'Microsoft.Network/firewallPolicies@2024-05-01' = {
  name: 'fwpol-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      tier: 'Premium'
    }
    threatIntelMode: 'Deny'
  }
}

resource firewall 'Microsoft.Network/azureFirewalls@2024-05-01' = {
  name: 'fw-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'AZFW_VNet'
      tier: 'Premium'
    }
    firewallPolicy: { id: firewallPolicy.id }
    ipConfigurations: [
      {
        name: 'fwIpConfig'
        properties: {
          publicIPAddress: { id: firewallPublicIp.id }
          subnet: { id: firewallSubnetId }
        }
      }
    ]
  }
}

output firewallId string = firewall.id
output firewallName string = firewall.name
output firewallPrivateIp string = firewall.properties.ipConfigurations[0].properties.privateIPAddress
