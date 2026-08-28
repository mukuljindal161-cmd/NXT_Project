FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/ /app/apps/api/
COPY workers/ /app/workers/
COPY .env /app/.env

WORKDIR /app/workers

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info"]
