@description('Name of the AI Project')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('AI Hub resource name')
param aiHubName string

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' existing = {
  name: aiHubName
}

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'Project'
  properties: {
    friendlyName: name
    description: 'AI Project for Teams Moderation Agent'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

output id string = aiProject.id
output name string = aiProject.name
output endpoint string = 'https://${location}.api.azureml.ms/api/projects/${name}'
output identityPrincipalId string = aiProject.identity.principalId
