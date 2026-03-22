// ============================================================
// Azure AI Search — Standard S1, Semantic Ranking
// ============================================================

param location string

var searchName = 'srch-${uniqueString(resourceGroup().id)}'

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: searchName
  location: location
  sku: {
    name: 'standard'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    hostingMode: 'default'
    publicNetworkAccess: 'disabled'
    partitionCount: 1
    replicaCount: 1
    semanticSearch: 'standard'
  }
}

output searchId string = searchService.id
output searchName string = searchService.name
output searchEndpoint string = 'https://${searchService.name}.search.windows.net'
