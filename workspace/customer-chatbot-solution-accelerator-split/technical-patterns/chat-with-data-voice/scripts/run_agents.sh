#!/bin/bash
set -e
echo "Started the agent creation script setup..."

resource_group=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            resource_group="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

projectEndpoint=""
solutionName=""
gptModelName=""
aiFoundryResourceId=""
apiAppName=""
searchEndpoint=""
azSubscriptionId=""
original_foundry_public_access=""
SKIP_ROLE_ASSIGNMENT=false

function test_azd_installed() {
    if command -v azd &> /dev/null; then
        return 0
    else
        return 1
    fi
}

function get_values_from_azd_env() {
    if ! test_azd_installed; then
        echo "Error: Azure Developer CLI is not installed."
        return 1
    fi

    echo "Getting values from azd environment..."

    projectEndpoint=$(azd env get-value AZURE_AI_AGENT_ENDPOINT 2>/dev/null)
    solutionName=$(azd env get-value SOLUTION_NAME 2>/dev/null)
    gptModelName=$(azd env get-value AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME 2>/dev/null)
    aiFoundryResourceId=$(azd env get-value AI_FOUNDRY_RESOURCE_ID 2>/dev/null)
    apiAppName=$(azd env get-value API_APP_NAME 2>/dev/null)
    resource_group=$(azd env get-value AZURE_RESOURCE_GROUP 2>/dev/null)
    if [[ -z "$resource_group" ]]; then
        resource_group=$(azd env get-value RESOURCE_GROUP_NAME 2>/dev/null)
    fi
    searchEndpoint=$(azd env get-value AZURE_AI_SEARCH_ENDPOINT 2>/dev/null)

    if [[ -z "$projectEndpoint" || -z "$solutionName" || -z "$gptModelName" || -z "$aiFoundryResourceId" || -z "$apiAppName" || -z "$resource_group" || -z "$searchEndpoint" ]]; then
        echo "Error: Could not retrieve all required values from azd environment."
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
    result=$(echo "$result" | xargs)
    echo "$result"
}

function get_values_from_az_deployment() {
    echo "Getting values from Azure deployment outputs..."

    echo "Fetching deployment name..."
    deploymentName=$(az group show --name "$resource_group" --query "tags.DeploymentName" -o tsv)
    if [[ -z "$deploymentName" ]]; then
        echo "Error: Could not find deployment name in resource group tags."
        return 1
    fi

    echo "Fetching deployment outputs for deployment: $deploymentName"
    deploymentOutputs=$(az deployment group show --resource-group "$resource_group" --name "$deploymentName" --query "properties.outputs" -o json)
    if [[ -z "$deploymentOutputs" ]]; then
        echo "Error: Could not fetch deployment outputs."
        return 1
    fi

    projectEndpoint=$(extract_value "azureAiAgentEndpoint" "AZURE_AI_AGENT_ENDPOINT")
    solutionName=$(extract_value "solutionName" "SOLUTION_NAME")
    gptModelName=$(extract_value "azureAiAgentModelDeploymentName" "AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")
    aiFoundryResourceId=$(extract_value "aiFoundryResourceId" "AI_FOUNDRY_RESOURCE_ID")
    apiAppName=$(extract_value "apiAppName" "API_APP_NAME")
    searchEndpoint=$(extract_value "azureAiSearchEndpoint" "AZURE_AI_SEARCH_ENDPOINT")

    echo "Extracted values:"
    echo "  projectEndpoint: $projectEndpoint"
    echo "  solutionName: $solutionName"
    echo "  gptModelName: $gptModelName"
    echo "  aiFoundryResourceId: $aiFoundryResourceId"
    echo "  apiAppName: $apiAppName"
    echo "  searchEndpoint: $searchEndpoint"

    if [[ -z "$projectEndpoint" || -z "$solutionName" || -z "$gptModelName" || -z "$aiFoundryResourceId" || -z "$apiAppName" || -z "$searchEndpoint" ]]; then
        echo "Error: Could not extract all required values from deployment outputs."
        return 1
    fi

    echo "Successfully retrieved values from deployment outputs."
    return 0
}

enable_public_access() {
	if [[ "${SKIP_NETWORK_TOGGLE:-}" == "true" ]]; then
		echo "SKIP_NETWORK_TOGGLE=true - skipping enable_public_access"
		return 0
	fi
	echo "=== Temporarily enabling public network access for services ==="
	aif_account_resource_id=$(echo "$aiFoundryResourceId" | sed 's|/projects/.*||')
	aif_resource_name=$(basename "$aif_account_resource_id")
	aif_resource_group=$(echo "$aif_account_resource_id" | sed -n 's|.*/resourceGroups/\([^/]*\)/.*|\1|p')
	aif_subscription_id=$(echo "$aif_account_resource_id" | sed -n 's|.*/subscriptions/\([^/]*\)/.*|\1|p')

	original_foundry_public_access=$(az cognitiveservices account show \
		--name "$aif_resource_name" \
		--resource-group "$aif_resource_group" \
		--subscription "$aif_subscription_id" \
		--query "properties.publicNetworkAccess" \
		--output tsv)
	if [ -z "$original_foundry_public_access" ] || [ "$original_foundry_public_access" = "null" ]; then
		echo "Info: Could not retrieve Azure AI Foundry network access status."
	elif [ "$original_foundry_public_access" != "Enabled" ]; then
		echo "Current Azure AI Foundry public access: $original_foundry_public_access"
		if MSYS_NO_PATHCONV=1 az resource update \
			--ids "$aif_account_resource_id" \
			--api-version 2024-10-01 \
			--set properties.publicNetworkAccess=Enabled properties.apiProperties="{}" \
			--output none; then
			echo "Azure AI Foundry public access enabled"
		else
			echo "Warning: Failed to enable Azure AI Foundry public access automatically."
		fi
	else
		echo "Azure AI Foundry public access already enabled - no changes needed"
	fi

	if [ -n "$original_foundry_public_access" ] && [ "$original_foundry_public_access" != "Enabled" ]; then
		echo "Waiting for network access changes to propagate (this may take up to 60 seconds)..."
		sleep 30
		current_access=$(az cognitiveservices account show \
			--name "$aif_resource_name" \
			--resource-group "$aif_resource_group" \
			--subscription "$aif_subscription_id" \
			--query "properties.publicNetworkAccess" \
			--output tsv 2>/dev/null || echo "Unknown")
		if [ "$current_access" = "Enabled" ]; then
			echo "Verified: Public network access is enabled"
		else
			echo "Warning: Public access verification returned: $current_access"
			sleep 30
		fi
	fi
	echo "=== Public network access enabled successfully ==="
	return 0
}

restore_network_access() {
	if [[ "${SKIP_NETWORK_TOGGLE:-}" == "true" ]]; then
		echo "SKIP_NETWORK_TOGGLE=true - skipping restore_network_access"
		return 0
	fi
	echo "=== Restoring original network access settings ==="
	if [ -n "$original_foundry_public_access" ] && [ "$original_foundry_public_access" != "Enabled" ]; then
		echo "Restoring Azure AI Foundry public access to: $original_foundry_public_access"
		aif_account_resource_id=$(echo "$aiFoundryResourceId" | sed 's|/projects/.*||')
		if MSYS_NO_PATHCONV=1 az resource update \
			--ids "$aif_account_resource_id" \
			--api-version 2024-10-01 \
			--set properties.publicNetworkAccess="$original_foundry_public_access" \
        	--set properties.apiProperties.qnaAzureSearchEndpointKey="" \
        	--set properties.networkAcls.bypass="AzureServices" \
			--output none 2>/dev/null; then
			echo "Azure AI Foundry access restored"
		else
			echo "Warning: Failed to restore Azure AI Foundry access automatically."
		fi
	else
		echo "Azure AI Foundry access unchanged (no restoration needed)"
	fi
	echo "=== Network access restoration completed ==="
}

assign_agent_identity_roles() {
	echo "=== Assigning RBAC roles to Agent Identity ==="

	ai_services_name=$(echo "$aiFoundryResourceId" | sed -n 's|.*/accounts/\([^/]*\)/projects/.*|\1|p')
	project_name=$(echo "$aiFoundryResourceId" | sed -n 's|.*/projects/\([^/]*\).*|\1|p')

	if [[ -z "$ai_services_name" ]]; then
		ai_services_name=$(echo "$aiFoundryResourceId" | sed -n 's|.*/accounts/\([^/]*\)$|\1|p')
	fi

	if [[ -z "$ai_services_name" ]]; then
		echo "Warning: Could not extract AI Services name from resource ID."
		return 1
	fi

	if [[ -z "$project_name" ]]; then
		echo "Project name not in resource ID, querying Azure for projects..."
		ai_services_resource_id="/subscriptions/$azSubscriptionId/resourceGroups/$resource_group/providers/Microsoft.CognitiveServices/accounts/$ai_services_name"
		full_project_name=$(az resource list \
			--resource-type "Microsoft.CognitiveServices/accounts/projects" \
			--query "[?starts_with(id, '${ai_services_resource_id}/')].name | [0]" \
			-o tsv 2>/dev/null)
		if [[ -z "$full_project_name" ]]; then
			echo "Warning: No projects found under AI Services account '$ai_services_name'."
			return 0
		fi
		project_name=$(basename "$full_project_name")
		echo "Found project: $project_name"
	fi

	agent_identity_name="${ai_services_name}-${project_name}-AgentIdentity"
	echo "Looking for agent identity: $agent_identity_name"

	agent_principal_id=$(az resource list \
		--resource-type "Microsoft.ManagedIdentity/userAssignedIdentities" \
		--name "$agent_identity_name" \
		--query "[0].properties.principalId" \
		-o tsv 2>/dev/null || true)

	if [[ -z "$agent_principal_id" ]]; then
		echo "Warning: Agent identity '$agent_identity_name' not found."
		return 0
	fi

	echo "Found agent identity with principal ID: $agent_principal_id"

	ai_services_resource_id=$(echo "$aiFoundryResourceId" | sed 's|/projects/.*||')
	search_service_name=$(echo "$searchEndpoint" | sed -n 's|https://\([^.]*\)\..*|\1|p')
	search_resource_id="/subscriptions/$azSubscriptionId/resourceGroups/$resource_group/providers/Microsoft.Search/searchServices/$search_service_name"

	echo "Assigning 'Cognitive Services Azure OpenAI User' role to agent identity on AI Services..."
	MSYS_NO_PATHCONV=1 az role assignment create \
		--assignee "$agent_principal_id" \
		--role "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd" \
		--scope "$ai_services_resource_id" \
		--output none 2>/dev/null || echo "  Role may already exist or failed to assign"

	echo "Assigning 'Search Index Data Reader' role to agent identity on Azure AI Search..."
	MSYS_NO_PATHCONV=1 az role assignment create \
		--assignee "$agent_principal_id" \
		--role "1407120a-92aa-4202-b7e9-c0e197c71c8f" \
		--scope "$search_resource_id" \
		--output none 2>/dev/null || echo "  Role may already exist or failed to assign"

	echo "=== Agent Identity RBAC roles assignment completed ==="
	return 0
}

cleanup_on_exit() {
	exit_code=$?
	echo ""
	if [ $exit_code -ne 0 ]; then
		echo "Script failed with exit code: $exit_code"
	fi
	echo "Performing cleanup..."
	restore_network_access
	exit $exit_code
}

trap cleanup_on_exit EXIT INT TERM

noninteractive=false
case "${POSTPROVISION_NON_INTERACTIVE:-}" in 1|true|TRUE) noninteractive=true ;; esac
case "${CI:-}" in true|TRUE) noninteractive=true ;; esac
[[ -n "${GITHUB_ACTIONS:-}" ]] && noninteractive=true
case "${TF_BUILD:-}" in True|true) noninteractive=true ;; esac

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

if [[ -z "$azSubscriptionId" ]]; then
    azSubscriptionId=$(az account show --query id -o tsv)
fi

currentSubscriptionId=$(az account show --query id -o tsv)
currentSubscriptionName=$(az account show --query name -o tsv)

if [[ "$currentSubscriptionId" != "$azSubscriptionId" && -n "$azSubscriptionId" ]]; then
    echo "Current selected subscription is $currentSubscriptionName ( $currentSubscriptionId )."
    if [[ "$noninteractive" == true ]]; then
        echo "Non-interactive: switching subscription to $azSubscriptionId"
        az account set --subscription "$azSubscriptionId" || exit 1
    else
        read -p "Do you want to continue with this subscription?(y/n): " confirmation
        if [[ "$confirmation" != "y" && "$confirmation" != "Y" ]]; then
            echo "Fetching available subscriptions..."
            availableSubscriptions=$(az account list --query "[?state=='Enabled'].[name,id]" --output tsv)
            readarray -t subscriptions <<< "$availableSubscriptions"
            while true; do
                echo ""
                echo "Available Subscriptions:"
                echo "========================"
                index=1
                for ((i=0; i<${#subscriptions[@]}; i++)); do
                    IFS=$'\t' read -r name id <<< "${subscriptions[i]}"
                    echo "$index. $name ( $id )"
                    ((index++))
                done
                echo "========================"
                echo ""
                read -p "Enter the number of the subscription (1-$((${#subscriptions[@]}))) to use: " subscriptionIndex
                if [[ "$subscriptionIndex" =~ ^[0-9]+$ ]] && [[ "$subscriptionIndex" -ge 1 ]] && [[ "$subscriptionIndex" -le "${#subscriptions[@]}" ]]; then
                    selectedIndex=$((subscriptionIndex - 1))
                    IFS=$'\t' read -r selectedSubscriptionName selectedSubscriptionId <<< "${subscriptions[selectedIndex]}"
                    if az account set --subscription "$selectedSubscriptionId"; then
                        echo "Switched to subscription: $selectedSubscriptionName ( $selectedSubscriptionId )"
                        azSubscriptionId="$selectedSubscriptionId"
                        break
                    else
                        echo "Failed to switch to subscription: $selectedSubscriptionName ( $selectedSubscriptionId )."
                    fi
                else
                    echo "Invalid selection. Please try again."
                fi
            done
        else
            echo "Proceeding with the current subscription: $currentSubscriptionName ( $currentSubscriptionId )"
            az account set --subscription "$currentSubscriptionId"
            azSubscriptionId="$currentSubscriptionId"
        fi
    fi
else
    echo "Proceeding with the subscription: $currentSubscriptionName ( $currentSubscriptionId )"
    az account set --subscription "$currentSubscriptionId"
    azSubscriptionId="$currentSubscriptionId"
fi

if [[ -z "$resource_group" ]]; then
    if ! get_values_from_azd_env; then
        echo "Failed to get values from azd environment."
        echo "If you want to use deployment outputs instead, please provide the resource group name as an argument."
        echo "Usage: ./run_agents.sh --resource-group <ResourceGroupName>"
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
echo "Project Endpoint: $projectEndpoint"
echo "Solution Name: $solutionName"
echo "GPT Model Name: $gptModelName"
echo "Azure AI Foundry Resource ID: $aiFoundryResourceId"
echo "API App Name: $apiAppName"
echo "Search Endpoint: $searchEndpoint"
echo "Subscription ID: $azSubscriptionId"
echo "==============================================="
echo ""

if [[ -n "${NETWORK_TOGGLE_ONLY:-}" ]]; then
    SKIP_NETWORK_TOGGLE=false
    trap - EXIT INT TERM
    case "$NETWORK_TOGGLE_ONLY" in
        enable)  enable_public_access; exit $? ;;
        restore) restore_network_access; exit $? ;;
        *) echo "Unknown NETWORK_TOGGLE_ONLY value: $NETWORK_TOGGLE_ONLY"; exit 1 ;;
    esac
fi

echo "Getting principal id (user or service principal)"
set +e
signed_user_id=$(az ad signed-in-user show --query id -o tsv 2>/dev/null)

if [ -z "$signed_user_id" ]; then
    echo "Not logged in as user, checking for service principal..."
    account_type=$(az account show --query 'user.type' -o tsv 2>/dev/null)
    if [ "$account_type" = "servicePrincipal" ]; then
        sp_name=$(az account show --query 'user.name' -o tsv 2>/dev/null)
        echo "Logged in as service principal: $sp_name"
        signed_user_id=$(az ad sp show --id "$sp_name" --query id -o tsv 2>/dev/null)
        if [ -z "$signed_user_id" ]; then
            echo "Warning: Could not get service principal object ID. Attempting to continue without role assignment..."
            SKIP_ROLE_ASSIGNMENT=true
        else
            echo "Service principal object ID: $signed_user_id"
        fi
    else
        echo "Warning: Could not determine principal ID (type: $account_type). Attempting to continue without role assignment..."
        SKIP_ROLE_ASSIGNMENT=true
    fi
else
    echo "Logged in as user: $signed_user_id"
fi
set -e

echo "Checking if the principal has Foundry User role on the Azure AI Foundry"

aif_subscription_id=$(echo "$aiFoundryResourceId" | sed -n 's|.*/subscriptions/\([^/]*\)/.*|\1|p')
if [ -z "$aif_subscription_id" ]; then
    aif_subscription_id="$azSubscriptionId"
fi

if [ "$SKIP_ROLE_ASSIGNMENT" != "true" ] && [ -n "$signed_user_id" ]; then
    role_assignment=$(MSYS_NO_PATHCONV=1 az role assignment list \
      --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" \
      --scope "$aiFoundryResourceId" \
      --assignee "$signed_user_id" \
      --subscription "$aif_subscription_id" \
      --query "[].roleDefinitionId" -o tsv)

    if [ -z "$role_assignment" ]; then
        echo "Principal does not have the Foundry User role. Assigning the role..."
        MSYS_NO_PATHCONV=1 az role assignment create \
          --assignee "$signed_user_id" \
          --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" \
          --scope "$aiFoundryResourceId" \
          --subscription "$aif_subscription_id" \
          --output none

        if [ $? -eq 0 ]; then
            echo "Foundry User role assigned successfully."
            echo "Waiting 10 seconds for role propagation..."
            sleep 10
        else
            echo "Failed to assign Foundry User role."
            exit 1
        fi
    else
        echo "Principal already has the Foundry User role."
    fi
else
    echo "Skipping role assignment (will rely on existing permissions)"
fi

requirementFile="scripts/requirements.txt"

python -m pip install --upgrade pip
python -m pip install --quiet -r "$requirementFile"

enable_public_access
if [ $? -ne 0 ]; then
	echo "Error: Failed to enable public network access for services."
	exit 1
fi

echo "Running Python agents creation script..."
python_output=$(python -m scripts.agents.run_agents --ai_project_endpoint="$projectEndpoint" --solution_name="$solutionName" --gpt_model_name="$gptModelName" --ai_search_endpoint="$searchEndpoint")
eval $(echo "$python_output" | grep -E "^(chatAgentName|catalogAgentName|policyAgentName)=")

echo "Agents creation completed."

assign_agent_identity_roles

az webapp config appsettings set \
  --resource-group "$resource_group" \
  --name "$apiAppName" \
  --settings FOUNDRY_CHAT_AGENT="$chatAgentName" FOUNDRY_CATALOG_AGENT="$catalogAgentName" FOUNDRY_POLICY_AGENT="$policyAgentName" \
  -o none

echo "Environment variables updated for App Service: $apiAppName"
echo "Network access will be restored to original settings..."
