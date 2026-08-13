"""Repositórios SQLAlchemy para persistência de dados.

Nota: Em cumprimento à Constituição, os repositórios NÃO executam commit ou rollback.
O controle de transação é feito no nível do caso de uso ou rota HTTP.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from src.domain.models import User, LoginAttempt, Ticket, Equipment


class DashboardRepository:
    """Repositório para consulta de métricas e indicadores do Dashboard."""

    def __init__(self, db: Session):
        self.db = db

    def count_tickets_by_status(self, status: str, user_id: int | None = None) -> int:
        """Conta a quantidade de tickets com determinado status (global ou por usuário)."""
        stmt = select(func.count(Ticket.id)).where(Ticket.status == status)
        if user_id is not None:
            stmt = stmt.where(Ticket.created_by_id == user_id)
        count = self.db.execute(stmt).scalar()
        return count or 0

    def count_total_equipments(self) -> int:
        """Conta a quantidade total de equipamentos cadastrados."""
        stmt = select(func.count(Equipment.id))
        count = self.db.execute(stmt).scalar()
        return count or 0


class UserRepository:
    """Repositório de acesso a dados da entidade User."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Busca usuário por email."""
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        """Busca usuário por ID."""
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User) -> User:
        """Adiciona novo usuário à sessão (sem commit)."""
        self.db.add(user)
        return user


class LoginAttemptRepository:
    """Repositório de registro e contagem de tentativas de login por IP."""

    def __init__(self, db: Session):
        self.db = db

    def count_recent_failed_attempts(self, ip_address: str, window_minutes: int = 15) -> int:
        """Conta tentativas malsucedidas de um IP na janela de tempo especificada."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        stmt = (
            select(func.count(LoginAttempt.id))
            .where(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.success.is_(False),
                LoginAttempt.attempted_at >= cutoff_time,
            )
        )
        count = self.db.execute(stmt).scalar()
        return count or 0

    def record_attempt(self, ip_address: str, success: bool) -> LoginAttempt:
        """Registra uma nova tentativa de login para um IP (sem commit)."""
        attempt = LoginAttempt(
            ip_address=ip_address,
            success=success,
            attempted_at=datetime.now(timezone.utc),
        )
        self.db.add(attempt)
        return attempt
