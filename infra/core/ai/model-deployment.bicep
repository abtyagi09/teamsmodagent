@description('AI Project name')
param projectName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Model deployment name')
param deploymentName string = 'gpt-4o-mini'

@description('Model name')
param modelName string = 'gpt-4o-mini'

@description('Model version')
param modelVersion string = '2024-07-18'

@description('Model format')
param modelFormat string = 'OpenAI'

@description('Deployment SKU name')
param skuName string = 'Standard'

@description('Deployment capacity')
param skuCapacity int = 10

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = {
  name: projectName
}

resource modelDeployment 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2024-04-01' = {
  name: deploymentName
  parent: aiProject
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'Managed'
  properties: {
    authMode: 'Key'
    description: 'GPT-4o mini deployment for moderation'
  }
}

resource deployment 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints/deployments@2024-04-01' = {
  name: deploymentName
  parent: modelDeployment
  location: location
  sku: {
    name: skuName
    capacity: skuCapacity
  }
  properties: {
    model: {
      name: modelName
      version: modelVersion
      format: modelFormat
    }
  }
}

output deploymentName string = deployment.name
output endpointName string = modelDeployment.name
