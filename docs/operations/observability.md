# Monitoring, Logging, and Observability Standards

> Defines structured logging, metrics, and alerting standards for all BeatTheBooks services.
> Related: [External APIs](../architecture/external-apis.md) | [Service Contracts](../architecture/service-contracts.md)

## Structured Logging

### Format

All services must use structured JSON logging. Use `structlog` for consistent output:

```python
import structlog

logger = structlog.get_logger()

# Good — structured with context
logger.info("scrape_completed", team="NYG", season=2024, rows_inserted=15)

# Bad — unstructured string
logger.info(f"Scraped NYG for 2024, inserted 15 rows")
```

### Output format

```json
{
  "event": "scrape_completed",
  "team": "NYG",
  "season": 2024,
  "rows_inserted": 15,
  "timestamp": "2026-02-25T12:00:00Z",
  "level": "info",
  "service": "beat-books-data"
}
```

### Log Levels

| Level | When to use | Example |
|-------|------------|---------|
| **DEBUG** | Detailed diagnostic info (disabled in production) | `logger.debug("query_result", rows=42)` |
| **INFO** | Normal operations, key milestones | `logger.info("scrape_completed", team="NYG")` |
| **WARNING** | Unexpected but recoverable situations | `logger.warning("rate_limited", source="PFR", retry_after=60)` |
| **ERROR** | Failures that affect functionality | `logger.error("scrape_failed", team="NYG", status_code=403)` |

### FastAPI Request Logging Middleware

Add to each service's `main.py`:

```python
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 1),
        )
        return response

# In app setup:
app.add_middleware(RequestLoggingMiddleware)
```

### structlog Configuration Template

```python
import structlog
import logging

def configure_logging(service_name: str, level: str = "INFO"):
    """Call once at service startup."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
```

## Key Metrics

### Per-service metrics to track

| Metric | Service | Why it matters |
|--------|---------|---------------|
| Request count by endpoint | All | Traffic patterns, capacity planning |
| Request latency (p50, p95, p99) | All | Performance monitoring |
| Error rate (4xx, 5xx) | All | Service health |
| Scrape success rate | beat-books-data | Data pipeline health |
| Scrape duration | beat-books-data | PFR throttling detection |
| PFR 403 count | beat-books-data | Bot detection alerts |
| Odds API quota remaining | beat-books-data | Budget management |
| Model prediction latency | beat-books-model | User experience |
| DB query duration | data, model | Performance bottlenecks |
| DB connection pool usage | data, model | Resource exhaustion |

### Health check as a metric source

The existing `/health` endpoint is the simplest metric. External uptime monitors can poll it and track availability over time.

## Alerting Thresholds

| Alert | Condition | Severity |
|-------|-----------|----------|
| Service down | `/health` returns non-200 for > 2 minutes | Critical |
| High error rate | 5xx rate > 5% over 5 minutes | Critical |
| Slow responses | p95 latency > 5s over 10 minutes | Warning |
| Scraper blocked | PFR 403 count > 5 in 1 hour | Warning |
| Odds API quota low | < 20% remaining | Warning |
| Odds API quota exhausted | 0 remaining | Critical |
| DB connection pool exhausted | Active connections = max pool size | Critical |

## Tooling Recommendations

Start simple. Add complexity only when the basic tools prove insufficient.

### Phase 1: Free / built-in (start here)

| Need | Tool | Cost |
|------|------|------|
| Log viewing | Hosting platform logs (Railway/Render dashboard) | Free |
| Uptime monitoring | [UptimeRobot](https://uptimerobot.com/) | Free (50 monitors) |
| Error tracking | Structured logs + `grep` | Free |

### Phase 2: Low-cost additions (when needed)

| Need | Tool | Cost |
|------|------|------|
| Log aggregation | [Logtail](https://betterstack.com/logtail) / [Axiom](https://axiom.co/) | Free tier |
| APM / Metrics | [Grafana Cloud](https://grafana.com/products/cloud/) | Free tier (10K metrics) |
| Error tracking | [Sentry](https://sentry.io/) | Free tier (5K events/mo) |

### Phase 3: Full observability (production at scale)

| Need | Tool | Cost |
|------|------|------|
| Metrics + dashboards | Prometheus + Grafana (self-hosted) | Free (compute cost) |
| Distributed tracing | OpenTelemetry + Jaeger | Free (self-hosted) |
| Log aggregation | ELK stack or Loki | Free (self-hosted) |

## Implementation Checklist

- [ ] Add `structlog` to each app repo's `requirements.txt`
- [ ] Configure structured logging at service startup
- [ ] Add `RequestLoggingMiddleware` to each FastAPI app
- [ ] Set up UptimeRobot to poll `/health` endpoints
- [ ] Add scrape success/failure logging to beat-books-data
- [ ] Add Odds API quota tracking to beat-books-data
- [ ] Add model prediction latency logging to beat-books-model
