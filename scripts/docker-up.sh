#!/usr/bin/env bash
# Start the BeatTheBooks stack using Docker Compose
# Usage: ./scripts/docker-up.sh [dev|test|prod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

MODE="${1:-prod}"

cd "$DOCKER_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✏️  Please edit docker/.env with your actual values before proceeding."
    exit 1
fi

case "$MODE" in
    dev)
        echo "🚀 Starting BeatTheBooks stack in DEVELOPMENT mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
        ;;
    test)
        echo "🧪 Starting BeatTheBooks stack in TEST mode..."
        docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit
        ;;
    prod)
        echo "🚀 Starting BeatTheBooks stack in PRODUCTION mode..."
        docker-compose up --build
        ;;
    *)
        echo "❌ Invalid mode: $MODE"
        echo "Usage: $0 [dev|test|prod]"
        exit 1
        ;;
esac
