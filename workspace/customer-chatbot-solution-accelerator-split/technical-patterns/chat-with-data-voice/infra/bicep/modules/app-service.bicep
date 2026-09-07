// ============================================================================
// Module: App Service
// Description: Ported from the source
//              `infra/bicep/modules/compute/app-service.bicep`.
//              Renamed from `web-app.bicep` to match technical-patterns/chat-with-data.
//              `identityPrincipalId` is added as an output — the source
//              module's own centralized role-assignments.bicep reads it but
//              the source module never emits it; kept here so the pattern's
//              own role assignments (modules/role-assignments.bicep) can
//              wire the managed identity without a compile-time gap.
// API: Microsoft.Web/sites@2025-05-01
// ============================================================================

@description('Solution name suffix used to derive the resource name.')
param solutionName string

@description('Name of the App Service.')
param name string = solutionName

@description('Azure region for the resource.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('Resource ID of the App Service Plan.')
param serverFarmResourceId string

@description('Docker image name (e.g., DOCKER|registry.azurecr.io/image:tag).')
param linuxFxVersion string

@description('Application settings key-value pairs.')
param appSettings object = {}

@description('Whether to enable Always On.')
param alwaysOn bool = true

@description('Optional. Health check path for the app.')
param healthCheckPath string = ''

@description('Optional. Whether to enable WebSockets.')
param webSocketsEnabled bool = false

@description('Optional. Command line for the application.')
param appCommandLine string = ''

@description('Required. Type of site to deploy.')
param kind string = 'app,linux,container'

@description('Public network access setting.')
param publicNetworkAccess string = 'Enabled'

@description('Optional. Managed identity configuration for the resource.')
param identity object = { type: 'SystemAssigned' }

@description('Optional. Whether to use managed identity credentials for ACR authentication.')
param acrUseManagedIdentityCreds bool = false

@description('Optional. Cross-Origin Resource Sharing (CORS) settings for the app.')
param cors object = {}

resource appService 'Microsoft.Web/sites@2025-05-01' = {
  name: name
  location: location
  tags: tags
  kind: kind
  identity: identity
  properties: {
    serverFarmId: serverFarmResourceId
    publicNetworkAccess: publicNetworkAccess
    siteConfig: {
      alwaysOn: alwaysOn
      ftpsState: 'Disabled'
      linuxFxVersion: linuxFxVersion
      minTlsVersion: '1.2'
      healthCheckPath: !empty(healthCheckPath) ? healthCheckPath : null
      webSocketsEnabled: webSocketsEnabled
      appCommandLine: appCommandLine
      acrUseManagedIdentityCreds: acrUseManagedIdentityCreds
      cors: !empty(cors) ? cors : null
    }
    endToEndEncryptionEnabled: true
  }

  resource basicPublishingCredentialsPoliciesFtp 'basicPublishingCredentialsPolicies' = {
    name: 'ftp'
    properties: {
      allow: false
    }
  }
  resource basicPublishingCredentialsPoliciesScm 'basicPublishingCredentialsPolicies' = {
    name: 'scm'
    properties: {
      allow: false
    }
  }
}

resource configAppSettings 'Microsoft.Web/sites/config@2025-05-01' = {
  name: 'appsettings'
  parent: appService
  properties: appSettings
}

resource configLogs 'Microsoft.Web/sites/config@2025-05-01' = {
  name: 'logs'
  parent: appService
  properties: {
    applicationLogs: { fileSystem: { level: 'Verbose' } }
    detailedErrorMessages: { enabled: true }
    failedRequestsTracing: { enabled: true }
    httpLogs: { fileSystem: { enabled: true, retentionInDays: 1, retentionInMb: 35 } }
  }
  dependsOn: [configAppSettings]
}

@description('Resource ID of the App Service.')
output resourceId string = appService.id

@description('Name of the App Service.')
output name string = appService.name

@description('Default hostname of the App Service.')
output defaultHostname string = appService.properties.defaultHostName

@description('URL of the App Service.')
output appUrl string = 'https://${appService.properties.defaultHostName}'

@description('Principal ID of the App Service system-assigned managed identity.')
output identityPrincipalId string = appService.identity.principalId
