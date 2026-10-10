# Changelog

## [1.2.0] - 2026-10-10

### Added
- SQLite key store (`KEY_STORE=sqlite`): each operation is its own transaction, so keys and usage counts stay exact across threads, workers and processes. On first start it imports an existing JSON store, hashing any legacy raw keys. JSON remains the default; CI runs the full suite against both backends.
- The Docker image now uses the SQLite store (still one worker: subscriptions, analytics and the signup throttle are per-process).

## [1.1.0] - 2026-10-10

### Security
- Removed the hardcoded `dev_key_123` and `pro_key_456` keys that were created on first run.
- API keys are now stored as SHA-256 digests. Existing plaintext stores migrate automatically on startup.
- `/payment/success` no longer issues a key for an unpaid checkout session.
- Key management and global analytics now require a dedicated operator key (`ADMIN_API_KEY`). Previously any paid-tier key could list keys, mint enterprise keys and read all analytics.
- Removed the unauthenticated `/debug/stripe-config` endpoint and made `/api/marketing/stats` operator-only.
- Throttled `POST /api/keys/free` per client IP and tightened email validation.
- Stopped combining wildcard CORS with credentials, stopped returning exception text in 500 responses, and escaped reflected values in the payment page.

### Fixed
- Invalid `category` or `risk_level` values returned a 500 instead of 422.
- Stripe webhooks crashed on Stripe SDK 13+ (`StripeObject` is not a dict). The verified payload is now parsed as JSON.
- `/payment/success` returned a 500 for JSON clients.
- Webhook cancellation edited the key file directly by raw key. It now goes through the key manager.
- Key and usage files are written atomically under a lock. Concurrent requests could previously lose counts or corrupt the file.
- Decision IDs collided for decisions made in the same second.
- The Dockerfile could not build (it copied files from outside the build context). Start commands are unified on `uvicorn api.main:app`.

### Changed
- Pydantic v2 validators, current Stripe exception names, bounded dependency ranges, and CI that runs a real pytest suite on Python 3.11 to 3.13.
- Removed unused modules, one-off deployment scripts and generated status reports.
