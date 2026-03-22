// ============================================================
// Azure Databricks — Premium SKU
// ============================================================

param location string
param projectPrefix string

var databricksName = 'dbw-${projectPrefix}-${uniqueString(resourceGroup().id)}'

resource databricks 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name: databricksName
  location: location
  sku: {
    name: 'premium'
  }
  properties: {
    managedResourceGroupId: subscriptionResourceId('Microsoft.Resources/resourceGroups', 'rg-dbw-managed-${uniqueString(resourceGroup().id)}')
    publicNetworkAccess: 'Disabled'
    requiredNsgRules: 'AllRules'
  }
}

output databricksId string = databricks.id
output databricksName string = databricks.name
output databricksUrl string = databricks.properties.workspaceUrl
