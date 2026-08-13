"""Caso de uso para autenticação de usuário com controle de rate limit e auditoria."""
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.core.security import verify_password, create_access_token, create_refresh_token
from src.domain.models import User
from src.infrastructure.repositories import UserRepository, LoginAttemptRepository


class RateLimitExceededException(Exception):
    """Exceção lançada quando o limite de tentativas de login é excedido por IP (HTTP 429)."""
    def __init__(self, message: str = "Acesso temporariamente bloqueado por motivos de segurança devido ao excesso de tentativas malsucedidas."):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsException(Exception):
    """Exceção genérica lançada quando as credenciais fornecidas são inválidas (HTTP 401)."""
    def __init__(self, message: str = "Credenciais de acesso inválidas."):
        self.message = message
        super().__init__(self.message)


class AuthenticateUserUseCase:
    """Caso de uso de autenticação de usuário."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.login_attempt_repo = LoginAttemptRepository(db)

    def execute(self, email: str, password: str, ip_address: str) -> Dict[str, Any]:
        """Executa a validação do login, aplicação de rate limit e emissão de tokens.
        
        Em conformidade com as regras da Constituição:
        - Controla a transação unificada no nível deste caso de uso.
        - Registra a tentativa por IP no banco de dados.
        - Lança exceção de rate limit (429) se houver 10 ou mais falhas nos últimos 15 min.
        - Lança exceção genérica (401) sem expor campo específico se inválido.
        """
        # 1. Verifica taxa de tentativas malsucedidas por IP (RN-02)
        failed_count = self.login_attempt_repo.count_recent_failed_attempts(ip_address, window_minutes=15)
        if failed_count >= 10:
            raise RateLimitExceededException()

        # 2. Busca usuário por email
        user = self.user_repo.get_by_email(email)

        # 3. Valida credenciais (existência de usuário, status ativo e hash da senha)
        is_valid = (
            user is not None
            and user.is_active
            and verify_password(password, user.hashed_password)
        )

        if not is_valid:
            # Registra falha de tentativa por IP e desfaz/confirma a transação
            self.login_attempt_repo.record_attempt(ip_address=ip_address, success=False)
            self.db.commit()
            raise InvalidCredentialsException()

        # 4. Registra sucesso da tentativa de login
        self.login_attempt_repo.record_attempt(ip_address=ip_address, success=True)
        self.db.commit()

        # 5. Gera tokens JWT (Access com claim role + Refresh)
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
