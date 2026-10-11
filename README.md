# AI Decision Engine API

[![CI](https://github.com/lowriskbtc/ai-decision-engine-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lowriskbtc/ai-decision-engine-api/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A FastAPI service that scores decisions by risk, remembers past outcomes, and gates how much an automated system may do on its own. It ships with API-key authentication, tiered quotas, optional Stripe subscriptions, and usage analytics.

The decision logic is deliberately simple and explainable: risk comes from amount thresholds, and an "autonomy level" that grows with recorded successes decides whether a task may run without a human. It is a framework for wiring that gate into your own agents, not a model.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export ADMIN_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
uvicorn api.main:app --reload
```

Open http://localhost:8000/docs for the interactive API reference, then:

```bash
# 1. get a free key (shown once, stored only as a SHA-256 digest)
curl -s -X POST localhost:8000/api/keys/free -H 'content-type: application/json' \
     -d '{"email": "you@example.com"}'

# 2. evaluate a decision
curl -s -X POST localhost:8000/decisions/evaluate \
     -H 'X-API-Key: <your key>' -H 'content-type: application/json' \
     -d '{"category": "FINANCIAL", "amount": 2500, "description": "renew hosting"}'
```

There are no built-in default keys. Every key is created through the API or with `python api/manage_api_keys.py generate pro`.

## Endpoints

| Route | Auth | Purpose |
|---|---|---|
| `GET /health` | none | Liveness and current autonomy level |
| `POST /decisions/evaluate` | API key | Score a decision, return risk level and required action |
| `POST /risk/assess` | API key | Risk assessment for an amount and category |
| `GET /autonomy/level` | API key | Current autonomy level |
| `POST /autonomy/should-execute` | API key | Whether a task type at a risk level may run unattended |
| `POST /memory/insights` | API key | Insights from stored decision history |
| `GET /api/usage`, `/api/billing`, `/api/key/info` | API key | Usage, overage billing summary, key details |
| `POST /api/keys/free` | none, throttled per IP | Issue a free-tier key |
| `GET /pricing` | none | Tier pricing (HTML or JSON by `Accept` header) |
| `POST /payment/checkout`, `GET /payment/success` | none | Stripe checkout; a key is issued only for a paid session |
| `POST /webhooks/stripe` | Stripe signature | Subscription lifecycle (cancellation downgrades the key to free) |
| `/api/keys/*`, `/analytics/*`, `GET /api/marketing/stats` | `X-Admin-Key` | Operator-only key management and global analytics |

Free keys are capped at 100 requests per month. Paid tiers may exceed their included quota and are billed for overage.

## Configuration

All settings are environment variables; see [.env.example](.env.example). The important ones:

| Variable | Purpose |
|---|---|
| `ADMIN_API_KEY` | Operator key for admin routes. If unset, admin routes are disabled. |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins. `*` is allowed but disables credentials. |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID`, `STRIPE_ENTERPRISE_PRICE_ID` | Enable billing. Without them, billing routes return 503. |
| `KEY_STORE` | `json` (default) or `sqlite`. SQLite keeps key and usage counts exact across processes and imports an existing JSON store on first start. |
| `KEY_DB_PATH` | SQLite file when `KEY_STORE=sqlite` (default `api_keys.sqlite3`). |
| `API_KEYS_FILE`, `RATE_LIMIT_FILE`, `SUBSCRIPTIONS_FILE` | JSON state files. Use a persistent volume. |

## Run in production

```bash
docker compose up --build        # state persists in the api-data volume
```

Or deploy to Railway or Render using the included `railway.json` / `render.yaml`. The start command in every case is `uvicorn api.main:app` from the repository root.

Stripe setup is covered in [STRIPE_SETUP_GUIDE.md](STRIPE_SETUP_GUIDE.md). Security properties and known limits are in [SECURITY.md](SECURITY.md).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite uses a temporary directory for all state, so it never touches your data. CI runs it twice, once per storage backend. It covers authentication and the key lifecycle, input validation, free-tier limits, the unpaid-checkout bypass, admin gating, webhook signature checks and subscription downgrades, plaintext-key migration, and concurrent usage counting.

## Known limitations

- Keys and usage can live in SQLite (`KEY_STORE=sqlite`), which is safe across processes. Subscriptions, analytics and the signup throttle are still per-process (JSON files and memory), so run a single worker until those move to the database too.
- The signup throttle is in memory and resets on restart.
- Decision risk is threshold-based on `amount`; the memory layer records history but does not yet adjust risk (see the `pass` in `_assess_risk`).
- The Docker image has not been built in CI; the app itself is exercised by the test suite and a live server smoke test.

## Project layout

```
api/                  FastAPI app, key manager, Stripe service, analytics, admin routes
ai_decision_engine.py risk assessment and action rules
ai_memory_system.py   decision and event history
autonomy_tracker.py   gradual autonomy levels
sdk/ integrations/ examples/ demos/   client SDK, CLI and usage examples
tests/                pytest suite
```
