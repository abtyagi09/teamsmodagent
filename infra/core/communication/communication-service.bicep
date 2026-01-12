@description('Name of the Communication Service')
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

@description('Email service domain resource ID')
param emailDomainId string

resource communicationService 'Microsoft.Communication/communicationServices@2023-04-01' = {
  name: name
  location: 'global'
  tags: tags
  properties: {
    dataLocation: dataLocation
    linkedDomains: [
      emailDomainId
    ]
  }
}

output id string = communicationService.id
output name string = communicationService.name
output endpoint string = communicationService.properties.hostName
output connectionString string = listKeys(communicationService.id, '2023-04-01').primaryConnectionString
