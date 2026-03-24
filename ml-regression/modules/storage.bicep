// ============================================================
// Storage Account — 학습 데이터 + 모델 아티팩트 저장
// ============================================================

param location string
param projectPrefix string

var storageName = 'st${uniqueString(resourceGroup().id, projectPrefix)}'

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageName
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output storageId string = storage.id
output storageName string = storage.name
