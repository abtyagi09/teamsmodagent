@description('Name of the AI Foundry Hub')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('AI Foundry Hub SKU')
param sku object = {
  name: 'S0'
}

@description('AI Foundry Hub kind')
param kind string = 'AIServices'

// AI Foundry Hub (Cognitive Services Account for AI Foundry)
resource aiFoundryHub 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: name
  location: location
  tags: tags
  kind: kind
  sku: sku
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: name
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

output id string = aiFoundryHub.id
output name string = aiFoundryHub.name
output endpoint string = aiFoundryHub.properties.endpoint
output identityPrincipalId string = aiFoundryHub.identity.principalId