// ============================================================================
// Module: Azure Cosmos DB
// Description: Ported from the source
//              `infra/bicep/modules/data/cosmos-db-nosql.bicep`. The source's
//              `carts` container is dropped per plan section 7.1 (cart
//              companion removal); `products` is renamed `catalog_items`
//              alongside the section 6 catalog vocabulary neutralization.
//              Renamed from `cosmos.bicep` to match technical-patterns/chat-with-data.
// API: Microsoft.DocumentDB/databaseAccounts@2025-10-15
// ============================================================================

@description('Solution name suffix used to derive the resource name.')
param solutionName string

@description('Name of the Azure Cosmos DB account.')
param name string = 'cosmos-${solutionName}'

@description('Azure region for the resource.')
param location string

@description('Tags to apply to the resource.')
param tags object = {}

@description('Database name.')
param databaseName string = 'chat_with_data_voice_db'

@description('Container definitions.')
param containers {
  name: string
  partitionKeyPath: string
}[] = [
  { name: 'chat_sessions', partitionKeyPath: '/user_id' }
  { name: 'catalog_items', partitionKeyPath: '/itemId' }
  { name: 'transactions', partitionKeyPath: '/user_id' }
  { name: 'users', partitionKeyPath: '/email' }
]

@description('Optional. Managed identity configuration for the resource.')
param identity object = { type: 'SystemAssigned' }

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2025-10-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  identity: identity
  properties: {
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    databaseAccountOfferType: 'Standard'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    disableLocalAuth: true
    capabilities: [ { name: 'EnableServerless' } ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2025-10-15' = {
  parent: cosmos
  name: databaseName
  properties: {
    resource: { id: databaseName }
  }

  resource list 'containers' = [for container in containers: {
    name: container.name
    properties: {
      resource: {
        id: container.name
        partitionKey: { paths: [ container.partitionKeyPath ] }
      }
      options: {}
    }
  }]
}

@description('Resource ID of the Azure Cosmos DB account.')
output resourceId string = cosmos.id

@description('Name of the Azure Cosmos DB account.')
output name string = cosmos.name

@description('Endpoint of the Azure Cosmos DB account.')
output endpoint string = 'https://${cosmos.name}.documents.azure.com:443/'

@description('Database name.')
output databaseName string = databaseName
