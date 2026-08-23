"""Testes unitários e de integração para os Casos de Uso de Equipamentos."""
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.orm import Session
from src.domain.schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentMovementCreate,
    EquipmentMaintenanceCreate,
    EquipmentTagCreate,
)
from src.use_cases.equipment_use_cases import (
    CreateEquipmentUseCase,
    ListEquipmentsUseCase,
    GetEquipmentDetailUseCase,
    UpdateEquipmentUseCase,
    RecordMovementUseCase,
    RecordMaintenanceUseCase,
    UpdateMaintenanceUseCase,
    DeleteMaintenanceUseCase,
    ManageTagsUseCase,
    GetSuggestionsUseCase,
)



def test_create_equipment_use_case_success_and_duplicates(db_session: Session):
    """Testa criação com sucesso e erros de unicidade."""
    create_uc = CreateEquipmentUseCase(db_session)

    data = EquipmentCreate(
        serial_number="SN_UNIQUE_001",
        patrimony_number="PAT_UNIQUE_001",
        hostname="HOST_UNIQUE_001",
        description="ThinkPad X1",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
    )
    eq = create_uc.execute(data)
    assert eq.id is not None
    assert eq.serial_number == "SN_UNIQUE_001"

    # Duplicidade de serial_number
    with pytest.raises(ValueError, match="Número de série.*já está cadastrado"):
        create_uc.execute(EquipmentCreate(
            serial_number="SN_UNIQUE_001",
            description="Outro",
            equipment_type="Notebook",
            location="TI",
        ))

    # Duplicidade de patrimony_number
    with pytest.raises(ValueError, match="Número de patrimônio.*já está cadastrado"):
        create_uc.execute(EquipmentCreate(
            serial_number="SN_OUTRO",
            patrimony_number="PAT_UNIQUE_001",
            description="Outro",
            equipment_type="Notebook",
            location="TI",
        ))

    # Duplicidade de hostname
    with pytest.raises(ValueError, match="Hostname.*já está cadastrado"):
        create_uc.execute(EquipmentCreate(
            serial_number="SN_OUTRO2",
            hostname="HOST_UNIQUE_001",
            description="Outro",
            equipment_type="Notebook",
            location="TI",
        ))


def test_list_and_get_equipment_detail_use_cases(db_session: Session):
    """Testa busca detalhada e listagem paginada."""
    create_uc = CreateEquipmentUseCase(db_session)
    list_uc = ListEquipmentsUseCase(db_session)
    detail_uc = GetEquipmentDetailUseCase(db_session)

    eq = create_uc.execute(EquipmentCreate(
        serial_number="SN_LIST_01",
        description="Monitor LG 29",
        equipment_type="Monitor",
        location="Comunicação",
    ))

    # Get Detail
    found = detail_uc.execute(eq.id)
    assert found.description == "Monitor LG 29"

    with pytest.raises(KeyError, match="não foi encontrado"):
        detail_uc.execute(99999)

    # List com filtros em formato de listas
    response = list_uc.execute(page=1, limit=10, equipment_type=["Monitor", "Desktop"])
    assert response.total == 1
    assert len(response.items) == 1
    assert response.items[0].equipment_type == "Monitor"


def test_update_equipment_use_case(db_session: Session):
    """Testa atualização e validação de duplicidade na edição de todos os campos."""
    create_uc = CreateEquipmentUseCase(db_session)
    update_uc = UpdateEquipmentUseCase(db_session)

    eq1 = create_uc.execute(EquipmentCreate(
        serial_number="SN_EQ1",
        patrimony_number="PAT_EQ1",
        hostname="HOST_EQ1",
        description="EQ 1",
        equipment_type="Desktop",
        location="TI",
    ))
    eq2 = create_uc.execute(EquipmentCreate(
        serial_number="SN_EQ2",
        patrimony_number="PAT_EQ2",
        hostname="HOST_EQ2",
        description="EQ 2",
        equipment_type="Desktop",
        location="TI",
    ))

    now = datetime.now(timezone.utc)
    # Atualização válida de todos os campos
    updated = update_uc.execute(eq1.id, EquipmentUpdate(
        serial_number="SN_EQ1_MODIFIED",
        patrimony_number="PAT_EQ1_MODIFIED",
        hostname="HOST_EQ1_MODIFIED",
        description="EQ 1 Atualizado",
        equipment_type="Notebook",
        location="Comunicação",
        status="Ocioso",
        brand="Dell",
        product_number="PROD123",
        windows_key="KEY123",
        last_maintenance_at=now,
        notes="Obs atualizada",
    ))
    assert updated.serial_number == "SN_EQ1_MODIFIED"
    assert updated.patrimony_number == "PAT_EQ1_MODIFIED"
    assert updated.hostname == "HOST_EQ1_MODIFIED"
    assert updated.equipment_type == "Notebook"
    assert updated.brand == "Dell"

    # Atualização vazia (nenhum campo alterado)
    empty_updated = update_uc.execute(eq1.id, EquipmentUpdate())
    assert empty_updated.id == eq1.id

    # Atualizar com serial de outro equipamento deve falhar
    with pytest.raises(ValueError, match="Número de série"):
        update_uc.execute(eq1.id, EquipmentUpdate(serial_number="SN_EQ2"))

    # Atualizar com patrimônio de outro equipamento deve falhar
    with pytest.raises(ValueError, match="Número de patrimônio"):
        update_uc.execute(eq1.id, EquipmentUpdate(patrimony_number="PAT_EQ2"))

    # Atualizar com hostname de outro equipamento deve falhar
    with pytest.raises(ValueError, match="Hostname"):
        update_uc.execute(eq1.id, EquipmentUpdate(hostname="HOST_EQ2"))

    # Equipamento inexistente
    with pytest.raises(KeyError):
        update_uc.execute(99999, EquipmentUpdate(description="Inexistente"))


def test_record_movement_use_case_updates_location_without_changing_status(db_session: Session):
    """Testa que movimentação atualiza localização mas NÃO altera a situação (RN-EQ-05 & RN-EQ-06)."""
    create_uc = CreateEquipmentUseCase(db_session)
    mov_uc = RecordMovementUseCase(db_session)

    eq = create_uc.execute(EquipmentCreate(
        serial_number="SN_MOV_01",
        description="Notebook Mov",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
    ))

    now = datetime.now(timezone.utc)
    mov_data = EquipmentMovementCreate(
        origin_location="TI",
        destination_location="Rádio Produção",
        movement_date=now,
        notes="Movimentação para o estúdio",
    )
    mov = mov_uc.execute(eq.id, mov_data)

    assert mov.id is not None
    assert eq.location == "Rádio Produção"
    assert eq.status == "Em uso"  # Situação inalterada!

    with pytest.raises(KeyError):
        mov_uc.execute(99999, mov_data)


def test_record_maintenance_use_case_updates_last_maintenance_date_without_changing_status(db_session: Session):
    """Testa que manutenção atualiza last_maintenance_at mas NÃO altera a situação (RN-EQ-04 & RN-EQ-06)."""
    create_uc = CreateEquipmentUseCase(db_session)
    maint_uc = RecordMaintenanceUseCase(db_session)

    eq = create_uc.execute(EquipmentCreate(
        serial_number="SN_MAINT_01",
        description="Notebook Maint",
        equipment_type="Notebook",
        location="TI",
        status="Ocioso",
    ))

    now = datetime.now(timezone.utc)
    maint_data = EquipmentMaintenanceCreate(
        maintenance_date=now,
        maintenance_type="Preventiva",
        description="Troca de SSD",
    )
    maint = maint_uc.execute(eq.id, maint_data)

    assert maint.id is not None
    assert eq.last_maintenance_at == now
    assert eq.status == "Ocioso"  # Situação inalterada!

    with pytest.raises(KeyError):
        maint_uc.execute(99999, maint_data)


def test_update_and_delete_maintenance_use_cases(db_session: Session):
    """Testa edição e exclusão de manutenções com recálculo da última manutenção (RN-EQ-10 & RN-EQ-11)."""
    create_uc = CreateEquipmentUseCase(db_session)
    maint_uc = RecordMaintenanceUseCase(db_session)
    update_maint_uc = UpdateMaintenanceUseCase(db_session)
    delete_maint_uc = DeleteMaintenanceUseCase(db_session)

    eq = create_uc.execute(EquipmentCreate(
        serial_number="SN_MAINT_CRUD_01",
        description="Desktop Maint",
        equipment_type="Desktop",
        location="TI",
    ))

    t1 = datetime.now(timezone.utc) - timedelta(days=10)
    t2 = datetime.now(timezone.utc) - timedelta(days=2)

    m1 = maint_uc.execute(eq.id, EquipmentMaintenanceCreate(maintenance_date=t1, description="Limpeza"))
    m2 = maint_uc.execute(eq.id, EquipmentMaintenanceCreate(maintenance_date=t2, description="Upgrade SSD"))

    assert eq.last_maintenance_at == t2

    # Editar m2 incluindo data e tipo
    t3 = datetime.now(timezone.utc)
    updated = update_maint_uc.execute(
        equipment_id=eq.id,
        maintenance_id=m2.id,
        maintenance_date=t3,
        maintenance_type="Corretiva",
        description="Upgrade SSD e RAM",
        notes="Concluído",
    )
    assert updated.description == "Upgrade SSD e RAM"
    assert updated.notes == "Concluído"
    assert updated.maintenance_type == "Corretiva"
    assert eq.last_maintenance_at == t3

    # Editar m2 omitindo parâmetros (testar ramos None)
    partial_updated = update_maint_uc.execute(
        equipment_id=eq.id,
        maintenance_id=m2.id,
        maintenance_date=None,
        maintenance_type=None,
        description=None,
        notes=None,
    )
    assert partial_updated.id == m2.id

    # Testar update quando list_by_equipment retorna vazio (ramo False de if maintenances)
    maint_uc.maint_repo.list_by_equipment = lambda eq_id: []
    update_maint_uc.execute(eq.id, m2.id, description="Sem manutenções no repo")

    # Editar m2 com data inexistente / validação de erros
    with pytest.raises(KeyError):
        update_maint_uc.execute(99999, m2.id, description="Erro")

    with pytest.raises(KeyError):
        update_maint_uc.execute(eq.id, 99999, description="Erro")

    # Excluir m2 -> last_maintenance_at deve passar para t1
    delete_maint_uc.execute(eq.id, m2.id)
    assert eq.last_maintenance_at == t1

    # Excluir m1 -> last_maintenance_at deve passar para None
    delete_maint_uc.execute(eq.id, m1.id)
    assert eq.last_maintenance_at is None

    # Excluir manutenção inexistente deve falhar
    with pytest.raises(KeyError):
        delete_maint_uc.execute(eq.id, 99999)

    with pytest.raises(KeyError):
        delete_maint_uc.execute(99999, 1)


def test_manage_tags_use_case(db_session: Session):
    """Testa criação, listagem, atualização com propagação e exclusão de tags."""
    tags_uc = ManageTagsUseCase(db_session)
    create_eq_uc = CreateEquipmentUseCase(db_session)

    # 1. Criação com sucesso
    t1 = tags_uc.create_tag(EquipmentTagCreate(category="tipo", name="Notebook"))
    assert t1.id is not None
    assert t1.name == "Notebook"

    loc_tag = tags_uc.create_tag(EquipmentTagCreate(category="localizacao", name="TI"))
    status_tag = tags_uc.create_tag(EquipmentTagCreate(category="situacao", name="Em uso"))

    # 2. Duplicidade na mesma categoria lança ValueError
    with pytest.raises(ValueError, match="já está cadastrada"):
        tags_uc.create_tag(EquipmentTagCreate(category="tipo", name="Notebook"))

    # 3. Nome vazio lança ValueError
    with pytest.raises(ValueError, match="não pode ser vazio"):
        tags_uc.create_tag(EquipmentTagCreate(category="tipo", name="   "))

    # 4. Listagem filtrada e geral
    assert len(tags_uc.list_tags(category="tipo")) == 1
    assert len(tags_uc.list_tags(category="localizacao")) == 1
    assert len(tags_uc.list_tags(category=None)) == 3

    # 5. Criação de equipamento para testar propagação de renomeação
    eq = create_eq_uc.execute(
        EquipmentCreate(
            serial_number="SN-TAG-PROP-1",
            description="Equipamento para teste de propagação",
            equipment_type="Notebook",
            location="TI",
            status="Em uso",
        )
    )
    db_session.commit()

    # 6. Atualização/Renomeação com propagação
    # 6.1 Renomeia tipo (Notebook -> Laptop)
    updated_t1 = tags_uc.update_tag(t1.id, "Laptop")
    assert updated_t1.name == "Laptop"
    db_session.refresh(eq)
    assert eq.equipment_type == "Laptop"

    # 6.2 Renomeia localização (TI -> Suporte TI)
    updated_loc = tags_uc.update_tag(loc_tag.id, "Suporte TI")
    assert updated_loc.name == "Suporte TI"
    db_session.refresh(eq)
    assert eq.location == "Suporte TI"

    # 6.3 Renomeia situação (Em uso -> Ativo Operacional)
    updated_status = tags_uc.update_tag(status_tag.id, "Ativo Operacional")
    assert updated_status.name == "Ativo Operacional"
    db_session.refresh(eq)
    assert eq.status == "Ativo Operacional"

    # 6.4 Manter o mesmo nome não causa erro
    same_tag = tags_uc.update_tag(t1.id, "Laptop")
    assert same_tag.name == "Laptop"

    # 6.5 Renomear com nome vazio lança ValueError
    with pytest.raises(ValueError, match="não pode ser vazio"):
        tags_uc.update_tag(t1.id, "  ")

    # 6.6 Renomear para nome já existente em outra tag da mesma categoria lança ValueError
    t_other = tags_uc.create_tag(EquipmentTagCreate(category="tipo", name="Desktop"))
    with pytest.raises(ValueError, match="Já existe uma tag"):
        tags_uc.update_tag(t_other.id, "Laptop")

    # 6.7 Renomear tag inexistente lança KeyError
    with pytest.raises(KeyError, match="não foi encontrada"):
        tags_uc.update_tag(99999, "Inexistente")

    # 7. Exclusão de tags
    tags_uc.delete_tag(t_other.id)
    assert len(tags_uc.list_tags(category="tipo")) == 1

    # 7.1 Excluir tag inexistente lança KeyError
    with pytest.raises(KeyError, match="não foi encontrada"):
        tags_uc.delete_tag(99999)


def test_get_suggestions_use_case(db_session: Session):
    """Testa validações e execução do caso de uso GetSuggestionsUseCase."""
    create_uc = CreateEquipmentUseCase(db_session)
    sug_uc = GetSuggestionsUseCase(db_session)

    # Cadastra alguns equipamentos
    create_uc.execute(
        EquipmentCreate(
            serial_number="SN_SUG_01",
            patrimony_number="PAT_SUG_100",
            product_number="PROD_SUG_01",
            description="Item 1",
            equipment_type="Notebook",
            location="TI",
        )
    )
    create_uc.execute(
        EquipmentCreate(
            serial_number="SN_SUG_02",
            patrimony_number="PAT_SUG_200",
            product_number="PROD_SUG_02",
            description="Item 2",
            equipment_type="Notebook",
            location="TI",
        )
    )
    db_session.commit()

    # Busca com sucesso
    res_pat = sug_uc.execute(field="patrimony_number", prefix="PAT_", limit=10)
    assert len(res_pat) == 2
    assert "PAT_SUG_100" in res_pat

    res_ser = sug_uc.execute(field="serial_number", prefix="SN_", limit=10)
    assert len(res_ser) == 2

    res_prod = sug_uc.execute(field="product_number", prefix="PROD", limit=10)
    assert len(res_prod) == 2

    # Validação: campo inválido
    with pytest.raises(ValueError, match="Campo inválido para sugestão"):
        sug_uc.execute(field="invalid_field", prefix="PAT")

    with pytest.raises(ValueError, match="Campo inválido para sugestão"):
        sug_uc.execute(field="", prefix="PAT")

    # Validação: prefixo vazio ou menor que 2 caracteres
    with pytest.raises(ValueError, match="pelo menos 2 caracteres"):
        sug_uc.execute(field="patrimony_number", prefix="")

    with pytest.raises(ValueError, match="pelo menos 2 caracteres"):
        sug_uc.execute(field="patrimony_number", prefix="P")

    with pytest.raises(ValueError, match="pelo menos 2 caracteres"):
        sug_uc.execute(field="patrimony_number", prefix="   ")

    # Limite com valores fora dos limites (min=1, max=50)
    res_limit_min = sug_uc.execute(field="patrimony_number", prefix="PAT_", limit=0)
    assert len(res_limit_min) == 1

    res_limit_max = sug_uc.execute(field="patrimony_number", prefix="PAT_", limit=100)
    assert len(res_limit_max) == 2


