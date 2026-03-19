@description('Azure 리전')
param location string

@description('VNet ID')
param vnetId string

@description('PE 서브넷 ID')
param peSubnetId string

@description('Foundry 리소스 ID')
param foundryId string

@description('AI Search 리소스 ID')
param searchId string

@description('Storage 리소스 ID')
param storageId string

@description('Key Vault 리소스 ID')
param keyVaultId string

// PE 구성 정의
var peConfigs = [
  {
    name: 'pe-foundry'
    serviceId: foundryId
    groupId: 'account'
    dnsZoneName: 'privatelink.cognitiveservices.azure.com'
  }
  {
    name: 'pe-search'
    serviceId: searchId
    groupId: 'searchService'
    dnsZoneName: 'privatelink.search.windows.net'
  }
  {
    name: 'pe-storage-blob'
    serviceId: storageId
    groupId: 'blob'
    #disable-next-line no-hardcoded-env-urls
    dnsZoneName: 'privatelink.blob.core.windows.net'
  }
  {
    name: 'pe-keyvault'
    serviceId: keyVaultId
    groupId: 'vault'
    dnsZoneName: 'privatelink.vaultcore.azure.net'
  }
]

// ── Private DNS Zones ──
resource dnsZones 'Microsoft.Network/privateDnsZones@2020-06-01' = [for config in peConfigs: {
  name: config.dnsZoneName
  location: 'global'
}]

// ── VNet Links ──
resource vnetLinks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = [for (config, i) in peConfigs: {
  parent: dnsZones[i]
  name: '${config.name}-vnet-link'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}]

// ── Private Endpoints ──
resource privateEndpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = [for config in peConfigs: {
  name: config.name
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'pls-${config.name}'
        properties: {
          privateLinkServiceId: config.serviceId
          groupIds: [config.groupId]
        }
      }
    ]
  }
}]

// ── DNS Zone Groups ──
resource dnsZoneGroups 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = [for (config, i) in peConfigs: {
  parent: privateEndpoints[i]
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config'
        properties: {
          privateDnsZoneId: dnsZones[i].id
        }
      }
    ]
  }
}]
