@description('프로젝트 이름')
param projectName string

@description('Azure 리전')
param location string

@description('환경')
param env string

var searchName = 'srch-${projectName}-${env}'

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchName
  location: location
  sku: { name: 'basic' }
  identity: { type: 'SystemAssigned' }
  properties: {
    hostingMode: 'Default'
    publicNetworkAccess: 'disabled'
    semanticSearch: 'free'
  }
}

output searchId string = search.id
output searchName string = search.name
