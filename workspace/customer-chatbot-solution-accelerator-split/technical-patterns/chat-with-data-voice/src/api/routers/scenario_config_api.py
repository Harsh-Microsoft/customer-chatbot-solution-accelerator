from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse

from scenario_loader import load_manifest as load_scenario_manifest

from config import settings

router = APIRouter(prefix='/api/scenario', tags=['scenario-config'])
_ALLOWED_ASSET_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.svg', '.webp', '.gif'}
_ALLOWED_CONFIG_KEYS = ('host', 'welcome', 'catalog', 'presentation')


def _browser_safe_manifest(manifest: dict) -> dict:
    return {key: manifest.get(key, {}) for key in _ALLOWED_CONFIG_KEYS}


def _reject_if_invalid(asset_path: str) -> None:
    if not asset_path:
        raise HTTPException(status_code=404, detail='Not found')
    decoded = unquote(asset_path)
    if decoded != asset_path:
        asset_path = decoded
    candidate = Path(asset_path)
    if candidate.is_absolute() or candidate.drive:
        raise HTTPException(status_code=404, detail='Not found')
    if any(part in ('..', '') for part in candidate.parts):
        raise HTTPException(status_code=404, detail='Not found')


def _resolve_asset_path(asset_path: str) -> Path:
    _reject_if_invalid(asset_path)
    scenario_root = settings.scenario_root.resolve()
    resolved = (scenario_root / asset_path).resolve()
    if scenario_root not in resolved.parents and resolved != scenario_root:
        raise HTTPException(status_code=404, detail='Not found')
    if resolved.suffix.lower() not in _ALLOWED_ASSET_EXTENSIONS:
        raise HTTPException(status_code=404, detail='Not found')
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail='Not found')
    return resolved


@router.get('/config')
async def get_scenario_config():
    manifest = load_scenario_manifest()
    return _browser_safe_manifest(manifest)


@router.get('/assets/{asset_path:path}')
async def get_scenario_asset(asset_path: str):
    resolved = _resolve_asset_path(asset_path)
    content_type, _ = mimetypes.guess_type(str(resolved))
    content_type = content_type or 'application/octet-stream'
    headers = {'Cache-Control': 'public, max-age=31536000, immutable'}
    if resolved.suffix.lower() == '.svg':
        headers.update(
            {
                'Content-Disposition': 'inline',
                'X-Content-Type-Options': 'nosniff',
                'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
            }
        )
    return FileResponse(path=resolved, media_type=content_type, headers=headers)
