"""Casos de uso de negócio para Gestão de Equipamentos (Patrimônio)."""
import math
from datetime import datetime
from sqlalchemy.orm import Session
from src.domain.models import Equipment, EquipmentTag, EquipmentMovement, EquipmentMaintenance
from src.domain.schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentTagCreate,
    EquipmentTagResponse,
    EquipmentMovementCreate,
    EquipmentMovementResponse,
    EquipmentMaintenanceCreate,
    EquipmentMaintenanceResponse,
)
from src.infrastructure.repositories import (
    EquipmentRepository,
    EquipmentTagRepository,
    EquipmentMovementRepository,
    EquipmentMaintenanceRepository,
)


class CreateEquipmentUseCase:
    """Caso de uso para cadastro de novos equipamentos com validações de unicidade."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentRepository(db)

    def execute(self, data: EquipmentCreate) -> Equipment:
        # Validação de unicidade do Nº de Série
        if self.repo.get_by_serial_number(data.serial_number):
            raise ValueError(f"Número de série '{data.serial_number}' já está cadastrado no sistema.")

        # Validação de unicidade do Nº de Patrimônio (se informado)
        if data.patrimony_number and self.repo.get_by_patrimony_number(data.patrimony_number):
            raise ValueError(f"Número de patrimônio '{data.patrimony_number}' já está cadastrado no sistema.")

        # Validação de unicidade do Hostname (se informado)
        if data.hostname and self.repo.get_by_hostname(data.hostname):
            raise ValueError(f"Hostname '{data.hostname}' já está cadastrado no sistema.")

        equipment = Equipment(
            serial_number=data.serial_number,
            description=data.description,
            equipment_type=data.equipment_type,
            location=data.location,
            status=data.status,
            patrimony_number=data.patrimony_number,
            hostname=data.hostname,
            brand=data.brand,
            product_number=data.product_number,
            windows_key=data.windows_key,
            last_maintenance_at=data.last_maintenance_at,
            notes=data.notes,
        )
        self.repo.create(equipment)
        self.db.flush()
        return equipment


class ListEquipmentsUseCase:
    """Caso de uso para listagem paginada e filtrada de equipamentos."""

    def __init__(self, db: Session):
        self.repo = EquipmentRepository(db)

    def execute(
        self,
        page: int = 1,
        limit: int = 25,
        equipment_type: list[str] | str | None = None,
        location: list[str] | str | None = None,
        status: list[str] | str | None = None,
        patrimony_number: list[str] | str | None = None,
        serial_number: list[str] | str | None = None,
        product_number: list[str] | str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> EquipmentListResponse:
        items, total = self.repo.list_paginated_and_filtered(
            page=page,
            limit=limit,
            equipment_type=equipment_type,
            location=location,
            status=status,
            patrimony_number=patrimony_number,
            serial_number=serial_number,
            product_number=product_number,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        pages = math.ceil(total / limit) if total > 0 else 1
        item_responses = [EquipmentResponse.model_validate(item) for item in items]

        return EquipmentListResponse(
            items=item_responses,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )


class GetEquipmentDetailUseCase:
    """Caso de uso para consulta detalhada de equipamento por ID."""

    def __init__(self, db: Session):
        self.repo = EquipmentRepository(db)

    def execute(self, equipment_id: int) -> Equipment:
        equipment = self.repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")
        return equipment


class UpdateEquipmentUseCase:
    """Caso de uso para atualização de equipamentos."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = EquipmentRepository(db)

    def execute(self, equipment_id: int, data: EquipmentUpdate) -> Equipment:
        equipment = self.repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")

        # Validações de unicidade se houver alteração
        if data.serial_number and data.serial_number != equipment.serial_number:
            if self.repo.get_by_serial_number(data.serial_number):
                raise ValueError(f"Número de série '{data.serial_number}' já está cadastrado no sistema.")
            equipment.serial_number = data.serial_number

        if data.patrimony_number and data.patrimony_number != equipment.patrimony_number:
            if self.repo.get_by_patrimony_number(data.patrimony_number):
                raise ValueError(f"Número de patrimônio '{data.patrimony_number}' já está cadastrado no sistema.")
            equipment.patrimony_number = data.patrimony_number

        if data.hostname and data.hostname != equipment.hostname:
            if self.repo.get_by_hostname(data.hostname):
                raise ValueError(f"Hostname '{data.hostname}' já está cadastrado no sistema.")
            equipment.hostname = data.hostname

        # Atualização dos demais campos
        if data.description is not None:
            equipment.description = data.description
        if data.equipment_type is not None:
            equipment.equipment_type = data.equipment_type
        if data.location is not None:
            equipment.location = data.location
        if data.status is not None:
            equipment.status = data.status
        if data.brand is not None:
            equipment.brand = data.brand
        if data.product_number is not None:
            equipment.product_number = data.product_number
        if data.windows_key is not None:
            equipment.windows_key = data.windows_key
        if data.last_maintenance_at is not None:
            equipment.last_maintenance_at = data.last_maintenance_at
        if data.notes is not None:
            equipment.notes = data.notes

        self.db.flush()
        return equipment


class RecordMovementUseCase:
    """Caso de uso para registro de movimentação de localização (RN-EQ-05 & RN-EQ-06)."""

    def __init__(self, db: Session):
        self.db = db
        self.eq_repo = EquipmentRepository(db)
        self.mov_repo = EquipmentMovementRepository(db)

    def execute(self, equipment_id: int, data: EquipmentMovementCreate) -> EquipmentMovement:
        equipment = self.eq_repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")

        movement = EquipmentMovement(
            equipment_id=equipment_id,
            origin_location=data.origin_location,
            destination_location=data.destination_location,
            movement_date=data.movement_date,
            notes=data.notes,
        )
        self.mov_repo.create(movement)

        # Atualiza a localização atual do equipamento para o Destino
        # Nota: RN-EQ-06 - NÃO altera a situação do equipamento!
        equipment.location = data.destination_location
        self.db.flush()
        return movement


class RecordMaintenanceUseCase:
    """Caso de uso para registro de manutenção (RN-EQ-09, RN-EQ-11 & RN-EQ-12)."""

    def __init__(self, db: Session):
        self.db = db
        self.eq_repo = EquipmentRepository(db)
        self.maint_repo = EquipmentMaintenanceRepository(db)

    def execute(self, equipment_id: int, data: EquipmentMaintenanceCreate) -> EquipmentMaintenance:
        equipment = self.eq_repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")

        maintenance = EquipmentMaintenance(
            equipment_id=equipment_id,
            maintenance_date=data.maintenance_date,
            maintenance_type=data.maintenance_type or "Manutenção",
            description=data.description,
            notes=data.notes,
        )
        self.maint_repo.create(maintenance)

        # Atualiza o campo 'last_maintenance_at' para a data informada (RN-EQ-11)
        equipment.last_maintenance_at = data.maintenance_date
        self.db.flush()
        return maintenance


class UpdateMaintenanceUseCase:
    """Caso de uso para alteração/edição de manutenção existente (RN-EQ-10)."""

    def __init__(self, db: Session):
        self.db = db
        self.eq_repo = EquipmentRepository(db)
        self.maint_repo = EquipmentMaintenanceRepository(db)

    def execute(
        self,
        equipment_id: int,
        maintenance_id: int,
        maintenance_date: datetime | None = None,
        maintenance_type: str | None = None,
        description: str | None = None,
        notes: str | None = None,
    ) -> EquipmentMaintenance:
        equipment = self.eq_repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")

        maintenance = self.maint_repo.get_by_id(maintenance_id)
        if not maintenance or maintenance.equipment_id != equipment_id:
            raise KeyError(f"Manutenção com ID {maintenance_id} não foi encontrada para este equipamento.")

        if maintenance_date is not None:
            maintenance.maintenance_date = maintenance_date
        if maintenance_type is not None:
            maintenance.maintenance_type = maintenance_type
        if description is not None:
            maintenance.description = description
        if notes is not None:
            maintenance.notes = notes

        maintenances = self.maint_repo.list_by_equipment(equipment_id)
        equipment.last_maintenance_at = max((m.maintenance_date for m in maintenances), default=None)

        self.db.flush()
        return maintenance


class DeleteMaintenanceUseCase:
    """Caso de uso para exclusão de registro de manutenção (RN-EQ-10)."""

    def __init__(self, db: Session):
        self.db = db
        self.eq_repo = EquipmentRepository(db)
        self.maint_repo = EquipmentMaintenanceRepository(db)

    def execute(self, equipment_id: int, maintenance_id: int) -> None:
        equipment = self.eq_repo.get_by_id(equipment_id)
        if not equipment:
            raise KeyError(f"Equipamento com ID {equipment_id} não foi encontrado.")

        maintenance = self.maint_repo.get_by_id(maintenance_id)
        if not maintenance or maintenance.equipment_id != equipment_id:
            raise KeyError(f"Manutenção com ID {maintenance_id} não foi encontrada para este equipamento.")

        self.maint_repo.delete(maintenance)
        self.db.flush()

        # Recalcula a última manutenção restante (ou None se não restar nenhuma)
        remaining = self.maint_repo.list_by_equipment(equipment_id)
        equipment.last_maintenance_at = max((m.maintenance_date for m in remaining), default=None)
        self.db.flush()


class ManageTagsUseCase:
    """Caso de uso para listar e criar tags dinâmicas."""

    def __init__(self, db: Session):
        self.db = db
        self.tag_repo = EquipmentTagRepository(db)

    def list_tags(self, category: str | None = None) -> list[EquipmentTag]:
        if category:
            return self.tag_repo.list_by_category(category)
        return self.tag_repo.list_all()

    def create_tag(self, data: EquipmentTagCreate) -> EquipmentTag:
        existing = self.tag_repo.get_by_category_and_name(data.category, data.name)
        if existing:
            return existing

        tag = EquipmentTag(category=data.category, name=data.name)
        self.tag_repo.create(tag)
        self.db.flush()
        return tag
