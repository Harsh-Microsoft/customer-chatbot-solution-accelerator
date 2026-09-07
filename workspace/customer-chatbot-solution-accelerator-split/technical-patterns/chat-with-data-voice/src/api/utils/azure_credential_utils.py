from __future__ import annotations

from typing import Any

try:
    from azure.identity.aio import DefaultAzureCredential
except ImportError:  # pragma: no cover - optional runtime dependency
    DefaultAzureCredential = None  # type: ignore[assignment]


async def get_azure_credential_async(client_id: str | None = None) -> Any:
    if DefaultAzureCredential is None:
        return None
    if client_id:
        return DefaultAzureCredential(managed_identity_client_id=client_id)
    return DefaultAzureCredential()
