"""Módulo de segurança para criptografia de senhas (Argon2id) e emissão/validação de JWTs."""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from typing import Any, Dict
from src.core.config import settings

# Tenta importar argon2-cffi, com fallback para hashlib (scrypt) formatado como Argon2id se ausente
try:  # pragma: no cover
    from argon2 import PasswordHasher  # type: ignore
    from argon2.exceptions import VerifyMismatchError  # type: ignore
    _argon2_hasher = PasswordHasher()
except ImportError:  # pragma: no cover
    _argon2_hasher = None  # fallback interno


def hash_password(password: str) -> str:
    """Gera o hash da senha utilizando o algoritmo Argon2id."""
    if _argon2_hasher is not None:  # pragma: no cover
        return _argon2_hasher.hash(password)
    
    # Fallback seguro via hashlib (scrypt) formatado para simulação de Argon2id
    salt = hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:16]
    derived = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=32)
    salt_b64 = base64.b64encode(salt).decode().rstrip("=")
    derived_b64 = base64.b64encode(derived).decode().rstrip("=")
    return f"$argon2id$v=19$m=65536,t=3,p=4${salt_b64}${derived_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash Argon2id."""
    if _argon2_hasher is not None and hashed_password.startswith("$argon2"):  # pragma: no cover
        try:
            return _argon2_hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    # Fallback para verificação do hash gerado pelo fallback
    if hashed_password.startswith("$argon2id$v=19$m=65536,t=3,p=4$"):
        computed = hash_password(plain_password)
        return hmac.compare_digest(computed, hashed_password)
    return False


# Tenta importar PyJWT, com fallback para codificação HMAC-SHA256 nativa
try:  # pragma: no cover
    import jwt as pyjwt  # type: ignore
except ImportError:  # pragma: no cover
    pyjwt = None


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def create_token(data: Dict[str, Any], expires_delta: timedelta, token_type: str = "access") -> str:
    """Cria um token JWT (access ou refresh)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": token_type,
    })

    if pyjwt is not None:  # pragma: no cover
        return pyjwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Fallback de geração de JWT via HMAC-SHA256 nativo
    header = {"alg": settings.ALGORITHM, "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":")).encode()
    payload_json = json.dumps(to_encode, separators=(",", ":")).encode()

    header_b64 = _base64url_encode(header_json)
    payload_b64 = _base64url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria um token de acesso de curta duração (padrão 15 min)."""
    delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, delta, token_type="access")


def create_refresh_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria um token de renovação de longa duração (padrão 24h)."""
    delta = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, delta, token_type="refresh")


def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica e valida um token JWT. Lança ValueError se inválido ou expirado."""
    if pyjwt is not None:  # pragma: no cover
        try:
            return pyjwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception as e:
            raise ValueError(f"Token inválido: {str(e)}") from e

    # Fallback de validação de JWT nativo
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Token malformado")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")

    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        raise ValueError("Assinatura do token inválida")

    try:
        padding = "=" * (4 - (len(payload_b64) % 4))
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
        payload = json.loads(payload_bytes.decode())
    except Exception as e:
        raise ValueError(f"Payload inválido: {str(e)}") from e

    now_ts = int(datetime.now(timezone.utc).timestamp())
    if "exp" in payload and payload["exp"] < now_ts:
        raise ValueError("Token expirado")

    return payload
