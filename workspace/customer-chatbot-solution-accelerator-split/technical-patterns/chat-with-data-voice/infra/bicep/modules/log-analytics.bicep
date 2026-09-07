// ============================================================================
// Module: Log Analytics Workspace
// Description: Vanilla Bicep module for Log Analytics Workspace, ported from
//              the source `infra/bicep/modules/monitoring/log-analytics.bicep`.
//              Greenfield only — the source's BYO-workspace branch is a
//              main.bicep-level decision (excluded per plan section 7.5),
//              not part of this module.
// Resource: Microsoft.OperationalInsights/workspaces@2023-09-01
// ============================================================================

@description('Solution name suffix used to derive the resource name.')
param solutionName string

@description('Optional. Override name for the Log Analytics workspace. Defaults to log-{solutionName}.')
param name string = 'log-${solutionName}'

@description('Azure region for the resource.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('Retention period in days.')
param retentionInDays int = 365

@description('SKU name for the workspace.')
param skuName string = 'PerGB2018'

@description('Optional. Managed identity configuration for the resource.')
param identity object = { type: 'SystemAssigned' }

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: name
  location: location
  tags: tags
  identity: identity
  properties: {
    retentionInDays: retentionInDays
    sku: {
      name: skuName
    }
  }
}

@description('Resource ID of the Log Analytics workspace.')
output resourceId string = logAnalytics.id

@description('Name of the Log Analytics workspace.')
output name string = logAnalytics.name

@description('Log Analytics workspace customer ID.')
output logAnalyticsWorkspaceId string = logAnalytics.properties.customerId
