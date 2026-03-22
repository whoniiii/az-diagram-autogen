// ============================================================
// Microsoft Fabric Capacity — F64
// administration.members 필수
// ============================================================

param location string
param adminEmail string

var fabricName = 'fabric${uniqueString(resourceGroup().id)}'

resource fabricCapacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: fabricName
  location: location
  sku: {
    name: 'F64'
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: [adminEmail]
    }
  }
}

output fabricCapacityId string = fabricCapacity.id
output fabricCapacityName string = fabricCapacity.name
