// ============================================================================
// Module: Model Deployment — Vanilla Bicep
// Description: Deploys a single AI model to an existing AI Services account.
//              Called in a loop from main.bicep, once per modelDeployments
//              array element. Element shape matches the modelDeploymentType
//              convention used by stable-cores/microsoft-iq: name,
//              model: { name, format, version }, sku: { name, capacity }.
// ============================================================================

targetScope = 'resourceGroup'

@description('Required. Name of the parent AI Services account.')
param aiServicesAccountName string

@description('Required. Name for this model deployment.')
param deploymentName string

@description('Required. Model definition for this deployment: name, format, version.')
param model object

@description('Required. SKU for this deployment: name, capacity.')
param sku object

@description('Optional. RAI policy name.')
param raiPolicyName string = 'Microsoft.Default'

resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: aiServicesAccountName
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-12-01' = {
  parent: aiServicesAccount
  name: deploymentName
  properties: {
    model: {
      format: model.format
      name: model.name
      version: model.?version
    }
    raiPolicyName: raiPolicyName
  }
  sku: {
    name: sku.name
    capacity: sku.?capacity
  }
}

output name string = modelDeployment.name
output resourceId string = modelDeployment.id
