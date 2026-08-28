import pytest
from app.security.passwords import get_password_hash, verify_password
from app.security.tokens import create_access_token, decode_access_token


def test_password_hashing():
    raw = "StrongPassword123!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    data = {"sub": "12345-uuid", "email": "test@example.edu", "role": "student"}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "12345-uuid"
    assert payload["email"] == "test@example.edu"
    assert payload["role"] == "student"
