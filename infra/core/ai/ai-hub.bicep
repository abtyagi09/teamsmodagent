@description('Name of the AI Hub')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('Storage account resource ID')
param storageAccountId string

@description('Key Vault resource ID')
param keyVaultId string

@description('Application Insights resource ID')
param applicationInsightsId string

@description('Container Registry resource ID')
param containerRegistryId string

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'Hub'
  properties: {
    friendlyName: name
    description: 'AI Hub for Teams Moderation Agent'
    storageAccount: storageAccountId
    keyVault: keyVaultId
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    publicNetworkAccess: 'Enabled'
  }
}

output id string = aiHub.id
output name string = aiHub.name
output identityPrincipalId string = aiHub.identity.principalId
