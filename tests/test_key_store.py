"""Backend-specific checks for the key store. The rest of the suite runs against whichever
backend KEY_STORE selects (CI runs it twice: json and sqlite)."""
import json
import threading

import pytest

import api.api_key_manager as akm


@pytest.fixture()
def sqlite_mgr(tmp_path, monkeypatch):
    monkeypatch.setenv("KEY_DB_PATH", str(tmp_path / "keys.sqlite3"))
    monkeypatch.setattr(akm, "API_KEYS_FILE", str(tmp_path / "none.json"))
    monkeypatch.setattr(akm, "RATE_LIMIT_FILE", str(tmp_path / "none-usage.json"))
    return akm.APIKeyManager(backend="sqlite")


def test_sqlite_round_trip(sqlite_mgr):
    key = sqlite_mgr.generate_api_key("pro", "t")
    assert sqlite_mgr.validate_api_key(key)["tier"] == "pro"
    assert key.encode() not in open(sqlite_mgr.keys_file, "rb").read()
    assert sqlite_mgr.set_tier(key, "free") and sqlite_mgr.get_key_info(key)["requests_per_month"] == 100
    assert sqlite_mgr.deactivate_key(key) and sqlite_mgr.validate_api_key(key) is None


def test_sqlite_concurrent_counts_are_exact(sqlite_mgr):
    key = sqlite_mgr.generate_api_key("pro", "t")
    threads = [threading.Thread(target=lambda: [sqlite_mgr.record_request(key) for _ in range(25)]) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    stats = sqlite_mgr.get_usage_stats(key)
    assert stats["total_requests"] == 200 and stats["overage_requests"] == 0


def test_sqlite_free_tier_cap(sqlite_mgr):
    key = sqlite_mgr.generate_api_key("free", "t")
    for _ in range(100):
        sqlite_mgr.record_request(key)
    assert sqlite_mgr.validate_api_key(key) is None
    assert sqlite_mgr.get_usage_stats(key)["total_requests"] == 100


def test_sqlite_imports_existing_json_store_once(tmp_path, monkeypatch):
    keys, usage = tmp_path / "k.json", tmp_path / "u.json"
    digest = akm.hash_key("already_hashed")
    keys.write_text(json.dumps({"legacy_raw_key": {"tier": "pro", "requests_per_month": 10000, "active": True},
                                digest: {"tier": "free", "requests_per_month": 100, "active": True}}))
    usage.write_text(json.dumps({"legacy_raw_key_2026-10": {"count": 7, "overage_requests": 0}}))
    monkeypatch.setattr(akm, "API_KEYS_FILE", str(keys))
    monkeypatch.setattr(akm, "RATE_LIMIT_FILE", str(usage))
    monkeypatch.setenv("KEY_DB_PATH", str(tmp_path / "db.sqlite3"))
    mgr = akm.APIKeyManager(backend="sqlite")
    assert mgr.get_key_info("legacy_raw_key")["tier"] == "pro"
    assert mgr.store.get_usage(akm.hash_key("legacy_raw_key") + "_2026-10")["count"] == 7
    assert set(mgr.list_keys()) == {akm.hash_key("legacy_raw_key"), digest}
    keys.write_text(json.dumps({"another": {"tier": "pro", "active": True}}))
    assert akm.APIKeyManager(backend="sqlite").get_key_info("another") is None   # import happens once


def test_unknown_backend_is_rejected():
    with pytest.raises(ValueError):
        akm.APIKeyManager(backend="postgres")
