"""
API key management.

Keys are issued once and only a SHA-256 digest is stored, so a leaked data file
does not leak usable keys.

Two storage backends, chosen with KEY_STORE:
  json   (default) a pair of JSON files, written atomically under a process-wide
         lock. Correct for a single worker.
  sqlite one SQLite database (KEY_DB_PATH). Every operation is its own short
         transaction, so it is safe across threads, workers and processes.
         On first start it imports any existing JSON key and usage files.
"""

import hashlib
import json
import os
import re
import secrets
import sqlite3
import tempfile
import threading
from datetime import datetime
from typing import Any, Dict, Optional

API_KEYS_FILE = os.getenv("API_KEYS_FILE", "api_keys.json")
RATE_LIMIT_FILE = os.getenv("RATE_LIMIT_FILE", "rate_limits.json")
KEY_DB_PATH = os.getenv("KEY_DB_PATH", "api_keys.sqlite3")

TIER_LIMITS = {
    "free": 100,
    "dev": 1000,
    "pro": 10000,
    "enterprise": 1000000,
}

_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_LOCK = threading.RLock()


def hash_key(api_key: str) -> str:
    """Stable digest used as the storage identifier for a key."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_json_atomic(path: str, data: Dict[str, Any]) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------------------------------
# Storage backends. Both speak in key digests, never raw keys.
# --------------------------------------------------------------------------

class JsonStore:
    def __init__(self, keys_file: str, usage_file: str):
        self.keys_file = keys_file
        self.usage_file = usage_file
        self._migrate_plaintext_keys()

    def all_keys(self) -> Dict[str, Any]:
        with _LOCK:
            return _read_json(self.keys_file)

    def get_key(self, digest: str) -> Optional[Dict[str, Any]]:
        return self.all_keys().get(digest)

    def put_key(self, digest: str, info: Dict[str, Any]) -> None:
        with _LOCK:
            keys = _read_json(self.keys_file)
            keys[digest] = info
            _write_json_atomic(self.keys_file, keys)

    def update_key(self, digest: str, **fields) -> bool:
        with _LOCK:
            keys = _read_json(self.keys_file)
            if digest not in keys:
                return False
            keys[digest].update(fields)
            _write_json_atomic(self.keys_file, keys)
            return True

    def get_usage(self, month_key: str) -> Dict[str, Any]:
        return _read_json(self.usage_file).get(month_key, {})

    def add_request(self, month_key: str, now: str, limit: int) -> None:
        with _LOCK:
            usage = _read_json(self.usage_file)
            entry = usage.setdefault(month_key, {"count": 0, "first_request": now, "overage_requests": 0})
            entry["count"] = entry.get("count", 0) + 1
            entry["last_request"] = now
            entry["overage_requests"] = max(0, entry["count"] - limit)
            _write_json_atomic(self.usage_file, usage)

    def _migrate_plaintext_keys(self) -> None:
        """Older versions stored raw keys. Rewrite them as digests in place."""
        with _LOCK:
            keys = _read_json(self.keys_file)
            if not keys or all(_DIGEST.match(k) for k in keys):
                return
            migrated = {(k if _DIGEST.match(k) else hash_key(k)): v for k, v in keys.items()}
            _write_json_atomic(self.keys_file, migrated)
            usage = _read_json(self.usage_file)
            if usage:
                moved = {}
                for k, v in usage.items():
                    ident, _, month = k.rpartition("_")
                    moved[k if _DIGEST.match(ident) else f"{hash_key(ident)}_{month}"] = v
                _write_json_atomic(self.usage_file, moved)


class SqliteStore:
    def __init__(self, db_path: str, import_keys_file: Optional[str] = None,
                 import_usage_file: Optional[str] = None):
        self.keys_file = db_path          # kept for parity with JsonStore
        self.db_path = db_path
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS api_keys (digest TEXT PRIMARY KEY, info TEXT NOT NULL)")
            c.execute("CREATE TABLE IF NOT EXISTS usage (month_key TEXT PRIMARY KEY, count INTEGER NOT NULL,"
                      " first_request TEXT, last_request TEXT, overage_requests INTEGER NOT NULL DEFAULT 0)")
        if import_keys_file:
            self._import_json(import_keys_file, import_usage_file)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return _Txn(conn)

    def all_keys(self) -> Dict[str, Any]:
        with self._conn() as c:
            return {d: json.loads(i) for d, i in c.execute("SELECT digest, info FROM api_keys")}

    def get_key(self, digest: str) -> Optional[Dict[str, Any]]:
        with self._conn() as c:
            row = c.execute("SELECT info FROM api_keys WHERE digest = ?", (digest,)).fetchone()
        return json.loads(row[0]) if row else None

    def put_key(self, digest: str, info: Dict[str, Any]) -> None:
        with self._conn() as c:
            c.execute("INSERT OR REPLACE INTO api_keys (digest, info) VALUES (?, ?)", (digest, json.dumps(info)))

    def update_key(self, digest: str, **fields) -> bool:
        with self._conn() as c:
            row = c.execute("SELECT info FROM api_keys WHERE digest = ?", (digest,)).fetchone()
            if not row:
                return False
            info = json.loads(row[0])
            info.update(fields)
            c.execute("UPDATE api_keys SET info = ? WHERE digest = ?", (json.dumps(info), digest))
            return True

    def get_usage(self, month_key: str) -> Dict[str, Any]:
        with self._conn() as c:
            row = c.execute("SELECT count, first_request, last_request, overage_requests FROM usage"
                            " WHERE month_key = ?", (month_key,)).fetchone()
        if not row:
            return {}
        return {"count": row[0], "first_request": row[1], "last_request": row[2], "overage_requests": row[3]}

    def add_request(self, month_key: str, now: str, limit: int) -> None:
        with self._conn() as c:
            c.execute("INSERT INTO usage (month_key, count, first_request, last_request, overage_requests)"
                      " VALUES (?, 1, ?, ?, MAX(0, 1 - ?))"
                      " ON CONFLICT(month_key) DO UPDATE SET count = count + 1, last_request = excluded.last_request,"
                      " overage_requests = MAX(0, count + 1 - ?)", (month_key, now, now, limit, limit))

    def _import_json(self, keys_file: str, usage_file: Optional[str]) -> None:
        """One-time import of an existing JSON store (raw keys are hashed on the way in)."""
        with self._conn() as c:
            if c.execute("SELECT COUNT(*) FROM api_keys").fetchone()[0]:
                return
        keys = _read_json(keys_file)
        if not keys:
            return
        with self._conn() as c:
            for k, info in keys.items():
                c.execute("INSERT OR IGNORE INTO api_keys (digest, info) VALUES (?, ?)",
                          (k if _DIGEST.match(k) else hash_key(k), json.dumps(info)))
            for k, v in (_read_json(usage_file) if usage_file else {}).items():
                ident, _, month = k.rpartition("_")
                mk = k if _DIGEST.match(ident) else f"{hash_key(ident)}_{month}"
                c.execute("INSERT OR IGNORE INTO usage (month_key, count, first_request, last_request, overage_requests)"
                          " VALUES (?, ?, ?, ?, ?)", (mk, int(v.get("count", 0)), v.get("first_request"),
                                                     v.get("last_request"), int(v.get("overage_requests", 0))))


class _Txn:
    """`with` wrapper: BEGIN IMMEDIATE on enter, COMMIT/ROLLBACK and close on exit."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self) -> sqlite3.Connection:
        self.conn.execute("BEGIN IMMEDIATE")
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        try:
            self.conn.execute("ROLLBACK" if exc_type else "COMMIT")
        finally:
            self.conn.close()
        return False


def make_store(backend: Optional[str] = None):
    backend = (backend or os.getenv("KEY_STORE", "json")).lower()
    if backend == "sqlite":
        return SqliteStore(os.getenv("KEY_DB_PATH", KEY_DB_PATH), API_KEYS_FILE, RATE_LIMIT_FILE)
    if backend == "json":
        return JsonStore(API_KEYS_FILE, RATE_LIMIT_FILE)
    raise ValueError(f"Unknown KEY_STORE {backend!r} (use 'json' or 'sqlite')")


# --------------------------------------------------------------------------
# Manager
# --------------------------------------------------------------------------

class APIKeyManager:
    """Manage API keys, authentication and monthly usage."""

    def __init__(self, backend: Optional[str] = None):
        self.store = make_store(backend)
        self.keys_file = self.store.keys_file

    # ---- keys ----------------------------------------------------------

    def generate_api_key(self, tier: str = "free", prefix: str = "key") -> str:
        """Create a key, store its digest, and return the raw key (shown once)."""
        tier = tier.lower()
        api_key = f"{prefix}_{secrets.token_urlsafe(32)}"
        self.store.put_key(hash_key(api_key), {
            "tier": tier,
            "requests_per_month": self._get_tier_limit(tier),
            "created_at": datetime.now().isoformat(),
            "active": True,
            "hint": api_key[:8] + "...",
        })
        return api_key

    def _get_tier_limit(self, tier: str) -> int:
        return TIER_LIMITS.get(tier.lower(), TIER_LIMITS["free"])

    def get_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        return self.store.get_key(hash_key(api_key))

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Return key info if the key exists, is active and is within its quota."""
        if not api_key:
            return None
        info = self.get_key_info(api_key)
        if not info or not info.get("active", False):
            return None
        if not self._check_rate_limit(api_key, info):
            return None
        return info

    def deactivate_key(self, api_key: str) -> bool:
        return self.store.update_key(hash_key(api_key), active=False)

    def set_tier(self, api_key: str, tier: str) -> bool:
        """Change a key's tier and quota (used when a subscription changes)."""
        return self.set_tier_by_digest(hash_key(api_key), tier)

    def set_tier_by_digest(self, digest: str, tier: str) -> bool:
        return self.store.update_key(digest, tier=tier.lower(), requests_per_month=self._get_tier_limit(tier))

    def list_keys(self) -> Dict[str, Any]:
        """Admin view. Never contains raw keys, only digests and hints."""
        return self.store.all_keys()

    # ---- usage ---------------------------------------------------------

    @staticmethod
    def _month_key(api_key: str) -> str:
        return f"{hash_key(api_key)}_{datetime.now().strftime('%Y-%m')}"

    def _check_rate_limit(self, api_key: str, key_info: Dict[str, Any]) -> bool:
        """Free keys have a hard monthly cap. Paid tiers may exceed it (billed as overage)."""
        if key_info.get("tier", "free") != "free":
            return True
        used = self.store.get_usage(self._month_key(api_key)).get("count", 0)
        return used < key_info.get("requests_per_month", TIER_LIMITS["free"])

    def record_request(self, api_key: str) -> None:
        info = self.get_key_info(api_key) or {}
        self.store.add_request(self._month_key(api_key), datetime.now().isoformat(),
                               info.get("requests_per_month", TIER_LIMITS["free"]))

    def get_usage_stats(self, api_key: str) -> Dict[str, Any]:
        info = self.get_key_info(api_key)
        if not info:
            return {"total_requests": 0, "included_requests": 0, "overage_requests": 0, "tier": "unknown"}
        max_requests = info.get("requests_per_month", TIER_LIMITS["free"])
        total = self.store.get_usage(self._month_key(api_key)).get("count", 0)
        return {
            "total_requests": total,
            "included_requests": min(total, max_requests),
            "overage_requests": max(0, total - max_requests),
            "max_requests": max_requests,
            "tier": info.get("tier", "free"),
            "month": datetime.now().strftime("%Y-%m"),
        }


# Global instance
api_key_manager = APIKeyManager()
