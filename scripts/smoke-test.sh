#!/usr/bin/env bash
# BeatTheBooks — Cross-service smoke test
# Validates that all services are running and can communicate.
# Usage: bash scripts/smoke-test.sh [base_url]
#   base_url defaults to http://localhost
set -e

BASE="${1:-http://localhost}"
PASS=0
FAIL=0

check() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    HTTP_CODE=$(curl -s -o /tmp/smoke_body -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "$expected_status" ]; then
        echo "  [PASS] $name (HTTP $HTTP_CODE)"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $name — expected $expected_status, got $HTTP_CODE"
        if [ -f /tmp/smoke_body ]; then
            echo "         $(cat /tmp/smoke_body | head -c 200)"
        fi
        FAIL=$((FAIL + 1))
    fi
}

check_json_field() {
    local name="$1"
    local url="$2"
    local field="$3"
    local expected="$4"

    BODY=$(curl -sf "$url" 2>/dev/null || echo "{}")
    ACTUAL=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$field',''))" 2>/dev/null || echo "")

    if [ "$ACTUAL" = "$expected" ]; then
        echo "  [PASS] $name ($field=$ACTUAL)"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $name — expected $field=$expected, got $field=$ACTUAL"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "======================================"
echo "  BeatTheBooks Smoke Tests"
echo "======================================"
echo ""

# --- Health checks ---
echo "1. Health Check Endpoints"
check "API Gateway /health"   "$BASE:8000/health"
check "Data Service /health"  "$BASE:8001/health"
check "Model Service /health" "$BASE:8002/health"

echo ""
echo "2. Health Response Schema"
check_json_field "API Gateway status field"   "$BASE:8000/health" "status"  "healthy"
check_json_field "Data Service status field"  "$BASE:8001/health" "status"  "healthy"
check_json_field "Model Service status field" "$BASE:8002/health" "status"  "healthy"

echo ""
echo "3. Service Identity"
check_json_field "Data Service name"  "$BASE:8001/health" "service" "beat-books-data"
check_json_field "Model Service name" "$BASE:8002/health" "service" "beat-books-model"

echo ""
echo "4. Error Contract (invalid request should return structured error)"
check "Data Service 404 on invalid team" "$BASE:8001/teams/nonexistent_team_xyz/stats?season=9999" "404"

echo ""
echo "======================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "======================================"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
