"""Testes unitários para os serviços de segurança, Argon2id e JWT."""
from datetime import timedelta
import base64
import pytest
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    create_token,
    _base64url_encode,
)


def test_password_hashing_and_verification():
    """Testa a geração de hash Argon2id e a verificação de senhas corretas e incorretas."""
    password = "MinhaSenhaSuperSegura123!"
    hashed = hash_password(password)

    assert hashed is not None
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("SenhaIncorreta", hashed) is False
    assert verify_password(password, "hash_invalido_corrompido") is False


def test_jwt_access_token_lifecycle():
    """Testa a geração e decodificação de access token JWT."""
    payload = {"sub": "1", "email": "tecnico@empresa.com", "role": "tecnico"}
    token = create_access_token(data=payload)

    assert isinstance(token, str)
    decoded = decode_token(token)

    assert decoded["sub"] == "1"
    assert decoded["email"] == "tecnico@empresa.com"
    assert decoded["role"] == "tecnico"
    assert decoded["type"] == "access"
    assert "exp" in decoded
    assert "iat" in decoded


def test_jwt_refresh_token_lifecycle():
    """Testa a geração e decodificação de refresh token JWT."""
    payload = {"sub": "1"}
    token = create_refresh_token(data=payload)

    assert isinstance(token, str)
    decoded = decode_token(token)

    assert decoded["sub"] == "1"
    assert decoded["type"] == "refresh"


def test_jwt_expired_token():
    """Testa a rejeição de tokens expirados."""
    payload = {"sub": "1"}
    # Token expirado há 10 segundos
    token = create_token(data=payload, expires_delta=timedelta(seconds=-10), token_type="access")

    with pytest.raises(ValueError, match="expirado"):
        decode_token(token)


def test_jwt_invalid_token_format_or_signature():
    """Testa a decodificação de tokens com formato ou assinatura inválida."""
    with pytest.raises(ValueError, match="malformado"):
        decode_token("token_invalido_sem_pontos")

    with pytest.raises(ValueError, match="Assinatura"):
        decode_token("header.payload.assinatura_falsa")


def test_jwt_invalid_payload_json():
    """Testa o tratamento de exceção em tokens com payload corrompido/não-JSON."""
    import hmac, hashlib
    from src.core.config import settings

    header_b64 = _base64url_encode(b'{"alg":"HS256","typ":"JWT"}')
    invalid_payload_b64 = _base64url_encode(b"not_a_json_string")
    signing_input = f"{header_b64}.{invalid_payload_b64}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    bad_token = f"{header_b64}.{invalid_payload_b64}.{sig_b64}"

    with pytest.raises(ValueError, match="Payload inválido"):
        decode_token(bad_token)
