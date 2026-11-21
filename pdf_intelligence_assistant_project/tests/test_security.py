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
