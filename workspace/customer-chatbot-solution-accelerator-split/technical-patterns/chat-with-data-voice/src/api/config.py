from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'chat-with-data-voice-api'
    environment: str = Field(default='development', alias='ENVIRONMENT')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    scenario_path: str = Field(default='', alias='SCENARIO_PATH')
    api_cors_origins: str = Field(default='*', alias='API_CORS_ORIGINS')

    cosmos_endpoint: str = Field(default='', alias='COSMOS_ENDPOINT')
    cosmos_key: str = Field(default='', alias='COSMOS_KEY')
    cosmos_database: str = Field(default='chatbot', alias='COSMOS_DATABASE')
    cosmos_container: str = Field(default='sessions', alias='COSMOS_CONTAINER')

    # Ported from chat-app/backend/app/config.py (plan row 11). `cosmos_service.py`
    # and `.env.sample` both use the `COSMOS_DB_*` names, so these are the fields
    # actually read at runtime; `cosmos_endpoint`/`cosmos_database` above predate
    # that reconciliation and are kept only for the `main.py` health check.
    cosmos_db_endpoint: str = Field(default='', alias='COSMOS_DB_ENDPOINT')
    cosmos_db_database_name: str = Field(default='chat_with_data_voice_db', alias='COSMOS_DB_DATABASE_NAME')

    azure_search_endpoint: str = Field(default='', alias='AZURE_SEARCH_ENDPOINT')
    azure_search_catalog_index: str = Field(default='catalog-index', alias='AZURE_SEARCH_CATALOG_INDEX')

    azure_foundry_endpoint: str = Field(default='', alias='AZURE_FOUNDRY_ENDPOINT')
    foundry_chat_agent: str = Field(default='chat-agent', alias='FOUNDRY_CHAT_AGENT')
    foundry_product_agent: str = Field(default='catalog-agent', alias='FOUNDRY_PRODUCT_AGENT')
    foundry_policy_agent: str = Field(default='policy-agent', alias='FOUNDRY_POLICY_AGENT')
    azure_client_id: str | None = Field(default=None, alias='AZURE_CLIENT_ID')

    azure_voicelive_agent_name: str = Field(default='', alias='AZURE_VOICELIVE_AGENT_NAME')
    azure_voicelive_project: str = Field(default='', alias='AZURE_VOICELIVE_PROJECT')
    voicelive_vad_threshold: float = Field(default=0.5, alias='VOICELIVE_VAD_THRESHOLD')
    voicelive_vad_silence_ms: int = Field(default=500, alias='VOICELIVE_VAD_SILENCE_MS')
    voicelive_voice: str = Field(default='alloy', alias='VOICELIVE_VOICE')

    @property
    def scenario_root(self) -> Path:
        if self.scenario_path.strip():
            return Path(self.scenario_path).expanduser().resolve()
        raise RuntimeError('SCENARIO_PATH is required')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def has_cosmos_db_config() -> bool:
    return bool(settings.cosmos_db_endpoint)


def has_azure_search_config() -> bool:
    return bool(settings.azure_search_endpoint)
