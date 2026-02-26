# External API Rate Limits, Costs, and Fallback Strategy

> Documents the external data sources the platform depends on, their constraints, and what happens when they're unavailable.
> Related: [Data Flow](data-flow.md) | [Architecture Overview](overview.md)

## Data Sources Overview

| Source | Purpose | Used By | Status |
|--------|---------|---------|--------|
| Pro-Football-Reference (PFR) | NFL stats (team, player, game) | beat-books-data | Active (scraping) |
| The Odds API | Live betting odds and lines | beat-books-data | Planned (beat-books-data#4) |

---

## Pro-Football-Reference (PFR)

### Access Method

Web scraping via Selenium + BeautifulSoup. No official API exists.

### Rate Limits and Bot Detection

| Constraint | Details |
|------------|---------|
| Rate limit | No published limit; observed throttling at ~20 req/min |
| Bot detection | Active — returns 403 errors and CAPTCHAs |
| User-Agent check | Yes — requires browser-like headers |
| IP blocking | Temporary blocks after sustained scraping |

### Recommended Request Cadence

```
Minimum delay between requests: 3-5 seconds
Maximum burst:                  10 requests before a longer pause
Long pause:                     30-60 seconds every 10 requests
Session limit:                  ~200 pages per session recommended
```

### Known Failure Modes

| Failure | HTTP Code | Behavior | Mitigation |
|---------|-----------|----------|------------|
| Rate limited | 403 | Page returns access denied | Back off, increase delay |
| CAPTCHA | 200 (with CAPTCHA HTML) | Page loads but no data | Rotate session, wait hours |
| Seasonal unavailability | N/A | Some pages only exist during season | Cache last-known data |
| HTML structure change | 200 | Parsing fails silently | Alert on empty results |

### Data Freshness Policy

| Data Type | Update Frequency | Staleness Threshold |
|-----------|-----------------|---------------------|
| Season standings | Weekly during season | 7 days |
| Team stats | Weekly during season | 7 days |
| Game results | Day after game | 2 days |
| Historical stats | Once at season start | 365 days |

### Fallback Strategy

1. **Primary:** Live scraping from PFR
2. **Fallback 1:** Serve cached data from PostgreSQL (always available if previously scraped)
3. **Fallback 2:** Log warning, return stale data with `"stale": true` flag
4. **Alerting:** If scrape success rate drops below 80% over 24 hours, alert

### Legal Considerations

- PFR's Terms of Service should be reviewed before scaling scraping
- Data is factual (game results, statistics) which is generally not copyrightable
- Respect `robots.txt` where applicable
- Consider reaching out to Sports Reference for data licensing if volume increases

---

## The Odds API

### Access Method

RESTful JSON API with API key authentication.

### Pricing Tiers

| Tier | Requests/Month | Cost | Best For |
|------|---------------|------|----------|
| Free | 500 | $0 | Development and testing |
| Starter | 10,000 | $20/mo | Light production use |
| Standard | 50,000 | $50/mo | Full production |
| Enterprise | Custom | Custom | High-volume |

### Key Endpoints

| Endpoint | Purpose | Typical Usage |
|----------|---------|---------------|
| `GET /v4/sports` | List available sports | Once on startup |
| `GET /v4/sports/{sport}/odds` | Get current odds | Periodically (see below) |
| `GET /v4/sports/{sport}/scores` | Get live scores | During games |
| `GET /v4/sports/{sport}/events` | Get upcoming events | Daily |

### Request Budget Planning

For NFL season (~18 weeks, 16 games/week):

| Usage Pattern | Requests/Week | Requests/Season |
|---------------|--------------|-----------------|
| Daily odds pull (1x/day) | 7 | 126 |
| Game-day odds (every 30min, 6hrs) | ~84 | ~1,512 |
| Score updates (every 5min during games) | ~192 | ~3,456 |
| **Total estimate** | ~283 | **~5,094** |

**Recommendation:** Start with Free tier for development. Move to Starter ($20/mo) for production — provides enough requests for the full season with headroom.

### Rate Limits

| Limit | Value |
|-------|-------|
| Per-second | 1 request/second |
| Per-minute | Not documented (stay under 30) |
| Monthly quota | Depends on tier |

### Quota Monitoring

```python
# The Odds API returns quota info in response headers
# X-Requests-Used: 42
# X-Requests-Remaining: 458
```

Track `X-Requests-Remaining` and alert at thresholds:

| Remaining | Action |
|-----------|--------|
| < 20% | Warning: reduce polling frequency |
| < 5% | Critical: switch to cached odds only |
| 0 | Stop: serve stale odds with warning flag |

### Fallback Strategy

1. **Primary:** Live API calls
2. **Fallback 1:** Serve last-known odds from PostgreSQL
3. **Fallback 2:** If odds are > 4 hours old, mark as stale in API response
4. **Alerting:** If quota drops below 20%, alert via monitoring

### API Key Management

- Store API key in environment variable: `ODDS_API_KEY`
- See [Secret Management](../operations/secret-management.md) for storage
- Never log or expose the API key in responses

---

## Monitoring Recommendations

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| PFR scrape success rate | beat-books-data logs | < 80% over 24h |
| PFR 403 error count | beat-books-data logs | > 5 in 1 hour |
| Odds API quota remaining | Response headers | < 20% of monthly |
| Data freshness | PostgreSQL `scraped_at` | > staleness threshold |
