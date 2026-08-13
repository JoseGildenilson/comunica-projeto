"""Testes unitários para validação dos schemas Pydantic de Equipamentos."""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from src.domain.schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentTagCreate,
    EquipmentMovementCreate,
    EquipmentMaintenanceCreate,
    EquipmentListResponse,
)


def test_equipment_create_schema_valid():
    """Testa criação válida do schema EquipmentCreate com campos obrigatórios."""
    data = EquipmentCreate(
        serial_number="SN12345",
        description="OptiPlex 7090",
        equipment_type="Desktop",
        location="TI",
    )
    assert data.serial_number == "SN12345"
    assert data.status == "Em uso"
    assert data.patrimony_number is None


def test_equipment_create_schema_missing_required():
    """Testa falha de validação ao omitir campos obrigatórios."""
    with pytest.raises(ValidationError):
        EquipmentCreate(
            description="Faltando serial_number, type, location",
        )


def test_equipment_tag_and_movement_schemas():
    """Testa schemas de Tag, Movimentação e Manutenção."""
    tag = EquipmentTagCreate(category="tipo", name="Notebook")
    assert tag.category == "tipo"

    now = datetime.now(timezone.utc)
    mov = EquipmentMovementCreate(
        origin_location="TI",
        destination_location="Rádio Produção",
        movement_date=now,
    )
    assert mov.destination_location == "Rádio Produção"

    maint = EquipmentMaintenanceCreate(
        maintenance_date=now,
        maintenance_type="Preventiva",
        description="Troca de SSD",
    )
    assert maint.description == "Troca de SSD"


def test_equipment_list_response_schema():
    """Testa o schema de resposta paginada EquipmentListResponse."""
    now = datetime.now(timezone.utc)
    eq_resp = EquipmentResponse(
        id=1,
        serial_number="SN001",
        description="Desk 01",
        equipment_type="Desktop",
        location="TI",
        status="Em uso",
        created_at=now,
        movements=[],
        maintenances=[],
    )
    list_resp = EquipmentListResponse(
        items=[eq_resp],
        total=1,
        page=1,
        limit=25,
        pages=1,
    )
    assert list_resp.total == 1
    assert len(list_resp.items) == 1
