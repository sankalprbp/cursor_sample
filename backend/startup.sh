#!/bin/bash
set -e

echo "Waiting for Postgres..."
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" >/dev/null 2>&1; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done

echo "Waiting for Redis..."
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done

if [ -n "$MINIO_HOST" ]; then
  echo "Waiting for MinIO..."
  until curl -sSf "http://$MINIO_HOST:$MINIO_PORT/minio/health/ready" >/dev/null 2>&1; do
    echo "MinIO is unavailable - sleeping"
    sleep 2
  done
fi

echo "Running database migrations..."
python -m app.core.database_init

echo "Starting backend..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
