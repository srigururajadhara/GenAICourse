import pytest
from fastapi import HTTPException

from app.core.security import resolve_principal, validate_filename


def test_development_api_key_maps_to_local_workspace():
    principal = resolve_principal("Bearer local-dev-key-change-before-deployment")
    assert principal.workspace_id == "local-development"


def test_invalid_api_key_is_rejected():
    with pytest.raises(HTTPException) as error:
        resolve_principal("Bearer incorrect")
    assert error.value.status_code == 401


def test_filename_is_normalized_and_pdf_only():
    assert validate_filename("../../folder/my-file.PDF") == "my-file.PDF"
    with pytest.raises(ValueError):
        validate_filename("../../secret.txt")


def test_oidc_module_imports():
    from app.core.oidc import verify_access_token

    assert callable(verify_access_token)


from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core import oidc


@pytest.fixture
def oidc_test_keys(monkeypatch):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    class FakeJwksClient:
        def get_signing_key_from_jwt(self, token):
            return SimpleNamespace(key=private_key.public_key())

    monkeypatch.setattr(
        oidc,
        "_jwks_client",
        lambda url: FakeJwksClient(),
    )
    return private_key


def make_test_token(private_key, **overrides):
    now = datetime.now(timezone.utc)

    claims = {
        "sub": "test-user-123",
        "iss": "https://keycloak.example.com/realms/guru",
        "aud": "guru-api",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    claims.update(overrides)

    return jwt.encode(claims, private_key, algorithm="RS256")


def test_valid_oidc_token_is_accepted(oidc_test_keys):
    token = make_test_token(oidc_test_keys)

    claims = oidc.verify_access_token(
        token,
        "https://keycloak.example.com/realms/guru",
        "guru-api",
        "https://keycloak.example.com/realms/guru/protocol/openid-connect/certs",
    )

    assert claims["sub"] == "test-user-123"


def test_wrong_audience_is_rejected(oidc_test_keys):
    token = make_test_token(oidc_test_keys)

    with pytest.raises(jwt.InvalidAudienceError):
        oidc.verify_access_token(
            token,
            "https://keycloak.example.com/realms/guru",
            "wrong-api",
            "https://keycloak.example.com/realms/guru/protocol/openid-connect/certs",
        )


def test_wrong_issuer_is_rejected(oidc_test_keys):
    token = make_test_token(oidc_test_keys)

    with pytest.raises(jwt.InvalidIssuerError):
        oidc.verify_access_token(
            token,
            "https://wrong.example.com/realms/guru",
            "guru-api",
            "https://keycloak.example.com/realms/guru/protocol/openid-connect/certs",
        )


def test_expired_token_is_rejected(oidc_test_keys):
    token = make_test_token(
        oidc_test_keys,
        exp=datetime.now(timezone.utc) - timedelta(minutes=5),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        oidc.verify_access_token(
            token,
            "https://keycloak.example.com/realms/guru",
            "guru-api",
            "https://keycloak.example.com/realms/guru/protocol/openid-connect/certs",
        )


def test_invalid_signature_is_rejected(oidc_test_keys):
    another_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    token = make_test_token(another_key)

    with pytest.raises(jwt.InvalidSignatureError):
        oidc.verify_access_token(
            token,
            "https://keycloak.example.com/realms/guru",
            "guru-api",
            "https://keycloak.example.com/realms/guru/protocol/openid-connect/certs",
        )


from types import SimpleNamespace
from app.core import security


def test_oidc_authentication_returns_user_workspace(monkeypatch):
    monkeypatch.setattr(
        security,
        "settings",
        SimpleNamespace(
            auth_mode="oidc",
            keycloak_issuer="https://keycloak.example.com/realms/guru",
            keycloak_audience="guru-api",
            keycloak_jwks_url="https://keycloak.example.com/certs",
        ),
    )

    monkeypatch.setattr(
        security,
        "verify_access_token",
        lambda *args: {
            "sub": "user-001",
            "email": "user@example.invalid",
            "name": "Guru Test User",
        },
    )

    monkeypatch.setattr(
        security,
        "get_or_create_user_workspace",
        lambda **kwargs: "workspace-user-001",
    )

    principal = security.resolve_principal("Bearer mocked-token")

    assert principal.workspace_id == "workspace-user-001"


def test_different_oidc_users_receive_separate_workspaces(monkeypatch):
    monkeypatch.setattr(
        security,
        "settings",
        SimpleNamespace(
            auth_mode="oidc",
            keycloak_issuer="https://keycloak.example.com/realms/guru",
            keycloak_audience="guru-api",
            keycloak_jwks_url="https://keycloak.example.com/certs",
        ),
    )

    identities = {
        "token-user-a": {
            "sub": "user-a",
            "email": "a@example.invalid",
        },
        "token-user-b": {
            "sub": "user-b",
            "email": "b@example.invalid",
        },
    }

    workspaces = {
        "user-a": "workspace-a",
        "user-b": "workspace-b",
    }

    monkeypatch.setattr(
        security,
        "verify_access_token",
        lambda token, *args: identities[token],
    )

    monkeypatch.setattr(
        security,
        "get_or_create_user_workspace",
        lambda **kwargs: workspaces[kwargs["keycloak_sub"]],
    )

    principal_a = security.resolve_principal("Bearer token-user-a")
    principal_b = security.resolve_principal("Bearer token-user-b")

    assert principal_a.workspace_id == "workspace-a"
    assert principal_b.workspace_id == "workspace-b"
    assert principal_a.workspace_id != principal_b.workspace_id


def test_invalid_oidc_token_is_rejected(monkeypatch):
    import jwt
    import pytest
    from fastapi import HTTPException

    monkeypatch.setattr(
        security,
        "settings",
        SimpleNamespace(
            auth_mode="oidc",
            keycloak_issuer="https://keycloak.example.com/realms/guru",
            keycloak_audience="guru-api",
            keycloak_jwks_url="https://keycloak.example.com/certs",
        ),
    )

    def reject_token(*args):
        raise jwt.InvalidTokenError("Invalid test token")

    monkeypatch.setattr(security, "verify_access_token", reject_token)

    with pytest.raises(HTTPException) as error:
        security.resolve_principal("Bearer invalid-token")

    assert error.value.status_code == 401
