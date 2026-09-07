import uuid
from typing import Any, Dict, List, Optional

from models import CatalogItem

# Ported from scenario-app/backend/app/memory_service.py (plan row 34).
# `Product` is renamed `CatalogItem` per the section 6 catalog vocabulary
# neutralization. The source `EcommerceMemoryService` also implements
# Customer/Cart/Order operations against `EcommerceDatabaseService`; none of
# those are ported: `Cart` per the section 7.1 cart companion removal, and
# `Customer`/`Order` because this pattern's `DatabaseService` (see
# `database.py`) carries no user/order abstraction to implement against --
# the same reasoning `routers/auth.py` already documents for skipping
# `services/user_onboarding.py`'s persistence path. This class is a
# standalone in-memory catalog store; `database.py`'s factory intentionally
# has no Cosmos DB fallback, so it is not wired there.


def _sample_catalog_items() -> List[CatalogItem]:
    return [
        CatalogItem(
            id=str(uuid.uuid4()),
            title="Sample Catalog Item A",
            category="general",
            description="Starter item for demos.",
            image="/placeholder-a.jpg",
            highlights=[],
            price=29.99,
            rating=4.5,
        ),
        CatalogItem(
            id=str(uuid.uuid4()),
            title="Sample Catalog Item B",
            category="general",
            description="Second starter item for demos.",
            image="/placeholder-b.jpg",
            highlights=[],
            price=45.0,
            rating=4.8,
        ),
        CatalogItem(
            id=str(uuid.uuid4()),
            title="Sample Catalog Item C",
            category="featured",
            description="Featured starter item for demos.",
            image="/placeholder-c.jpg",
            highlights=[],
            price=38.5,
            rating=4.2,
        ),
    ]


class InMemoryCatalogService:
    """Standalone in-memory catalog store for local development and tests."""

    def __init__(self) -> None:
        self._items: Dict[str, CatalogItem] = {}
        for item in _sample_catalog_items():
            self._items[item.id] = item

    async def get_catalog_items(
        self, search_params: Optional[Dict[str, Any]] = None
    ) -> List[CatalogItem]:
        items = list(self._items.values())
        if not search_params:
            return sorted(items, key=lambda x: x.title.lower())

        category = search_params.get("category")
        query = (search_params.get("query") or "").strip().lower()
        sort_by = search_params.get("sort_by") or "name"
        sort_order = search_params.get("sort_order") or "asc"

        if category and category != "All":
            items = [i for i in items if i.category == category]
        if query:
            items = [
                i
                for i in items
                if query in i.title.lower()
                or (i.description and query in i.description.lower())
            ]

        reverse = sort_order == "desc"
        if sort_by == "price":
            items.sort(key=lambda x: x.price or 0.0, reverse=reverse)
        elif sort_by == "rating":
            items.sort(key=lambda x: x.rating or 0.0, reverse=reverse)
        else:
            items.sort(key=lambda x: x.title.lower(), reverse=reverse)
        return items

    async def get_catalog_item(self, item_id: str) -> Optional[CatalogItem]:
        return self._items.get(item_id)

    async def get_catalog_categories(self) -> List[str]:
        return sorted({i.category for i in self._items.values()})

    async def get_featured_catalog_items(self, limit: int = 10) -> List[CatalogItem]:
        items = sorted(self._items.values(), key=lambda x: x.rating or 0.0, reverse=True)
        return items[:limit]

    async def get_related_catalog_items(
        self, item_id: str, limit: int = 5
    ) -> List[CatalogItem]:
        base = self._items.get(item_id)
        if not base:
            return []
        same = [
            i
            for i in self._items.values()
            if i.category == base.category and i.id != item_id
        ]
        same.sort(key=lambda x: x.rating or 0.0, reverse=True)
        return same[:limit]
