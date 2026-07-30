#!/usr/bin/env bash

set -Eeuo pipefail
umask 077

# Production backup for the Docker Compose deployment.
#
# The backend is stopped only while PostgreSQL, Chroma and uploads snapshots are
# created. It is started again before validation and remote upload.
#
# Usage:
#   ./scripts/backup_databases.sh --once
#
# Required environment:
#   RCLONE_REMOTE=yandex-crypt:sentra
#
# Optional environment:
#   BACKUP_DIR=/var/backups/sentra
#   LOCAL_RETENTION_DAYS=7
#   REMOTE_RETENTION_DAYS=30
#   COMPOSE_FILE=/opt/sentra/docker-compose.yml
#   BACKEND_STOP_TIMEOUT_SECONDS=60
#   MIN_FREE_SPACE_MB=2048
#   RCLONE_TIMEOUT=60m

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
LOCAL_RETENTION_DAYS="${LOCAL_RETENTION_DAYS:-${BACKUP_RETENTION_DAYS:-7}}"
REMOTE_RETENTION_DAYS="${REMOTE_RETENTION_DAYS:-30}"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_DIR/docker-compose.yml}"
BACKEND_STOP_TIMEOUT_SECONDS="${BACKEND_STOP_TIMEOUT_SECONDS:-60}"
MIN_FREE_SPACE_MB="${MIN_FREE_SPACE_MB:-2048}"
RCLONE_REMOTE="${RCLONE_REMOTE:-}"
RCLONE_TIMEOUT="${RCLONE_TIMEOUT:-60m}"

temporary=""
backend_restart_required=false
backend_was_running=false

log() {
    printf '[%s] %s\n' "$(date -Is)" "$*"
}

die() {
    log "ERROR: $*" >&2
    exit 1
}

require_command() {
    command -v "$1" >/dev/null 2>&1 || die "$1 is required"
}

validate_non_negative_integer() {
    local name="$1" value="$2"
    [[ "$value" =~ ^[0-9]+$ ]] || die "$name must be a non-negative integer"
}

validate_positive_integer() {
    local name="$1" value="$2"
    [[ "$value" =~ ^[1-9][0-9]*$ ]] || die "$name must be a positive integer"
}

compose() {
    docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" "$@"
}

start_backend_if_required() {
    if [[ "$backend_restart_required" == true ]]; then
        log "Starting backend"
        compose start backend
        backend_restart_required=false
    fi
}

cleanup() {
    local status=$?
    trap - EXIT INT TERM

    if [[ "$backend_restart_required" == true ]]; then
        log "Backup interrupted; attempting to start backend" >&2
        if ! compose start backend; then
            log "ERROR: backend could not be restarted" >&2
            status=1
        fi
        backend_restart_required=false
    fi

    if [[ -n "$temporary" && -d "$temporary" ]]; then
        rm -rf -- "$temporary"
    fi

    exit "$status"
}

timestamp_to_epoch() {
    local value="$1"
    local iso_date="${value:0:10}"
    local iso_time="${value:11:2}:${value:14:2}:${value:17:2}"
    date -u -d "$iso_date $iso_time UTC" +%s
}

prune_local_backups() {
    local cutoff path name epoch

    (( LOCAL_RETENTION_DAYS > 0 )) || return 0
    cutoff="$(date -u -d "$LOCAL_RETENTION_DAYS days ago" +%s)"

    for path in "$BACKUP_DIR"/*; do
        [[ -d "$path" ]] || continue
        name="$(basename -- "$path")"
        [[ "$name" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z$ ]] || continue
        [[ -f "$path/MANIFEST.env" && -f "$path/postgres.dump" ]] || continue
        epoch="$(timestamp_to_epoch "$name")"
        if (( epoch < cutoff )); then
            log "Removing expired local backup: $path"
            rm -rf -- "$path"
        fi
    done
}

prune_remote_backups() {
    local cutoff directories directory name epoch files

    (( REMOTE_RETENTION_DAYS > 0 )) || return 0
    cutoff="$(date -u -d "$REMOTE_RETENTION_DAYS days ago" +%s)"
    directories="$(rclone lsf "$RCLONE_REMOTE" --dirs-only)"

    while IFS= read -r directory; do
        name="${directory%/}"
        [[ "$name" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z$ ]] || continue
        files="$(rclone lsf "$RCLONE_REMOTE/$name" --files-only --max-depth 1)"
        grep -qx 'MANIFEST.env' <<< "$files" || continue
        grep -qx 'postgres.dump' <<< "$files" || continue
        epoch="$(timestamp_to_epoch "$name")"
        if (( epoch < cutoff )); then
            log "Removing expired remote backup: $RCLONE_REMOTE/$name"
            rclone purge "$RCLONE_REMOTE/$name"
        fi
    done <<< "$directories"
}

if [[ "${1:-}" != "--once" || $# -ne 1 ]]; then
    printf 'Usage: %s --once\n' "$0" >&2
    exit 2
fi

validate_non_negative_integer "LOCAL_RETENTION_DAYS" "$LOCAL_RETENTION_DAYS"
validate_non_negative_integer "REMOTE_RETENTION_DAYS" "$REMOTE_RETENTION_DAYS"
validate_positive_integer "BACKEND_STOP_TIMEOUT_SECONDS" "$BACKEND_STOP_TIMEOUT_SECONDS"
validate_positive_integer "MIN_FREE_SPACE_MB" "$MIN_FREE_SPACE_MB"

[[ -f "$COMPOSE_FILE" ]] || die "Compose file not found: $COMPOSE_FILE"
[[ "$RCLONE_REMOTE" =~ ^[A-Za-z0-9._-]+:.+ ]] ||
    die "RCLONE_REMOTE must include a remote and a dedicated path, for example yandex-crypt:sentra"

require_command docker
require_command df
require_command flock
require_command awk
require_command grep
require_command rclone
require_command sha256sum
require_command sync
require_command tar

rclone_remote_name="${RCLONE_REMOTE%%:*}"
rclone_remote_type="$(
    rclone config show "$rclone_remote_name" |
        awk -F '[[:space:]]*=[[:space:]]*' '$1 == "type" { print $2 }'
)"
[[ "$rclone_remote_type" == "crypt" ]] ||
    die "RCLONE_REMOTE must use an rclone crypt remote; '$rclone_remote_name' has type '$rclone_remote_type'"

mkdir -p -- "$BACKUP_DIR"
BACKUP_DIR="$(cd -- "$BACKUP_DIR" && pwd)"

exec 9>"$BACKUP_DIR/.backup.lock"
flock -n 9 || die "Another backup process is already running"
trap cleanup EXIT INT TERM

available_space_mb="$(df -Pm "$BACKUP_DIR" | awk 'NR == 2 { print $4 }')"
[[ "$available_space_mb" =~ ^[0-9]+$ ]] || die "Could not determine free backup space"
(( available_space_mb >= MIN_FREE_SPACE_MB )) ||
    die "Only ${available_space_mb} MiB is free in $BACKUP_DIR; at least ${MIN_FREE_SPACE_MB} MiB is required"

compose config --services | grep -qx 'db' || die "Compose service 'db' is missing"
compose config --services | grep -qx 'backend' || die "Compose service 'backend' is missing"

migrations_container_id="$(compose ps -q migrations 2>/dev/null || true)"
if [[ -n "$migrations_container_id" ]] &&
    [[ "$(docker inspect --format '{{.State.Running}}' "$migrations_container_id")" == true ]]; then
    die "The migrations service is running; retry the backup after migrations finish"
fi

compose exec -T db sh -ec \
    'exec pg_isready --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' \
    >/dev/null

timestamp="$(date -u +'%Y-%m-%dT%H-%M-%SZ')"
destination="$BACKUP_DIR/$timestamp"
[[ ! -e "$destination" ]] || die "Backup already exists: $destination"
temporary="$(mktemp -d "$BACKUP_DIR/.${timestamp}.XXXXXX.tmp")"

backend_container_id="$(compose ps -q backend)"
if [[ -n "$backend_container_id" ]]; then
    backend_was_running="$(docker inspect --format '{{.State.Running}}' "$backend_container_id")"
fi

log "Starting consistent local snapshot: $timestamp"
if [[ "$backend_was_running" == true ]]; then
    log "Stopping backend for the snapshot"
    backend_restart_required=true
    compose stop -t "$BACKEND_STOP_TIMEOUT_SECONDS" backend
fi

compose exec -T db sh -ec \
    'exec pg_dump --format=custom --compress=6 --no-owner --no-privileges --lock-wait-timeout=30s --username="$POSTGRES_USER" "$POSTGRES_DB"' \
    > "$temporary/postgres.dump"

compose run --rm --no-deps -T --entrypoint tar backend \
    -C /app/backend/database/chroma \
    -czf - chroma_db \
    > "$temporary/chroma.tar.gz"

compose run --rm --no-deps -T --entrypoint tar backend \
    -C /app \
    -czf - uploads \
    > "$temporary/uploads.tar.gz"

start_backend_if_required

log "Validating backup archives"
[[ -s "$temporary/postgres.dump" ]] || die "PostgreSQL dump is empty"
[[ -s "$temporary/chroma.tar.gz" ]] || die "Chroma archive is empty"
[[ -s "$temporary/uploads.tar.gz" ]] || die "Uploads archive is empty"

compose exec -T db pg_restore --list \
    < "$temporary/postgres.dump" \
    > "$temporary/postgres.restore-list"
tar -tzf "$temporary/chroma.tar.gz" >/dev/null
tar -tzf "$temporary/uploads.tar.gz" >/dev/null

project_revision="unknown"
if command -v git >/dev/null 2>&1; then
    project_revision="$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || printf 'unknown')"
fi
postgres_version="$(compose exec -T db postgres --version | tr -d '\r')"
chroma_version="unknown"
if [[ "$backend_was_running" == true ]]; then
    chroma_version="$(
        compose exec -T backend /app/.venv/bin/python -c \
            'import chromadb; print(chromadb.__version__)' |
            tr -d '\r'
    )"
fi

{
    printf 'BACKUP_FORMAT_VERSION=1\n'
    printf 'CREATED_AT_UTC=%s\n' "$timestamp"
    printf 'HOSTNAME=%s\n' "$(hostname)"
    printf 'PROJECT_REVISION=%s\n' "$project_revision"
    printf 'POSTGRES_VERSION=%s\n' "$postgres_version"
    printf 'CHROMA_VERSION=%s\n' "$chroma_version"
    printf 'BACKEND_WAS_RUNNING=%s\n' "$backend_was_running"
} > "$temporary/MANIFEST.env"

(
    cd -- "$temporary"
    sha256sum \
        MANIFEST.env \
        postgres.dump \
        postgres.restore-list \
        chroma.tar.gz \
        uploads.tar.gz \
        > SHA256SUMS
    sha256sum --check SHA256SUMS
)

mv -- "$temporary" "$destination"
temporary=""
sync -f "$BACKUP_DIR"
log "Local backup completed: $destination"

remote_destination="${RCLONE_REMOTE%/}/$timestamp"
log "Uploading backup to $remote_destination"
rclone copy "$destination" "$remote_destination" \
    --immutable \
    --transfers 2 \
    --checkers 4 \
    --retries 5 \
    --low-level-retries 10 \
    --contimeout 30s \
    --timeout "$RCLONE_TIMEOUT"

log "Checking remote backup"
rclone cryptcheck "$destination" "$remote_destination" --one-way

prune_local_backups
prune_remote_backups

log "Backup completed and verified: $remote_destination"
