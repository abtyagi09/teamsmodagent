@description('Name of the App Configuration store')
param name string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Tags for the resources')
param tags object = {}

@description('SKU of App Configuration store')
@allowed([
  'free'
  'standard'
])
param sku string = 'standard'

@description('Enable public network access')
param publicNetworkAccess string = 'Enabled'

resource appConfig 'Microsoft.AppConfiguration/configurationStores@2023-03-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    publicNetworkAccess: publicNetworkAccess
  }
}

output id string = appConfig.id
output name string = appConfig.name
output endpoint string = appConfig.properties.endpoint
