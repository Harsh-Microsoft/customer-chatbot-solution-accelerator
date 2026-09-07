// ============================================================================
// main.bicep — Orchestrator (Technical Pattern: chat-with-data-voice)
// Ported and reduced from the source `infra/bicep/main.bicep`
// (31,704 B) plus its `modules/compute`, `modules/monitoring`,
// `modules/data`, and `modules/identity` subtree, per split-plan.md rows
// 51, 52, 52a, 53.
//
// What this pattern owns and provisions (vanilla Bicep, no AVM):
//   ACR, App Service Plan, exactly two App Services (api, app), Cosmos DB,
//   Log Analytics + Application Insights (greenfield only — the source's
//   BYO/attach-existing-workspace branch is excluded per plan section 7.5),
//   and the role assignments those resources need.
//
// What this pattern does NOT own: the Azure AI Foundry account/project and
// Azure AI Search are provisioned by the `stableCore` module below, which
// declares `stable-cores/agentic-apps/infra/bicep/main.bicep` directly
// (mirroring `technical-patterns/chat-with-data/infra/bicep/main.bicep`) —
// never duplicated here. `existing-project-setup.bicep` and its
// `cross-scope-role-assignment.bicep` helper are out of scope per plan
// rows 50a/52a and are not staged.
//
// Row 53 also reduces the source's four App Service module invocations
// (chat + scenario, frontend + backend) to exactly two (api, app), per the
// section 6/6A router and UI merge, and drops the deploymentScenario-keyed
// hostAppTitle/chatWelcomeTitle/catalogSearchIndex/... string ternaries —
// those values are no longer compiled into infra; they are scenario
// manifest configuration served at runtime over SCENARIO_PATH (section 6A).
// ============================================================================
targetScope = 'resourceGroup'

@minLength(3)
@maxLength(16)
@description('Optional. A unique application/solution name for all resources in this deployment.')
param solutionName string = 'cdv'

@maxLength(5)
@description('Optional. A unique text suffix appended to resource names for uniqueness.')
param solutionUniqueText string = substring(uniqueString(subscription().id, resourceGroup().name, solutionName), 0, 5)

@description('Required. Primary Azure region for resource deployment.')
param location string = resourceGroup().location

@description('Optional. Tags to apply to all resources.')
param tags object = {}

@allowed(['F1', 'D1', 'B1', 'B2', 'B3', 'S1', 'S2', 'S3', 'P1', 'P2', 'P3', 'P1v3', 'P1v4'])
@description('Optional. App Service Plan SKU.')
param appServicePlanSku string = 'B2'

@description('Optional. Enable monitoring (App Insights + Log Analytics), provisioned greenfield.')
param enableMonitoring bool = false

// ============================================================================
// Parameters — Stable Core (agentic-apps) composition inputs
// The Foundry account/project and Azure AI Search are provisioned by the
// `stableCore` module declared below; this pattern never re-provisions
// them. See `supportedStableCores` in metadata.yaml.
// ============================================================================

@allowed([
  'eastus2'
  'francecentral'
  'swedencentral'
  'centralus'
  'southindia'
])
@description('Required. Location for Azure AI Foundry and model deployments, passed to the composed `agentic-apps` Stable Core.')
param azureAiServiceLocation string

// ============================================================================
// Parameters — AI Configuration (model identifiers only; capacity/SKU are core-owned)
// ============================================================================

@description('Optional. Name of the GPT model deployment used for chat and voice.')
param gptModelName string = 'gpt-5.4-mini'

@description('Optional. Azure OpenAI API version.')
param azureOpenaiAPIVersion string = '2025-01-01-preview'

@description('Optional. Azure AI Agent API version.')
param azureAiAgentApiVersion string = '2025-05-01'

@description('Optional. Name of the realtime (voice) model deployment.')
param gptRealtimeModelName string = 'gpt-realtime-mini'

@allowed([
  'Standard'
  'GlobalStandard'
])
@description('Optional. GPT model deployment type.')
param deploymentType string = 'GlobalStandard'

@description('Optional. Version of the GPT model to deploy.')
param gptModelVersion string = '2026-03-17'

@minValue(10)
@description('Optional. Capacity of the GPT deployment (TPM in thousands).')
param gptDeploymentCapacity int = 50

@allowed([
  'text-embedding-3-small'
])
@description('Optional. Name of the embedding model to deploy.')
param embeddingModelName string = 'text-embedding-3-small'

@minValue(10)
@description('Optional. Capacity of the embedding model deployment.')
param embeddingDeploymentCapacity int = 10

@description('Optional. Version of the realtime model to deploy.')
param gptRealtimeModelVersion string = '2025-12-15'

@minValue(1)
@description('Optional. Capacity of the realtime model deployment.')
param gptRealtimeDeploymentCapacity int = 1

// ============================================================================
// Parameters — Composition
// ============================================================================

@description('Required. Path the API resolves the composed scenario\'\'s config/data/assets from at runtime. Set by the Builder per the composition contract (plan section 6A.1).')
param scenarioPath string

// ============================================================================
// Variables
// ============================================================================

var solutionSuffix = toLower(trim(replace(
  replace(
    replace(replace(replace(replace('${solutionName}${solutionUniqueText}', '-', ''), '_', ''), '.', ''), '/', ''),
    ' ',
    ''
  ),
  '*',
  ''
)))

var existingTags = resourceGroup().tags ?? {}
var resourceTags = union(existingTags, tags, {
  TemplateName: 'chat-with-data-voice'
  Type: 'Non-WAF'
})

var apiAppName = 'api-${solutionSuffix}'
var webAppName = 'app-${solutionSuffix}'
var helloWorldDefaultImageName = 'DOCKER|mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

// ============================================================================
// Module: Stable Core (AI Foundry account/project + AI Search + model
// deployments). Declared directly, mirroring
// technical-patterns/chat-with-data — never duplicate these resources or
// the model-deployment module in this pattern; the core owns deployment.
// ============================================================================
module stableCore '../../../../stable-cores/agentic-apps/infra/bicep/main.bicep' = {
  name: take('module.stable-core.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    azureAiServiceLocation: azureAiServiceLocation
    tags: resourceTags
    modelDeployments: [
      {
        name: gptModelName
        model: {
          name: gptModelName
          format: 'OpenAI'
          version: gptModelVersion
        }
        sku: {
          name: deploymentType
          capacity: gptDeploymentCapacity
        }
      }
      {
        name: embeddingModelName
        model: {
          name: embeddingModelName
          format: 'OpenAI'
          version: '1'
        }
        sku: {
          name: 'GlobalStandard'
          capacity: embeddingDeploymentCapacity
        }
      }
      {
        name: gptRealtimeModelName
        model: {
          name: gptRealtimeModelName
          format: 'OpenAI'
          version: gptRealtimeModelVersion
        }
        sku: {
          name: 'GlobalStandard'
          capacity: gptRealtimeDeploymentCapacity
        }
      }
    ]
  }
}

module log_analytics './modules/log-analytics.bicep' = if (enableMonitoring) {
  name: take('module.log-analytics.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: resourceTags
  }
}

module app_insights './modules/application-insights.bicep' = if (enableMonitoring) {
  name: take('module.app-insights.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: resourceTags
    workspaceResourceId: log_analytics!.outputs.resourceId
  }
}

// ============================================================================
// Module: Compute
// ============================================================================

module acr './modules/container-registry.bicep' = {
  name: take('module.acr.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: resourceTags
  }
}

module plan './modules/app-service-plan.bicep' = {
  name: take('module.app-service-plan.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: resourceTags
    skuName: appServicePlanSku
  }
}

module apiApp './modules/app-service.bicep' = {
  name: take('module.app-service-api.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    name: apiAppName
    location: location
    tags: resourceTags
    serverFarmResourceId: plan.outputs.resourceId
    linuxFxVersion: helloWorldDefaultImageName
    healthCheckPath: '/health'
    webSocketsEnabled: true
    acrUseManagedIdentityCreds: true
    cors: {
      allowedOrigins: [ 'https://${webAppName}.azurewebsites.net' ]
      supportCredentials: true
    }
    appSettings: {
      AZURE_OPENAI_DEPLOYMENT_MODEL: gptModelName
      AZURE_OPENAI_ENDPOINT: stableCore.outputs.foundryAccountEndpoint
      AZURE_OPENAI_API_VERSION: azureOpenaiAPIVersion
      AZURE_AI_AGENT_ENDPOINT: stableCore.outputs.foundryProjectEndpoint
      AZURE_AI_AGENT_API_VERSION: azureAiAgentApiVersion
      AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME: gptModelName
      AZURE_AI_SEARCH_ENDPOINT: stableCore.outputs.aiSearchEndpoint
      AZURE_COSMOSDB_ACCOUNT: cosmos.outputs.name
      AZURE_COSMOSDB_DATABASE: cosmos.outputs.databaseName
      COSMOS_DB_ENDPOINT: cosmos.outputs.endpoint
      COSMOS_DB_DATABASE_NAME: cosmos.outputs.databaseName
      SCENARIO_PATH: scenarioPath
      USE_FOUNDRY_AGENTS: 'True'
      RATE_LIMIT_REQUESTS: '100'
      RATE_LIMIT_WINDOW: '60'
      AZURE_VOICELIVE_ENDPOINT: stableCore.outputs.foundryAccountEndpoint
      VOICELIVE_MODEL: gptRealtimeModelName
      VOICELIVE_VOICE: 'alloy'
      VOICELIVE_TRANSCRIBE_MODEL: 'gpt-4o-transcribe'
      VOICELIVE_VAD_SILENCE_MS: '1200'
      VOICELIVE_VAD_THRESHOLD: '0.5'
      VOICELIVE_VAD_PREFIX_PADDING_MS: '300'
      APPLICATIONINSIGHTS_CONNECTION_STRING: enableMonitoring ? app_insights!.outputs.connectionString : ''
    }
  }
}

module webApp './modules/app-service.bicep' = {
  name: take('module.app-service-web.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    name: webAppName
    location: location
    tags: resourceTags
    serverFarmResourceId: plan.outputs.resourceId
    linuxFxVersion: helloWorldDefaultImageName
    acrUseManagedIdentityCreds: true
    appSettings: {
      NODE_ENV: 'production'
      VITE_API_BASE_URL: apiApp.outputs.appUrl
      APPLICATIONINSIGHTS_CONNECTION_STRING: enableMonitoring ? app_insights!.outputs.connectionString : ''
    }
  }
}

// ============================================================================
// Module: Data
// ============================================================================

module cosmos './modules/cosmos-db-nosql.bicep' = {
  name: take('module.cosmos.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: resourceTags
  }
}

// ============================================================================
// Module: Role Assignments (ACR Pull + Cosmos DB + AI Foundry/Search for
// both App Services, consolidated into one module — mirrors
// technical-patterns/chat-with-data/infra/bicep/modules/role-assignments.bicep)
// ============================================================================

module role_assignments './modules/role-assignments.bicep' = {
  name: take('module.role-assignments.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    backendAppServicePrincipalId: apiApp.outputs.identityPrincipalId
    frontendAppServicePrincipalId: webApp.outputs.identityPrincipalId
    containerRegistryName: acr.outputs.name
    cosmosDbAccountName: cosmos.outputs.name
    aiFoundryName: stableCore.outputs.foundryAccountName
    aiSearchName: stableCore.outputs.aiSearchName
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('Solution suffix used for naming resources.')
output SOLUTION_NAME string = solutionSuffix

@description('Resource ID of the App Service Plan.')
output appServicePlanId string = plan.outputs.resourceId

@description('Default hostname of the API App Service.')
output apiHostName string = apiApp.outputs.defaultHostname

@description('Default hostname of the web App Service.')
output webHostName string = webApp.outputs.defaultHostname

@description('Login server of the Azure Container Registry.')
output acrLoginServer string = acr.outputs.loginServer

@description('Azure Cosmos DB endpoint.')
output cosmosEndpoint string = cosmos.outputs.endpoint

@description('Application Insights connection string (empty when monitoring is disabled).')
output APPLICATIONINSIGHTS_CONNECTION_STRING string = enableMonitoring ? app_insights!.outputs.connectionString : ''
