from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from auth import get_current_user
from utils.event_utils import track_event_if_configured

# Ported from chat-app/backend/app/routers/auth.py (plan row 10). The
# source additionally persists a `User` record to Cosmos DB and seeds demo
# order history via `services/user_onboarding.py` on first sign-in; neither
# is ported here because this pattern's `DatabaseService` interface (see
# `database.py`) carries no user/order model or container -- persisting a
# user record on top of that abstraction would be new authoring, not a
# port. This surface returns the Easy Auth identity as resolved by
# `auth.get_current_user`, unchanged from the source's header handling.

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.get("/debug")
async def debug_auth_headers(request: Request):
    """Debug endpoint to see all headers and Easy Auth status."""
    headers = dict(request.headers)
    easy_auth_headers = {k: v for k, v in headers.items() if "x-ms-client" in k.lower()}

    return {
        "has_easy_auth": len(easy_auth_headers) > 0,
        "user_agent": headers.get("user-agent", "unknown"),
        "host": headers.get("host", "unknown"),
        "x_forwarded_for": headers.get("x-forwarded-for", "none"),
        "x_forwarded_proto": headers.get("x-forwarded-proto", "none"),
    }


@router.get("/me")
async def get_current_user_info(request: Request):
    try:
        current_user = await get_current_user(request)

        response_data = {
            "id": current_user["id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "roles": current_user["roles"],
            "is_authenticated": not current_user.get("is_guest", True),
            "is_guest": current_user.get("is_guest", True),
        }
        track_event_if_configured(
            "Auth_Guest_User" if current_user.get("is_guest") else "Auth_User_Authenticated",
            {"user_id": current_user["id"]},
        )
        return response_data

    except Exception as e:
        logger.error(f"Error in get_current_user_info: {e}")
        return {
            "id": "guest-user-00000000",
            "name": "Guest User",
            "email": "guest@example.invalid",
            "roles": ["guest"],
            "is_authenticated": False,
            "is_guest": True,
        }
