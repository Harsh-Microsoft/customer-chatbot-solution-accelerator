import logging
from typing import Any, Dict, List, Optional

from azure.search.documents import SearchClient

from config import has_azure_search_config, settings
from utils.azure_credential_utils import get_azure_credential

# Ported from chat-app/backend/app/services/search.py (plan row 13). Live
# dependency of `cosmos_service.py` (`search_catalog_items_hybrid` /
# `search_catalog_items_ai_search`), not dead code. Renamed to catalog
# vocabulary: `get_product_search_client` -> `get_catalog_search_client`,
# `search_products` -> `search_catalog_items`, `search_products_fast` ->
# `search_catalog_items_fast`.

logger = logging.getLogger(__name__)

_client = None
_catalog_client = None


def get_search_client() -> Optional[SearchClient]:
    """Get Azure Search client (reference documents) with AAD authentication."""
    global _client
    if _client is None and has_azure_search_config():
        try:
            endpoint = settings.azure_search_endpoint
            if not endpoint:
                logger.warning("Azure Search endpoint not configured")
                return None

            credential = get_azure_credential()
            _client = SearchClient(
                endpoint=endpoint,
                index_name="reference-docs",
                credential=credential,  # type: ignore
            )
            logger.info("Azure Search client initialized successfully with AAD authentication")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Search client: {e}")
            _client = None
    return _client


def get_catalog_search_client() -> Optional[SearchClient]:
    """Get Azure Search client for catalog items with AAD authentication."""
    global _catalog_client
    if _catalog_client is None and has_azure_search_config():
        try:
            endpoint = settings.azure_search_endpoint
            if not endpoint:
                logger.warning("Azure Search endpoint not configured")
                return None

            credential = get_azure_credential()
            _catalog_client = SearchClient(
                endpoint=endpoint,
                index_name=settings.azure_search_catalog_index,
                credential=credential,  # type: ignore
            )
            logger.info("Azure Catalog Search client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Catalog Search client: {e}")
            _catalog_client = None
    return _catalog_client


def search_reference(query: str, top: int = 5) -> List[Dict[str, Any]]:
    """Search reference (policy) documents with semantic search, falling back to simple search."""
    client = get_search_client()
    if not client:
        logger.warning("Azure Search not configured, returning empty results")
        return []

    try:
        try:
            results = client.search(  # type: ignore
                search_text=query,
                top=top,
                query_type="semantic",
                semantic_configuration_name="default",
                query_language="en-us",
                speller="lexicon",
                query_answer="extractive|count-3",
                query_caption="extractive|highlight-true",
            )
        except Exception as semantic_error:
            logger.warning(f"Semantic search failed, falling back to simple search: {semantic_error}")
            results = client.search(search_text=query, top=top, query_type="simple")  # type: ignore

        hits = []
        for r in results:
            hit = {
                "id": r.get("id"),
                "title": r.get("title"),
                "content": r.get("content"),
                "score": getattr(r, "@search.score", None),
            }
            if hasattr(r, "@search.answers") and r.get("@search.answers"):
                hit["answers"] = [answer["text"] for answer in r["@search.answers"]]
            if hasattr(r, "@search.captions") and r.get("@search.captions"):
                hit["captions"] = [caption["text"] for caption in r["@search.captions"]]
            hits.append(hit)

        logger.info(f"Search query '{query}' returned {len(hits)} results")
        return hits
    except Exception as e:
        logger.error(f"Error searching reference documents: {e}")
        return []


def search_catalog_items(query: str, top: int = 5, context: str = "") -> List[Dict[str, Any]]:
    """Search catalog items using Azure AI Search with semantic capabilities."""
    client = get_catalog_search_client()
    if not client:
        logger.warning("Azure Catalog Search not configured, returning empty results")
        return []

    try:
        enhanced_query = f"{query} {context}".strip()

        search_strategies = [
            {
                "query_type": "semantic",
                "semantic_configuration_name": "default",
                "query_answer": "extractive|count-3",
                "query_caption": "extractive|highlight-true",
            },
            {
                "query_type": "full",
                "highlight": "title,description,content",
                "highlight_pre_tag": "<mark>",
                "highlight_post_tag": "</mark>",
            },
            {"query_type": "simple"},
            {},
        ]

        hits: List[Dict[str, Any]] = []
        for strategy in search_strategies:
            try:
                results = client.search(search_text=enhanced_query, top=top, **strategy)  # type: ignore

                hits = []
                for r in results:
                    hit = {
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "description": r.get("description"),
                        "price": r.get("price"),
                        "category": r.get("category"),
                        "image": r.get("image"),
                        "score": getattr(r, "@search.score", None),
                    }
                    if "query_answer" in strategy and hasattr(r, "@search.answers"):
                        hit["answers"] = [answer["text"] for answer in r.get("@search.answers", [])]
                    if "highlight" in strategy and hasattr(r, "@search.highlights"):
                        hit["highlights"] = r.get("@search.highlights", {})
                    hits.append(hit)

                if hits:
                    logger.info(
                        f"Catalog search strategy '{strategy.get('query_type', 'basic')}' returned {len(hits)} results"
                    )
                    break

            except Exception as strategy_error:
                logger.warning(f"Catalog search strategy failed: {strategy_error}")
                continue

        return hits
    except Exception as e:
        logger.error(f"Catalog search error: {e}")
        return []


def search_catalog_items_fast(query: str, top: int = 3) -> List[Dict[str, Any]]:
    """Fast catalog item search optimized for chat responses."""
    client = get_catalog_search_client()
    if not client:
        return []

    try:
        try:
            results = client.search(  # type: ignore
                search_text=query,
                top=top,
                query_type="semantic",
                semantic_configuration_name="default",
                query_answer="extractive|count-2",
                query_caption="extractive|highlight-false",
            )
        except Exception:
            results = client.search(search_text=query, top=top)  # type: ignore

        hits = []
        for r in results:
            hit = {
                "id": r.get("id"),
                "title": r.get("title"),
                "description": r.get("description"),
                "price": r.get("price"),
                "category": r.get("category"),
                "score": getattr(r, "@search.score", None),
            }
            if hasattr(r, "@search.answers") and r.get("@search.answers"):
                hit["answers"] = [answer["text"] for answer in r["@search.answers"]]
            hits.append(hit)

        logger.info(f"Fast catalog search returned {len(hits)} results for query: {query}")
        return hits

    except Exception as e:
        logger.error(f"Fast catalog search error: {e}")
        return []
