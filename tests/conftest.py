"""Test setup: every state file lives in a temp dir so tests never touch the repo."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_STATE = tempfile.mkdtemp(prefix="ade-tests-")

# Must be set before any api module is imported: several read env at import time.
for name, fname in {
    "API_KEYS_FILE": "api_keys.json",
    "RATE_LIMIT_FILE": "rate_limits.json",
    "SUBSCRIPTIONS_FILE": "subscriptions.json",
    "MARKETING_ANALYTICS_FILE": "marketing_analytics.json",
    "KEY_DB_PATH": "api_keys.sqlite3",
}.items():
    os.environ[name] = str(Path(_STATE) / fname)
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"
os.environ.pop("STRIPE_SECRET_KEY", None)
os.environ.pop("ALLOWED_ORIGINS", None)
os.environ["PYTHONIOENCODING"] = "utf-8"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _state_dir():
    """Relative-path state files (memory, analytics, cache) land in the temp dir."""
    prev = os.getcwd()
    os.chdir(_STATE)
    yield
    os.chdir(prev)


@pytest.fixture(scope="session")
def app():
    from api.main import app as _app
    return _app


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def manager():
    from api.api_key_manager import api_key_manager
    return api_key_manager


@pytest.fixture()
def pro_key(manager):
    return manager.generate_api_key(tier="pro", prefix="test")


@pytest.fixture()
def free_key(manager):
    return manager.generate_api_key(tier="free", prefix="test")


@pytest.fixture()
def auth(pro_key):
    return {"X-API-Key": pro_key}
