from __future__ import annotations

from uuid import uuid4

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.repositories.common import as_string_list


def test_as_string_list_preserves_order_and_deduplicates() -> None:
    first = uuid4()
    second = uuid4()

    result = as_string_list([first, second, first, None, str(second)])

    assert result == [str(first), str(second)]


def test_security_helpers_hash_and_decode_token(test_settings) -> None:
    password = "super-secret"
    encoded_password = get_password_hash(password)

    assert verify_password(password, encoded_password) is True
    assert verify_password("wrong-password", encoded_password) is False

    token = create_access_token(subject="user-id", settings=test_settings)
    payload = decode_access_token(token, test_settings)

    assert payload["sub"] == "user-id"
    assert payload["type"] == "access"
