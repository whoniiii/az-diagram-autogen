// ============================================================
// Private Endpoints — AML Workspace + Storage + Key Vault
// ============================================================

param location string
param vnetId string
param peSubnetId string
param workspaceId string
param storageId string
param keyVaultId string

// ── AML Workspace PE ────────────────────────────────────────
resource peAml 'Microsoft.Network/privateEndpoints@2025-05-01' = {
  name: 'pe-mlworkspace'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'pls-mlworkspace'
        properties: {
          privateLinkServiceId: workspaceId
          groupIds: ['amlworkspace']
        }
      }
    ]
  }
}

resource dnsZoneAml 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.api.azureml.ms'
  location: 'global'
}

resource dnsZoneAmlNotebooks 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.notebooks.azure.net'
  location: 'global'
}

resource vnetLinkAml 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneAml
  name: 'link-aml'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource vnetLinkAmlNotebooks 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneAmlNotebooks
  name: 'link-aml-notebooks'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource dnsGroupAml 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2025-05-01' = {
  parent: peAml
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'aml-zone'
        properties: { privateDnsZoneId: dnsZoneAml.id }
      }
      {
        name: 'aml-notebooks-zone'
        properties: { privateDnsZoneId: dnsZoneAmlNotebooks.id }
      }
    ]
  }
}

// ── Storage PE (blob) ───────────────────────────────────────
resource peStorage 'Microsoft.Network/privateEndpoints@2025-05-01' = {
  name: 'pe-storage-blob'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'pls-storage-blob'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['blob']
        }
      }
    ]
  }
}

resource dnsZoneBlob 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
}

resource vnetLinkBlob 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneBlob
  name: 'link-blob'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource dnsGroupBlob 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2025-05-01' = {
  parent: peStorage
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'blob-zone'
        properties: { privateDnsZoneId: dnsZoneBlob.id }
      }
    ]
  }
}

// ── Storage PE (file — AML 필수) ────────────────────────────
resource peStorageFile 'Microsoft.Network/privateEndpoints@2025-05-01' = {
  name: 'pe-storage-file'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'pls-storage-file'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['file']
        }
      }
    ]
  }
}

resource dnsZoneFile 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.file.core.windows.net'
  location: 'global'
}

resource vnetLinkFile 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneFile
  name: 'link-file'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource dnsGroupFile 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2025-05-01' = {
  parent: peStorageFile
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'file-zone'
        properties: { privateDnsZoneId: dnsZoneFile.id }
      }
    ]
  }
}

// ── Key Vault PE ────────────────────────────────────────────
resource peKv 'Microsoft.Network/privateEndpoints@2025-05-01' = {
  name: 'pe-keyvault'
  location: location
  properties: {
    subnet: { id: peSubnetId }
    privateLinkServiceConnections: [
      {
        name: 'pls-keyvault'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: ['vault']
        }
      }
    ]
  }
}

resource dnsZoneKv 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.vaultcore.azure.net'
  location: 'global'
}

resource vnetLinkKv 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneKv
  name: 'link-kv'
  location: 'global'
  properties: {
    virtualNetwork: { id: vnetId }
    registrationEnabled: false
  }
}

resource dnsGroupKv 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2025-05-01' = {
  parent: peKv
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'kv-zone'
        properties: { privateDnsZoneId: dnsZoneKv.id }
      }
    ]
  }
}
