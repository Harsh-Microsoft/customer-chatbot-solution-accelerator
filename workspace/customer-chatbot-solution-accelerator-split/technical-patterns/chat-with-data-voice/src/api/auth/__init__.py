from __future__ import annotations

import logging
from typing import Any

from fastapi import Request

from utils.auth_utils import get_authenticated_user_details, get_sample_user, get_user_email

# Ported from chat-app/backend/app/auth.py (plan row 11). Trimmed the
# source's verbose per-header debug logging (it logged raw Easy Auth token
# header values, an OWASP-flagged sensitive-data-in-logs pattern) without
# changing the identity-resolution behavior. `guest@contoso.com` is replaced
# with a domain-neutral placeholder per the zero-domain-vocabulary rule.

logger = logging.getLogger(__name__)

_GUEST_EMAIL = "guest@example.invalid"


async def get_current_user(request: Request) -> dict[str, Any]:
    try:
        headers = dict(request.headers)

        forwarded_easy_auth_headers = {
            "x-ms-client-principal-id": headers.get("x-ms-client-principal-id"),
            "x-ms-client-principal-name": headers.get("x-ms-client-principal-name"),
            "x-ms-client-principal-idp": headers.get("x-ms-client-principal-idp"),
            "x-ms-client-principal": headers.get("x-ms-client-principal"),
            "x-ms-token-aad-id-token": headers.get("x-ms-token-aad-id-token"),
        }
        forwarded_easy_auth_headers = {k: v for k, v in forwarded_easy_auth_headers.items() if v is not None}

        if forwarded_easy_auth_headers and forwarded_easy_auth_headers.get("x-ms-client-principal-id"):
            user_details: dict[str, Any] = dict(forwarded_easy_auth_headers)
            user_details["is_guest"] = False
            user_details["user_principal_id"] = forwarded_easy_auth_headers.get("x-ms-client-principal-id") or ""
            user_details["user_name"] = forwarded_easy_auth_headers.get("x-ms-client-principal-name") or ""
            user_details["auth_provider"] = forwarded_easy_auth_headers.get("x-ms-client-principal-idp") or ""
        else:
            user_details = get_authenticated_user_details(headers)

        is_guest_value = user_details.get("is_guest")
        is_guest = is_guest_value is True or is_guest_value == "true"

        if is_guest:
            return {
                "id": user_details["user_principal_id"],
                "user_id": user_details["user_principal_id"],
                "sub": user_details["user_principal_id"],
                "name": user_details["user_name"],
                "email": _GUEST_EMAIL,
                "preferred_username": _GUEST_EMAIL,
                "roles": ["guest"],
                "is_guest": True,
            }

        logger.info(f"Authenticated user: {user_details.get('user_name')} ({user_details.get('user_principal_id')})")

        user_email = ""
        client_principal_b64 = user_details.get("client_principal_b64") or user_details.get("x-ms-client-principal")
        if client_principal_b64:
            user_email = get_user_email(client_principal_b64)
        if not user_email:
            user_email = user_details.get("user_name", "")

        return {
            "id": user_details["user_principal_id"],
            "user_id": user_details["user_principal_id"],
            "sub": user_details["user_principal_id"],
            "name": user_details["user_name"],
            "email": user_email,
            "preferred_username": user_email or user_details["user_name"],
            "roles": ["user"],
            "auth_provider": user_details.get("auth_provider"),
            "is_guest": False,
        }

    except Exception as e:
        logger.error(f"Error getting user from Easy Auth headers: {e}", exc_info=True)
        guest_user = get_sample_user()
        return {
            "id": guest_user["user_principal_id"],
            "user_id": guest_user["user_principal_id"],
            "sub": guest_user["user_principal_id"],
            "name": guest_user["user_name"],
            "email": _GUEST_EMAIL,
            "preferred_username": _GUEST_EMAIL,
            "roles": ["guest"],
            "is_guest": True,
        }


async def get_current_user_optional(request: Request) -> dict[str, Any] | None:
    try:
        return await get_current_user(request)
    except Exception:
        return None
