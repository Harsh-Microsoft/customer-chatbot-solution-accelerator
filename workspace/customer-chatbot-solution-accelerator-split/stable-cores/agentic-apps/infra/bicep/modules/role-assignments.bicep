// ============================================================================
// Module: Role Assignments (Foundry Account, Search Service)
// Description: Grants the control-plane role assignments needed for the
//              Foundry project and AI Search service to operate together,
//              mirroring technical-patterns/chat-with-data-voice/infra/bicep/modules/role-assignments.bicep.
// ============================================================================

@description('Solution name suffix for generating unique role assignment GUIDs.')
param solutionName string = ''

@description('Required. Name of the AI Foundry account.')
param aiFoundryName string

@description('Required. Name of the AI Search service.')
param aiSearchName string

@description('Required. Principal ID of the AI Search service system-assigned identity.')
param aiSearchPrincipalId string

@description('Required. Principal ID of the AI Foundry project system-assigned identity.')
param aiFoundryProjectPrincipalId string

var roleDefinitions = {
  cognitiveServicesOpenAiUser: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  searchIndexDataReader: '1407120a-92aa-4202-b7e9-c0e197c71c8f'
  searchServiceContributor: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
}

resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2025-12-01' existing = {
  name: aiFoundryName
}

resource aiSearchService 'Microsoft.Search/searchServices@2025-05-01' existing = {
  name: aiSearchName
}

resource searchToFoundryOpenAiUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiFoundryAccount.id, aiSearchPrincipalId, roleDefinitions.cognitiveServicesOpenAiUser)
  scope: aiFoundryAccount
  properties: {
    principalId: aiSearchPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.cognitiveServicesOpenAiUser)
    principalType: 'ServicePrincipal'
  }
}

resource foundryProjectToSearchIndexReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiSearchService.id, aiFoundryProjectPrincipalId, roleDefinitions.searchIndexDataReader)
  scope: aiSearchService
  properties: {
    principalId: aiFoundryProjectPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.searchIndexDataReader)
    principalType: 'ServicePrincipal'
  }
}

resource foundryProjectToSearchServiceContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(solutionName, aiSearchService.id, aiFoundryProjectPrincipalId, roleDefinitions.searchServiceContributor)
  scope: aiSearchService
  properties: {
    principalId: aiFoundryProjectPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitions.searchServiceContributor)
    principalType: 'ServicePrincipal'
  }
}
