// ============================================================================
// Module: Azure AI Foundry Project (Account + Project) — Vanilla Bicep
// Description: Creates an Azure AI Services account and Azure AI Foundry project.
//              Generic, reusable across agentic apps.
// ============================================================================

targetScope = 'resourceGroup'

@description('Required. Solution name suffix used to generate resource names.')
param solutionName string

@description('Optional. Override name for the AI Services account. Defaults to aif-{solutionName}.')
param name string = 'aif-${solutionName}'

@description('Optional. Override name for the Azure AI Foundry project. Defaults to proj-{solutionName}.')
param projectName string = 'proj-${solutionName}'

@description('Required. Azure region for the resources.')
param location string

@description('Optional. Tags to apply to resources.')
param tags object = {}

@description('Optional. SKU name for the AI Services account.')
param skuName string = 'S0'

@description('Optional. Whether to disable local (key-based) authentication.')
param disableLocalAuth bool = true

@description('Optional. Whether to allow project management (Azure AI Foundry hub).')
param allowProjectManagement bool = true

@description('Optional. Public network access setting.')
param publicNetworkAccess string = 'Enabled'

@description('Optional. Managed identity configuration for the resources.')
param identity object = { type: 'SystemAssigned' }

@description('Optional. Network ACLs default action.')
@allowed(['Allow', 'Deny'])
param networkAclsDefaultAction string = 'Allow'

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-12-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  kind: 'AIServices'
  identity: identity
  properties: {
    allowProjectManagement: allowProjectManagement
    customSubDomainName: name
    networkAcls: {
      defaultAction: networkAclsDefaultAction
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: publicNetworkAccess
    disableLocalAuth: disableLocalAuth
  }
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-12-01' = {
  parent: aiServices
  name: projectName
  location: location
  kind: 'AIServices'
  identity: identity
  properties: {}
}

output resourceId string = aiServices.id
output name string = aiServices.name
output endpoint string = aiServices.properties.endpoints['OpenAI Language Model Instance API']
output cognitiveServicesEndpoint string = aiServices.properties.endpoint
output azureOpenAiCuEndpoint string = aiServices.properties.endpoints['Content Understanding']
output principalId string = aiServices.identity.principalId
output projectResourceId string = aiProject.id
output projectName string = aiProject.name
output projectEndpoint string = aiProject.properties.endpoints['AI Foundry API']
output projectIdentityPrincipalId string = aiProject.identity.principalId
