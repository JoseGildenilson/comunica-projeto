"""Testes para utilitários de banco de dados e repositórios."""
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.infrastructure.repositories import UserRepository
from src.domain.models import User


def test_get_db_generator():
    """Testa a injeção de dependência get_db."""
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    # Fecha o gerador
    try:
        next(db_gen)
    except StopIteration:
        pass


def test_user_repository_create_and_get_by_id(db_session: Session, create_test_user):
    """Testa o repositório UserRepository (create e get_by_id)."""
    repo = UserRepository(db_session)
    new_user = User(email="new_repo_user@empresa.com", hashed_password="hash", role="tecnico")

    created = repo.create(new_user)
    db_session.commit()
    assert created.id is not None

    found = repo.get_by_id(created.id)
    assert found is not None
    assert found.email == "new_repo_user@empresa.com"

    not_found = repo.get_by_id(999999)
    assert not_found is None
