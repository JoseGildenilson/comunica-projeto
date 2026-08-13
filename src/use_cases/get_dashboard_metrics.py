"""Caso de uso para consulta das métricas do Dashboard baseando-se no papel (role) do usuário."""
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.domain.schemas import DashboardMetricsResponse
from src.infrastructure.repositories import DashboardRepository


class GetDashboardMetricsUseCase:
    """Caso de uso para obter métricas consolidada para a tela inicial do Dashboard."""

    def __init__(self, db: Session):
        self.db = db
        self.dashboard_repo = DashboardRepository(db)

    def execute(self, user_id: int, role: str) -> DashboardMetricsResponse:
        """Executa a consulta de métricas de acordo com a role do usuário.

        - Role 'tecnico': busca contagens globais de tickets e total de equipamentos.
        - Role 'colaborador' (ou outras): busca contagens filtradas apenas pelo user_id do criador e omite equipamentos.
        """
        if role == "tecnico":
            tickets_pending = self.dashboard_repo.count_tickets_by_status(status="pendente")
            tickets_in_progress = self.dashboard_repo.count_tickets_by_status(status="em_andamento")
            equipments_total = self.dashboard_repo.count_total_equipments()
            return DashboardMetricsResponse(
                tickets_pending=tickets_pending,
                tickets_in_progress=tickets_in_progress,
                equipments_total=equipments_total,
            )

        # Visão de colaborador
        tickets_pending = self.dashboard_repo.count_tickets_by_status(status="pendente", user_id=user_id)
        tickets_in_progress = self.dashboard_repo.count_tickets_by_status(status="em_andamento", user_id=user_id)
        return DashboardMetricsResponse(
            tickets_pending=tickets_pending,
            tickets_in_progress=tickets_in_progress,
            equipments_total=None,
        )
