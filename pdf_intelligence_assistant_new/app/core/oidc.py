from __future__ import annotations

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient


@lru_cache(maxsize=8)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(
        jwks_url,
        cache_keys=True,
        lifespan=300,
        timeout=5,
    )


def verify_access_token(
    token: str,
    issuer: str,
    audience: str,
    jwks_url: str,
) -> dict[str, Any]:
    """Verify a Keycloak access token and return its trusted claims."""

    if not all([token, issuer, audience, jwks_url]):
        raise ValueError("OIDC authentication configuration is incomplete")

    if len(token) > 16384:
        raise ValueError("Access token is too large")

    signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=issuer,
        audience=audience,
        leeway=30,
        options={
            "require": ["exp", "iat", "sub", "iss", "aud"],
        },
    )

    if not isinstance(claims.get("sub"), str) or not claims["sub"].strip():
        raise jwt.InvalidTokenError("Token subject is missing")

    return claims
