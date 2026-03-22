// ============================================================
// Azure SQL Server + Database
// ============================================================

param location string
param sqlServerName string = 'sql-${uniqueString(resourceGroup().id)}'
param sqlDatabaseName string = 'sqldb-${uniqueString(resourceGroup().id)}'
param sqlAdminLogin string = 'sqladmin'

@secure()
param sqlAdminPassword string = newGuid()

resource sqlServer 'Microsoft.Sql/servers@2024-05-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
  }
}

// Azure 서비스 접근 허용 방화벽 규칙
resource firewallRule 'Microsoft.Sql/servers/firewallRules@2024-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2024-05-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  sku: {
    name: 'S0'
    tier: 'Standard'
  }
  properties: {
    maxSizeBytes: 268435456000
    collation: 'SQL_Latin1_General_CP1_CI_AS'
  }
}

output sqlServerId string = sqlServer.id
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDatabase.name
