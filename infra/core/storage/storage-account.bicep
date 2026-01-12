metadata description = 'Creates an Azure Storage Account for AI Foundry.'

@description('The name of the storage account')
param name string

@description('The location of the storage account')
param location string = resourceGroup().location

@description('Tags for the resource')
param tags object = {}

@description('Storage account SKU')
param sku string = 'Standard_LRS'

@description('Storage account kind')
param kind string = 'StorageV2'

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  kind: kind
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    supportsHttpsTrafficOnly: true
  }
}

output id string = storage.id
output name string = storage.name
output primaryEndpoints object = storage.properties.primaryEndpoints
