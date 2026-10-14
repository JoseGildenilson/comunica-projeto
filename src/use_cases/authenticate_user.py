"""Caso de uso para autenticação de usuário com controle de rate limit e auditoria."""

from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.security import verify_password, create_access_token, create_refresh_token
from src.domain.models import User
from src.infrastructure.repositories import UserRepository, LoginAttemptRepository


class RateLimitExceededException(Exception):
    """Exceção lançada quando o limite de tentativas de login é excedido por IP (HTTP 429)."""

    def __init__(
        self,
        message: str = "Acesso temporariamente bloqueado por motivos de segurança devido ao excesso de tentativas malsucedidas.",
    ):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsException(Exception):
    """Exceção genérica lançada quando as credenciais fornecidas são inválidas (HTTP 401)."""

    def __init__(self, message: str = "Credenciais de acesso inválidas."):
        self.message = message
        super().__init__(self.message)


class AuthenticateUserUseCase:
    """Caso de uso de autenticação de usuário com auditoria por email_attempted e IP."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.login_attempt_repo = LoginAttemptRepository(db)

    def execute(self, email: str, password: str, ip_address: str) -> Dict[str, Any]:
        """Executa validação, rate limiting e auditoria no login.

        Em conformidade com a Constituição e RN-REF-03 / RN-REF-04:
        - Bloqueia IP com 10 ou mais falhas nos últimos 15 minutos.
        - Busca usuário de forma case-insensitive e valida deleted_at IS NULL e is_active.
        - Grava email_attempted e ip_address na tabela login_attempts sem armazenar a senha.
        - Controla transação unificada.
        """
        # 1. Verifica taxa de tentativas malsucedidas por IP
        failed_count = self.login_attempt_repo.count_recent_failed_attempts(
            ip_address, window_minutes=15
        )
        if failed_count >= 10:
            raise RateLimitExceededException()

        # 2. Busca usuário por email (case-insensitive e deleted_at IS NULL)
        user = self.user_repo.get_by_email(email)

        # 3. Valida credenciais (existência do usuário, ativo, não deletado e senha correta)
        is_valid = (
            user is not None
            and user.is_active
            and user.deleted_at is None
            and verify_password(password, user.hashed_password)
        )

        if not is_valid:
            # Registra falha de tentativa para auditoria sem expor credenciais
            self.login_attempt_repo.record_attempt(
                ip_address=ip_address,
                email_attempted=email,
                success=False,
            )
            self.db.commit()
            raise InvalidCredentialsException()

        # 4. Registra sucesso da tentativa de login
        self.login_attempt_repo.record_attempt(
            ip_address=ip_address,
            email_attempted=email,
            success=True,
        )
        self.db.commit()

        # 5. Gera tokens JWT
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
