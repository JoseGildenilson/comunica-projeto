"""Testes unitários para os casos de uso de importação de planilhas."""
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from src.domain.models import Equipment, EquipmentTag, EquipmentMaintenance
from src.infrastructure.repositories import (
    EquipmentRepository,
    EquipmentTagRepository,
    EquipmentMaintenanceRepository,
)
from src.use_cases.import_spreadsheet_use_cases import (
    PreviewSpreadsheetUseCase,
    ExecuteSpreadsheetImportUseCase,
)
from tests.test_spreadsheet_parser import create_mock_excel


def test_preview_spreadsheet_use_case():
    headers = ["TIPO", "LOCALIZAÇÃO", "SITUAÇÃO", "DESCRIÇÃO", "Nº PATRIMÔNIO", "Nº SÉRIE", "ÚLTIMA MANUTENÇÃO"]
    rows = [headers]
    for i in range(15):
        rows.append(["DESKTOP", f"SALA {i}", "EM USO", f"PC {i}", f"PAT-{i}", f"SN-{i}", datetime(2023, 1, 1)])

    excel_bytes = create_mock_excel("Patrimônio", rows)
    use_case = PreviewSpreadsheetUseCase()
    preview = use_case.execute(excel_bytes, "inventario.xlsx")

    assert preview.total_rows == 15
    assert len(preview.sample_rows) == 10
    assert preview.detected_sheet == "Patrimônio"
    assert preview.sample_rows[0].patrimony_number == "PAT-0"
    assert preview.sample_rows[0].last_maintenance_at == "01/01/2023"


def test_execute_spreadsheet_import_empty_rows(db_session: Session):
    headers = ["TIPO", "LOCALIZAÇÃO", "SITUAÇÃO", "DESCRIÇÃO"]
    excel_bytes = create_mock_excel("Patrimônio", [headers])
    use_case = ExecuteSpreadsheetImportUseCase(db_session)
    result = use_case.execute(excel_bytes, "vazio.xlsx")

    assert result.success is True
    assert result.total_rows == 0
    assert result.created_count == 0


def test_execute_spreadsheet_import_creation_and_tags(db_session: Session):
    headers = [
        "TIPO", "LOCALIZAÇÃO", "SITUAÇÃO", "DESCRIÇÃO", "Nº PATRIMÔNIO",
        "Nº SÉRIE", "MARCA", "ÚLTIMA MANUTENÇÃO", "HISTÓRICO DE MOVIMENTAÇÕES", "OBSERVAÇÕES"
    ]
    row1 = [
        "NOTEBOOK", "SALA DIRETORIA", "EM USO", "Dell Latitude 5420", "PAT-1001",
        "SN-NOTE-1", "Dell", "10/05/2023", "Troca de teclado e limpeza", "Uso exclusivo da gerência"
    ]
    row_sem_ident = [
        "PERIFÉRICO", "ALMOXARIFADO", "OCIOSO", "Mouse USB", None,
        None, "Logitech", None, None, "Reserva de estoque"
    ]

    excel_bytes = create_mock_excel("Patrimônio", [headers, row1, row_sem_ident])
    use_case = ExecuteSpreadsheetImportUseCase(db_session)
    result = use_case.execute(excel_bytes, "lote1.xlsx")

    assert result.success is True
    assert result.total_rows == 2
    assert result.created_count == 2
    assert result.updated_count == 0
    assert result.tags_created_count >= 4  # NOTEBOOK, PERIFÉRICO, SALA DIRETORIA, ALMOXARIFADO, etc.
    assert result.maintenances_created_count == 1

    # Valida no banco
    eq_repo = EquipmentRepository(db_session)
    eq1 = eq_repo.get_by_patrimony_number("PAT-1001")
    assert eq1 is not None
    assert eq1.description == "Dell Latitude 5420"
    assert eq1.serial_number == "SN-NOTE-1"
    assert eq1.notes == "Uso exclusivo da gerência"
    assert len(eq1.maintenances) == 1
    assert eq1.maintenances[0].description == "Troca de teclado e limpeza"
    assert eq1.maintenances[0].maintenance_date.replace(tzinfo=timezone.utc) == datetime(2023, 5, 10, 0, 0, tzinfo=timezone.utc)

    # Valida item sem serial/patrimônio
    tag_repo = EquipmentTagRepository(db_session)
    tag_note = tag_repo.get_by_category_and_name("tipo", "NOTEBOOK")
    assert tag_note is not None


def test_execute_spreadsheet_import_upsert_all_fields(db_session: Session):
    eq_repo = EquipmentRepository(db_session)
    # Cria equipamento inicial com apenas serial
    eq_existing = Equipment(
        description="Equipamento Antigo",
        equipment_type="DESKTOP",
        location="CTM",
        status="OCIOSO",
        patrimony_number=None,
        serial_number="SN-MATCH-1",
        brand=None,
        hostname=None,
        product_number=None,
        windows_key=None,
        notes=None,
    )
    eq_repo.create(eq_existing)

    # Cria equipamento inicial com apenas patrimônio
    eq_existing_pat = Equipment(
        description="Monitor Antigo",
        equipment_type="MONITOR",
        location="CTM",
        status="OCIOSO",
        patrimony_number="PAT-MATCH-2",
        serial_number=None,
    )
    eq_repo.create(eq_existing_pat)
    db_session.commit()

    # Planilha atualizando ambos
    headers = [
        "TIPO", "LOCALIZAÇÃO", "SITUAÇÃO", "DESCRIÇÃO", "Nº PATRIMÔNIO",
        "Nº SÉRIE", "MARCA", "ÚLTIMA MANUTENÇÃO", "HISTÓRICO DE MOVIMENTAÇÕES",
        "HOSTNAME", "Nº PRODUTO", "CHAVE WINDOWS", "OBSERVAÇÕES"
    ]
    row1 = [
        "DESKTOP", "SALA 100", "EM USO", "Desktop Atualizado Completo", "PAT-FILLED-1",
        "SN-MATCH-1", "HP", "01/02/2024", "Manutenção realizada",
        "HOST-100", "PN-100", "KEY-100", "Observação nova 1"
    ]
    row2 = [
        "MONITOR", "SALA 200", "EM USO", "Monitor Atualizado Completo", "PAT-MATCH-2",
        "SN-FILLED-2", "Dell", "05/03/2024", None,
        "HOST-200", "PN-200", "KEY-200", "Observação nova 2"
    ]
    excel_bytes = create_mock_excel("Patrimônio", [headers, row1, row2])

    use_case = ExecuteSpreadsheetImportUseCase(db_session)
    result = use_case.execute(excel_bytes, "update_all.xlsx")

    assert result.success is True
    assert result.updated_count == 2
    assert result.created_count == 0

    # Verifica atualização de todos os campos
    db_session.refresh(eq_existing)
    assert eq_existing.patrimony_number == "PAT-FILLED-1"
    assert eq_existing.hostname == "HOST-100"
    assert eq_existing.product_number == "PN-100"
    assert eq_existing.windows_key == "KEY-100"
    assert eq_existing.notes == "Observação nova 1"
    assert eq_existing.brand == "HP"
    assert eq_existing.last_maintenance_at is not None

    db_session.refresh(eq_existing_pat)
    assert eq_existing_pat.serial_number == "SN-FILLED-2"
    assert eq_existing_pat.hostname == "HOST-200"


def test_execute_spreadsheet_import_rollback_on_error(db_session: Session, monkeypatch):
    headers = ["TIPO", "LOCALIZAÇÃO", "SITUAÇÃO", "DESCRIÇÃO", "Nº PATRIMÔNIO", "Nº SÉRIE"]
    row = ["DESKTOP", "TI", "EM USO", "PC Teste", "PAT-FAIL", "SN-FAIL"]
    excel_bytes = create_mock_excel("Patrimônio", [headers, row])

    use_case = ExecuteSpreadsheetImportUseCase(db_session)
    
    # Simula erro de banco durante o flush/commit
    def mock_create(self, eq):
        raise RuntimeError("Falha forçada de banco de dados")
        
    monkeypatch.setattr(EquipmentRepository, "create", mock_create)

    with pytest.raises(RuntimeError, match="Falha forçada de banco de dados"):
        use_case.execute(excel_bytes, "falha.xlsx")

    # Verifica que não salvou
    eq_repo = EquipmentRepository(db_session)
    assert eq_repo.get_by_patrimony_number("PAT-FAIL") is None
