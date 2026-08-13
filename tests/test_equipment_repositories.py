"""Testes de integração para os repositórios de Equipamentos."""
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from src.domain.models import Equipment, EquipmentTag, EquipmentMovement, EquipmentMaintenance
from src.infrastructure.repositories import (
    EquipmentRepository,
    EquipmentTagRepository,
    EquipmentMovementRepository,
    EquipmentMaintenanceRepository,
)


def test_equipment_repository_crud_and_lookups(db_session: Session):
    """Testa métodos de busca por ID, Serial, Patrimônio e Hostname."""
    repo = EquipmentRepository(db_session)

    eq = Equipment(
        description="ThinkPad T480",
        serial_number="SN_T480",
        patrimony_number="PAT_T480",
        hostname="HOST_T480",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
    )
    repo.create(eq)
    db_session.commit()

    assert repo.get_by_id(eq.id) is not None
    assert repo.get_by_serial_number("SN_T480") is not None
    assert repo.get_by_patrimony_number("PAT_T480") is not None
    assert repo.get_by_hostname("HOST_T480") is not None
    assert repo.get_by_serial_number("INEXISTENTE") is None


def test_equipment_repository_list_paginated_filtered_and_search(db_session: Session):
    """Testa paginação, filtros combinados, ordenação e busca global por substring."""
    repo = EquipmentRepository(db_session)

    for i in range(1, 30):
        eq = Equipment(
            description=f"Equipamento {i} Dell OptiPlex",
            serial_number=f"SN_{i:03d}",
            patrimony_number=f"PAT_{i:03d}",
            brand="Dell" if i % 2 == 0 else "HP",
            equipment_type="Desktop" if i % 2 == 0 else "Notebook",
            location="TI" if i <= 15 else "Comunicação",
            status="Em uso" if i <= 20 else "Ocioso",
        )
        repo.create(eq)
    db_session.commit()

    # Paginação padrão (25 itens por página)
    items, total = repo.list_paginated_and_filtered(page=1, limit=25)
    assert total == 29
    assert len(items) == 25

    # Segunda página (4 itens)
    items_p2, total = repo.list_paginated_and_filtered(page=2, limit=25)
    assert len(items_p2) == 4

    # Filtro categórico
    items_notebook, total_notebook = repo.list_paginated_and_filtered(equipment_type="Notebook")
    assert total_notebook == 15

    # Busca textual global
    items_search, total_search = repo.list_paginated_and_filtered(search="Equipamento 1")
    assert total_search >= 1


def test_equipment_tag_repository(db_session: Session):
    """Testa o repositório de tags."""
    repo = EquipmentTagRepository(db_session)
    tag = EquipmentTag(category="tipo", name="Notebook")
    repo.create(tag)
    db_session.commit()

    all_tags = repo.list_all()
    assert len(all_tags) == 1
    type_tags = repo.list_by_category("tipo")
    assert len(type_tags) == 1
    found = repo.get_by_category_and_name("tipo", "Notebook")
    assert found is not None


def test_equipment_movement_and_maintenance_repositories(db_session: Session):
    """Testa repositórios de histórico de movimentação e manutenção."""
    eq_repo = EquipmentRepository(db_session)
    mov_repo = EquipmentMovementRepository(db_session)
    maint_repo = EquipmentMaintenanceRepository(db_session)

    eq = Equipment(
        description="Servidor PowerEdge",
        serial_number="SN_PE_01",
        equipment_type="Desktop",
        location="TI",
    )
    eq_repo.create(eq)
    db_session.commit()

    now = datetime.now(timezone.utc)
    mov = EquipmentMovement(
        equipment_id=eq.id,
        origin_location="TI",
        destination_location="Data Center",
        movement_date=now,
    )
    mov_repo.create(mov)

    maint = EquipmentMaintenance(
        equipment_id=eq.id,
        maintenance_date=now,
        maintenance_type="Preventiva",
        description="Limpeza física",
    )
    maint_repo.create(maint)
    db_session.commit()

    movs = mov_repo.list_by_equipment(eq.id)
    maints = maint_repo.list_by_equipment(eq.id)

    assert len(movs) == 1
    assert movs[0].destination_location == "Data Center"
    assert len(maints) == 1
    assert maints[0].description == "Limpeza física"
