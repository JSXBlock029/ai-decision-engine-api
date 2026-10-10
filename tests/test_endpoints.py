import hashlib
import hmac
import json
import time

import pytest

PROTECTED = [
    ("post", "/decisions/evaluate", {"category": "FINANCIAL", "amount": 10}),
    ("post", "/risk/assess", {"amount": 10}),
    ("get", "/autonomy/level", None),
    ("post", "/autonomy/should-execute", {"task_type": "x"}),
    ("post", "/memory/insights", {"decision_data": {}}),
    ("get", "/api/usage", None),
    ("get", "/api/billing", None),
    ("get", "/api/key/info", None),
]


def call(client, method, path, body=None, headers=None):
    fn = getattr(client, method)
    if method == "post":
        return fn(path, json=body, headers=headers or {})
    return fn(path, headers=headers or {})


# ---------- basics ----------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_root_json_and_html(client):
    assert client.get("/").status_code == 200
    r = client.get("/", headers={"accept": "text/html"})
    assert r.status_code == 200 and "<html" in r.text.lower()


# ---------- authentication ----------

@pytest.mark.parametrize("method,path,body", PROTECTED)
def test_protected_requires_key(client, method, path, body):
    assert call(client, method, path, body).status_code == 401


@pytest.mark.parametrize("method,path,body", PROTECTED)
def test_protected_rejects_bad_key(client, method, path, body):
    assert call(client, method, path, body, {"X-API-Key": "nope"}).status_code == 401


@pytest.mark.parametrize("known", ["dev_key_123", "pro_key_456"])
def test_no_well_known_default_keys(client, known):
    """A fresh deployment must not ship usable hardcoded keys."""
    r = client.get("/autonomy/level", headers={"X-API-Key": known})
    assert r.status_code == 401


def test_valid_key_accepted(client, auth):
    assert client.get("/autonomy/level", headers=auth).status_code == 200


def test_deactivated_key_rejected(client, manager, auth, pro_key):
    assert client.get("/autonomy/level", headers=auth).status_code == 200
    assert manager.deactivate_key(pro_key) is True
    assert client.get("/autonomy/level", headers=auth).status_code == 401


def test_keys_not_stored_in_plaintext(manager, pro_key):
    raw = open(manager.keys_file, "rb").read()
    assert pro_key.encode() not in raw


# ---------- decisions / validation ----------

def test_evaluate_decision(client, auth):
    r = client.post("/decisions/evaluate", json={"category": "financial", "amount": 50, "description": "buy"}, headers=auth)
    assert r.status_code == 200, r.text


@pytest.mark.parametrize("body", [
    {"category": "NOT_A_CATEGORY", "amount": 1},
    {"category": "FINANCIAL", "amount": -5},
    {"amount": 1},
    {"category": "FINANCIAL", "description": "x" * 1001},
])
def test_evaluate_validation(client, auth, body):
    assert client.post("/decisions/evaluate", json=body, headers=auth).status_code == 422


def test_risk_assess(client, auth):
    r = client.post("/risk/assess", json={"amount": 100, "category": "OPERATIONAL"}, headers=auth)
    assert r.status_code == 200, r.text


def test_should_execute_validation(client, auth):
    bad = client.post("/autonomy/should-execute", json={"task_type": "t", "risk_level": "EXTREME"}, headers=auth)
    assert bad.status_code == 422
    ok = client.post("/autonomy/should-execute", json={"task_type": "t", "risk_level": "low"}, headers=auth)
    assert ok.status_code == 200, ok.text


def test_malformed_json_is_4xx_not_500(client, auth):
    r = client.post("/decisions/evaluate", content=b"{not json", headers={**auth, "content-type": "application/json"})
    assert 400 <= r.status_code < 500


# ---------- tiers / limits ----------

def test_free_tier_hard_limit(client, free_key):
    h = {"X-API-Key": free_key}
    codes = [client.get("/autonomy/level", headers=h).status_code for _ in range(103)]
    assert codes[0] == 200
    assert codes[-1] == 401  # free tier is capped at 100 requests per month


def test_usage_counts_requests(client, auth):
    for _ in range(3):
        client.get("/autonomy/level", headers=auth)
    r = client.get("/api/usage", headers=auth)
    assert r.status_code == 200
    assert r.json() is not None


# ---------- free key endpoint ----------

def test_free_key_issues_working_key(client):
    r = client.post("/api/keys/free", json={"email": "someone@example.com"})
    assert r.status_code == 200, r.text
    key = r.json().get("api_key") or r.json().get("key")
    assert key
    assert client.get("/autonomy/level", headers={"X-API-Key": key}).status_code == 200


@pytest.mark.parametrize("email", ["", "no-at-sign", "a@b", "@x.com", "a b@x.com"])
def test_free_key_rejects_bad_email(client, email):
    assert client.post("/api/keys/free", json={"email": email}).status_code in (400, 422)


def test_free_key_endpoint_is_rate_limited(client):
    codes = [client.post("/api/keys/free", json={"email": f"u{i}@example.com"}).status_code for i in range(30)]
    assert 429 in codes, "unauthenticated key minting must be throttled"


# ---------- locked-down / debug surfaces ----------

def test_debug_endpoint_removed(client):
    assert client.get("/debug/stripe-config").status_code == 404


def test_marketing_stats_not_public(client):
    assert client.get("/api/marketing/stats").status_code in (401, 403)


def test_marketing_stats_with_admin_key(client):
    r = client.get("/api/marketing/stats", headers={"X-Admin-Key": "test-admin-key"})
    assert r.status_code == 200, r.text


def test_cors_wildcard_has_no_credentials(client):
    r = client.options("/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert r.headers.get("access-control-allow-credentials") != "true"


def test_errors_do_not_leak_internals(client, auth):
    r = client.post("/memory/insights", json={"decision_data": {"x": object.__name__}}, headers=auth)
    assert "Traceback" not in r.text and "File \"" not in r.text


# ---------- stripe webhook ----------

def _signed(payload: bytes, secret="whsec_test_secret"):
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return {"stripe-signature": f"t={ts},v1={sig}", "content-type": "application/json"}


def test_webhook_missing_signature(client):
    assert client.post("/webhooks/stripe", content=b"{}").status_code == 400


def test_webhook_bad_signature(client):
    r = client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "t=1,v1=deadbeef"})
    assert r.status_code == 400


def test_webhook_valid_signature_unknown_event(client):
    payload = json.dumps({"id": "evt_1", "object": "event", "type": "ping.test", "data": {"object": {}}}).encode()
    r = client.post("/webhooks/stripe", content=payload, headers=_signed(payload))
    assert r.status_code == 200, r.text


def test_webhook_wrong_secret_rejected(client):
    payload = b'{"type":"ping.test","data":{"object":{}}}'
    r = client.post("/webhooks/stripe", content=payload, headers=_signed(payload, secret="whsec_other"))
    assert r.status_code == 400


# ---------- checkout without stripe configured degrades cleanly ----------

def test_checkout_validation(client):
    assert client.post("/payment/checkout", json={"email": "bad", "tier": "pro"}).status_code in (400, 422)
    assert client.post("/payment/checkout", json={"email": "a@example.com", "tier": "gold"}).status_code in (400, 422)


def test_checkout_without_stripe_is_503_not_500(client):
    r = client.post("/payment/checkout", json={"email": "a@example.com", "tier": "pro"})
    assert r.status_code in (500, 503) and r.status_code != 500, r.text


def test_pricing(client):
    assert client.get("/pricing", headers={"accept": "application/json"}).status_code == 200
