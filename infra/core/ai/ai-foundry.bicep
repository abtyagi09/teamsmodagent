@description('Name of the AI Foundry project')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('Name of the model deployment')
param modelDeploymentName string = 'gpt-4o-mini'

// Azure OpenAI resource for AI agent functionality
resource azureOpenAI 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: name
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

// Model deployment for gpt-4o-mini
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  name: modelDeploymentName
  parent: azureOpenAI
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
      version: '2024-07-18'
    }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
    currentCapacity: 10
  }
}

output id string = azureOpenAI.id
output name string = azureOpenAI.name
output endpoint string = azureOpenAI.properties.endpoint
output identityPrincipalId string = azureOpenAI.identity.principalId
output modelDeploymentName string = modelDeploymentName
