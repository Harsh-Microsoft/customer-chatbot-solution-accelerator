from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from database import get_db_service
from models import APIResponse, CatalogItem
from .scenario_config_api import load_scenario_manifest

_manifest = load_scenario_manifest()
_catalog_config = _manifest.get('catalog', {}) if isinstance(_manifest, dict) else {}
router = APIRouter(prefix=str(_catalog_config.get('routePrefix', '/api/catalog')), tags=['catalog'])


@router.get('/', response_model=List[CatalogItem])
async def list_catalog_items(
    category: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    sort_by: str = Query('name'),
    sort_order: str = Query('asc'),
):
    try:
        return await get_db_service().get_catalog_items(
            {
                'category': category,
                'query': query,
                'sort_by': sort_by,
                'sort_order': sort_order,
            }
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Error fetching catalog items: {exc}')


@router.get('/categories', response_model=List[str])
async def list_catalog_categories():
    try:
        return await get_db_service().get_catalog_categories()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Error fetching catalog categories: {exc}')


@router.get('/featured', response_model=List[CatalogItem])
async def list_featured_catalog_items(limit: int = Query(10, ge=1, le=50)):
    try:
        return await get_db_service().get_featured_catalog_items(limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Error fetching featured catalog items: {exc}')


@router.get('/{item_id}', response_model=CatalogItem)
async def read_catalog_item(item_id: str):
    try:
        item = await get_db_service().get_catalog_item(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail='Item not found')
        return item
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Error fetching catalog item: {exc}')


@router.get('/{item_id}/related', response_model=List[CatalogItem])
async def list_related_catalog_items(item_id: str, limit: int = Query(5, ge=1, le=20)):
    try:
        return await get_db_service().get_related_catalog_items(item_id, limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f'Error fetching related catalog items: {exc}')
