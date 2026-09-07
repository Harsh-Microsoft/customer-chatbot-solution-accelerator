from __future__ import annotations

import argparse
import asyncio

from dotenv import load_dotenv

from .create_agents import create_agents


def main() -> int:
    load_dotenv()
    p = argparse.ArgumentParser()
    p.add_argument('--ai_project_endpoint', required=True)
    p.add_argument('--solution_name', required=True)
    p.add_argument('--gpt_model_name', required=True)
    p.add_argument('--ai_search_endpoint', required=True)
    args = p.parse_args()

    catalog_agent_name, policy_agent_name, chat_agent_name = asyncio.run(
        create_agents(
            args.ai_project_endpoint,
            args.solution_name,
            args.gpt_model_name,
            args.ai_search_endpoint,
        )
    )
    print(f'chatAgentName={chat_agent_name}')
    print(f'catalogAgentName={catalog_agent_name}')
    print(f'policyAgentName={policy_agent_name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
