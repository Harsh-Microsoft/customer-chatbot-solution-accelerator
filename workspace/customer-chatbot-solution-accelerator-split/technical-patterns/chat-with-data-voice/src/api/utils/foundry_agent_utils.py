from __future__ import annotations

from typing import Any

from scenario_config import build_voice_grounding_instructions


async def call_foundry_agent(
    question: str,
    foundry_endpoint: str,
    chat_agent_name: str,
    product_agent_name: str,
    policy_agent_name: str,
    azure_client_id: str | None = None,
) -> str:
    _ = (foundry_endpoint, chat_agent_name, product_agent_name, policy_agent_name, azure_client_id)
    instructions = build_voice_grounding_instructions()
    question_text = question.strip() or 'No question provided.'
    return f'{instructions}\n\nQuestion: {question_text}\nAnswer: I can help with that request.'
