// ============================================================
// VNet Peering — Hub ↔ Spoke
// ============================================================

param hubVnetName string
param spokeVnetName string
param hubVnetId string
param spokeVnetId string

resource hubToSpokePeering 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2024-05-01' = {
  name: '${hubVnetName}/hub-to-spoke'
  properties: {
    remoteVirtualNetwork: { id: spokeVnetId }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: true
    useRemoteGateways: false
  }
}

resource spokeToHubPeering 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2024-05-01' = {
  name: '${spokeVnetName}/spoke-to-hub'
  properties: {
    remoteVirtualNetwork: { id: hubVnetId }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: false
    useRemoteGateways: true
  }
}
