@description('Name of the Service Bus namespace')
param name string

@description('Location for the resource')
param location string = resourceGroup().location

@description('Tags for the resource')
param tags object = {}

@description('SKU name')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Standard'

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
    tier: skuName
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true // Force managed identity authentication
  }
}

// Queue for Teams messages
resource messagesQueue 'Microsoft.ServiceBus/namespaces/queues@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'teams-messages'
  properties: {
    maxDeliveryCount: 10
    lockDuration: 'PT5M' // 5 minutes
    defaultMessageTimeToLive: 'P1D' // 1 day
    deadLetteringOnMessageExpiration: true
    enablePartitioning: false
    requiresDuplicateDetection: false
  }
}

output id string = serviceBusNamespace.id
output name string = serviceBusNamespace.name
output endpoint string = serviceBusNamespace.properties.serviceBusEndpoint
output queueName string = messagesQueue.name
