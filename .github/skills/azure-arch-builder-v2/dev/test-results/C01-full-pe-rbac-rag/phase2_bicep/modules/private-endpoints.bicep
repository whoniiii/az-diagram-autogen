// ============================================================
// Private Endpoints + DNS Zones + VNet Links + DNS Zone Groups
// Foundry: 2 DNS zones (cognitiveservices + openai)
// ADLS Gen2: 2 PEs (blob + dfs)
// ============================================================

param location string
param vnetId string
param peSubnetId string
param foundryId string
param searchId string
param storageId string
param keyVaultId string

// ── Foundry PE ────────────────────────────────────────────
resource dnsZoneCognitive 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.cognitiveservices.azure.com'
  location: 'global'
}

resource dnsZoneOpenAI 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.openai.azure.com'
  location: 'global'
}

resource dnsZoneCognitiveLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneCognitive
  name: 'link-cognitive'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource dnsZoneOpenAILink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneOpenAI
  name: 'link-openai'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource peFoundry 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-foundry-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'foundry-connection'
        properties: {
          privateLinkServiceId: foundryId
          groupIds: ['account']
        }
      }
    ]
  }
}

resource peFoundryDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peFoundry
  name: 'foundry-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'cognitive-config'
        properties: {
          privateDnsZoneId: dnsZoneCognitive.id
        }
      }
      {
        name: 'openai-config'
        properties: {
          privateDnsZoneId: dnsZoneOpenAI.id
        }
      }
    ]
  }
}

// ── AI Search PE ──────────────────────────────────────────
resource dnsZoneSearch 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.search.windows.net'
  location: 'global'
}

resource dnsZoneSearchLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneSearch
  name: 'link-search'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource peSearch 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-search-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'search-connection'
        properties: {
          privateLinkServiceId: searchId
          groupIds: ['searchService']
        }
      }
    ]
  }
}

resource peSearchDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peSearch
  name: 'search-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'search-config'
        properties: {
          privateDnsZoneId: dnsZoneSearch.id
        }
      }
    ]
  }
}

// ── Storage Blob PE ───────────────────────────────────────
resource dnsZoneBlob 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
}

resource dnsZoneBlobLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneBlob
  name: 'link-blob'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource peStorageBlob 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-storage-blob-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'storage-blob-connection'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['blob']
        }
      }
    ]
  }
}

resource peStorageBlobDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peStorageBlob
  name: 'storage-blob-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'blob-config'
        properties: {
          privateDnsZoneId: dnsZoneBlob.id
        }
      }
    ]
  }
}

// ── Storage DFS PE (ADLS Gen2 필수) ───────────────────────
resource dnsZoneDfs 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.dfs.core.windows.net'
  location: 'global'
}

resource dnsZoneDfsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneDfs
  name: 'link-dfs'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource peStorageDfs 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-storage-dfs-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'storage-dfs-connection'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['dfs']
        }
      }
    ]
  }
}

resource peStorageDfsDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peStorageDfs
  name: 'storage-dfs-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dfs-config'
        properties: {
          privateDnsZoneId: dnsZoneDfs.id
        }
      }
    ]
  }
}

// ── Key Vault PE ──────────────────────────────────────────
resource dnsZoneVault 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
}

resource dnsZoneVaultLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneVault
  name: 'link-vault'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource peKeyVault 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-kv-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'keyvault-connection'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: ['vault']
        }
      }
    ]
  }
}

resource peKeyVaultDnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peKeyVault
  name: 'keyvault-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'vault-config'
        properties: {
          privateDnsZoneId: dnsZoneVault.id
        }
      }
    ]
  }
}
