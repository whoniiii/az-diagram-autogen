// ============================================================
// Hybrid Network — Hub-Spoke Architecture — main.bicep
// VPN Gateway + Firewall + Bastion + App Service + SQL + KV
// ============================================================

targetScope = 'resourceGroup'

param location string
param projectPrefix string

// Hub VNet
param hubVnetAddressPrefix string = '10.0.0.0/16'
param gatewaySubnetPrefix string = '10.0.0.0/27'
param firewallSubnetPrefix string = '10.0.1.0/26'
param bastionSubnetPrefix string = '10.0.2.0/26'

// Spoke VNet
param spokeVnetAddressPrefix string = '10.1.0.0/16'
param appSubnetPrefix string = '10.1.0.0/24'
param dataSubnetPrefix string = '10.1.1.0/24'

// VPN
param onPremisesAddressPrefix string = '192.168.0.0/16'
param vpnGatewaySharedKey string = 'YourSharedKey123!'
param localGatewayIpAddress string = '203.0.113.1'

@secure()
param sqlAdminPassword string = newGuid()
param sqlAdminLogin string = 'sqladmin'
param aadAdminLogin string = 'aad-admin'
param aadAdminObjectId string
param aadAdminTenantId string = subscription().tenantId

// ── Hub Network ───────────────────────────────────────────
module hubNetwork './modules/hub-network.bicep' = {
  name: 'deploy-hub-network'
  params: {
    location: location
    projectPrefix: projectPrefix
    hubVnetAddressPrefix: hubVnetAddressPrefix
    gatewaySubnetPrefix: gatewaySubnetPrefix
    firewallSubnetPrefix: firewallSubnetPrefix
    bastionSubnetPrefix: bastionSubnetPrefix
  }
}

// ── Spoke Network ─────────────────────────────────────────
module spokeNetwork './modules/spoke-network.bicep' = {
  name: 'deploy-spoke-network'
  params: {
    location: location
    projectPrefix: projectPrefix
    spokeVnetAddressPrefix: spokeVnetAddressPrefix
    appSubnetPrefix: appSubnetPrefix
    dataSubnetPrefix: dataSubnetPrefix
  }
}

// ── VNet Peering ──────────────────────────────────────────
module peering './modules/peering.bicep' = {
  name: 'deploy-peering'
  params: {
    hubVnetName: hubNetwork.outputs.hubVnetName
    spokeVnetName: spokeNetwork.outputs.spokeVnetName
    hubVnetId: hubNetwork.outputs.hubVnetId
    spokeVnetId: spokeNetwork.outputs.spokeVnetId
  }
}

// ── VPN Gateway ───────────────────────────────────────────
module vpnGateway './modules/vpn-gateway.bicep' = {
  name: 'deploy-vpn-gateway'
  params: {
    location: location
    projectPrefix: projectPrefix
    gatewaySubnetId: hubNetwork.outputs.gatewaySubnetId
    onPremisesAddressPrefix: onPremisesAddressPrefix
    vpnGatewaySharedKey: vpnGatewaySharedKey
    localGatewayIpAddress: localGatewayIpAddress
  }
}

// ── Azure Firewall ────────────────────────────────────────
module firewall './modules/firewall.bicep' = {
  name: 'deploy-firewall'
  params: {
    location: location
    projectPrefix: projectPrefix
    firewallSubnetId: hubNetwork.outputs.firewallSubnetId
  }
}

// ── Azure Bastion ─────────────────────────────────────────
module bastion './modules/bastion.bicep' = {
  name: 'deploy-bastion'
  params: {
    location: location
    projectPrefix: projectPrefix
    bastionSubnetId: hubNetwork.outputs.bastionSubnetId
  }
}

// ── App Service ───────────────────────────────────────────
module appService './modules/appservice.bicep' = {
  name: 'deploy-appservice'
  params: {
    location: location
    projectPrefix: projectPrefix
    appSubnetId: spokeNetwork.outputs.appSubnetId
  }
}

// ── SQL ───────────────────────────────────────────────────
module sql './modules/sql.bicep' = {
  name: 'deploy-sql'
  params: {
    location: location
    sqlAdminLogin: sqlAdminLogin
    sqlAdminPassword: sqlAdminPassword
    aadAdminLogin: aadAdminLogin
    aadAdminObjectId: aadAdminObjectId
    aadAdminTenantId: aadAdminTenantId
  }
}

// ── Key Vault ─────────────────────────────────────────────
module keyVault './modules/keyvault.bicep' = {
  name: 'deploy-keyvault'
  params: {
    location: location
  }
}

// ── 출력 ──────────────────────────────────────────────────
output hubVnetId string = hubNetwork.outputs.hubVnetId
output spokeVnetId string = spokeNetwork.outputs.spokeVnetId
output firewallPrivateIp string = firewall.outputs.firewallPrivateIp
output bastionName string = bastion.outputs.bastionName
output appServiceUrl string = appService.outputs.appServiceUrl
output sqlServerFqdn string = sql.outputs.sqlServerFqdn
output keyVaultName string = keyVault.outputs.keyVaultName
