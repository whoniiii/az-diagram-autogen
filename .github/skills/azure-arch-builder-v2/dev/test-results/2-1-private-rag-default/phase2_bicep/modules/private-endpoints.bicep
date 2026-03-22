// ============================================================
// Private Endpoints — Foundry, Search, Storage, Key Vault
// 각 서비스: PE + Private DNS Zone + VNet Link + DNS Zone Group
// ============================================================

param location string
param vnetId string
param peSubnetId string
param foundryId string
param foundryName string
param searchId string
param searchName string
param storageId string
param storageName string
param keyVaultId string
param keyVaultName string

// ── Foundry PE ────────────────────────────────────────────
resource peFoundry 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-${foundryName}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'plsc-foundry'
        properties: {
          privateLinkServiceId: foundryId
          groupIds: [
            'account'
          ]
        }
      }
    ]
  }
}

resource dnsZoneFoundry 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.cognitiveservices.azure.com'
  location: 'global'
}

resource vnetLinkFoundry 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneFoundry
  name: 'link-foundry'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource dnsGroupFoundry 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peFoundry
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config-foundry'
        properties: {
          privateDnsZoneId: dnsZoneFoundry.id
        }
      }
    ]
  }
}

// ── OpenAI DNS Zone (Foundry AIServices에 추가 필요) ──────
resource dnsZoneOpenAI 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.openai.azure.com'
  location: 'global'
}

resource vnetLinkOpenAI 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneOpenAI
  name: 'link-openai'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

// ── Search PE ─────────────────────────────────────────────
resource peSearch 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-${searchName}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'plsc-search'
        properties: {
          privateLinkServiceId: searchId
          groupIds: [
            'searchService'
          ]
        }
      }
    ]
  }
}

resource dnsZoneSearch 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.search.windows.net'
  location: 'global'
}

resource vnetLinkSearch 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneSearch
  name: 'link-search'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource dnsGroupSearch 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peSearch
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config-search'
        properties: {
          privateDnsZoneId: dnsZoneSearch.id
        }
      }
    ]
  }
}

// ── Storage PE ────────────────────────────────────────────
resource peStorage 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-${storageName}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'plsc-storage'
        properties: {
          privateLinkServiceId: storageId
          groupIds: [
            'blob'
          ]
        }
      }
    ]
  }
}

resource dnsZoneStorage 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.blob.${environment().suffixes.storage}'
  location: 'global'
}

resource vnetLinkStorage 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneStorage
  name: 'link-storage'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource dnsGroupStorage 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peStorage
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config-storage'
        properties: {
          privateDnsZoneId: dnsZoneStorage.id
        }
      }
    ]
  }
}

// ── Key Vault PE ──────────────────────────────────────────
resource peKeyVault 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-${keyVaultName}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'plsc-keyvault'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: [
            'vault'
          ]
        }
      }
    ]
  }
}

resource dnsZoneKeyVault 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
}

resource vnetLinkKeyVault 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneKeyVault
  name: 'link-keyvault'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource dnsGroupKeyVault 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peKeyVault
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'config-keyvault'
        properties: {
          privateDnsZoneId: dnsZoneKeyVault.id
        }
      }
    ]
  }
}
