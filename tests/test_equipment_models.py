"""Testes de unidade e integração dos modelos ORM de Equipamentos."""
from datetime import datetime, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.domain.models import Equipment, EquipmentTag, EquipmentMovement, EquipmentMaintenance


def test_create_equipment_model(db_session: Session):
    """Testa criação bem-sucedida do modelo Equipment com relacionamentos."""
    equipment = Equipment(
        description="Dell OptiPlex 7090",
        serial_number="SN12345678",
        patrimony_number="10342",
        hostname="DESKTOP-TI01",
        brand="Dell",
        product_number="20L50001BR",
        equipment_type="Desktop",
        location="TI",
        status="Em uso",
        windows_key="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
        notes="Equipamento da diretoria",
    )
    db_session.add(equipment)
    db_session.commit()
    db_session.refresh(equipment)

    assert equipment.id is not None
    assert equipment.description == "Dell OptiPlex 7090"
    assert equipment.serial_number == "SN12345678"
    assert equipment.patrimony_number == "10342"
    assert equipment.hostname == "DESKTOP-TI01"
    assert equipment.status == "Em uso"
    assert len(equipment.movements) == 0
    assert len(equipment.maintenances) == 0


def test_unique_constraint_serial_number(db_session: Session):
    """Testa que a duplicidade de serial_number levanta IntegrityError."""
    eq1 = Equipment(
        description="Notebook 1",
        serial_number="DUP_SERIAL",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq1)
    db_session.commit()

    eq2 = Equipment(
        description="Notebook 2",
        serial_number="DUP_SERIAL",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_constraint_patrimony_number(db_session: Session):
    """Testa que a duplicidade de patrimony_number levanta IntegrityError."""
    eq1 = Equipment(
        description="Notebook 1",
        serial_number="SN_001",
        patrimony_number="PAT_DUP",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq1)
    db_session.commit()

    eq2 = Equipment(
        description="Notebook 2",
        serial_number="SN_002",
        patrimony_number="PAT_DUP",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_constraint_hostname(db_session: Session):
    """Testa que a duplicidade de hostname levanta IntegrityError."""
    eq1 = Equipment(
        description="Notebook 1",
        serial_number="SN_001",
        hostname="HOST_DUP",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq1)
    db_session.commit()

    eq2 = Equipment(
        description="Notebook 2",
        serial_number="SN_002",
        hostname="HOST_DUP",
        equipment_type="Notebook",
        location="TI",
    )
    db_session.add(eq2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_equipment_tag_model(db_session: Session):
    """Testa modelo EquipmentTag e constraint de unicidade composta."""
    tag1 = EquipmentTag(category="tipo", name="Notebook")
    db_session.add(tag1)
    db_session.commit()
    assert tag1.id is not None

    tag2 = EquipmentTag(category="tipo", name="Notebook")
    db_session.add(tag2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_equipment_movement_and_maintenance_relationships(db_session: Session):
    """Testa inserção e navegação nos relacionamentos de movimentação e manutenção."""
    equipment = Equipment(
        description="Monitor LG 29",
        serial_number="SN_MONITOR_01",
        equipment_type="Monitor",
        location="TI",
    )
    db_session.add(equipment)
    db_session.commit()

    now = datetime.now(timezone.utc)
    mov = EquipmentMovement(
        equipment_id=equipment.id,
        origin_location="TI",
        destination_location="Rádio Produção",
        movement_date=now,
        notes="Transferência de estúdio",
    )
    maint = EquipmentMaintenance(
        equipment_id=equipment.id,
        maintenance_date=now,
        maintenance_type="Preventiva",
        description="Troca de fonte interna",
    )
    db_session.add(mov)
    db_session.add(maint)
    db_session.commit()

    db_session.refresh(equipment)
    assert len(equipment.movements) == 1
    assert equipment.movements[0].destination_location == "Rádio Produção"
    assert len(equipment.maintenances) == 1
    assert equipment.maintenances[0].description == "Troca de fonte interna"
