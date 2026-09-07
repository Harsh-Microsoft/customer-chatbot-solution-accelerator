#!/bin/sh
# Ported from scenario-app/frontend/startup.sh (plan row 38), adapted for the
# collapsed two-app-service topology: one API backend (src/api) instead of the
# source's separate scenario/chat backends, and no VITE_SCENARIO enum (the
# pattern is scenario-free - GET /api/scenario/config supplies presentation data).

# Escape a value for safe inclusion inside a single-quoted JS string literal.
js_escape() {
  printf '%s' "$1" | sed "s/\\\\/\\\\\\\\/g; s/'/\\\\'/g"
}

API_BASE_URL="${VITE_API_BASE_URL:-}"
CHAT_API_BASE_URL="${VITE_CHAT_API_BASE_URL:-/api}"

# WAF/private networking deployment (BACKEND_API_URL set): the SPA calls its own
# origin and nginx reverse-proxies /api/ to the private backend over the VNet.
if [ -n "${BACKEND_API_URL:-}" ]; then
  cat > /usr/share/nginx/html/runtime-config.js << EOF
window.__RUNTIME_CONFIG__ = {
  VITE_API_BASE_URL: window.location.origin,
  VITE_CHAT_API_BASE_URL: '/api',
  VITE_CHAT_WIDGET_THEME: '$(js_escape "${VITE_CHAT_WIDGET_THEME:-}")',
  VITE_HOST_APP_TITLE: '$(js_escape "${VITE_HOST_APP_TITLE:-}")'
};
EOF
else
  if [ -z "$API_BASE_URL" ]; then
    host="${WEBSITE_HOSTNAME:-}"
    case "$host" in
      app-*.*)
        suf="${host#app-}"
        API_BASE_URL="https://api-${suf}"
        ;;
    esac
  fi
  CHAT_API_BASE_URL="$API_BASE_URL"

  cat > /usr/share/nginx/html/runtime-config.js << EOF
window.__RUNTIME_CONFIG__ = {
  VITE_API_BASE_URL: '$(js_escape "${API_BASE_URL}")',
  VITE_CHAT_API_BASE_URL: '$(js_escape "${CHAT_API_BASE_URL}")',
  VITE_CHAT_WIDGET_THEME: '$(js_escape "${VITE_CHAT_WIDGET_THEME:-}")',
  VITE_HOST_APP_TITLE: '$(js_escape "${VITE_HOST_APP_TITLE:-}")'
};
EOF
fi

# Generate the API reverse proxy config for WAF/private networking deployments.
if [ -n "${BACKEND_API_URL:-}" ]; then
  BACKEND_API_URL="${BACKEND_API_URL%/}"
  BACKEND_HOST=$(printf '%s' "${BACKEND_API_URL}" | sed 's|https\?://||; s|/.*||')
  cat > /etc/nginx/conf.d/api-proxy.conf << PROXYEOF
location /api/ {
    resolver 168.63.129.16 valid=30s;
    set \$backend "${BACKEND_API_URL}";
    proxy_pass \$backend;
    proxy_set_header Host "${BACKEND_HOST}";
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_ssl_server_name on;
    proxy_read_timeout 300s;
    proxy_connect_timeout 60s;
    proxy_buffering off;

    # WebSocket support (needed for /api/voice/ws/... connections)
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
}
PROXYEOF
else
  > /etc/nginx/conf.d/api-proxy.conf
fi

exec nginx -g "daemon off;"
