// ============================================================
// AKS Cluster — Private, Azure CNI
// ============================================================

param location string
param projectPrefix string
param aksSubnetId string
param appGwId string

var aksName = 'aks-${projectPrefix}-${uniqueString(resourceGroup().id)}'

resource aksCluster 'Microsoft.ContainerService/managedClusters@2024-09-01' = {
  name: aksName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: 'aks-${uniqueString(resourceGroup().id)}'
    apiServerAccessProfile: {
      enablePrivateCluster: true
    }
    networkProfile: {
      networkPlugin: 'azure'
      serviceCidr: '10.2.0.0/16'
      dnsServiceIP: '10.2.0.10'
    }
    agentPoolProfiles: [
      {
        name: 'system'
        count: 3
        vmSize: 'Standard_D4s_v5'
        mode: 'System'
        osType: 'Linux'
        vnetSubnetID: aksSubnetId
      }
    ]
    ingressProfile: {
      webAppRouting: {
        enabled: false
      }
    }
    addonProfiles: {
      ingressApplicationGateway: {
        enabled: true
        config: {
          applicationGatewayId: appGwId
        }
      }
      azureKeyvaultSecretsProvider: {
        enabled: true
      }
    }
  }
}

output aksClusterName string = aksCluster.name
output aksClusterId string = aksCluster.id
output aksPrincipalId string = aksCluster.identity.principalId
