@description('Name of the Email Communication Service')
param name string

@description('Location for the resource')
param location string = resourceGroup().location

@description('Tags for the resource')
param tags object = {}

@description('Data location')
@allowed([
  'United States'
  'Europe'
  'Asia Pacific'
  'United Kingdom'
  'France'
  'Germany'
  'Switzerland'
  'Norway'
  'United Arab Emirates'
  'Australia'
])
param dataLocation string = 'United States'

resource emailService 'Microsoft.Communication/emailServices@2023-04-01' = {
  name: name
  location: 'global'
  tags: tags
  properties: {
    dataLocation: dataLocation
  }
}

// Default domain (Azure Managed Domain - free)
resource emailDomain 'Microsoft.Communication/emailServices/domains@2023-04-01' = {
  parent: emailService
  name: 'AzureManagedDomain'
  location: 'global'
  properties: {
    domainManagement: 'AzureManaged'
  }
}

output id string = emailService.id
output name string = emailService.name
output domainId string = emailDomain.id
output domainName string = emailDomain.properties.mailFromSenderDomain
