// ============================================================
// Azure AI Search — 벡터 + 시맨틱 검색 (Private)
// ============================================================

param location string
param searchName string = 'srch-${uniqueString(resourceGroup().id)}'
param skuName string = 'standard'

resource search 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: searchName
  location: location
  sku: {
    name: skuName
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'disabled'
    semanticSearch: 'standard'
  }
}

output searchId string = search.id
output searchName string = search.name
output searchEndpoint string = 'https://${search.name}.search.windows.net'
