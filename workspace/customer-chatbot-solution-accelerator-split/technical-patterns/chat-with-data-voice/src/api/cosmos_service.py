import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from azure.cosmos import ContainerProxy, CosmosClient, DatabaseProxy, PartitionKey

from config import settings
from database import DatabaseService
from models import (
    CatalogItem,
    ChatMessage,
    ChatMessageCreate,
    ChatMessageType,
    ChatSession,
    ChatSessionCreate,
    ChatSessionUpdate,
)
from utils.azure_credential_utils import get_azure_credential

# Ported from chat-app/backend/app/cosmos_service.py (plan row 11). `Product`
# is renamed `CatalogItem` / `products_container` is renamed
# `catalog_container` per the section 6 catalog vocabulary neutralization;
# the `cart_container` and its CRUD helpers are dropped per the section 7.1
# cart companion removal (item 7 in that section's list). `transactions_container`
# and `get_orders_by_customer` are retained -- the plan's domain-leakage note
# names both as vocabulary that must survive because `services/user_onboarding.py`
# (plan row 13) is a live dependency of this module. The write endpoints
# `create_transaction`/`get_order_by_id`/`get_orders_in_date_range`/
# `is_order_returnable` are not ported: zero callers are staged anywhere in
# this pattern, matching the zero-caller skip applied to `orders.py` /
# `banking_transactions.py` / `healthcare_appointments.py` in section 7.1.
# `search_products_hybrid` / `search_products_ai_search` are ported and renamed
# `search_catalog_items_hybrid` / `search_catalog_items_ai_search` because
# `services/search.py` (plan row 13) is a live dependency of this module, not
# dead code. The write endpoints (`create`/`update`/`delete`) are not ported:
# section 6.3 of the plan drops them from the generic `catalog` router as an
# explicit, documented skip, and no other staged caller reaches them.

logger = logging.getLogger(__name__)


def _prepare_query_parameters(params: List[Dict[str, Any]]) -> List[Dict[str, object]]:
    """Ensure query parameters are properly typed for the Cosmos SDK."""
    return [{"name": p["name"], "value": p["value"]} for p in params]


class CosmosDatabaseService(DatabaseService):
    """Azure Cosmos DB implementation of the database service."""

    def __init__(self):
        self.client: CosmosClient
        self.database: DatabaseProxy
        self.catalog_container: ContainerProxy
        self.chat_container: ContainerProxy
        self.transactions_container: ContainerProxy

        try:
            if not settings.cosmos_db_endpoint:
                raise Exception("Azure Cosmos DB endpoint is required")

            logger.info("Attempting to authenticate to Azure Cosmos DB with Azure credentials...")

            client_id = str(settings.azure_client_id) if settings.azure_client_id else None
            credential = get_azure_credential(client_id=client_id)

            logger.info(f"Using Azure credential from utility (client_id: {client_id or 'system-assigned'})")

            self.client = CosmosClient(settings.cosmos_db_endpoint, credential=credential)  # type: ignore
            logger.info("Successfully created Cosmos client with environment-based credential")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to create Cosmos client with AAD auth: {error_msg}")

            if "RBAC permissions" in error_msg or "principal" in error_msg:
                raise Exception(
                    f"""
Permission error: the caller lacks Azure Cosmos DB permissions.

To fix this, run:

az cosmosdb sql role assignment create \\
    --account-name <cosmos-account-name> \\
    --resource-group <resource-group> \\
    --scope "/" \\
    --principal-id <principal-id> \\
    --role-definition-name "Cosmos DB Built-in Data Contributor"

Original error: {error_msg}
                """
                )

            if "Local Authorization is disabled" in error_msg:
                raise Exception(
                    f"""
Authentication error: this Azure Cosmos DB requires AAD authentication and the caller's
credentials don't have the required permissions. Grant the "Cosmos DB Built-in Data
Contributor" role to the calling identity.

Original error: {error_msg}
                """
                )

            raise Exception(
                f"Cannot authenticate to Azure Cosmos DB with Azure credentials. Check login and permissions. Error: {error_msg}"
            )

        self.database = self.client.get_database_client(settings.cosmos_db_database_name)
        self._initialize_containers()

    def _serialize_datetime_fields(self, data: dict) -> dict:
        """Convert datetime objects to ISO format for Azure Cosmos DB serialization."""
        serialized_data = data.copy()
        for key, value in serialized_data.items():
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    serialized_data[key] = value.replace(tzinfo=None).isoformat() + "Z"
                else:
                    serialized_data[key] = value.isoformat()
        return serialized_data

    def _initialize_containers(self):
        """Initialize Azure Cosmos DB containers."""
        try:
            self.database = self.client.create_database_if_not_exists(
                id=settings.cosmos_db_database_name
            )

            self.catalog_container = self.database.create_container_if_not_exists(
                id="catalog_items",
                partition_key=PartitionKey(path="/category"),
                offer_throughput=400,
            )

            self.chat_container = self.database.create_container_if_not_exists(
                id="chat_sessions",
                partition_key=PartitionKey(path="/user_id"),
                offer_throughput=400,
            )

            self.transactions_container = self.database.create_container_if_not_exists(
                id="transactions",
                partition_key=PartitionKey(path="/user_id"),
                offer_throughput=400,
            )

            logger.info("Azure Cosmos DB containers initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing Azure Cosmos DB containers: {str(e)}")
            raise

    # ------------------------------------------------------------------
    # Catalog operations
    # ------------------------------------------------------------------

    def _item_from_cosmos(self, item: dict) -> CatalogItem:
        return CatalogItem(
            id=item.get("id"),
            title=item.get("title", ""),
            category=item.get("category", ""),
            description=item.get("description", ""),
            image=item.get("image", ""),
            highlights=item.get("highlights", []),
            price=item.get("price"),
            rating=item.get("rating"),
        )

    async def get_catalog_items(
        self, search_params: Optional[Dict[str, Any]] = None
    ) -> List[CatalogItem]:
        """Get catalog items with optional filtering."""
        try:
            query = "SELECT * FROM c"
            parameters: List[Dict[str, Any]] = []

            if search_params:
                conditions = []

                if search_params.get("category") and search_params["category"] != "All":
                    conditions.append("c.category = @category")
                    parameters.append({"name": "@category", "value": search_params["category"]})

                if search_params.get("query"):
                    conditions.append(
                        "(CONTAINS(LOWER(c.title), LOWER(@query)) OR CONTAINS(LOWER(c.description), LOWER(@query)))"
                    )
                    parameters.append({"name": "@query", "value": search_params["query"]})

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

            sort_by = search_params.get("sort_by", "name") if search_params else "name"
            sort_order = search_params.get("sort_order", "asc") if search_params else "asc"

            if sort_by == "name":
                query += f" ORDER BY c.title {'DESC' if sort_order == 'desc' else 'ASC'}"
            elif sort_by == "price":
                query += f" ORDER BY c.price {'DESC' if sort_order == 'desc' else 'ASC'}"
            elif sort_by == "rating":
                query += f" ORDER BY c.rating {'DESC' if sort_order == 'desc' else 'ASC'}"

            items = list(
                self.catalog_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    enable_cross_partition_query=True,
                )
            )
            return [self._item_from_cosmos(item) for item in items]

        except Exception as e:
            logger.error(f"Error fetching catalog items from Azure Cosmos DB: {str(e)}")
            raise

    async def get_catalog_item(self, item_id: str) -> Optional[CatalogItem]:
        """Get a single catalog item by ID."""
        try:
            query = "SELECT * FROM c WHERE c.id = @item_id"
            parameters = [{"name": "@item_id", "value": item_id}]

            items = list(
                self.catalog_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    enable_cross_partition_query=True,
                )
            )
            return self._item_from_cosmos(items[0]) if items else None

        except Exception as e:
            logger.error(f"Error fetching catalog item from Azure Cosmos DB: {str(e)}")
            raise

    async def get_catalog_categories(self) -> List[str]:
        """Get the distinct set of catalog categories."""
        try:
            query = "SELECT DISTINCT VALUE c.category FROM c"
            items = list(
                self.catalog_container.query_items(
                    query=query,
                    enable_cross_partition_query=True,
                )
            )
            return [category for category in items if category]

        except Exception as e:
            logger.error(f"Error fetching catalog categories from Azure Cosmos DB: {str(e)}")
            raise

    async def get_featured_catalog_items(self, limit: int = 10) -> List[CatalogItem]:
        """Get the top-rated catalog items."""
        try:
            query = f"SELECT TOP {int(limit)} * FROM c ORDER BY c.rating DESC"
            items = list(
                self.catalog_container.query_items(
                    query=query,
                    enable_cross_partition_query=True,
                )
            )
            return [self._item_from_cosmos(item) for item in items]

        except Exception as e:
            logger.error(f"Error fetching featured catalog items from Azure Cosmos DB: {str(e)}")
            raise

    async def get_related_catalog_items(self, item_id: str, limit: int = 5) -> List[CatalogItem]:
        """Get other catalog items in the same category as `item_id`."""
        try:
            item = await self.get_catalog_item(item_id)
            if item is None:
                return []

            query = f"SELECT TOP {int(limit)} * FROM c WHERE c.category = @category AND c.id != @item_id"
            parameters = [
                {"name": "@category", "value": item.category},
                {"name": "@item_id", "value": item_id},
            ]
            items = list(
                self.catalog_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    enable_cross_partition_query=True,
                )
            )
            return [self._item_from_cosmos(item) for item in items]

        except Exception as e:
            logger.error(f"Error fetching related catalog items from Azure Cosmos DB: {str(e)}")
            raise

    async def get_catalog_items_by_category(self, category: str, limit: int = 10) -> List[CatalogItem]:
        """Get catalog items in a single category."""
        items = await self.get_catalog_items({"category": category})
        return items[:limit]

    # ------------------------------------------------------------------
    # Transaction history operations (read path for services/user_onboarding.py)
    # ------------------------------------------------------------------

    async def get_orders_by_customer(self, customer_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get transaction history for a customer from the transactions container."""
        try:
            query = "SELECT * FROM c WHERE c.user_id = @customer_id ORDER BY c.created_at DESC"
            parameters = [{"name": "@customer_id", "value": customer_id}]

            items = list(
                self.transactions_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    enable_cross_partition_query=False,
                )
            )
            return items[:limit]

        except Exception as e:
            logger.error(f"Error getting orders for customer {customer_id}: {e}")
            return []

    async def search_catalog_items(self, query: str, limit: int = 10) -> List[CatalogItem]:
        """Search catalog items by query (title/description substring)."""
        items = await self.get_catalog_items({"query": query})
        return items[:limit]

    async def search_catalog_items_hybrid(self, query: str, limit: int = 10) -> List[CatalogItem]:
        """Hybrid search: Azure AI Search first (fast), then Azure Cosmos DB fallback."""
        try:
            try:
                from services.search import search_catalog_items_fast

                ai_search_results = search_catalog_items_fast(query, limit)

                if ai_search_results:
                    logger.info(
                        f"Azure AI Search returned {len(ai_search_results)} catalog items for query: {query}"
                    )

                    items: List[CatalogItem] = []
                    for hit in ai_search_results:
                        try:
                            full_item = await self.get_catalog_item(hit["id"])
                            if full_item:
                                items.append(full_item)
                            else:
                                items.append(
                                    CatalogItem(
                                        id=hit["id"],
                                        title=hit.get("title", ""),
                                        price=hit.get("price"),
                                        image=hit.get("image", ""),
                                        category=hit.get("category", ""),
                                        description=hit.get("description", ""),
                                    )
                                )
                        except Exception as e:
                            logger.warning(f"Failed to get full catalog item for {hit['id']}: {e}")
                            continue

                    if items:
                        logger.info(f"Hybrid search (Azure AI Search) returned {len(items)} catalog items")
                        return items[:limit]

            except ImportError:
                logger.warning("Azure AI Search not available, falling back to Azure Cosmos DB")
            except Exception as e:
                logger.warning(f"Azure AI Search failed: {e}, falling back to Azure Cosmos DB")

            logger.info(f"Falling back to enhanced Azure Cosmos DB search for query: {query}")
            return await self.search_catalog_items_enhanced(query, limit)

        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return await self.search_catalog_items(query, limit)

    async def search_catalog_items_ai_search(self, query: str, limit: int = 10) -> List[CatalogItem]:
        """Search catalog items using Azure AI Search only."""
        try:
            from services.search import search_catalog_items as _search_catalog_items_index

            ai_search_results = _search_catalog_items_index(query, limit)
            if not ai_search_results:
                return []

            items: List[CatalogItem] = []
            for hit in ai_search_results:
                try:
                    full_item = await self.get_catalog_item(hit["id"])
                    if full_item:
                        items.append(full_item)
                    else:
                        items.append(
                            CatalogItem(
                                id=hit["id"],
                                title=hit.get("title", ""),
                                price=hit.get("price"),
                                image=hit.get("image", ""),
                                category=hit.get("category", ""),
                                description=hit.get("description", ""),
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to process Azure AI Search result {hit['id']}: {e}")
                    continue

            logger.info(f"Azure AI Search returned {len(items)} catalog items for query: {query}")
            return items[:limit]

        except Exception as e:
            logger.error(f"Azure AI Search error: {e}")
            return []

    async def search_catalog_items_enhanced(self, query: str, limit: int = 10) -> List[CatalogItem]:
        """Enhanced catalog search with fuzzy, per-term, and category fallback strategies."""
        try:
            terms = query.lower().split()

            search_strategies: List[Dict[str, Any]] = [
                {
                    "query": """
                        SELECT * FROM c
                        WHERE CONTAINS(LOWER(c.title), LOWER(@query))
                           OR CONTAINS(LOWER(c.description), LOWER(@query))
                        ORDER BY c.rating DESC, c.price ASC
                    """,
                    "params": [{"name": "@query", "value": query}],
                },
                {
                    "query": """
                        SELECT * FROM c
                        WHERE {conditions}
                        ORDER BY c.rating DESC, c.price ASC
                    """,
                    "params": [],
                },
                {
                    "query": """
                        SELECT * FROM c
                        WHERE CONTAINS(LOWER(c.category), LOWER(@query))
                        ORDER BY c.rating DESC, c.price ASC
                    """,
                    "params": [{"name": "@query", "value": query}],
                },
            ]

            if len(terms) > 1:
                conditions = []
                for i, term in enumerate(terms):
                    param_name = f"@term{i}"
                    conditions.append(
                        f"""
                        (CONTAINS(LOWER(c.title), LOWER({param_name})) OR
                         CONTAINS(LOWER(c.description), LOWER({param_name})))
                    """
                    )
                    search_strategies[1]["params"].append({"name": param_name, "value": term})

                search_strategies[1]["query"] = search_strategies[1]["query"].format(
                    conditions=" OR ".join(conditions)
                )

            for strategy in search_strategies:
                try:
                    items = list(
                        self.catalog_container.query_items(
                            query=strategy["query"],
                            parameters=strategy["params"],
                            enable_cross_partition_query=True,
                        )
                    )

                    results = [self._item_from_cosmos(item) for item in items[:limit]]
                    if results:
                        logger.info(
                            f"Enhanced search strategy returned {len(results)} catalog items for query: {query}"
                        )
                        return results

                except Exception as strategy_error:
                    logger.warning(f"Search strategy failed: {strategy_error}")
                    continue

            logger.warning(f"All enhanced search strategies failed for query: {query}")
            return await self.search_catalog_items(query, limit)

        except Exception as e:
            logger.error(f"Enhanced catalog search error: {e}")
            return await self.search_catalog_items(query, limit)

    # ------------------------------------------------------------------
    # Chat session operations (messages embedded in ChatSession.messages)
    # ------------------------------------------------------------------

    async def get_chat_session(
        self, session_id: str, user_id: Optional[str] = None
    ) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        try:
            query = "SELECT * FROM c WHERE c.id = @session_id"
            parameters = [{"name": "@session_id", "value": session_id}]

            items = list(
                self.chat_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    enable_cross_partition_query=True,
                )
            )
            if not items:
                return None

            session_data = items[0]
            for field in ["created_at", "updated_at", "last_message_at"]:
                if field in session_data and isinstance(session_data[field], str):
                    session_data[field] = datetime.fromisoformat(session_data[field].replace("Z", "+00:00"))

            messages = session_data.get("messages", [])
            for message in messages:
                if "created_at" in message and isinstance(message["created_at"], str):
                    message["created_at"] = datetime.fromisoformat(message["created_at"].replace("Z", "+00:00"))

            session_data["message_count"] = len(messages)
            return ChatSession(**session_data)

        except Exception as e:
            logger.error(f"Error fetching chat session from Azure Cosmos DB: {str(e)}")
            raise

    async def get_chat_sessions_by_user(self, user_id: str) -> List[ChatSession]:
        """Get all chat sessions for a user."""
        try:
            query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.last_message_at DESC"
            parameters = [{"name": "@user_id", "value": user_id}]

            items = list(
                self.chat_container.query_items(
                    query=query,
                    parameters=_prepare_query_parameters(parameters),
                    partition_key=user_id,
                )
            )

            sessions = []
            for item in items:
                for field in ["created_at", "updated_at", "last_message_at"]:
                    if field in item and isinstance(item[field], str):
                        item[field] = datetime.fromisoformat(item[field].replace("Z", "+00:00"))
                for message in item.get("messages", []):
                    if "created_at" in message and isinstance(message["created_at"], str):
                        message["created_at"] = datetime.fromisoformat(message["created_at"].replace("Z", "+00:00"))
                sessions.append(ChatSession(**item))

            return sessions

        except Exception as e:
            logger.error(f"Error fetching chat sessions from Azure Cosmos DB: {str(e)}")
            raise

    async def create_chat_session(self, session: ChatSessionCreate) -> ChatSession:
        """Create a new chat session."""
        try:
            new_session = ChatSession(
                id=str(uuid.uuid4()),
                user_id=session.user_id,
                session_name=session.session_name or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                context=session.context,
                messages=[],
                message_count=0,
            )
            session_dict = self._serialize_datetime_fields(new_session.model_dump())
            for msg in session_dict.get("messages", []):
                if "created_at" in msg and isinstance(msg["created_at"], datetime):
                    msg["created_at"] = msg["created_at"].isoformat()

            self.chat_container.create_item(session_dict)  # type: ignore
            return new_session

        except Exception as e:
            logger.error(f"Error creating chat session in Azure Cosmos DB: {str(e)}")
            raise

    async def add_message_to_session(
        self, session_id: str, message: ChatMessageCreate, user_id: Optional[str] = None
    ) -> ChatSession:
        """Add a message to an existing chat session, creating it if missing."""
        try:
            session = await self.get_chat_session(session_id, user_id)
            if not session:
                session = ChatSession(
                    id=session_id,
                    user_id=user_id,
                    session_name=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    context={},
                    messages=[],
                    message_count=0,
                )
                session_dict = self._serialize_datetime_fields(session.model_dump())
                for msg in session_dict.get("messages", []):
                    if "created_at" in msg and isinstance(msg["created_at"], datetime):
                        msg["created_at"] = msg["created_at"].isoformat()
                self.chat_container.create_item(session_dict)  # type: ignore

            new_message = ChatMessage(
                content=message.content,
                message_type=message.message_type or ChatMessageType.USER,
                user_id=user_id,
                metadata=message.metadata,
            )
            session.messages.append(new_message)
            session.message_count = len(session.messages)
            session.last_message_at = new_message.created_at
            session.updated_at = datetime.utcnow()

            session_dict = session.model_dump()
            for field in ["created_at", "updated_at", "last_message_at"]:
                if field in session_dict and isinstance(session_dict[field], datetime):
                    session_dict[field] = session_dict[field].isoformat()
            for msg in session_dict.get("messages", []):
                if "created_at" in msg and isinstance(msg["created_at"], datetime):
                    msg["created_at"] = msg["created_at"].isoformat()

            self.chat_container.upsert_item(session_dict)  # type: ignore

            updated_session = await self.get_chat_session(session_id, user_id)
            if not updated_session:
                raise Exception(f"Failed to retrieve updated session {session_id}")
            return updated_session

        except Exception as e:
            logger.error(f"Error adding message to chat session in Azure Cosmos DB: {str(e)}")
            raise

    async def update_chat_session(
        self, session_id: str, session_update: ChatSessionUpdate, user_id: Optional[str] = None
    ) -> Optional[ChatSession]:
        """Update a chat session's metadata."""
        try:
            session = await self.get_chat_session(session_id, user_id)
            if not session:
                return None

            update_data = session_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(session, field, value)
            session.updated_at = datetime.utcnow()

            session_dict = session.model_dump()
            for field in ["created_at", "updated_at", "last_message_at"]:
                if field in session_dict and isinstance(session_dict[field], datetime):
                    session_dict[field] = session_dict[field].isoformat()
            for msg in session_dict.get("messages", []):
                if "created_at" in msg and isinstance(msg["created_at"], datetime):
                    msg["created_at"] = msg["created_at"].isoformat()

            self.chat_container.upsert_item(session_dict)  # type: ignore
            return session

        except Exception as e:
            logger.error(f"Error updating chat session in Azure Cosmos DB: {str(e)}")
            raise

    async def delete_chat_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a chat session."""
        try:
            session = await self.get_chat_session(session_id, user_id)
            if not session:
                return False

            partition_key = session.user_id or user_id or "anonymous"
            self.chat_container.delete_item(item=session_id, partition_key=partition_key)  # type: ignore
            return True

        except Exception as e:
            logger.error(f"Error deleting chat session from Azure Cosmos DB: {str(e)}")
            raise


_cosmos_service: Optional["CosmosDatabaseService"] = None


def get_cosmos_service() -> "CosmosDatabaseService":
    """Get the global Cosmos DB service instance (lazy initialization)."""
    global _cosmos_service
    if _cosmos_service is None:
        _cosmos_service = CosmosDatabaseService()
    return _cosmos_service
