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
    """Testa todos os métodos do repositório de tags."""
    repo = EquipmentTagRepository(db_session)
    eq_repo = EquipmentRepository(db_session)

    # Criação
    tag = EquipmentTag(category="tipo", name="Notebook")
    repo.create(tag)
    loc_tag = EquipmentTag(category="localizacao", name="TI")
    repo.create(loc_tag)
    status_tag = EquipmentTag(category="situacao", name="Em uso")
    repo.create(status_tag)
    db_session.commit()

    # Listagens e buscas
    all_tags = repo.list_all()
    assert len(all_tags) == 3
    type_tags = repo.list_by_category("tipo")
    assert len(type_tags) == 1
    found = repo.get_by_category_and_name("tipo", "Notebook")
    assert found is not None
    assert repo.get_by_id(tag.id) is not None
    assert repo.get_by_id(99999) is None

    # Propagação de renomeação nos 3 campos
    eq = Equipment(
        description="Equipamento teste repo tag",
        serial_number="SN-TAG-REPO-1",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
    )
    eq_repo.create(eq)
    db_session.commit()

    repo.propagate_tag_rename("tipo", "Notebook", "Laptop")
    repo.propagate_tag_rename("localizacao", "TI", "Suporte")
    repo.propagate_tag_rename("situacao", "Em uso", "Operando")
    repo.propagate_tag_rename("outra_categoria", "A", "B")  # categoria sem efeito
    db_session.commit()
    db_session.refresh(eq)

    assert eq.equipment_type == "Laptop"
    assert eq.location == "Suporte"
    assert eq.status == "Operando"

    # Exclusão
    repo.delete(tag)
    db_session.commit()
    assert repo.get_by_id(tag.id) is None



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


def test_equipment_repository_get_distinct_values_by_prefix(db_session: Session):
    """Testa busca de sugestões distintas por prefixo com ordenação e limite."""
    repo = EquipmentRepository(db_session)

    # Cria equipamentos com diferentes prefixos e campos nulos
    equipments_data = [
        ("Notebook A", "SN_ABC_01", "PAT_100", "PROD_X1"),
        ("Notebook B", "SN_ABC_02", "PAT_101", "PROD_X2"),
        ("Notebook C", "SN_XYZ_01", "PAT_200", None),
        ("Notebook D", "SN_abc_03", "pat_102", "PROD_X1"),  # duplicado em produto, case diferente
        ("Desktop E", "SN_DEF_01", None, "PROD_Y1"),
    ]

    for desc, sn, pat, prod in equipments_data:
        eq = Equipment(
            description=desc,
            serial_number=sn,
            patrimony_number=pat,
            product_number=prod,
            equipment_type="Notebook",
            location="TI",
        )
        repo.create(eq)
    db_session.commit()

    # Busca prefixo 'pat_' (case-insensitive)
    pats = repo.get_distinct_values_by_prefix("patrimony_number", "pat", limit=10)
    assert len(pats) == 4
    assert "PAT_100" in pats
    assert "PAT_101" in pats
    assert "PAT_200" in pats
    assert "pat_102" in pats


    # Busca com limite menor
    pats_limited = repo.get_distinct_values_by_prefix("patrimony_number", "PAT", limit=2)
    assert len(pats_limited) == 2

    # Busca prefixo serial_number
    serials = repo.get_distinct_values_by_prefix("serial_number", "sn_abc", limit=10)
    assert len(serials) == 3

    # Busca prefixo product_number (valores distintos)
    products = repo.get_distinct_values_by_prefix("product_number", "PROD", limit=10)
    assert len(products) == 3  # PROD_X1, PROD_X2, PROD_Y1
    assert "PROD_X1" in products

    # Campo inválido retorna lista vazia
    invalid = repo.get_distinct_values_by_prefix("campo_inexistente", "teste")
    assert invalid == []


def test_equipment_repository_list_all_filtered(db_session: Session):
    """Testa busca completa não paginada list_all_filtered."""
    repo = EquipmentRepository(db_session)
    eq1 = Equipment(
        description="Notebook Dell XPS",
        serial_number="SN_XPS_01",
        patrimony_number="PAT_XPS_01",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
    )
    eq2 = Equipment(
        description="Desktop HP ProDesk",
        serial_number="SN_HP_01",
        patrimony_number="PAT_HP_01",
        equipment_type="Desktop",
        location="RH",
        status="Disponível",
    )
    repo.create(eq1)
    repo.create(eq2)
    db_session.commit()

    all_items = repo.list_all_filtered()
    assert len(all_items) >= 2

    # Filtrado por tipo e localizacao
    filtered = repo.list_all_filtered(equipment_type=["Notebook"], location=["TI"])
    assert len(filtered) == 1
    assert filtered[0].serial_number == "SN_XPS_01"

    # Ordenação asc
    ordered = repo.list_all_filtered(sort_by="description", sort_dir="asc")
    assert len(ordered) >= 2


