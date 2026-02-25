#!/usr/bin/env bash
# BeatTheBooks — Multi-repo bootstrap script
# Clones all repos, checks prerequisites, sets up environment, starts the stack.
# Usage: bash bootstrap.sh [--skip-docker]
#
# Assumes you want all repos as siblings in the same parent directory.
# If run from inside beat-books-infra, it clones siblings next to it.
set -e

SKIP_DOCKER=false
if [ "$1" = "--skip-docker" ]; then
    SKIP_DOCKER=true
fi

GITHUB_ORG="Kame4201"
REPOS=("beat-books-data" "beat-books-model" "beat-books-api" "beat-books-infra")

# ---------- helpers ----------
info()  { echo "  [INFO]  $*"; }
warn()  { echo "  [WARN]  $*"; }
fail()  { echo "  [FAIL]  $*" >&2; exit 1; }
ok()    { echo "  [ OK ]  $*"; }

check_cmd() {
    if command -v "$1" &>/dev/null; then
        ok "$1 found: $(command -v "$1")"
        return 0
    else
        warn "$1 not found"
        return 1
    fi
}

# ---------- prerequisite check ----------
echo ""
echo "======================================"
echo "  BeatTheBooks Bootstrap"
echo "======================================"
echo ""
echo "Checking prerequisites..."

MISSING=0
check_cmd git     || MISSING=1
check_cmd docker  || MISSING=1
check_cmd python3 || check_cmd python || MISSING=1

# docker compose (v2 plugin or standalone)
if docker compose version &>/dev/null 2>&1; then
    ok "docker compose v2 found"
elif command -v docker-compose &>/dev/null; then
    ok "docker-compose (standalone) found"
else
    warn "docker compose not found"
    MISSING=1
fi

# gh CLI (optional but recommended)
if check_cmd gh; then
    info "gh CLI will be used for cloning (faster auth)"
fi

if [ "$MISSING" -eq 1 ]; then
    echo ""
    warn "Some prerequisites are missing. Install them and re-run."
    warn "Required: git, docker, docker compose, python3"
    exit 1
fi

# ---------- determine workspace ----------
# If we're inside beat-books-infra, go up one level
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/../CLAUDE.md" ] && grep -q "beat-books-infra" "$SCRIPT_DIR/../CLAUDE.md" 2>/dev/null; then
    WORKSPACE="$(dirname "$SCRIPT_DIR/..")"
    WORKSPACE="$(cd "$SCRIPT_DIR/.." && cd .. && pwd)"
    info "Detected beat-books-infra repo; workspace is $WORKSPACE"
else
    WORKSPACE="$(pwd)"
    info "Using current directory as workspace: $WORKSPACE"
fi

# ---------- clone repos ----------
echo ""
echo "Cloning repositories..."
for REPO in "${REPOS[@]}"; do
    TARGET="$WORKSPACE/$REPO"
    if [ -d "$TARGET/.git" ]; then
        ok "$REPO already cloned at $TARGET"
        (cd "$TARGET" && git fetch origin --prune -q)
    else
        info "Cloning $REPO..."
        git clone "https://github.com/$GITHUB_ORG/$REPO.git" "$TARGET"
        ok "$REPO cloned"
    fi
done

# ---------- environment setup ----------
echo ""
echo "Setting up environment files..."
INFRA_DIR="$WORKSPACE/beat-books-infra"
DOCKER_DIR="$INFRA_DIR/docker"

if [ -f "$DOCKER_DIR/.env" ]; then
    ok "docker/.env already exists"
else
    if [ -f "$DOCKER_DIR/.env.example" ]; then
        cp "$DOCKER_DIR/.env.example" "$DOCKER_DIR/.env"
        ok "Created docker/.env from .env.example"
        warn "Edit $DOCKER_DIR/.env and set DB_PASSWORD before starting the stack"
    else
        warn "No .env.example found in $DOCKER_DIR"
    fi
fi

# Copy .env.example in each app repo if .env doesn't exist
for REPO in "beat-books-data" "beat-books-model" "beat-books-api"; do
    REPO_DIR="$WORKSPACE/$REPO"
    if [ -f "$REPO_DIR/.env.example" ] && [ ! -f "$REPO_DIR/.env" ]; then
        cp "$REPO_DIR/.env.example" "$REPO_DIR/.env"
        ok "Created $REPO/.env from .env.example"
    fi
done

# ---------- start stack ----------
if [ "$SKIP_DOCKER" = true ]; then
    info "Skipping Docker start (--skip-docker flag)"
else
    echo ""
    echo "Starting the stack in development mode..."
    cd "$DOCKER_DIR"
    if docker compose version &>/dev/null 2>&1; then
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    else
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
    fi
    ok "Stack started in background"

    # ---------- health check ----------
    echo ""
    echo "Waiting for services to become healthy (up to 60s)..."
    SERVICES=("8000" "8001" "8002")
    NAMES=("API Gateway" "Data Service" "Model Service")
    for i in 0 1 2; do
        PORT="${SERVICES[$i]}"
        NAME="${NAMES[$i]}"
        HEALTHY=false
        for ATTEMPT in $(seq 1 12); do
            if curl -sf "http://localhost:$PORT/health" > /dev/null 2>&1; then
                ok "$NAME (port $PORT) is healthy"
                HEALTHY=true
                break
            fi
            sleep 5
        done
        if [ "$HEALTHY" = false ]; then
            warn "$NAME (port $PORT) did not respond within 60s"
        fi
    done
fi

# ---------- done ----------
echo ""
echo "======================================"
echo "  Bootstrap complete!"
echo "======================================"
echo ""
echo "  Repos cloned to: $WORKSPACE"
echo "  Services:"
echo "    API Gateway:   http://localhost:8000"
echo "    Data Service:  http://localhost:8001"
echo "    Model Service: http://localhost:8002"
echo "    PostgreSQL:    localhost:5432"
echo ""
echo "  Useful commands:"
echo "    docker compose -f docker/docker-compose.yml logs -f"
echo "    docker compose -f docker/docker-compose.yml down -v"
echo ""
