from __future__ import annotations

from scenario_loader import load_manifest as load_scenario_manifest

_ALLOWED_KEYS = ('host', 'welcome', 'catalog', 'presentation')


def current_scenario() -> str:
    manifest = load_scenario_manifest()
    candidate = str(manifest.get('id') or manifest.get('name') or 'default').strip()
    return candidate or 'default'


def catalog_tool_name() -> str:
    manifest = load_scenario_manifest()
    agents = manifest.get('agents', {}) if isinstance(manifest, dict) else {}
    name = str(agents.get('catalogToolName') or '').strip()
    if not name:
        raise RuntimeError("Scenario manifest is missing required 'agents.catalogToolName'")
    return name


def policy_tool_name() -> str:
    manifest = load_scenario_manifest()
    agents = manifest.get('agents', {}) if isinstance(manifest, dict) else {}
    name = str(agents.get('policyToolName') or '').strip()
    if not name:
        raise RuntimeError("Scenario manifest is missing required 'agents.policyToolName'")
    return name


def welcome_config() -> dict:
    manifest = load_scenario_manifest()
    welcome = manifest.get('welcome', {}) if isinstance(manifest, dict) else {}
    return {
        'title': str(welcome.get('title') or 'Welcome'),
        'subtitle': str(welcome.get('subtitle') or ''),
        'hint': str(welcome.get('hint') or ''),
    }


def compliance_banner() -> str:
    manifest = load_scenario_manifest()
    host = manifest.get('host', {}) if isinstance(manifest, dict) else {}
    return str(host.get('complianceBanner') or '')


def voice_grounding_config() -> dict:
    return {
        'tool_description': 'Answer questions using the composed scenario context and catalog data.',
        'voice_enabled': True,
        'scenario': current_scenario(),
    }


def build_voice_grounding_instructions() -> str:
    cfg = voice_grounding_config()
    return (
        'You are a concise voice assistant for the current composed scenario. '
        'Use the configured catalog and policy tools when answering questions. '
        f"Scenario: {cfg['scenario']}."
    )
