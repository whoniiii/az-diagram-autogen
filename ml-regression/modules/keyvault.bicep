// ============================================================
// Key Vault — 시크릿 관리 (RBAC 인증)
// ============================================================

param location string
param projectPrefix string
param tenantId string

var keyVaultName = 'kv-${uniqueString(resourceGroup().id, projectPrefix)}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output keyVaultId string = keyVault.id
output keyVaultName string = keyVault.name
