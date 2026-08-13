"""Testes automatizados da funcionalidade de Dashboard (repositório, use case e API)."""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from src.core.security import create_access_token
from src.domain.models import Ticket, Equipment
from src.infrastructure.repositories import DashboardRepository
from src.use_cases.get_dashboard_metrics import GetDashboardMetricsUseCase


@pytest.fixture
def seed_dashboard_data(db_session: Session, create_test_user):
    """Fixture para criar dados de teste para o dashboard."""
    tecnico = create_test_user(email="tecnico_dash@empresa.com", role="tecnico")
    colaborador = create_test_user(email="colaborador_dash@empresa.com", role="colaborador")

    equipments = [
        Equipment(name="Note 1", status="disponível"),
        Equipment(name="Monitor 1", status="em_uso"),
    ]
    db_session.add_all(equipments)

    tickets = [
        Ticket(title="Ticket Colab Pendente", status="pendente", created_by_id=colaborador.id),
        Ticket(title="Ticket Colab Andamento", status="em_andamento", created_by_id=colaborador.id),
        Ticket(title="Ticket Tec Pendente", status="pendente", created_by_id=tecnico.id),
    ]
    db_session.add_all(tickets)
    db_session.commit()

    return {"tecnico": tecnico, "colaborador": colaborador}


def test_dashboard_repository(db_session: Session, seed_dashboard_data):
    repo = DashboardRepository(db_session)

    # Globais
    assert repo.count_tickets_by_status("pendente") == 2
    assert repo.count_tickets_by_status("em_andamento") == 1
    assert repo.count_total_equipments() == 2

    # Por usuário
    colab = seed_dashboard_data["colaborador"]
    assert repo.count_tickets_by_status("pendente", user_id=colab.id) == 1
    assert repo.count_tickets_by_status("em_andamento", user_id=colab.id) == 1

    tec = seed_dashboard_data["tecnico"]
    assert repo.count_tickets_by_status("pendente", user_id=tec.id) == 1
    assert repo.count_tickets_by_status("em_andamento", user_id=tec.id) == 0


def test_dashboard_use_case_tecnico(db_session: Session, seed_dashboard_data):
    tec = seed_dashboard_data["tecnico"]
    use_case = GetDashboardMetricsUseCase(db_session)
    response = use_case.execute(user_id=tec.id, role=tec.role)

    assert response.tickets_pending == 2
    assert response.tickets_in_progress == 1
    assert response.equipments_total == 2


def test_dashboard_use_case_colaborador(db_session: Session, seed_dashboard_data):
    colab = seed_dashboard_data["colaborador"]
    use_case = GetDashboardMetricsUseCase(db_session)
    response = use_case.execute(user_id=colab.id, role=colab.role)

    assert response.tickets_pending == 1
    assert response.tickets_in_progress == 1
    assert response.equipments_total is None


@pytest.mark.anyio
async def test_dashboard_api_tecnico(client: AsyncClient, seed_dashboard_data):
    tec = seed_dashboard_data["tecnico"]
    token = create_access_token({"sub": str(tec.id), "email": tec.email, "role": tec.role})

    client.cookies.set("access_token", token)
    response = await client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["tickets_pending"] == 2
    assert data["tickets_in_progress"] == 1
    assert data["equipments_total"] == 2


@pytest.mark.anyio
async def test_dashboard_api_colaborador(client: AsyncClient, seed_dashboard_data):
    colab = seed_dashboard_data["colaborador"]
    token = create_access_token({"sub": str(colab.id), "email": colab.email, "role": colab.role})

    client.cookies.set("access_token", token)
    response = await client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["tickets_pending"] == 1
    assert data["tickets_in_progress"] == 1
    assert data["equipments_total"] is None


@pytest.mark.anyio
async def test_dashboard_api_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 401
