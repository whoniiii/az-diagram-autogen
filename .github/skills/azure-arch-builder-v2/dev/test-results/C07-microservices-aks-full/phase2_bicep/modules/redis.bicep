// ============================================================
// Azure Cache for Redis — Standard C1
// ============================================================

param location string

var redisName = 'redis-${uniqueString(resourceGroup().id)}'

resource redis 'Microsoft.Cache/redis@2024-11-01' = {
  name: redisName
  location: location
  properties: {
    sku: {
      name: 'Standard'
      family: 'C'
      capacity: 1
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
}

output redisId string = redis.id
output redisName string = redis.name
output redisHostName string = redis.properties.hostName
