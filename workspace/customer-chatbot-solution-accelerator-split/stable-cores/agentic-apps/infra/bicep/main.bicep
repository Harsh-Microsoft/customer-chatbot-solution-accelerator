// ============================================================================
// main.bicep — Agentic Apps Stable Core
// Description: Provisions the shared Foundry and search control plane for
//              agentic application patterns.
//              Approved split: Bicep only, greenfield Foundry project creation.
// ============================================================================

targetScope = 'resourceGroup'

@minLength(3)
@maxLength(16)
@description('Optional. A unique solution name used to derive resource names.')
param solutionName string = 'agentic-apps'

@maxLength(5)
@description('Optional. A unique suffix appended to resource names for uniqueness.')
param solutionUniqueText string = substring(uniqueString(subscription().id, resourceGroup().name, solutionName), 0, 5)

@metadata({
  azd: {
    type: 'location'
  }
})
@allowed([
  'australiaeast'
  'centralus'
  'eastasia'
  'eastus2'
  'japaneast'
  'northeurope'
  'southeastasia'
  'uksouth'
])
@description('Required. Primary Azure region for resource deployment.')
param location string

@allowed([
  'eastus2'
  'francecentral'
  'swedencentral'
  'centralus'
  'southindia'
])
@metadata({
  azd: {
    type: 'location'
  }
})
@description('Required. Location for the Azure AI Foundry account and project.')
param azureAiServiceLocation string

@description('Optional. Tags to apply to all resources.')
param tags object = {}

@description('Optional. Model deployments to create on the Foundry account. Empty by default — consumers pass the models they need.')
param modelDeployments array = []

var solutionSuffix = toLower(trim(replace(
  replace(
    replace(replace(replace(replace('${solutionName}${solutionUniqueText}', '-', ''), '_', ''), '.', ''), '/', ''),
    ' ',
    ''
  ),
  '*',
  ''
)))

var aiFoundryProjectName = 'proj-${solutionSuffix}'
var aiFoundryAccountName = 'aif-${solutionSuffix}'

module ai_foundry_project './modules/ai-foundry-project.bicep' = {
  name: take('module.ai-foundry-project.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: azureAiServiceLocation
    tags: tags
  }
  scope: resourceGroup(resourceGroup().name)
}

module ai_search './modules/ai-search.bicep' = {
  name: take('module.ai-search.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    location: location
    tags: tags
    disableLocalAuth: false
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
    networkRuleSet: {
      bypass: 'AzureServices'
    }
  }
  scope: resourceGroup(resourceGroup().name)
}

module role_assignments './modules/role-assignments.bicep' = {
  name: take('module.role-assignments.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    aiFoundryName: ai_foundry_project.outputs.name
    aiSearchName: ai_search.outputs.name
    aiSearchPrincipalId: ai_search.outputs.identityPrincipalId
    aiFoundryProjectPrincipalId: ai_foundry_project.outputs.projectIdentityPrincipalId
  }
  scope: resourceGroup(resourceGroup().name)
}

@batchSize(1)
module model_deployments './modules/ai-foundry-model-deployment.bicep' = [for (deployment, i) in modelDeployments: {
  name: take('module.model-deployment-${i}.${solutionName}', 64)
  params: {
    aiServicesAccountName: ai_foundry_project.outputs.name
    deploymentName: deployment.name
    model: deployment.model
    sku: deployment.sku
    raiPolicyName: deployment.?raiPolicyName ?? 'Microsoft.Default'
  }
  scope: resourceGroup(resourceGroup().name)
}]

module foundry_search_connection './modules/ai-foundry-connection.bicep' = {
  name: take('module.foundry-search-conn.${solutionName}', 64)
  params: {
    solutionName: solutionSuffix
    aiServicesAccountName: ai_foundry_project.outputs.name
    projectName: aiFoundryProjectName
    connectionName: 'aifp-srch-connection-${solutionSuffix}'
    category: 'CognitiveSearch'
    target: ai_search.outputs.endpoint
    authType: 'AAD'
    metadata: {
      ApiType: 'Azure'
      ResourceId: ai_search.outputs.resourceId
    }
  }
  scope: resourceGroup(resourceGroup().name)
}

output foundryAccountName string = ai_foundry_project.outputs.name
output foundryAccountEndpoint string = ai_foundry_project.outputs.endpoint
output foundryProjectName string = aiFoundryProjectName
output foundryProjectResourceId string = ai_foundry_project.outputs.projectResourceId
output foundryProjectEndpoint string = ai_foundry_project.outputs.projectEndpoint
output aiSearchName string = ai_search.outputs.name
output aiSearchEndpoint string = ai_search.outputs.endpoint
output aiSearchResourceId string = ai_search.outputs.resourceId
output aiSearchIdentityPrincipalId string = ai_search.outputs.identityPrincipalId
