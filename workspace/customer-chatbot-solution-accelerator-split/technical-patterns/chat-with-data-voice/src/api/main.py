from __future__ import annotations

import json
import logging
import os
import re

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

try:
    from opentelemetry import trace
except ImportError:

    class _Trace:
        @staticmethod
        def get_current_span():
            return None

    trace = _Trace()

try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
except ImportError:
    configure_azure_monitor = None
    FastAPIInstrumentor = None

from config import settings
from routers.auth import router as auth_router
from routers.catalog import router as catalog_router
from routers.chat import router as chat_router
from routers.chat_config import router as chat_config_router
from routers.scenario_config_api import router as scenario_config_router
from routers.voice_live import router as voice_live_router

# Merge of chat-app/backend/app/main.py and scenario-app/backend/app/main.py
# (plan section 4.8/6): single collapsed entrypoint, registering only the
# retained routers (no cart/orders/banking_transactions/healthcare_appointments).

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
)
for _logger_name in (
    'azure.core.pipeline.policies.http_logging_policy',
    'azure.core.pipeline.policies._universal',
    'azure.identity',
    'azure.monitor.opentelemetry.exporter.export._base',
    'azure.cosmos',
    'httpx',
    'httpcore',
):
    logging.getLogger(_logger_name).setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

instrumentation_key = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')

_SESSION_PATH_RE = re.compile(r'/api/chat/sessions/([^/]+)')


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version='1.0.0',
        description='Grounded multi-agent customer chat with a real-time voice channel',
        docs_url='/docs',
        redoc_url='/redoc',
    )

    if instrumentation_key and configure_azure_monitor is not None and FastAPIInstrumentor is not None:
        configure_azure_monitor(
            connection_string=instrumentation_key,
            enable_live_metrics=False,
            enable_performance_counters=False,
            instrumentation_options={'fastapi': {'enabled': False}},
        )
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls='/health$,/healthz$,/robots933456\\.txt$',
            exclude_spans=['receive', 'send'],
        )
        logger.info('Application Insights configured with FastAPI instrumentation')
    elif instrumentation_key:
        logger.warning(
            'APPLICATIONINSIGHTS_CONNECTION_STRING is set but OpenTelemetry packages '
            'are missing; install azure-monitor-opentelemetry to enable telemetry.'
        )
    else:
        logger.warning('No Application Insights connection string found. Telemetry disabled.')

    @app.middleware('http')
    async def attach_trace_attributes(request: Request, call_next):
        span = trace.get_current_span()
        if span and span.is_recording():
            match = _SESSION_PATH_RE.match(request.url.path)
            if match and match.group(1) != 'new':
                span.set_attribute('session_id', match.group(1))
            else:
                sid = request.query_params.get('session_id')
                if sid:
                    span.set_attribute('session_id', sid)
                elif request.method == 'POST' and 'application/json' in (request.headers.get('content-type') or ''):
                    try:
                        body = await request.body()
                        if body:
                            data = json.loads(body)
                            sid = data.get('session_id')
                            if sid:
                                span.set_attribute('session_id', sid)
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        logger.debug('Failed to parse request body for session_id: %s', exc)
        return await call_next(request)

    origins = [origin.strip() for origin in settings.api_cors_origins.split(',') if origin.strip()] or ['*']
    _cors_origins = frozenset(origins)

    class _FixCredentialedCorsMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)
            origin = request.headers.get('origin')
            if origin and origin in _cors_origins:
                response.headers['access-control-allow-origin'] = origin
                response.headers['access-control-allow-credentials'] = 'true'
            return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_middleware(_FixCredentialedCorsMiddleware)

    app.include_router(scenario_config_router)
    app.include_router(catalog_router)
    app.include_router(chat_router)
    app.include_router(chat_config_router)
    app.include_router(auth_router)
    app.include_router(voice_live_router)

    @app.get('/')
    async def read_root() -> dict[str, str]:
        return {
            'message': f'Welcome to {settings.app_name}!',
            'version': '1.0.0',
            'docs': '/docs',
            'status': 'healthy',
        }

    @app.get('/health')
    @app.get('/healthz')
    async def health_check() -> dict[str, str]:
        return {
            'status': 'healthy',
            'database': 'connected' if settings.cosmos_endpoint else 'not_configured',
            'foundry': 'configured' if settings.azure_foundry_endpoint else 'not_configured',
        }

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={'success': False, 'message': exc.detail, 'error': exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error('Unhandled exception: %s', exc)
        return JSONResponse(
            status_code=500,
            content={'success': False, 'message': 'Internal server error', 'error': 'An unexpected error occurred'},
        )

    return app


app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False)
