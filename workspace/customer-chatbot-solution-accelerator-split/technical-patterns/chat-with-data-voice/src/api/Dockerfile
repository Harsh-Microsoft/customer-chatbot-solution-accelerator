# API Dockerfile — ported from chat-app/backend/Dockerfile and
# scenario-app/backend/Dockerfile (plan row 36), reconciled onto the
# collapsed `src/api` layout (no `app/` package — plan section 4.8).
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN useradd -m -u 1001 apiuser && chown -R apiuser:apiuser /app
USER apiuser

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["/bin/sh", "startup.sh"]
