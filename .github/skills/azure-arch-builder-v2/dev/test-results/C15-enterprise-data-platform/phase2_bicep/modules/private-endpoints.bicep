// ============================================================
// Private Endpoints — Storage(blob+dfs), KV, SQL, Databricks, ADF
// ============================================================

param location string
param vnetId string
param peSubnetId string
param storageId string
param keyVaultId string
param sqlServerId string
param databricksId string
param dataFactoryId string

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
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peStorageBlob 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-storage-blob-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'storage-blob'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['blob']
        }
      }
    ]
  }
}

resource peStorageBlobDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peStorageBlob
  name: 'blob-dns-group'
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
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peStorageDfs 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-storage-dfs-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'storage-dfs'
        properties: {
          privateLinkServiceId: storageId
          groupIds: ['dfs']
        }
      }
    ]
  }
}

resource peStorageDfsDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peStorageDfs
  name: 'dfs-dns-group'
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
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peKeyVault 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-kv-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'kv-conn'
        properties: {
          privateLinkServiceId: keyVaultId
          groupIds: ['vault']
        }
      }
    ]
  }
}

resource peKeyVaultDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peKeyVault
  name: 'kv-dns-group'
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

// ── SQL PE ────────────────────────────────────────────────
resource dnsZoneSql 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.database.windows.net'
  location: 'global'
}

resource dnsZoneSqlLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneSql
  name: 'link-sql'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peSql 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-sql-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'sql-conn'
        properties: {
          privateLinkServiceId: sqlServerId
          groupIds: ['sqlServer']
        }
      }
    ]
  }
}

resource peSqlDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peSql
  name: 'sql-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'sql-config'
        properties: {
          privateDnsZoneId: dnsZoneSql.id
        }
      }
    ]
  }
}

// ── Databricks PE ─────────────────────────────────────────
resource dnsZoneDatabricks 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.azuredatabricks.net'
  location: 'global'
}

resource dnsZoneDatabricksLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneDatabricks
  name: 'link-databricks'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peDatabricks 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-dbw-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'dbw-conn'
        properties: {
          privateLinkServiceId: databricksId
          groupIds: ['databricks_ui_api']
        }
      }
    ]
  }
}

resource peDatabricksDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peDatabricks
  name: 'dbw-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'dbw-config'
        properties: {
          privateDnsZoneId: dnsZoneDatabricks.id
        }
      }
    ]
  }
}

// ── Data Factory PE ───────────────────────────────────────
resource dnsZoneAdf 'Microsoft.Network/privateDnsZones@2024-06-01' = {
  name: 'privatelink.datafactory.azure.net'
  location: 'global'
}

resource dnsZoneAdfLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2024-06-01' = {
  parent: dnsZoneAdf
  name: 'link-adf'
  location: 'global'
  properties: {
    virtualNetwork: {
      id: vnetId
    }
    registrationEnabled: false
  }
}

resource peAdf 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: 'pe-adf-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    subnet: {
      id: peSubnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'adf-conn'
        properties: {
          privateLinkServiceId: dataFactoryId
          groupIds: ['dataFactory']
        }
      }
    ]
  }
}

resource peAdfDns 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2024-05-01' = {
  parent: peAdf
  name: 'adf-dns-group'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'adf-config'
        properties: {
          privateDnsZoneId: dnsZoneAdf.id
        }
      }
    ]
  }
}
