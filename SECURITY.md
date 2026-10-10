# Security

## What the service does to protect itself

- **Keys are stored hashed.** Only a SHA-256 digest of each API key is written to disk. A leaked `api_keys.json` does not leak usable keys. Raw keys are shown once, at creation.
- **No default credentials.** A fresh install has zero valid keys.
- **Operator routes are separate from customer keys.** Key management and global analytics require `X-Admin-Key` matching `ADMIN_API_KEY` (constant-time comparison). Customer keys of any tier cannot reach them. With `ADMIN_API_KEY` unset those routes return 403.
- **Checkout cannot be bypassed.** `/payment/success` issues a key only when Stripe reports the session as paid and a subscription exists.
- **Webhooks are verified.** `/webhooks/stripe` rejects missing, malformed and wrongly signed requests, and a cancelled subscription downgrades the matching key.
- **Signup abuse is throttled.** `POST /api/keys/free` is limited per client IP (`FREE_KEY_LIMIT_PER_HOUR`).
- **CORS never combines `*` with credentials.**
- **Error responses are generic.** Exception text is logged, not returned. Reflected values on the payment page are HTML-escaped.
- **State writes are atomic** and serialized under a lock, so a crash or concurrent requests cannot corrupt the key store.

## Known limits

- JSON-file state suits a single worker. Use a database before scaling out.
- The per-IP throttle is in memory. Behind a proxy, set `TRUST_PROXY=true` only if the proxy overwrites `X-Forwarded-For`.
- A lost key cannot be recovered; it has to be reissued.

## Reporting a vulnerability

Open a private security advisory on the GitHub repository rather than a public issue.
