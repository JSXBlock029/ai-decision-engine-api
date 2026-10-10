"""Regression tests for the holes found in the audit."""
import json
import threading
import time
from types import SimpleNamespace

import pytest

ADMIN = {"X-Admin-Key": "test-admin-key"}


# ---------- admin-only surfaces ----------

@pytest.mark.parametrize("method,path", [
    ("get", "/api/keys/list"),
    ("post", "/api/keys/generate"),
    ("get", "/analytics/stats"),
])
def test_customer_keys_are_not_admin(client, auth, method, path):
    r = getattr(client, method)(path, headers=auth, **({"json": {"tier": "enterprise"}} if method == "post" else {}))
    assert r.status_code in (401, 403)


@pytest.mark.parametrize("method,path", [
    ("get", "/api/keys/list"),
    ("get", "/analytics/stats"),
])
def test_admin_key_works(client, method, path):
    assert getattr(client, method)(path, headers=ADMIN).status_code == 200


def test_admin_cannot_see_raw_keys(client, pro_key):
    body = client.get("/api/keys/list", headers=ADMIN).text
    assert pro_key not in body


def test_admin_can_mint_and_key_works(client):
    r = client.post("/api/keys/generate", json={"tier": "pro"}, headers=ADMIN)
    assert r.status_code == 200, r.text
    key = r.json()["key"]
    assert client.get("/autonomy/level", headers={"X-API-Key": key}).status_code == 200


def test_admin_disabled_without_env(client, monkeypatch):
    monkeypatch.delenv("ADMIN_API_KEY", raising=False)
    assert client.get("/api/keys/list", headers=ADMIN).status_code == 403


# ---------- payment success must require a paid session ----------

def _fake_session(paid=True, sub="sub_123"):
    return SimpleNamespace(
        mode="subscription", subscription=sub if paid else None,
        payment_status="paid" if paid else "unpaid",
        metadata={"tier": "pro"}, customer_email="buyer@example.com",
    )


def test_unpaid_session_gets_no_key(client, manager, monkeypatch):
    import stripe
    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda sid: _fake_session(paid=False)))
    before = len(manager.list_keys())
    r = client.get("/payment/success?session_id=cs_test_unpaid", headers={"accept": "application/json"})
    assert r.status_code == 402
    assert len(manager.list_keys()) == before


def test_paid_session_issues_key_once(client, manager, monkeypatch):
    import stripe
    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(lambda sid: _fake_session(sub="sub_once")))
    h = {"accept": "application/json"}
    first = client.get("/payment/success?session_id=cs_test_paid", headers=h)
    assert first.status_code == 200, first.text
    key = first.json()["api_key"]
    assert client.get("/autonomy/level", headers={"X-API-Key": key}).status_code == 200
    again = client.get("/payment/success?session_id=cs_test_paid", headers=h)
    assert again.status_code == 200 and "api_key" not in again.json()


def test_success_page_escapes_reflected_input(client, monkeypatch):
    import stripe

    def boom(sid):
        raise RuntimeError("<script>alert(1)</script>")

    monkeypatch.setattr(stripe.checkout.Session, "retrieve", staticmethod(boom))
    r = client.get("/payment/success", params={"session_id": "<img src=x onerror=alert(1)>"}, headers={"accept": "text/html"})
    assert "<script>alert(1)</script>" not in r.text
    assert "<img src=x" not in r.text


# ---------- subscription lifecycle via webhook ----------

def _signed(payload: bytes, secret="whsec_test_secret"):
    import hashlib
    import hmac
    ts = str(int(time.time()))
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return {"stripe-signature": f"t={ts},v1={sig}", "content-type": "application/json"}


def test_cancelled_subscription_downgrades_key(client, manager, pro_key):
    from api.stripe_service import stripe_service
    stripe_service.link_subscription_to_api_key(pro_key, "sub_cancel", "x@example.com", "pro")
    assert manager.get_key_info(pro_key)["tier"] == "pro"
    payload = json.dumps({"id": "evt_2", "object": "event", "type": "customer.subscription.deleted",
                          "data": {"object": {"id": "sub_cancel"}}}).encode()
    r = client.post("/webhooks/stripe", content=payload, headers=_signed(payload))
    assert r.status_code == 200, r.text
    info = manager.get_key_info(pro_key)
    assert info["tier"] == "free" and info["requests_per_month"] == 100


def test_subscription_store_has_no_raw_key(pro_key):
    from api.stripe_service import stripe_service
    stripe_service.link_subscription_to_api_key(pro_key, "sub_hash", "x@example.com", "pro")
    assert pro_key not in open(stripe_service.subscriptions_file, encoding="utf-8").read()


# ---------- key store ----------

def test_plaintext_store_is_migrated(tmp_path, monkeypatch):
    import api.api_key_manager as akm
    keys_file, usage_file = tmp_path / "k.json", tmp_path / "u.json"
    keys_file.write_text(json.dumps({"legacy_key_abc": {"tier": "pro", "requests_per_month": 10000, "active": True}}))
    usage_file.write_text(json.dumps({"legacy_key_abc_2026-10": {"count": 7}}))
    monkeypatch.setattr(akm, "API_KEYS_FILE", str(keys_file))
    monkeypatch.setattr(akm, "RATE_LIMIT_FILE", str(usage_file))
    mgr = akm.APIKeyManager()
    assert "legacy_key_abc" not in keys_file.read_text()
    assert mgr.get_key_info("legacy_key_abc")["tier"] == "pro"
    assert "legacy_key_abc" not in usage_file.read_text()


def test_corrupt_store_does_not_crash(tmp_path, monkeypatch):
    import api.api_key_manager as akm
    keys_file = tmp_path / "k.json"
    keys_file.write_text("{ not json")
    monkeypatch.setattr(akm, "API_KEYS_FILE", str(keys_file))
    monkeypatch.setattr(akm, "RATE_LIMIT_FILE", str(tmp_path / "u.json"))
    mgr = akm.APIKeyManager()
    assert mgr.validate_api_key("anything") is None


def test_concurrent_usage_counts_are_exact(manager, pro_key):
    def worker():
        for _ in range(25):
            manager.record_request(pro_key)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert manager.get_usage_stats(pro_key)["total_requests"] == 200
