from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

# Consolidated manifest loader. Previously duplicated across
# scripts/shared/scenario_loader.py, scenario_config.py, and
# routers/scenario_config_api.py; this is now the single implementation.
# Moved here (rather than staying under scripts/) because the API
# Dockerfile builds from src/api as its context and scripts/ never ships
# in the container image.


def resolve_scenario_path() -> Path:
    """Resolve the composed scenario folder, failing fast if it is missing."""
    raw = os.environ.get('SCENARIO_PATH', '').strip()
    if not raw:
        raise RuntimeError('SCENARIO_PATH is required')
    path = Path(raw).resolve()
    if not (path / 'manifest.json').is_file():
        raise RuntimeError(f'No manifest.json found under SCENARIO_PATH={path}')
    return path


@lru_cache(maxsize=1)
def load_manifest() -> dict[str, Any]:
    """Load the composed scenario's manifest.json, cached for the process lifetime."""
    path = resolve_scenario_path() / 'manifest.json'
    with path.open(encoding='utf-8') as handle:
        return json.load(handle)


def load_agent_instructions() -> list[tuple[str, str]]:
    agents_dir = resolve_scenario_path() / 'agents'
    if not agents_dir.is_dir():
        return []
    items: list[tuple[str, str]] = []
    for item in sorted(agents_dir.glob('*.txt')):
        items.append((item.stem, item.read_text(encoding='utf-8')))
    return items


def load_catalog_rows() -> Path:
    manifest = load_manifest()
    data = manifest.get('data', {}) if isinstance(manifest, dict) else {}
    catalog_csv = str(data.get('catalogCsv', 'data/catalog.csv')).strip()
    return (resolve_scenario_path() / catalog_csv).resolve()


def load_policy_docs() -> Iterable[Path]:
    manifest = load_manifest()
    data = manifest.get('data', {}) if isinstance(manifest, dict) else {}
    policies_dir = str(data.get('policiesDir', 'data/policies')).strip()
    root = (resolve_scenario_path() / policies_dir).resolve()
    if not root.is_dir():
        return []
    return sorted(root.glob('*'))
