"""Fixtures do Pytest para isolamento e testes da aplicação."""
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from src.core.database import Base, get_db
from src.core.security import hash_password
from src.domain.models import User
from src.main import app

# Utiliza banco SQLite em memória com StaticPool para compartilhar a mesma instância nos testes de API
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
def db_session():
    """Cria tabelas no banco de dados descartável e fornece uma sessão isolada para cada teste."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def client(db_session: Session):
    """Cliente HTTP assíncrono httpx.AsyncClient para os testes da API FastAPI."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_user(db_session: Session):
    """Fixture auxiliar para criar usuários de teste."""
    def _create_user(
        email: str = "tecnico@empresa.com",
        password: str = "SenhaSegura123!",
        role: str = "tecnico",
        is_active: bool = True,
    ) -> User:
        hashed = hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed,
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user
