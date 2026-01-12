targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment to be used as a prefix for all resources')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name for the container registry')
param containerRegistryName string = ''

@description('Name for the Container Apps environment')
param containerAppsEnvironmentName string = ''

@description('Name for the agent container app')
param agentContainerAppName string = ''

@description('Name for the UI container app')
param uiContainerAppName string = ''

@description('CPU cores for agent container (e.g., 0.5, 1.0)')
param agentCpu string = '0.5'

@description('Memory for agent container (e.g., 1.0Gi)')
param agentMemory string = '1.0Gi'

@description('CPU cores for UI container (e.g., 0.5, 1.0)')
param uiCpu string = '0.5'

@description('Memory for UI container (e.g., 1.0Gi)')
param uiMemory string = '1.0Gi'

@description('Enable application insights')
param enableApplicationInsights bool = true

@description('Log Analytics workspace name')
param logAnalyticsName string = ''

// Application configuration parameters
@secure()
@description('Content Safety API key')
param contentSafetyKey string

@secure()
@description('Teams client secret')
param teamsClientSecret string



@description('Foundry model deployment name')
param foundryModelDeployment string



@description('Teams tenant ID')
param teamsTenantId string

@description('Teams client ID')
param teamsClientId string

@description('Teams team ID')
param teamsTeamId string

@description('Email sender address (optional - for future use)')
param emailSender string = ''

@description('Email connection string (optional - set manually after deployment)')
param emailConnectionString string = ''

@description('Notification email address (optional)')
param notificationEmail string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// User Assigned Managed Identity (following Microsoft best practices)
module userAssignedIdentity './core/security/managed-identity.bicep' = {
  name: 'user-assigned-identity'
  scope: rg
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container registry
module containerRegistry './core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    tags: tags
  }
}

// Log Analytics workspace
module logAnalytics './core/monitor/loganalytics.bicep' = {
  name: 'log-analytics'
  scope: rg
  params: {
    name: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    location: location
    tags: tags
  }
}

// Application Insights
module applicationInsights './core/monitor/applicationinsights.bicep' = if (enableApplicationInsights) {
  name: 'application-insights'
  scope: rg
  params: {
    name: '${abbrs.insightsComponents}${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// App Configuration
module appConfig './core/config/app-configuration.bicep' = {
  name: 'app-configuration'
  scope: rg
  params: {
    name: '${abbrs.appConfigurationConfigurationStores}${resourceToken}'
    location: location
    tags: tags
    sku: 'standard'
  }
}

// AI Foundry Hub (Azure AI Services for AI Foundry)
module aiFoundryHub './core/ai/ai-foundry-hub.bicep' = {
  name: 'ai-foundry-hub'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    location: location
    tags: tags
  }
}

// AI Foundry Project with model deployment
module aiFoundryProject './core/ai/ai-foundry-project.bicep' = {
  name: 'ai-foundry-project'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServicesAccounts}proj-${resourceToken}'
    location: location
    tags: tags
    aiFoundryHubName: aiFoundryHub.outputs.name
    modelDeploymentName: foundryModelDeployment
  }
}

// Container Apps environment
module containerAppsEnvironment './core/host/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: !empty(containerAppsEnvironmentName) ? containerAppsEnvironmentName : '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceName: logAnalytics.outputs.name
    applicationInsightsName: enableApplicationInsights ? applicationInsights.outputs.name : ''
  }
}

// Agent container app
module agentContainerApp './core/host/container-app.bicep' = {
  name: 'agent-container-app'
  scope: rg
  params: {
    name: !empty(agentContainerAppName) ? agentContainerAppName : '${abbrs.appContainerApps}agent-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'agent' })
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    containerCpuCoreCount: agentCpu
    containerMemory: agentMemory
    containerName: 'agent'
    imageName: 'teams-mod-agent:latest'
    targetPort: 8080
    enableIngress: false
    enableSystemAssignedIdentity: false
    userAssignedIdentityId: userAssignedIdentity.outputs.id
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: userAssignedIdentity.outputs.clientId
      }
      {
        name: 'APP_CONFIG_ENDPOINT'
        value: appConfig.outputs.endpoint
      }
      {
        name: 'FOUNDRY_PROJECT_ENDPOINT'
        value: aiFoundryProject.outputs.endpoint
      }
      {
        name: 'FOUNDRY_MODEL_DEPLOYMENT'
        value: foundryModelDeployment
      }
      {
        name: 'AZURE_SUBSCRIPTION_ID'
        value: subscription().subscriptionId
      }
      {
        name: 'CONTENT_SAFETY_ENDPOINT'
        value: aiFoundryHub.outputs.endpoint
      }
      {
        name: 'CONTENT_SAFETY_KEY'
        secretRef: 'content-safety-key'
      }
      {
        name: 'TEAMS_TENANT_ID'
        value: teamsTenantId
      }
      {
        name: 'TEAMS_CLIENT_ID'
        value: teamsClientId
      }
      {
        name: 'TEAMS_CLIENT_SECRET'
        secretRef: 'teams-client-secret'
      }
      {
        name: 'TEAMS_TEAM_ID'
        value: teamsTeamId
      }
      {
        name: 'EMAIL_CONNECTION_STRING'
        secretRef: 'email-connection-string'
      }
      {
        name: 'EMAIL_SENDER'
        value: emailSender
      }
      {
        name: 'NOTIFICATION_EMAIL'
        value: notificationEmail
      }
      {
        name: 'LOG_LEVEL'
        value: 'INFO'
      }
      {
        name: 'MODERATION_MODE'
        value: 'monitor'
      }
    ]
    secrets: [
      {
        name: 'content-safety-key'
        value: contentSafetyKey
      }
      {
        name: 'teams-client-secret'
        value: teamsClientSecret
      }
      {
        name: 'email-connection-string'
        value: !empty(emailConnectionString) ? emailConnectionString : 'placeholder'
      }
    ]
  }
}

// UI container app
module uiContainerApp './core/host/container-app.bicep' = {
  name: 'ui-container-app'
  scope: rg
  params: {
    name: !empty(uiContainerAppName) ? uiContainerAppName : '${abbrs.appContainerApps}ui-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'ui' })
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    containerCpuCoreCount: uiCpu
    containerMemory: uiMemory
    containerName: 'ui'
    imageName: 'teams-mod-ui:latest'
    targetPort: 8501
    enableIngress: true
    externalIngress: true
    enableSystemAssignedIdentity: false
    userAssignedIdentityId: userAssignedIdentity.outputs.id
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: userAssignedIdentity.outputs.clientId
      }
      {
        name: 'APP_CONFIG_ENDPOINT'
        value: appConfig.outputs.endpoint
      }
      {
        name: 'FOUNDRY_PROJECT_ENDPOINT'
        value: aiFoundryProject.outputs.endpoint
      }
      {
        name: 'FOUNDRY_MODEL_DEPLOYMENT'
        value: foundryModelDeployment
      }
      {
        name: 'AZURE_SUBSCRIPTION_ID'
        value: subscription().subscriptionId
      }
      {
        name: 'CONTENT_SAFETY_ENDPOINT'
        value: aiFoundryHub.outputs.endpoint
      }
      {
        name: 'CONTENT_SAFETY_KEY'
        secretRef: 'content-safety-key'
      }
      {
        name: 'TEAMS_TENANT_ID'
        value: teamsTenantId
      }
      {
        name: 'TEAMS_CLIENT_ID'
        value: teamsClientId
      }
      {
        name: 'TEAMS_CLIENT_SECRET'
        secretRef: 'teams-client-secret'
      }
      {
        name: 'TEAMS_TEAM_ID'
        value: teamsTeamId
      }
      {
        name: 'EMAIL_CONNECTION_STRING'
        secretRef: 'email-connection-string'
      }
      {
        name: 'EMAIL_SENDER'
        value: emailSender
      }
      {
        name: 'NOTIFICATION_EMAIL'
        value: notificationEmail
      }
      {
        name: 'LOG_LEVEL'
        value: 'INFO'
      }
      {
        name: 'MODERATION_MODE'
        value: 'monitor'
      }
    ]
    secrets: [
      {
        name: 'content-safety-key'
        value: contentSafetyKey
      }
      {
        name: 'teams-client-secret'
        value: teamsClientSecret
      }
      {
        name: 'email-connection-string'
        value: !empty(emailConnectionString) ? emailConnectionString : 'placeholder'
      }
    ]
  }
}

// RBAC role assignments for App Configuration access
var appConfigDataReaderRole = '516239f1-63e1-4d78-a4de-a74fb236a071' // App Configuration Data Reader role
var appConfigDataOwnerRole = '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b' // App Configuration Data Owner role

// RBAC role assignments for AI Foundry access (following Microsoft best practices)
var azureAIUserRole = '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Azure AI User role
var azureAIDeveloperRole = '64702f94-c441-49e6-a78b-ef80e0188fee' // Azure AI Developer role
var cognitiveServicesUserRole = 'a97b65f3-24c7-4388-baec-2e87135dc908' // Cognitive Services User role
var cognitiveServicesOpenAIUserRole = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User role

// Additional role assignments for Communication Services and Service Bus
var communicationServicesOwnerRole = '09976791-48a7-449e-bb21-39d1a415f350' // Communication and Email Service Owner role
var serviceBusDataOwnerRole = '090c5cfd-751d-490a-894a-3ce6f1109419' // Azure Service Bus Data Owner role

// Agent only needs read access to App Configuration
module agentAppConfigRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-appconfig-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: appConfigDataReaderRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs Azure AI User role for AI Foundry access (account level)
module agentAIUserRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-ai-user-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: azureAIUserRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs AI Developer role for AI Foundry access (account level)
module agentAIDeveloperRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-ai-developer-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: azureAIDeveloperRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs Cognitive Services User role for AI Foundry access
module agentCognitiveServicesRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-cognitive-services-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: cognitiveServicesUserRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs Cognitive Services OpenAI User role for OpenAI endpoints
module agentCognitiveServicesOpenAIRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-cognitive-openai-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: cognitiveServicesOpenAIUserRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs write access to save configuration changes
module uiAppConfigRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-appconfig-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: appConfigDataOwnerRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs Azure AI User role for AI Foundry access
module uiAIUserRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-ai-user-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: azureAIUserRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs AI Developer role for Azure AI Foundry access
module uiAIDeveloperRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-ai-developer-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: azureAIDeveloperRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs Cognitive Services User role for AI Foundry access
module uiCognitiveServicesRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-cognitive-services-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: cognitiveServicesUserRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs Cognitive Services OpenAI User role for OpenAI endpoints
module uiCognitiveServicesOpenAIRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-cognitive-openai-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: cognitiveServicesOpenAIUserRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs Communication Services Contributor role for email notifications
// NOTE: This role assignment is scoped to the current resource group. If Communication Services
// is in a different resource group, you may need to assign this role manually.
module agentCommunicationServicesRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-communication-services-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: communicationServicesOwnerRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs Communication Services Contributor role for email testing
// NOTE: This role assignment is scoped to the current resource group. If Communication Services
// is in a different resource group, you may need to assign this role manually.
module uiCommunicationServicesRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'ui-communication-services-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: communicationServicesOwnerRole
    principalType: 'ServicePrincipal'
  }
}

// Agent needs Service Bus roles for message processing (if Service Bus is used)
// NOTE: This role assignment is scoped to the current resource group. If Service Bus
// is in a different resource group, you may need to assign this role manually.
module agentServiceBusDataOwnerRoleAssignment './core/security/role-assignment.bicep' = {
  name: 'agent-servicebus-data-owner-role'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: serviceBusDataOwnerRole
    principalType: 'ServicePrincipal'
  }
}

// UI needs Cognitive Services OpenAI User role for OpenAI endpoints - Secondary Assignment
module uiCognitiveServicesOpenAIRoleAssignment2 './core/security/role-assignment.bicep' = {
  name: 'ui-cognitive-openai-role-2'
  scope: rg
  params: {
    principalId: userAssignedIdentity.outputs.principalId
    roleDefinitionId: cognitiveServicesOpenAIUserRole
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output AGENT_CONTAINER_APP_NAME string = agentContainerApp.outputs.name
output USER_ASSIGNED_IDENTITY_PRINCIPAL_ID string = userAssignedIdentity.outputs.principalId
output USER_ASSIGNED_IDENTITY_CLIENT_ID string = userAssignedIdentity.outputs.clientId
output UI_CONTAINER_APP_NAME string = uiContainerApp.outputs.name
output UI_CONTAINER_APP_URI string = uiContainerApp.outputs.uri
output APP_CONFIG_ENDPOINT string = appConfig.outputs.endpoint
output FOUNDRY_PROJECT_ENDPOINT string = aiFoundryProject.outputs.endpoint
output FOUNDRY_MODEL_DEPLOYMENT string = foundryModelDeployment
output AI_PROJECT_NAME string = aiFoundryProject.outputs.name
output AI_FOUNDRY_HUB_NAME string = aiFoundryHub.outputs.name
