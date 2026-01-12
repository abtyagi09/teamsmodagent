@description('Name of the AI Foundry Project')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('AI Foundry Hub name')
param aiFoundryHubName string

@description('Model deployment name')
param modelDeploymentName string = 'gpt-4o-mini'

resource aiFoundryHub 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: aiFoundryHubName
}

// AI Foundry Project (Cognitive Services Account Project) 
resource aiFoundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  name: name
  parent: aiFoundryHub
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

// Model deployment for the hub (OpenAI models are deployed to the hub, not the project)
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: modelDeploymentName
  parent: aiFoundryHub
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
    }
  }
}

output id string = aiFoundryProject.id
output name string = aiFoundryProject.name
output endpoint string = aiFoundryProject.properties.endpoints['AI Foundry API']
output hubId string = aiFoundryHub.id
output hubName string = aiFoundryHub.name
output hubEndpoint string = aiFoundryHub.properties.endpoint
output deploymentName string = modelDeployment.name