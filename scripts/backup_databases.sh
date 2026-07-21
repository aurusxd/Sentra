#!/usr/bin/env bash

set -Eeuo pipefail

# Usage:
#   ./scripts/backup_databases.sh          # back up immediately, then every hour
#   ./scripts/backup_databases.sh --once   # one backup (recommended for cron)
#
# Optional environment variables:
#   BACKUP_DIR=/var/backups/sentra
#   BACKUP_INTERVAL_SECONDS=3600
#   BACKUP_RETENTION_DAYS=14
#   COMPOSE_FILE=/path/to/docker-compose.yml

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-3600}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_DIR/docker-compose.yml}"
RUN_ONCE=false

if [[ "${1:-}" == "--once" ]]; then
    RUN_ONCE=true
elif [[ $# -gt 0 ]]; then
    echo "Usage: $0 [--once]" >&2
    exit 2
fi

if ! [[ "$BACKUP_INTERVAL_SECONDS" =~ ^[1-9][0-9]*$ ]]; then
    echo "BACKUP_INTERVAL_SECONDS must be a positive integer" >&2
    exit 2
fi

if ! [[ "$BACKUP_RETENTION_DAYS" =~ ^[1-9][0-9]*$ ]]; then
    echo "BACKUP_RETENTION_DAYS must be a positive integer" >&2
    exit 2
fi

command -v docker >/dev/null 2>&1 || {
    echo "docker is required" >&2
    exit 1
}

mkdir -p -- "$BACKUP_DIR"

# Prevent two cron jobs or daemon instances from writing the same backup.
LOCK_DIR="$BACKUP_DIR/.backup.lock"
if ! mkdir -- "$LOCK_DIR" 2>/dev/null; then
    echo "Another backup process is already running: $LOCK_DIR" >&2
    exit 1
fi
trap 'rm -rf -- "$LOCK_DIR"' EXIT INT TERM

compose() {
    docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" "$@"
}

backup_once() {
    local timestamp destination temporary
    timestamp="$(date -u +'%Y-%m-%dT%H-%M-%SZ')"
    destination="$BACKUP_DIR/$timestamp"
    temporary="$BACKUP_DIR/.${timestamp}.tmp"

    mkdir -p -- "$temporary"
    echo "[$(date -Is)] Starting backup: $timestamp"

    # Custom pg_dump format is compressed and can be restored with pg_restore.
    compose exec -T db sh -c \
        'exec pg_dump --format=custom --no-owner --no-privileges --username="$POSTGRES_USER" "$POSTGRES_DB"' \
        > "$temporary/postgres.dump"

    # Chroma persists its SQLite database and vector index files in this volume.
    compose exec -T backend tar \
        -C /app/backend/database/chroma \
        -czf - chroma_db \
        > "$temporary/chroma.tar.gz"

    if command -v sha256sum >/dev/null 2>&1; then
        (
            cd -- "$temporary"
            sha256sum postgres.dump chroma.tar.gz > SHA256SUMS
        )
    fi

    mv -- "$temporary" "$destination"
    echo "[$(date -Is)] Backup completed: $destination"

    find "$BACKUP_DIR" \
        -mindepth 1 -maxdepth 1 -type d \
        ! -name '.backup.lock' ! -name '.*.tmp' \
        -mtime "+$BACKUP_RETENTION_DAYS" \
        -exec rm -rf -- {} +
}

while true; do
    backup_once

    if [[ "$RUN_ONCE" == true ]]; then
        break
    fi

    echo "[$(date -Is)] Next backup in $BACKUP_INTERVAL_SECONDS seconds"
    sleep "$BACKUP_INTERVAL_SECONDS"
done
