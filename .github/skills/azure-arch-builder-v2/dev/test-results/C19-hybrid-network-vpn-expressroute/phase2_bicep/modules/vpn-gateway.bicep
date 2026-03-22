// ============================================================
// VPN Gateway + Local Network Gateway + Connection
// ============================================================

param location string
param projectPrefix string
param gatewaySubnetId string
param onPremisesAddressPrefix string
param vpnGatewaySharedKey string
param localGatewayIpAddress string

resource vpnPublicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: 'pip-vpngw-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

resource vpnGateway 'Microsoft.Network/virtualNetworkGateways@2024-05-01' = {
  name: 'vpngw-${projectPrefix}-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    gatewayType: 'Vpn'
    vpnType: 'RouteBased'
    sku: {
      name: 'VpnGw1'
      tier: 'VpnGw1'
    }
    ipConfigurations: [
      {
        name: 'vpnGwIpConfig'
        properties: {
          publicIPAddress: { id: vpnPublicIp.id }
          subnet: { id: gatewaySubnetId }
        }
      }
    ]
  }
}

resource localNetworkGateway 'Microsoft.Network/localNetworkGateways@2024-05-01' = {
  name: 'lgw-onprem-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    gatewayIpAddress: localGatewayIpAddress
    localNetworkAddressSpace: {
      addressPrefixes: [onPremisesAddressPrefix]
    }
  }
}

resource vpnConnection 'Microsoft.Network/connections@2024-05-01' = {
  name: 'conn-s2s-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    connectionType: 'IPsec'
    virtualNetworkGateway1: { id: vpnGateway.id }
    localNetworkGateway2: { id: localNetworkGateway.id }
    sharedKey: vpnGatewaySharedKey
    connectionProtocol: 'IKEv2'
  }
}

output vpnGatewayId string = vpnGateway.id
output vpnPublicIp string = vpnPublicIp.properties.ipAddress
