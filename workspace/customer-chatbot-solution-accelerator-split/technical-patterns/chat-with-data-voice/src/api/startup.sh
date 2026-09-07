#!/bin/bash
# Ported from chat-app/backend/startup.sh and scenario-app/backend/startup.sh
# (plan row 36), rewritten for the collapsed layout: `uvicorn main:app`
# instead of `uvicorn app.main:app` (plan section 4.8).
cd /home/site/wwwroot 2>/dev/null || cd /app
python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
