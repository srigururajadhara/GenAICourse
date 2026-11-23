from __future__ import annotations

import re
import secrets
from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.core.oidc import verify_access_token
from app.services.user_repository import get_or_create_user_workspace

import jwt
from jwt import PyJWKClientError


@dataclass(frozen=True)
class Principal:
    workspace_id: str


def resolve_principal(authorization: str | None) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
        )

    supplied = authorization.removeprefix("Bearer ").strip()

    if settings.auth_mode == "api_key":
        try:
            key_map = settings.api_key_map()
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=500,
                detail="Authentication configuration is invalid",
            ) from exc

        for configured_key, workspace_id in key_map.items():
            if secrets.compare_digest(supplied, configured_key):
                return Principal(workspace_id=workspace_id)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    if settings.auth_mode != "oidc":
        raise HTTPException(
            status_code=500,
            detail="Unsupported authentication mode",
        )

    try:
        claims = verify_access_token(
            supplied,
            settings.keycloak_issuer,
            settings.keycloak_audience,
            settings.keycloak_jwks_url,
        )
    except PyJWKClientError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity provider signing keys are unavailable",
        ) from exc
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from exc

    try:
        workspace_id = get_or_create_user_workspace(
            keycloak_sub=claims["sub"],
            email=claims.get("email"),
            display_name=claims.get("name"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User workspace service is temporarily unavailable",
        ) from exc

    return Principal(workspace_id=workspace_id)


def get_principal(authorization: str | None = Header(default=None)) -> Principal:
    return resolve_principal(authorization)


INJECTION_PATTERNS = [
    re.compile(r"\b(ignore|disregard|override)\b.{0,80}\b(system|developer|previous|above)\b", re.I),
    re.compile(r"\b(reveal|print|show)\b.{0,50}\b(system prompt|secret key|api key|credentials)\b", re.I),
    re.compile(r"\b(access|read|retrieve)\b.{0,50}\b(other users?|another workspace|other documents?)\b", re.I),
]


def is_suspicious_question(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def validate_filename(filename: str) -> str:
    # Do not preserve directory components supplied by the client.
    name = filename.replace("\\", "/").split("/")[-1].strip()
    if not name or len(name) > 180 or not name.lower().endswith(".pdf"):
        raise ValueError("Only PDF files with a valid .pdf filename are accepted")
    return name
