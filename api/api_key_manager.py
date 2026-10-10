"""
API key management.

Keys are issued once and only a SHA-256 digest is stored, so a leaked data file
does not leak usable keys. State is a pair of JSON files (keys and monthly usage),
written atomically under a process-wide lock. That is fine for a single worker;
run more than one worker and you should move this to a real database.
"""

import hashlib
import json
import os
import re
import secrets
import tempfile
import threading
from datetime import datetime
from typing import Any, Dict, Optional

API_KEYS_FILE = os.getenv("API_KEYS_FILE", "api_keys.json")
RATE_LIMIT_FILE = os.getenv("RATE_LIMIT_FILE", "rate_limits.json")

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


class APIKeyManager:
    """Manage API keys, authentication and monthly usage."""

    def __init__(self):
        self.keys_file = API_KEYS_FILE
        self.rate_limit_file = RATE_LIMIT_FILE
        self._migrate_plaintext_keys()

    # ---- storage -------------------------------------------------------

    def _load_keys(self) -> Dict[str, Any]:
        with _LOCK:
            return _read_json(self.keys_file)

    def _save_keys(self, keys: Dict[str, Any]) -> None:
        with _LOCK:
            _write_json_atomic(self.keys_file, keys)

    def _migrate_plaintext_keys(self) -> None:
        """Older versions stored raw keys. Rewrite them as digests in place."""
        with _LOCK:
            keys = self._load_keys()
            if not keys or all(_DIGEST.match(k) for k in keys):
                return
            migrated = {(k if _DIGEST.match(k) else hash_key(k)): v for k, v in keys.items()}
            self._save_keys(migrated)
            usage = _read_json(self.rate_limit_file)
            if usage:
                moved = {}
                for k, v in usage.items():
                    ident, _, month = k.rpartition("_")
                    moved[k if _DIGEST.match(ident) else f"{hash_key(ident)}_{month}"] = v
                _write_json_atomic(self.rate_limit_file, moved)

    # ---- keys ----------------------------------------------------------

    def generate_api_key(self, tier: str = "free", prefix: str = "key") -> str:
        """Create a key, store its digest, and return the raw key (shown once)."""
        tier = tier.lower()
        api_key = f"{prefix}_{secrets.token_urlsafe(32)}"
        with _LOCK:
            keys = self._load_keys()
            keys[hash_key(api_key)] = {
                "tier": tier,
                "requests_per_month": self._get_tier_limit(tier),
                "created_at": datetime.now().isoformat(),
                "active": True,
                "hint": api_key[:8] + "...",
            }
            self._save_keys(keys)
        return api_key

    def _get_tier_limit(self, tier: str) -> int:
        return TIER_LIMITS.get(tier.lower(), TIER_LIMITS["free"])

    def get_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        return self._load_keys().get(hash_key(api_key))

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
        with _LOCK:
            keys = self._load_keys()
            ident = hash_key(api_key)
            if ident not in keys:
                return False
            keys[ident]["active"] = False
            self._save_keys(keys)
            return True

    def set_tier(self, api_key: str, tier: str) -> bool:
        """Change a key's tier and quota (used when a subscription changes)."""
        with _LOCK:
            keys = self._load_keys()
            ident = hash_key(api_key)
            if ident not in keys:
                return False
            keys[ident]["tier"] = tier.lower()
            keys[ident]["requests_per_month"] = self._get_tier_limit(tier)
            self._save_keys(keys)
            return True

    def set_tier_by_digest(self, digest: str, tier: str) -> bool:
        with _LOCK:
            keys = self._load_keys()
            if digest not in keys:
                return False
            keys[digest]["tier"] = tier.lower()
            keys[digest]["requests_per_month"] = self._get_tier_limit(tier)
            self._save_keys(keys)
            return True

    def list_keys(self) -> Dict[str, Any]:
        """Admin view. Never contains raw keys, only digests and hints."""
        return self._load_keys()

    # ---- usage ---------------------------------------------------------

    @staticmethod
    def _month_key(api_key: str) -> str:
        return f"{hash_key(api_key)}_{datetime.now().strftime('%Y-%m')}"

    def _check_rate_limit(self, api_key: str, key_info: Dict[str, Any]) -> bool:
        """Free keys have a hard monthly cap. Paid tiers may exceed it (billed as overage)."""
        if key_info.get("tier", "free") != "free":
            return True
        used = _read_json(self.rate_limit_file).get(self._month_key(api_key), {}).get("count", 0)
        return used < key_info.get("requests_per_month", TIER_LIMITS["free"])

    def record_request(self, api_key: str) -> None:
        with _LOCK:
            usage = _read_json(self.rate_limit_file)
            mk = self._month_key(api_key)
            now = datetime.now().isoformat()
            entry = usage.setdefault(mk, {"count": 0, "first_request": now, "overage_requests": 0})
            entry["count"] = entry.get("count", 0) + 1
            entry["last_request"] = now
            info = self.get_key_info(api_key)
            if info:
                entry["overage_requests"] = max(0, entry["count"] - info.get("requests_per_month", TIER_LIMITS["free"]))
            _write_json_atomic(self.rate_limit_file, usage)

    def get_usage_stats(self, api_key: str) -> Dict[str, Any]:
        info = self.get_key_info(api_key)
        if not info:
            return {"total_requests": 0, "included_requests": 0, "overage_requests": 0, "tier": "unknown"}
        max_requests = info.get("requests_per_month", TIER_LIMITS["free"])
        total = _read_json(self.rate_limit_file).get(self._month_key(api_key), {}).get("count", 0)
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
