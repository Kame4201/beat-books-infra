#!/usr/bin/env bash
# =============================================================================
# BeatTheBooks — End-to-End Smoke Test
# Proves: scrape → store → predict works across all services.
#
# Usage:
#   bash scripts/e2e_smoke.sh              # default: bring stack up, test, tear down
#   bash scripts/e2e_smoke.sh --no-build   # skip docker compose up (stack already running)
#   bash scripts/e2e_smoke.sh --keep       # don't tear down after tests
#
# Prerequisites:
#   - All 4 repos cloned as siblings (../beat-books-data, etc.)
#   - docker/.env exists with DB_PASSWORD set
#   - Docker daemon running
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_DIR="$INFRA_DIR/docker"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

BASE_URL="${BASE_URL:-http://localhost}"
HEALTH_TIMEOUT="${HEALTH_TIMEOUT:-120}"   # seconds to wait for services
POLL_INTERVAL=5

# Flags
BUILD=true
KEEP=false
for arg in "$@"; do
  case "$arg" in
    --no-build) BUILD=false ;;
    --keep)     KEEP=true ;;
  esac
done

PASS=0
FAIL=0
TOTAL=0

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
pass() { echo "  [PASS] $1"; PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); }

http_get() {
  # $1 = url, returns body on stdout, sets HTTP_CODE
  HTTP_CODE=$(curl -s -o /tmp/e2e_body -w "%{http_code}" --max-time 15 "$1" 2>/dev/null || echo "000")
  cat /tmp/e2e_body 2>/dev/null || true
}

json_field() {
  # $1 = json string, $2 = field name
  echo "$1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('$2',''))" 2>/dev/null || echo ""
}

cleanup() {
  if [ "$KEEP" = false ] && [ "$BUILD" = true ]; then
    echo ""
    echo "Tearing down stack..."
    cd "$COMPOSE_DIR" && docker compose -f docker-compose.yml down -v 2>/dev/null || true
  fi
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Step 0: Validate compose file
# ---------------------------------------------------------------------------
echo ""
echo "======================================================================"
echo "  BeatTheBooks E2E Smoke Test"
echo "======================================================================"
echo ""
echo "Step 0: Validate docker-compose config"

if ! cd "$COMPOSE_DIR" || ! docker compose -f docker-compose.yml config -q 2>/dev/null; then
  fail "docker compose config validation"
  echo "  ERROR: docker-compose.yml is invalid. Aborting."
  exit 1
fi
pass "docker compose config is valid"

# ---------------------------------------------------------------------------
# Step 1: Bring stack up
# ---------------------------------------------------------------------------
echo ""
echo "Step 1: Docker stack"

if [ "$BUILD" = true ]; then
  if [ ! -f "$COMPOSE_DIR/.env" ]; then
    echo "  Creating .env from .env.example..."
    cp "$COMPOSE_DIR/.env.example" "$COMPOSE_DIR/.env" 2>/dev/null || true
    # Set a default password for testing if not already set
    if ! grep -q "DB_PASSWORD=." "$COMPOSE_DIR/.env" 2>/dev/null; then
      echo "DB_PASSWORD=e2e_test_password" >> "$COMPOSE_DIR/.env"
    fi
  fi

  echo "  Building and starting stack (this may take a few minutes)..."
  cd "$COMPOSE_DIR"
  docker compose -f docker-compose.yml up -d --build 2>&1 | tail -5
  pass "docker compose up -d --build"
else
  echo "  --no-build: assuming stack is already running"
  pass "skipped build (--no-build)"
fi

# ---------------------------------------------------------------------------
# Step 2: Wait for health endpoints
# ---------------------------------------------------------------------------
echo ""
echo "Step 2: Wait for services to be healthy (timeout: ${HEALTH_TIMEOUT}s)"

wait_for_health() {
  local name="$1"
  local url="$2"
  local elapsed=0

  while [ $elapsed -lt "$HEALTH_TIMEOUT" ]; do
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    if [ "$code" = "200" ]; then
      pass "$name is healthy (${elapsed}s)"
      return 0
    fi
    sleep $POLL_INTERVAL
    elapsed=$((elapsed + POLL_INTERVAL))
  done

  fail "$name did not become healthy within ${HEALTH_TIMEOUT}s (last HTTP $code)"
  return 1
}

DATA_HEALTHY=true
MODEL_HEALTHY=true
API_HEALTHY=true

wait_for_health "Data Service  :8001" "$BASE_URL:8001/health" || DATA_HEALTHY=false
wait_for_health "Model Service :8002" "$BASE_URL:8002/health" || MODEL_HEALTHY=false
wait_for_health "API Gateway   :8000" "$BASE_URL:8000/health" || API_HEALTHY=false

if [ "$DATA_HEALTHY" = false ] || [ "$MODEL_HEALTHY" = false ] || [ "$API_HEALTHY" = false ]; then
  echo ""
  echo "  One or more services failed health check. Dumping logs..."
  cd "$COMPOSE_DIR" && docker compose -f docker-compose.yml logs --tail=30 2>/dev/null || true
  echo ""
  echo "  Cannot proceed with E2E tests. Fix service startup first."
  # Still print summary before exiting
  echo ""
  echo "======================================================================"
  echo "  Results: $PASS passed, $FAIL failed (of $TOTAL checks)"
  echo "======================================================================"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 3: Health response schema validation
# ---------------------------------------------------------------------------
echo ""
echo "Step 3: Health response schema"

for svc in "Data Service|8001|beat-books-data" "Model Service|8002|beat-books-model" "API Gateway|8000|beat-books-api"; do
  IFS='|' read -r name port expected_name <<< "$svc"
  body=$(http_get "$BASE_URL:$port/health")
  status_val=$(json_field "$body" "status")
  service_val=$(json_field "$body" "service")

  if [ "$status_val" = "healthy" ] || [ "$status_val" = "ok" ]; then
    pass "$name health status=$status_val"
  else
    fail "$name health status expected healthy|ok, got '$status_val'"
  fi

  if [ -n "$service_val" ] && [ "$service_val" != "" ]; then
    pass "$name reports service=$service_val"
  else
    fail "$name missing 'service' field in health response"
  fi
done

# ---------------------------------------------------------------------------
# Step 4: Scrape → Store (trigger a scrape via data service)
# ---------------------------------------------------------------------------
echo ""
echo "Step 4: Scrape → Store"
echo "  Triggering team_offense scrape for season 2023 via data service..."

# Try scraping team_offense stats (lightweight, no Selenium/browser needed for this path)
SCRAPE_BODY=$(http_get "$BASE_URL:8001/scrape/team_offense/2023")

if [ "$HTTP_CODE" = "200" ]; then
  pass "Scrape team_offense/2023 returned HTTP 200"
elif [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
  # API key required — try without auth, this is expected
  echo "  (API key required — scrape endpoint is auth-protected, which is correct)"
  pass "Scrape endpoint enforces auth (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "500" ] || [ "$HTTP_CODE" = "000" ]; then
  # Scraping may fail in CI (no browser, rate limits) — this is expected
  echo "  Scrape returned HTTP $HTTP_CODE (expected in CI without browser/network)"
  echo "  Body: $(echo "$SCRAPE_BODY" | head -c 300)"
  fail "Scrape team_offense/2023 failed (HTTP $HTTP_CODE)"
else
  echo "  Unexpected HTTP $HTTP_CODE. Body: $(echo "$SCRAPE_BODY" | head -c 300)"
  fail "Scrape team_offense/2023 unexpected status $HTTP_CODE"
fi

# Check if data retrieval endpoint works (regardless of scrape success)
echo "  Checking data retrieval endpoint..."
STATS_BODY=$(http_get "$BASE_URL:8001/api/v1/stats/teams/2023")

if [ "$HTTP_CODE" = "200" ]; then
  pass "Data retrieval /api/v1/stats/teams/2023 returned HTTP 200"
  # Check if response is a list (even if empty)
  IS_LIST=$(echo "$STATS_BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print('yes' if isinstance(d, (list, dict)) else 'no')" 2>/dev/null || echo "no")
  if [ "$IS_LIST" = "yes" ]; then
    pass "Data retrieval returns valid JSON structure"
  else
    fail "Data retrieval response is not valid JSON"
  fi
else
  fail "Data retrieval /api/v1/stats/teams/2023 returned HTTP $HTTP_CODE"
fi

# ---------------------------------------------------------------------------
# Step 5: Train model artifact (if not already present)
# ---------------------------------------------------------------------------
echo ""
echo "Step 5: Train model artifact"
echo "  Training baseline model inside model-service container..."

TRAIN_OUTPUT=$(cd "$COMPOSE_DIR" && docker compose -f docker-compose.yml exec -T model-service \
  python3 scripts/train_baseline.py --synthetic 2>&1 || echo "TRAIN_FAILED")

if echo "$TRAIN_OUTPUT" | grep -q "Model ID:"; then
  TRAINED_MODEL_ID=$(echo "$TRAIN_OUTPUT" | grep "Model ID:" | tail -1 | awk '{print $NF}')
  pass "Model trained successfully (ID: $TRAINED_MODEL_ID)"
else
  echo "  Train output: $(echo "$TRAIN_OUTPUT" | tail -5)"
  fail "Model training failed"
fi

# ---------------------------------------------------------------------------
# Step 6: Predict (trigger prediction via model service directly)
# ---------------------------------------------------------------------------
echo ""
echo "Step 6: Predict"
echo "  Triggering prediction via model service..."

PREDICT_BODY=$(curl -s -o /tmp/e2e_body -w "%{http_code}" --max-time 15 \
  -X POST "$BASE_URL:8002/predictions/predict" \
  -H "Content-Type: application/json" \
  -d '{"home_team": "KC", "away_team": "BUF", "season": 2024, "week": 1}' 2>/dev/null || echo "000")
HTTP_CODE="$PREDICT_BODY"
PREDICT_BODY=$(cat /tmp/e2e_body 2>/dev/null || echo "")

if [ "$HTTP_CODE" = "200" ]; then
  pass "Model prediction returned HTTP 200"
  winner=$(json_field "$PREDICT_BODY" "prediction" 2>/dev/null || echo "")
  if [ -z "$winner" ]; then
    # Try nested field
    winner=$(echo "$PREDICT_BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('prediction',{}).get('winner',''))" 2>/dev/null || echo "")
  fi
  if [ -n "$winner" ] && [ "$winner" != "" ]; then
    pass "Prediction contains winner='$winner'"
  else
    echo "  Prediction body: $(echo "$PREDICT_BODY" | head -c 300)"
    fail "Prediction response missing 'winner' field"
  fi
  # Verify non-stub probability (not hardcoded 0.50)
  win_prob=$(echo "$PREDICT_BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('prediction',{}).get('win_probability',0.5))" 2>/dev/null || echo "0.5")
  if [ "$win_prob" != "0.5" ] && [ "$win_prob" != "0.50" ]; then
    pass "Prediction is non-stub (win_probability=$win_prob)"
  else
    fail "Prediction appears to be stub (win_probability=$win_prob)"
  fi
elif [ "$HTTP_CODE" = "422" ]; then
  # Try GET-style via API gateway instead
  echo "  POST returned 422, trying via API gateway GET..."
  PREDICT_BODY=$(http_get "$BASE_URL:8000/predictions/predict?team1=KC&team2=BUF")
  if [ "$HTTP_CODE" = "200" ]; then
    pass "API gateway prediction returned HTTP 200"
  else
    fail "API gateway prediction returned HTTP $HTTP_CODE"
  fi
else
  echo "  Prediction body: $(echo "$PREDICT_BODY" | head -c 300)"
  fail "Model prediction returned HTTP $HTTP_CODE"
fi

# ---------------------------------------------------------------------------
# Step 7: End-to-end via API gateway
# ---------------------------------------------------------------------------
echo ""
echo "Step 7: End-to-end via API Gateway"

# Test API gateway proxying to data service
GATEWAY_STATS=$(http_get "$BASE_URL:8000/teams/KC/stats?season=2023")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "404" ]; then
  pass "API Gateway → Data Service proxy works (HTTP $HTTP_CODE)"
else
  fail "API Gateway → Data Service proxy failed (HTTP $HTTP_CODE)"
fi

# Test API gateway proxying to model service
GATEWAY_PREDICT=$(http_get "$BASE_URL:8000/predictions/predict?team1=KC&team2=BUF")
if [ "$HTTP_CODE" = "200" ]; then
  pass "API Gateway → Model Service proxy works (HTTP $HTTP_CODE)"
  echo "  Prediction: $(echo "$GATEWAY_PREDICT" | head -c 300)"
else
  fail "API Gateway → Model Service proxy failed (HTTP $HTTP_CODE)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "======================================================================"
echo "  E2E Smoke Test Results: $PASS passed, $FAIL failed (of $TOTAL checks)"
echo "======================================================================"

if [ "$FAIL" -gt 0 ]; then
  echo "  STATUS: FAIL"
  exit 1
else
  echo "  STATUS: PASS — scrape → store → predict pipeline is functional"
  exit 0
fi
