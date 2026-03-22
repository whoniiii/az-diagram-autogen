// ============================================================
// SQL Server + Database — AAD-only Auth
// ============================================================

param location string
param sqlAdminLogin string
@secure()
param sqlAdminPassword string
param aadAdminLogin string
param aadAdminObjectId string
param aadAdminTenantId string

var sqlServerName = 'sql-${uniqueString(resourceGroup().id)}'

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    administratorLogin: sqlAdminLogin
    administratorLoginPassword: sqlAdminPassword
    minimalTlsVersion: '1.2'
    administrators: {
      administratorType: 'ActiveDirectory'
      login: aadAdminLogin
      sid: aadAdminObjectId
      tenantId: aadAdminTenantId
      azureADOnlyAuthentication: true
    }
  }
}

resource sqlDb 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: 'db-workload'
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
  }
  properties: {}
}

output sqlServerId string = sqlServer.id
output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
