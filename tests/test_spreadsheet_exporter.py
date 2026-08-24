"""Testes unitários para o gerador de planilhas Excel (spreadsheet_exporter)."""
import io
from datetime import datetime, timezone
import openpyxl
from src.domain.models import Equipment, EquipmentMaintenance
from src.infrastructure.spreadsheet_exporter import (
    HEADERS,
    COLUMN_WIDTHS,
    _format_maintenances,
    _format_date,
    generate_equipments_excel,
)


def test_format_date():
    assert _format_date(None) == ""
    dt = datetime(2026, 8, 23, 14, 30, tzinfo=timezone.utc)
    assert _format_date(dt) == "23/08/2026"


def test_format_maintenances_empty():
    eq = Equipment(id=1, description="PC Test", equipment_type="Desktop", location="TI")
    eq.maintenances = []
    assert _format_maintenances(eq) == ""


def test_format_maintenances_sorting_and_variations():
    eq = Equipment(id=1, description="PC Test", equipment_type="Desktop", location="TI")
    
    # 3 manutenções fora de ordem cronológica
    m1 = EquipmentMaintenance(
        id=1,
        equipment_id=1,
        maintenance_date=datetime(2024, 5, 10, tzinfo=timezone.utc),
        maintenance_type="Manutenção",
        description="Troca de SSD",
        notes="SSD 500GB",
    )
    m2 = EquipmentMaintenance(
        id=2,
        equipment_id=1,
        maintenance_date=datetime(2022, 1, 15, tzinfo=timezone.utc),
        maintenance_type="Manutenção",
        description="Atualização de SO",
        notes=None,
    )
    m3 = EquipmentMaintenance(
        id=3,
        equipment_id=1,
        maintenance_date=None,
        maintenance_type="Manutenção",
        description="Limpeza básica",
        notes=None,
    )
    m4 = EquipmentMaintenance(
        id=4,
        equipment_id=1,
        maintenance_date=datetime(2025, 3, 1, tzinfo=timezone.utc),
        maintenance_type="Manutenção",
        description="",
        notes="Apenas observação",
    )
    
    m5 = EquipmentMaintenance(
        id=5,
        equipment_id=1,
        maintenance_date=None,
        maintenance_type="Manutenção",
        description=None,
        notes="Apenas notas",
    )
    m6 = EquipmentMaintenance(
        id=6,
        equipment_id=1,
        maintenance_date=None,
        maintenance_type="Manutenção",
        description=None,
        notes=None,
    )
    
    eq.maintenances = [m1, m2, m3, m4, m5, m6]
    formatted = _format_maintenances(eq)
    lines = formatted.split("\n")
    
    # Deve conter todas as manutenções ordenadas cronologicamente
    assert len(lines) == 5
    assert "Limpeza básica" in lines[0]
    assert "Apenas notas" in lines[1]
    assert "15/01/2022: Atualização de SO" in lines[2]
    assert "10/05/2024: Troca de SSD (Obs: SSD 500GB)" in lines[3]
    assert "01/03/2025 (Obs: Apenas observação)" in lines[4]


def test_generate_equipments_excel_empty_list():
    excel_bytes = generate_equipments_excel([])
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0

    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    assert "Patrimônio" in wb.sheetnames
    ws = wb["Patrimônio"]
    assert ws.max_row == 1
    assert ws.max_column == 13

    # Verifica cabeçalhos e estilos
    for col_idx, expected_header in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col_idx)
        assert cell.value == expected_header
        assert cell.font.bold is True
        assert cell.fill.start_color.rgb in ("FF4DD0E1", "004DD0E1", "4DD0E1")


def test_generate_equipments_excel_with_data_and_styles():
    eq1 = Equipment(
        id=1,
        description="ThinkPad T480",
        serial_number="PF123456",
        patrimony_number="PAT-1001",
        hostname="NOTE-TI-01",
        brand="Lenovo",
        product_number="20L6001VBR",
        equipment_type="Notebook",
        location="TI",
        status="Em uso",
        windows_key="XXXXX-XXXXX-XXXXX",
        last_maintenance_at=datetime(2024, 6, 20, tzinfo=timezone.utc),
        notes="Equipamento de alta performance",
    )
    maint = EquipmentMaintenance(
        id=1,
        equipment_id=1,
        maintenance_date=datetime(2024, 6, 20, tzinfo=timezone.utc),
        maintenance_type="Manutenção",
        description="Upgrade para 32GB RAM",
        notes="2x16GB",
    )
    eq1.maintenances = [maint]

    eq2 = Equipment(
        id=2,
        description="Monitor LG 24",
        serial_number=None,
        patrimony_number=None,
        hostname=None,
        brand="LG",
        product_number=None,
        equipment_type="Monitor",
        location="Recepção",
        status="Disponível",
        windows_key=None,
        last_maintenance_at=None,
        notes=None,
    )
    eq2.maintenances = []

    excel_bytes = generate_equipments_excel([eq1, eq2])
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    ws = wb["Patrimônio"]

    assert ws.max_row == 3
    assert ws.freeze_panes == "A2"
    assert ws.views.sheetView[0].showGridLines is True

    # Linha 2 (eq1)
    assert ws.cell(row=2, column=1).value == "Notebook"
    assert ws.cell(row=2, column=2).value == "TI"
    assert ws.cell(row=2, column=3).value == "Em uso"
    assert ws.cell(row=2, column=4).value == "ThinkPad T480"
    assert ws.cell(row=2, column=5).value == "PAT-1001"
    assert ws.cell(row=2, column=6).value == "PF123456"
    assert ws.cell(row=2, column=7).value == "Lenovo"
    assert ws.cell(row=2, column=8).value == "20/06/2024"
    assert ws.cell(row=2, column=9).value == "XXXXX-XXXXX-XXXXX"
    assert ws.cell(row=2, column=10).value == "20L6001VBR"
    assert "Upgrade para 32GB RAM (Obs: 2x16GB)" in ws.cell(row=2, column=11).value
    assert ws.cell(row=2, column=12).value == "NOTE-TI-01"
    assert ws.cell(row=2, column=13).value == "Equipamento de alta performance"

    # Linha 3 (eq2) com campos vazios tratados como string vazia ou None
    assert ws.cell(row=3, column=1).value == "Monitor"
    assert ws.cell(row=3, column=2).value == "Recepção"
    assert ws.cell(row=3, column=5).value in ("", None)
    assert ws.cell(row=3, column=6).value in ("", None)
    assert ws.cell(row=3, column=8).value in ("", None)
    assert ws.cell(row=3, column=11).value in ("", None)

    # Verifica largura das colunas
    for col_idx, width in COLUMN_WIDTHS.items():
        col_letter = openpyxl.utils.get_column_letter(col_idx)
        assert ws.column_dimensions[col_letter].width == width
