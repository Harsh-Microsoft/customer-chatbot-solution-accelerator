#!/usr/bin/env bash
set -e
echo "Starting the data upload script"

resource_group="${1:-}"

solutionName=""
aiFoundryName=""
ai_search_endpoint=""
azure_openai_endpoint=""
embedding_model_name=""
aiFoundryResourceId=""
aiSearchResourceId=""
cosmosdb_account=""
azSubscriptionId=""

test_azd_installed() {
    if command -v azd &> /dev/null; then
        return 0
    else
        return 1
    fi
}

test_az_env_value_ok() {
    local value="$1"
    [[ -n "${value// }" && ! "$value" =~ ^[[:space:]]*ERROR: ]]
}

get_values_from_azd_env() {
    if ! test_azd_installed; then
        echo "Error: Azure Developer CLI is not installed."
        return 1
    fi

    echo "Getting values from azd environment..."

    solutionName=$(azd env get-value SOLUTION_NAME 2>/dev/null)
    aiFoundryName=$(azd env get-value AI_SERVICE_NAME 2>/dev/null)
    resource_group=$(azd env get-value RESOURCE_GROUP_NAME 2>/dev/null)
    if ! test_az_env_value_ok "$resource_group"; then
        resource_group=$(azd env get-value AZURE_RESOURCE_GROUP 2>/dev/null)
    fi
    ai_search_endpoint=$(azd env get-value AZURE_AI_SEARCH_ENDPOINT 2>/dev/null)
    azure_openai_endpoint=$(azd env get-value AZURE_OPENAI_ENDPOINT 2>/dev/null)
    embedding_model_name=$(azd env get-value AZURE_OPENAI_EMBEDDING_MODEL 2>/dev/null)
    aiFoundryResourceId=$(azd env get-value AI_FOUNDRY_RESOURCE_ID 2>/dev/null)
    aiSearchResourceId=$(azd env get-value AI_SEARCH_SERVICE_RESOURCE_ID 2>/dev/null)
    cosmosdb_account=$(azd env get-value AZURE_COSMOSDB_ACCOUNT 2>/dev/null)

    if ! test_az_env_value_ok "$resource_group" || ! test_az_env_value_ok "$ai_search_endpoint" || ! test_az_env_value_ok "$azure_openai_endpoint" || ! test_az_env_value_ok "$cosmosdb_account" || ! test_az_env_value_ok "$aiSearchResourceId"; then
        echo "Error: Could not retrieve all required values from azd environment (provision this stack or run with a resource group and deployment outputs)."
        return 1
    fi

    echo "Successfully retrieved values from azd environment."
    return 0
}

extract_value() {
    local primary_key="$1"
    local fallback_key="$2"
    local result
    result=$(echo "$deploymentOutputs" | grep -i -A 3 "\"$primary_key\"" | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/' | head -1)
    if [ -z "$result" ]; then
        result=$(echo "$deploymentOutputs" | grep -i -A 3 "\"$fallback_key\"" | grep '"value"' | sed 's/.*"value": *"\([^"]*\)".*/\1/' | head -1)
    fi
    echo "$result" | xargs
}

get_values_from_az_deployment() {
    echo "Getting values from Azure deployment outputs..."

    deploymentName=$(az group show --name "$resource_group" --query "tags.DeploymentName" -o tsv)
    if [[ -z "$deploymentName" ]]; then
        echo "Error: Could not find deployment name in resource group tags."
        return 1
    fi

    deploymentOutputs=$(az deployment group show --resource-group "$resource_group" --name "$deploymentName" --query "properties.outputs" -o json)
    if [[ -z "$deploymentOutputs" ]]; then
        echo "Error: Could not fetch deployment outputs."
        return 1
    fi

    ai_search_endpoint=$(extract_value "azureAiSearchEndpoint" "AZURE_AI_SEARCH_ENDPOINT")
    azure_openai_endpoint=$(extract_value "azureOpenaiEndpoint" "AZURE_OPENAI_ENDPOINT")
    embedding_model_name=$(extract_value "azureOpenaiEmbeddingModel" "AZURE_OPENAI_EMBEDDING_MODEL")
    aiFoundryResourceId=$(extract_value "aiFoundryResourceId" "AI_FOUNDRY_RESOURCE_ID")
    aiSearchResourceId=$(extract_value "aiSearchServiceResourceId" "AI_SEARCH_SERVICE_RESOURCE_ID")
    cosmosdb_account=$(extract_value "azureCosmosdbAccount" "AZURE_COSMOSDB_ACCOUNT")

    if [[ -z "$ai_search_endpoint" || -z "$azure_openai_endpoint" || -z "$cosmosdb_account" ]]; then
        echo "Error: Could not extract all required values from deployment outputs."
        return 1
    fi

    echo "Successfully retrieved values from deployment outputs."
    return 0
}

if az account show &> /dev/null; then
    echo "Already authenticated with Azure."
else
    echo "Not authenticated with Azure. Attempting to authenticate..."
    az login
fi

if test_azd_installed; then
    azSubscriptionId=$(azd env get-value AZURE_SUBSCRIPTION_ID 2>/dev/null || echo "")
    if [[ -z "$azSubscriptionId" ]]; then
        azSubscriptionId="${AZURE_SUBSCRIPTION_ID:-}"
    fi
fi

currentSubscriptionId=$(az account show --query id -o tsv)
currentSubscriptionName=$(az account show --query name -o tsv)

if [[ "$currentSubscriptionId" != "$azSubscriptionId" && -n "$azSubscriptionId" ]]; then
    echo "Current selected subscription is $currentSubscriptionName ( $currentSubscriptionId )."
    az account set --subscription "$currentSubscriptionId"
    azSubscriptionId="$currentSubscriptionId"
else
    az account set --subscription "$currentSubscriptionId"
    azSubscriptionId="$currentSubscriptionId"
fi

if [[ -z "$resource_group" ]]; then
    if ! get_values_from_azd_env; then
        echo "Failed to get values from azd environment."
        echo "Usage: ./run_data_upload.sh <ResourceGroupName>"
        exit 1
    fi
else
    echo "Resource group provided: $resource_group"
    if ! get_values_from_az_deployment; then
        echo "Failed to get values from deployment outputs."
        exit 1
    fi
fi

echo ""
echo "==============================================="
echo "Values to be used:"
echo "==============================================="
echo "Resource Group: $resource_group"
echo "Azure AI Search Endpoint: $ai_search_endpoint"
echo "Azure OpenAI Endpoint: $azure_openai_endpoint"
echo "Azure Cosmos DB Account: $cosmosdb_account"
echo "Subscription ID: $azSubscriptionId"
echo "==============================================="
echo ""

echo "Getting signed in user id"
signed_user_id=$(az ad signed-in-user show --query id -o tsv)

echo "Checking if the user has Search roles on the Azure AI Search Service"
# search service contributor role id: 7ca78c08-252a-4471-8644-bb5ff32d4ba0
# search index data contributor role id: 8ebe5a00-799e-43f5-93ac-243d3dce84a7
# search index data reader role id: 1407120a-92aa-4202-b7e9-c0e197c71c8f
for role_id in "7ca78c08-252a-4471-8644-bb5ff32d4ba0" "8ebe5a00-799e-43f5-93ac-243d3dce84a7" "1407120a-92aa-4202-b7e9-c0e197c71c8f"; do
    role_assignment=$(az role assignment list --role "$role_id" --scope "$aiSearchResourceId" --assignee "$signed_user_id" --query "[].roleDefinitionId" -o tsv)
    if [[ -z "$role_assignment" ]]; then
        echo "User does not have role $role_id on the Azure AI Search Service. Assigning..."
        az role assignment create --assignee "$signed_user_id" --role "$role_id" --scope "$aiSearchResourceId" --output none
        echo "Waiting 10 seconds for role propagation..."
        sleep 10
    else
        echo "User already has role $role_id."
    fi
done

echo "Checking if the user has the Azure AI Developer role on AI Services"
# Azure AI Developer role id: 64702f94-c441-49e6-a78b-ef80e0188fee
role_assignment=$(az role assignment list --role "64702f94-c441-49e6-a78b-ef80e0188fee" --scope "$aiFoundryResourceId" --assignee "$signed_user_id" --query "[].roleDefinitionId" -o tsv)
if [[ -z "$role_assignment" ]]; then
    echo "User does not have the Azure AI Developer role. Assigning..."
    az role assignment create --assignee "$signed_user_id" --role "64702f94-c441-49e6-a78b-ef80e0188fee" --scope "$aiFoundryResourceId" --output none
    echo "Waiting 10 seconds for role propagation..."
    sleep 10
else
    echo "User already has the Azure AI Developer role."
fi

echo "Checking if user has the Azure Cosmos DB Built-in Data Contributor role"
roleExists=$(az cosmosdb sql role assignment list --resource-group "$resource_group" --account-name "$cosmosdb_account" --query "[?roleDefinitionId.ends_with(@, '00000000-0000-0000-0000-000000000002') && principalId == '$signed_user_id']" -o tsv)
if [[ -n "$roleExists" ]]; then
    echo "User already has the Azure Cosmos DB Built-in Data contributor role."
else
    echo "User does not have the Azure Cosmos DB Built-in Data contributor role. Assigning..."
    az cosmosdb sql role assignment create --resource-group "$resource_group" --account-name "$cosmosdb_account" --role-definition-id 00000000-0000-0000-0000-000000000002 --principal-id "$signed_user_id" --scope "/" --output none
    echo "Waiting 10 seconds for role propagation..."
    sleep 10
fi

requirementFile="scripts/requirements.txt"
python -m pip install --upgrade pip
python -m pip install --quiet -r "$requirementFile"

echo "=== Checking Azure AI Foundry network access for embeddings ==="
aif_account_resource_id=$(echo "$aiFoundryResourceId" | sed 's|/projects/.*||')
aif_resource_name=$(basename "$aif_account_resource_id")
aif_resource_group=$(echo "$aif_account_resource_id" | sed -n 's|.*/resourceGroups/\([^/]*\)/.*|\1|p')
aif_subscription_id=$(echo "$aif_account_resource_id" | sed -n 's|.*/subscriptions/\([^/]*\)/.*|\1|p')

original_foundry_public_access=$(az cognitiveservices account show --name "$aif_resource_name" --resource-group "$aif_resource_group" --subscription "$aif_subscription_id" --query "properties.publicNetworkAccess" -o tsv 2>/dev/null)
foundry_access_enabled=false

if [[ "$original_foundry_public_access" == "Disabled" ]]; then
    echo "Azure AI Foundry public network access is disabled. Temporarily enabling for embeddings..."
    if MSYS_NO_PATHCONV=1 az resource update --ids "$aif_account_resource_id" --api-version 2024-10-01 --set properties.publicNetworkAccess=Enabled properties.apiProperties="{}" --output none 2>/dev/null; then
        foundry_access_enabled=true
    fi
    echo "Waiting for network settings to propagate (60 seconds)..."
    sleep 60
else
    echo "Azure AI Foundry public network access is already enabled."
fi

echo "Running data upload scripts..."
python -m scripts.data.create_catalog_search_index --ai_search_endpoint="$ai_search_endpoint" --azure_openai_endpoint="$azure_openai_endpoint" --embedding_model_name="$embedding_model_name"
python -m scripts.data.upload_policy_docs --ai_search_endpoint="$ai_search_endpoint" --azure_openai_endpoint="$azure_openai_endpoint" --embedding_model_name="$embedding_model_name"

echo "=== Temporarily enabling public network access for Azure Cosmos DB ==="
subscription_id=$(az account show --query id -o tsv)
cosmos_resource_id="/subscriptions/${subscription_id}/resourceGroups/${resource_group}/providers/Microsoft.DocumentDB/databaseAccounts/${cosmosdb_account}"

original_cosmos_public_access=$(az resource show --ids "$cosmos_resource_id" --api-version 2021-04-15 --query "properties.publicNetworkAccess" -o tsv 2>/dev/null)
original_cosmos_ip_filter=$(az resource show --ids "$cosmos_resource_id" --api-version 2021-04-15 --query "properties.ipRules" -o json 2>/dev/null)
[[ -z "$original_cosmos_ip_filter" ]] && original_cosmos_ip_filter="[]"
cosmos_access_enabled=false

if [[ "$original_cosmos_public_access" != "Enabled" ]]; then
    current_ip="${COSMOS_FIREWALL_IP:-$(curl -s --max-time 10 https://api.ipify.org || echo "")}"
    if [[ -n "$current_ip" ]]; then
        ip_rule_json="[{\"ipAddressOrRange\":\"$current_ip\"}]"
        if az resource update --ids "$cosmos_resource_id" --api-version 2021-04-15 --set "properties.ipRules=$ip_rule_json" --set "properties.publicNetworkAccess=Enabled" --output none 2>/dev/null; then
            cosmos_access_enabled=true
            echo "Waiting for Azure Cosmos DB network changes to take effect (30 seconds)..."
            sleep 30
        fi
    else
        echo "ERROR: Could not determine an IP to whitelist for the Azure Cosmos DB firewall. Set COSMOS_FIREWALL_IP and re-run." >&2
        exit 1
    fi
else
    echo "Azure Cosmos DB public access already enabled - no changes needed"
fi

data_upload_failed=0
if ! python -m scripts.data.upload_catalog_data --cosmosdb_account="$cosmosdb_account"; then
    data_upload_failed=1
fi

echo "=== Restoring original network access settings ==="
if [[ "$cosmos_access_enabled" == true ]]; then
    az resource update --ids "$cosmos_resource_id" --api-version 2021-04-15 --set "properties.ipRules=$original_cosmos_ip_filter" --set "properties.publicNetworkAccess=$original_cosmos_public_access" --output none 2>/dev/null || true
fi
if [[ "$foundry_access_enabled" == true ]]; then
    MSYS_NO_PATHCONV=1 az resource update --ids "$aif_account_resource_id" --api-version 2024-10-01 --set properties.publicNetworkAccess=Disabled properties.apiProperties.qnaAzureSearchEndpointKey="" properties.networkAcls.bypass=AzureServices --output none 2>/dev/null || true
fi

if [[ "$data_upload_failed" -ne 0 ]]; then
    echo "Data upload script failed. Network settings have been restored." >&2
    exit 1
fi

echo "Data upload script completed successfully."
