from __future__ import annotations

import os
import sys

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import ConnectionType
from agent_framework.azure import AzureAIProjectAgentProvider
from azure.identity.aio import AzureCliCredential

# scenario_loader now lives under src/api (the API's Dockerfile build context;
# scripts/ never ships in the container), so it is reached via sys.path here.
_API_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src', 'api')
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from scenario_loader import load_agent_instructions, load_manifest  # noqa: E402


async def _get_ai_search_connection_id(project_client: AIProjectClient, ai_search_endpoint: str) -> str:
    async for connection in project_client.connections.list():
        if connection.type == ConnectionType.AZURE_AI_SEARCH and connection.target == ai_search_endpoint:
            return connection.id
    raise RuntimeError(f'Could not find Azure AI Search connection for {ai_search_endpoint}.')


async def create_agents(
    ai_project_endpoint: str,
    solution_name: str,
    gpt_model_name: str,
    ai_search_endpoint: str,
) -> tuple[str, str, str]:
    manifest = load_manifest()
    instructions = dict(load_agent_instructions())
    catalog_index = manifest['search']['catalogIndex']
    policies_index = manifest['search']['policiesIndex']
    catalog_prefix = manifest['agents']['catalogAgentPrefix']
    policy_prefix = manifest['agents']['policyAgentPrefix']
    chat_prefix = manifest['agents']['chatAgentPrefix']
    catalog_tool_name = manifest['agents']['catalogToolName']
    policy_tool_name = manifest['agents']['policyToolName']

    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=ai_project_endpoint, credential=credential) as project_client,
        AzureAIProjectAgentProvider(project_client=project_client, credential=credential) as provider,
    ):
        ai_search_conn_id = await _get_ai_search_connection_id(project_client, ai_search_endpoint)

        catalog_agent = await provider.create_agent(
            name=f'{catalog_prefix}-{solution_name}',
            model=gpt_model_name,
            instructions=instructions['catalog_agent'],
            tools={
                'type': 'azure_ai_search',
                'azure_ai_search': {
                    'indexes': [
                        {
                            'project_connection_id': ai_search_conn_id,
                            'index_name': catalog_index,
                            'query_type': 'vector_simple',
                            'top_k': 5,
                        }
                    ]
                },
            },
        )

        policy_agent = await provider.create_agent(
            name=f'{policy_prefix}-{solution_name}',
            model=gpt_model_name,
            instructions=instructions['policy_agent'],
            tools={
                'type': 'azure_ai_search',
                'azure_ai_search': {
                    'indexes': [
                        {
                            'project_connection_id': ai_search_conn_id,
                            'index_name': policies_index,
                            'query_type': 'vector_simple',
                            'top_k': 5,
                        }
                    ]
                },
            },
        )

        chat_agent = await provider.create_agent(
            name=f'{chat_prefix}-{solution_name}',
            model=gpt_model_name,
            instructions=instructions['chat_agent'],
            tools=[
                catalog_agent.as_tool(name=catalog_tool_name),
                policy_agent.as_tool(name=policy_tool_name),
            ],
        )

        return catalog_agent.name, policy_agent.name, chat_agent.name
