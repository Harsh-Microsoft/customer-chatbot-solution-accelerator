// ============================================================================
// Module: Role Assignments (App Service, Foundry, Search, Cosmos, ACR)
// Description: Consolidated from the four previously separate staged
//              modules (acr-pull-role-assignment.bicep,
//              ai-search-role-assignment.bicep,
//              cosmos-reader-role-assignment.bicep,
//              foundry-role-assignment.bicep), mirroring
//              technical-patterns/chat-with-data/infra/bicep/modules/role-assignments.bicep.
//              All target resources (ACR, Cosmos, Foundry, Search) are
//              deployed in the same resource group as this pattern — the
//              Foundry/Search resources come from the `stableCore` module
//              declared inline in main.bicep, not a cross-scope reference.
//              Backend gets Search Index Data Contributor (write, not just
//              read) on AI Search, plus Cognitive Services User on Foundry
//              in addition to the existing Azure AI User assignment.
// ============================================================================

@description('Solution name suffix for generating unique role assignment GUIDs.')
param solutionName string = ''

@description('Required. Principal ID of the backend (API) App Service system-assigned identity.')
param backendAppServicePrincipalId string

@description('Required. Principal ID of the frontend (web) App Service system-assigned identity.')
param frontendAppServicePrincipalId string

@description('Required. Name of the Azure Container Registry.')
param containerRegistryName string

@description('Required. Name of the Cosmos DB account.')
param cosmosDbAccountName string

@description('Required. Name of the AI Foundry account.')
param aiFoundryName string

@description('Required. Name of the AI Search service.')
param aiSearchName string

var roleDefinitions = {
  acrPull: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
  azureAiUser: '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Foundry User
  cognitiveServicesUser: 'a97b65f3-24c7-4388-baec-2e87135dc908'
  searchIndexDataContributor: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = {
  name: containerRegistryName
}

resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: aiFoundryName
}

resource aiSearchService 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: aiSearchName
}

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2025-10-15' existing = {
  name: cosmosDbAccountName
}

resource cosmosContributorRoleDefinition 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2025-10-15' existing = {
  parent: cosmosAccount
  name: '00000000-0000-0000-0000-000000000002' // Cosmos DB Built-in Data Contributor
}

resource backendAppAcrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, containerRegistry.id, backendAppServicePrincipalId, roleDefinitions.acrPull)
  scope: containerRegistry
  properties: {
    principalId: backendAppServicePrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.acrPull)
    principalType: 'ServicePrincipal'
  }
}

resource frontendAppAcrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, containerRegistry.id, frontendAppServicePrincipalId, roleDefinitions.acrPull)
  scope: containerRegistry
  properties: {
    principalId: frontendAppServicePrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.acrPull)
    principalType: 'ServicePrincipal'
  }
}

resource backendAppCosmosRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2025-10-15' = {
  parent: cosmosAccount
  name: guid(solutionName, cosmosContributorRoleDefinition.id, cosmosAccount.id, backendAppServicePrincipalId)
  properties: {
    principalId: backendAppServicePrincipalId
    roleDefinitionId: cosmosContributorRoleDefinition.id
    scope: cosmosAccount.id
  }
}

resource backendAppAiUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiFoundryAccount.id, backendAppServicePrincipalId, roleDefinitions.azureAiUser)
  scope: aiFoundryAccount
  properties: {
    principalId: backendAppServicePrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.azureAiUser)
    principalType: 'ServicePrincipal'
  }
}

resource backendAppSearchContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiSearchService.id, backendAppServicePrincipalId, roleDefinitions.searchIndexDataContributor)
  scope: aiSearchService
  properties: {
    principalId: backendAppServicePrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.searchIndexDataContributor)
    principalType: 'ServicePrincipal'
  }
}

resource backendAppCognitiveServicesUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiFoundryAccount.id, backendAppServicePrincipalId, roleDefinitions.cognitiveServicesUser)
  scope: aiFoundryAccount
  properties: {
    principalId: backendAppServicePrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.cognitiveServicesUser)
    principalType: 'ServicePrincipal'
  }
}
