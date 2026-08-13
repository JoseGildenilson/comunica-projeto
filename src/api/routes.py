"""Rotas da API de Autenticação."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from src.api.dependencies import get_current_user
from src.core.config import settings
from src.core.database import get_db
from src.core.security import decode_token, create_access_token
from src.domain.models import User
from src.domain.schemas import LoginRequest, TokenResponse, UserResponse, MessageResponse
from src.infrastructure.repositories import UserRepository
from src.use_cases.authenticate_user import (
    AuthenticateUserUseCase,
    InvalidCredentialsException,
    RateLimitExceededException,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


def _extract_client_ip(request: Request) -> str:
    """Extrai o IP do cliente considerando os cabeçalhos de proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": MessageResponse, "description": "Credenciais inválidas"},
        429: {"model": MessageResponse, "description": "Bloqueado por excesso de tentativas (Rate Limit)"},
    },
)
def login(
    request_data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Endpoint HTTP para login de usuários."""
    ip_address = _extract_client_ip(request)
    use_case = AuthenticateUserUseCase(db)

    try:
        result = use_case.execute(
            email=request_data.email,
            password=request_data.password,
            ip_address=ip_address,
        )
    except RateLimitExceededException as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
        )
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )

    access_token = result["access_token"]
    refresh_token = result["refresh_token"]

    # Define os cookies HttpOnly
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(result["user"]),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Endpoint HTTP para renovar o access_token utilizando o refresh_token enviado via Cookie."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ausente.",
        )

    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token inválido.",
        )

    user_id = int(payload.get("sub", "0"))
    user = UserRepository(db).get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou não encontrado.",
        )

    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
def logout(response: Response):
    """Endpoint HTTP para encerrar a sessão limpando os cookies HttpOnly."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return MessageResponse(message="Logout realizado com sucesso.")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_me(current_user: User = Depends(get_current_user)):
    """Endpoint de rota protegida que retorna as informações do usuário autenticado."""
    return UserResponse.model_validate(current_user)
