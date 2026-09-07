from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from config import has_cosmos_db_config
from models import (
    CatalogItem,
    ChatMessageCreate,
    ChatSession,
    ChatSessionCreate,
    ChatSessionUpdate,
)

# Ported from chat-app/backend/app/database.py (plan row 11), reconciled with
# scenario-app/backend/app/database.py (plan row 34). `Product` is renamed
# `CatalogItem` per the section 6 catalog vocabulary neutralization; the
# `Cart`/`Order` abstract methods and their models are dropped outright per
# the section 7.1 cart companion removal (item 7 - "cosmos_service.py /
# database.py - the cart container binding and cart CRUD helpers"). Chat
# messages are embedded in `ChatSession.messages` in the real Cosmos
# implementation (`add_message_to_session`), matching the source design
# rather than a separate messages collection.


class DatabaseService(ABC):
    """Abstract base class for database operations."""

    # Catalog operations
    @abstractmethod
    async def get_catalog_items(
        self, search_params: Optional[Dict[str, Any]] = None
    ) -> List[CatalogItem]:
        pass

    @abstractmethod
    async def get_catalog_item(self, item_id: str) -> Optional[CatalogItem]:
        pass

    @abstractmethod
    async def get_catalog_categories(self) -> List[str]:
        pass

    @abstractmethod
    async def get_featured_catalog_items(self, limit: int = 10) -> List[CatalogItem]:
        pass

    @abstractmethod
    async def get_related_catalog_items(self, item_id: str, limit: int = 5) -> List[CatalogItem]:
        pass

    # Chat session operations (messages are embedded in ChatSession.messages)
    @abstractmethod
    async def get_chat_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[ChatSession]:
        pass

    @abstractmethod
    async def get_chat_sessions_by_user(self, user_id: str) -> List[ChatSession]:
        pass

    @abstractmethod
    async def create_chat_session(self, session: ChatSessionCreate) -> ChatSession:
        pass

    @abstractmethod
    async def add_message_to_session(
        self, session_id: str, message: ChatMessageCreate, user_id: Optional[str] = None
    ) -> ChatSession:
        pass

    @abstractmethod
    async def update_chat_session(
        self, session_id: str, session_update: ChatSessionUpdate, user_id: Optional[str] = None
    ) -> Optional[ChatSession]:
        pass

    @abstractmethod
    async def delete_chat_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        pass


def get_database_service() -> DatabaseService:
    """Get the appropriate database service based on configuration."""
    if has_cosmos_db_config():
        try:
            from cosmos_service import CosmosDatabaseService
        except ImportError as exc:
            raise RuntimeError(
                f"Cannot connect to Azure Cosmos DB: {exc}. Please check your COSMOS_DB_ENDPOINT configuration."
            )
        return CosmosDatabaseService()

    # No fallback - raise error if Azure Cosmos DB config is missing
    raise RuntimeError(
        "Azure Cosmos DB is not configured. Please set COSMOS_DB_ENDPOINT environment variable."
    )


# Global database service instance - lazy initialization
db_service = None


def get_db_service() -> DatabaseService:
    """Get the database service instance with lazy initialization."""
    global db_service
    if db_service is None:
        db_service = get_database_service()
    return db_service
