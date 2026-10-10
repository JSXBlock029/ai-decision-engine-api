"""Shared admin guard for operator-only routes (key management, global analytics)."""

import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException, status


def verify_admin(x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key")) -> bool:
    """
    Require the operator key from the ADMIN_API_KEY environment variable.

    Customer API keys (even enterprise ones) never grant admin access. If
    ADMIN_API_KEY is not set, admin routes are disabled entirely.
    """
    expected = os.getenv("ADMIN_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access is not enabled")
    if not x_admin_key or not hmac.compare_digest(x_admin_key.encode(), expected.encode()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin key required")
    return True
