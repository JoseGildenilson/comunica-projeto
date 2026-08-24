"""Casos de uso para pré-visualização e execução de importação de planilhas."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.domain.models import Equipment, EquipmentTag, EquipmentMaintenance
from src.domain.schemas import (
    SpreadsheetImportPreviewResponse,
    SpreadsheetImportResultResponse,
    SpreadsheetRowPreview,
)
from src.infrastructure.repositories import (
    EquipmentRepository,
    EquipmentTagRepository,
    EquipmentMaintenanceRepository,
)
from src.infrastructure.spreadsheet_parser import parse_spreadsheet, ParsedSpreadsheetRow


class PreviewSpreadsheetUseCase:
    """Caso de uso para gerar prévia da planilha enviada sem persistência."""

    def execute(self, file_bytes: bytes, filename: str) -> SpreadsheetImportPreviewResponse:
        parsed = parse_spreadsheet(file_bytes, filename)
        
        sample_rows: list[SpreadsheetRowPreview] = []
        for r in parsed.rows[:10]:
            sample_rows.append(
                SpreadsheetRowPreview(
                    row_number=r.row_number,
                    equipment_type=r.equipment_type,
                    location=r.location,
                    status=r.status,
                    description=r.description,
                    patrimony_number=r.patrimony_number,
                    serial_number=r.serial_number,
                    brand=r.brand,
                    last_maintenance_at=r.last_maintenance_at.strftime("%d/%m/%Y") if r.last_maintenance_at else None,
                    windows_key=r.windows_key,
                    product_number=r.product_number,
                    hist_mov=r.hist_mov,
                    hostname=r.hostname,
                    notes=r.notes,
                )
            )
            
        return SpreadsheetImportPreviewResponse(
            filename=parsed.filename,
            total_rows=len(parsed.rows),
            sample_rows=sample_rows,
            detected_sheet=parsed.detected_sheet,
            headers=parsed.headers,
        )


class ExecuteSpreadsheetImportUseCase:
    """Caso de uso para execução transacional da importação da planilha no banco de dados."""

    def __init__(self, db: Session):
        self.db = db
        self.equipment_repo = EquipmentRepository(db)
        self.tag_repo = EquipmentTagRepository(db)
        self.maintenance_repo = EquipmentMaintenanceRepository(db)

    def execute(self, file_bytes: bytes, filename: str) -> SpreadsheetImportResultResponse:
        parsed = parse_spreadsheet(file_bytes, filename)
        
        if not parsed.rows:
            return SpreadsheetImportResultResponse(
                success=True,
                total_rows=0,
                created_count=0,
                updated_count=0,
                tags_created_count=0,
                maintenances_created_count=0,
                errors=[],
                message="Nenhuma linha de dados encontrada na planilha.",
            )

        # Cache em memória das tags existentes para otimização
        all_tags = self.tag_repo.list_all()
        existing_tags = {(t.category, t.name.lower()): t for t in all_tags}
        
        tags_created_count = 0

        def ensure_tag(category: str, name: str) -> None:
            nonlocal tags_created_count
            clean_name = name.strip()
            key = (category, clean_name.lower())
            if key not in existing_tags:
                new_tag = EquipmentTag(category=category, name=clean_name)
                self.tag_repo.create(new_tag)
                existing_tags[key] = new_tag
                tags_created_count += 1

        created_count = 0
        updated_count = 0
        maintenances_created_count = 0
        errors: list[str] = []

        try:
            for row in parsed.rows:
                # 1. Garante tags dinâmicas
                ensure_tag("tipo", row.equipment_type)
                ensure_tag("localizacao", row.location)
                ensure_tag("situacao", row.status)

                # 2. Busca por equipamento existente (por patrimônio ou por serial)
                equipment: Equipment | None = None
                if row.patrimony_number:
                    equipment = self.equipment_repo.get_by_patrimony_number(row.patrimony_number)
                if equipment is None and row.serial_number:
                    equipment = self.equipment_repo.get_by_serial_number(row.serial_number)

                if equipment is not None:
                    # Atualiza registro existente
                    equipment.description = row.description
                    equipment.equipment_type = row.equipment_type
                    equipment.location = row.location
                    equipment.status = row.status
                    equipment.brand = row.brand or equipment.brand
                    equipment.hostname = row.hostname or equipment.hostname
                    equipment.product_number = row.product_number or equipment.product_number
                    equipment.windows_key = row.windows_key or equipment.windows_key
                    equipment.notes = row.notes or equipment.notes
                    equipment.last_maintenance_at = row.last_maintenance_at or equipment.last_maintenance_at
                    if row.patrimony_number and not equipment.patrimony_number:
                        equipment.patrimony_number = row.patrimony_number
                    if row.serial_number and not equipment.serial_number:
                        equipment.serial_number = row.serial_number
                        
                    updated_count += 1
                else:
                    # Cria novo equipamento
                    equipment = Equipment(
                        description=row.description,
                        equipment_type=row.equipment_type,
                        location=row.location,
                        status=row.status,
                        patrimony_number=row.patrimony_number,
                        serial_number=row.serial_number,
                        brand=row.brand,
                        hostname=row.hostname,
                        product_number=row.product_number,
                        windows_key=row.windows_key,
                        last_maintenance_at=row.last_maintenance_at,
                        notes=row.notes,
                    )
                    self.equipment_repo.create(equipment)
                    self.db.flush()
                    created_count += 1

                # 3. Registro único consolidado de manutenção se houver histórico de movimentações
                if row.hist_mov:
                    maint_date = row.last_maintenance_at or datetime.now(timezone.utc)
                    maintenance = EquipmentMaintenance(
                        equipment_id=equipment.id,
                        maintenance_date=maint_date,
                        maintenance_type="Histórico Importado",
                        description=row.hist_mov,
                        notes=None,
                    )
                    self.maintenance_repo.create(maintenance)
                    maintenances_created_count += 1

            self.db.commit()
            
            return SpreadsheetImportResultResponse(
                success=True,
                total_rows=len(parsed.rows),
                created_count=created_count,
                updated_count=updated_count,
                tags_created_count=tags_created_count,
                maintenances_created_count=maintenances_created_count,
                errors=errors,
                message=f"Importação concluída: {created_count} novos equipamentos, {updated_count} atualizados e {tags_created_count} tags cadastradas.",
            )
        except Exception:
            self.db.rollback()
            raise
