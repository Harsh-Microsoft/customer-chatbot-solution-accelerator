// ============================================================================
// Module: Azure AI Search
// Description: Deploys Azure AI Search with managed identity and full config
//   in a single resource declaration.
// ============================================================================

targetScope = 'resourceGroup'

@description('Solution name suffix used to derive the resource name.')
@minLength(3)
param solutionName string

@description('Optional. Override name for the search service. Defaults to srch-{solutionName}.')
param name string = 'srch-${solutionName}'

@description('Azure region for the resource.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('SKU name for the search service.')
@allowed(['free', 'basic', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2'])
param skuName string = 'basic'

@description('Number of replicas.')
param replicaCount int = 1

@description('Number of partitions.')
param partitionCount int = 1

@description('Hosting mode.')
@allowed(['Default', 'HighDensity'])
param hostingMode string = 'Default'

@description('Semantic search tier.')
@allowed(['disabled', 'free', 'standard'])
param semanticSearch string = 'free'

@description('Whether to disable local authentication.')
param disableLocalAuth bool = true

@description('Optional. Authentication options for the search service.')
param authOptions object = {}

@description('Optional. Network rule set for the search service.')
param networkRuleSet object = {}

@description('Optional. Managed identity configuration for the resource.')
param identity object = { type: 'SystemAssigned' }

@description('Public network access setting.')
param publicNetworkAccess string = 'Enabled'

resource aiSearch 'Microsoft.Search/searchServices@2025-05-01' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: skuName
  }
  identity: identity
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: hostingMode
    semanticSearch: semanticSearch
    disableLocalAuth: disableLocalAuth
    publicNetworkAccess: publicNetworkAccess
    authOptions: !empty(authOptions) ? authOptions : null
    networkRuleSet: !empty(networkRuleSet) ? networkRuleSet : null
  }
}

output resourceId string = aiSearch.id
output name string = aiSearch.name
output endpoint string = 'https://${aiSearch.name}.search.windows.net'
output identityPrincipalId string = aiSearch.identity.principalId
