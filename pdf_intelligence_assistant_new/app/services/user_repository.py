from __future__ import annotations

import os
from uuid import uuid4

import psycopg
from psycopg.conninfo import make_conninfo


def _connect():
    """Connect to the private PostgreSQL authentication database."""
    required = ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            "PostgreSQL configuration is incomplete: " + ", ".join(missing)
        )

    conninfo = make_conninfo(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=5,
        application_name="guru-user-repository",
    )
    return psycopg.connect(conninfo)


def get_or_create_user_workspace(
    keycloak_sub: str,
    email: str | None = None,
    display_name: str | None = None,
) -> str:
    """Return the persistent workspace assigned to a verified Keycloak user."""

    if not isinstance(keycloak_sub, str) or not keycloak_sub.strip():
        raise ValueError("A valid Keycloak subject is required")

    keycloak_sub = keycloak_sub.strip()

    if len(keycloak_sub) > 255:
        raise ValueError("Keycloak subject is too long")

    if email is not None and len(email) > 320:
        raise ValueError("Email address is too long")

    if display_name is not None and len(display_name) > 255:
        raise ValueError("Display name is too long")

    new_workspace_id = uuid4().hex
    new_user_id = uuid4()

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT workspace_id
                FROM users
                WHERE keycloak_sub = %s
                """,
                (keycloak_sub,),
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE users
                    SET email = COALESCE(%s, email),
                        display_name = COALESCE(%s, display_name),
                        updated_at = NOW()
                    WHERE keycloak_sub = %s
                    RETURNING workspace_id
                    """,
                    (email, display_name, keycloak_sub),
                )
                return cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO workspaces (workspace_id)
                VALUES (%s)
                """,
                (new_workspace_id,),
            )

            cursor.execute(
                """
                INSERT INTO users (
                    user_id,
                    keycloak_sub,
                    email,
                    display_name,
                    workspace_id
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (keycloak_sub)
                DO UPDATE SET
                    email = COALESCE(EXCLUDED.email, users.email),
                    display_name = COALESCE(
                        EXCLUDED.display_name, users.display_name
                    ),
                    updated_at = NOW()
                RETURNING workspace_id
                """,
                (
                    new_user_id,
                    keycloak_sub,
                    email,
                    display_name,
                    new_workspace_id,
                ),
            )

            assigned_workspace_id = cursor.fetchone()[0]

            # A simultaneous first login may have created the user first.
            # Remove this transaction's unused workspace in that case.
            if assigned_workspace_id != new_workspace_id:
                cursor.execute(
                    """
                    DELETE FROM workspaces
                    WHERE workspace_id = %s
                    """,
                    (new_workspace_id,),
                )

            return assigned_workspace_id
