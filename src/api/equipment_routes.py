"""Roteador HTTP do FastAPI para Gestão de Equipamentos (Patrimônio)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from src.api.dependencies import require_tecnico_role
from src.core.database import get_db
from src.domain.models import User
from src.domain.schemas import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
    EquipmentListResponse,
    EquipmentSecretKeyResponse,
    EquipmentMovementCreate,
    EquipmentMovementUpdate,
    EquipmentMovementResponse,
    EquipmentMaintenanceStart,
    EquipmentMaintenanceComplete,
    EquipmentMaintenanceUpdate,
    EquipmentMaintenanceResponse,
    MessageResponse,
)
from src.use_cases.equipment_use_cases import (
    CreateEquipmentUseCase,
    ListEquipmentsUseCase,
    GetEquipmentDetailUseCase,
    UpdateEquipmentUseCase,
    DeleteEquipmentUseCase,
    RestoreEquipmentUseCase,
    GetDecryptedWindowsKeyUseCase,
    MovementsUseCase,
    MaintenancesUseCase,
    GetSuggestionsUseCase,
    ExportEquipmentsUseCase,
    ConflictError,
)


router = APIRouter(prefix="/api/v1/equipments", tags=["Equipamentos"])


@router.get("", response_model=EquipmentListResponse)
def list_equipments(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=25, ge=1, le=100, description="Itens por página"),
    type: List[int] | None = Query(default=None, description="Filtro por IDs de tipo de equipamento"),
    sector: List[int] | None = Query(default=None, description="Filtro por IDs de setor"),
    status_id: List[int] | None = Query(default=None, alias="status", description="Filtro por IDs de situação patrimonial"),
    patrimony_number: List[str] | None = Query(default=None, description="Filtro por número de patrimônio"),
    serial_number: List[str] | None = Query(default=None, description="Filtro por número de série"),
    search: str | None = Query(default=None, description="Busca textual global"),
    sort_by: str = Query(default="created_at", description="Campo para ordenação"),
    sort_dir: str = Query(default="desc", description="Direção da ordenação: asc/desc"),
    include_deleted: bool = Query(default=False, description="Incluir equipamentos excluídos logicamente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Lista equipamentos cadastrados com paginação, ordenação e múltiplos filtros combinados (Role: Técnico)."""
    use_case = ListEquipmentsUseCase(db)
    return use_case.execute(
        page=page,
        limit=limit,
        equipment_type_ids=type,
        sector_ids=sector,
        status_ids=status_id,
        patrimony_number=patrimony_number,
        serial_number=serial_number,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
        include_deleted=include_deleted,
    )


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Cadastra um novo equipamento (Role: Técnico)."""
    use_case = CreateEquipmentUseCase(db)
    detail_use_case = GetEquipmentDetailUseCase(db)
    try:
        equipment = use_case.execute(data)
        db.commit()
        return detail_use_case.execute(equipment.id)
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/suggestions", response_model=List[str])
def get_suggestions(
    field: str = Query(..., description="Nome do campo: patrimony_number, serial_number, model"),
    prefix: str = Query(..., description="Prefixo de busca (mínimo 2 caracteres)"),
    limit: int = Query(default=10, ge=1, le=50, description="Quantidade máxima de sugestões"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Retorna lista de sugestões de valores cadastrados por prefixo em bens ativos (Role: Técnico)."""
    use_case = GetSuggestionsUseCase(db)
    try:
        return use_case.execute(field=field, prefix=prefix, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/export")
def export_equipments(
    type: List[int] | None = Query(default=None, description="Filtro por IDs de tipo de equipamento"),
    sector: List[int] | None = Query(default=None, description="Filtro por IDs de setor"),
    status_id: List[int] | None = Query(default=None, alias="status", description="Filtro por IDs de situação patrimonial"),
    patrimony_number: List[str] | None = Query(default=None, description="Filtro por número de patrimônio"),
    serial_number: List[str] | None = Query(default=None, description="Filtro por número de série"),
    search: str | None = Query(default=None, description="Busca textual global"),
    sort_by: str = Query(default="created_at", description="Campo para ordenação"),
    sort_dir: str = Query(default="desc", description="Direção da ordenação: asc/desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Exporta equipamentos cadastrados em planilha Excel .xlsx (Role: Técnico)."""
    use_case = ExportEquipmentsUseCase(db)
    file_bytes, filename = use_case.execute(
        equipment_type_ids=type,
        sector_ids=sector,
        status_ids=status_id,
        patrimony_number=patrimony_number,
        serial_number=serial_number,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return Response(
        content=file_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{id}", response_model=EquipmentResponse)
def get_equipment_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Retorna detalhes de um equipamento e seu histórico (Role: Técnico)."""
    use_case = GetEquipmentDetailUseCase(db)
    try:
        return use_case.execute(id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}", response_model=EquipmentResponse)
def update_equipment(
    id: int,
    data: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Atualiza dados de um equipamento (Role: Técnico)."""
    use_case = UpdateEquipmentUseCase(db)
    detail_use_case = GetEquipmentDetailUseCase(db)
    try:
        use_case.execute(id, data)
        db.commit()
        return detail_use_case.execute(id)
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{id}", response_model=MessageResponse)
def delete_equipment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Executa exclusão lógica (Soft Delete) do equipamento (Role: Técnico)."""
    use_case = DeleteEquipmentUseCase(db)
    try:
        use_case.execute(id)
        db.commit()
        return MessageResponse(message="Equipamento excluído logicamente com sucesso.")
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{id}/restore", response_model=EquipmentResponse)
def restore_equipment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Restaura equipamento previamente excluído logicamente (Role: Técnico). Retorna 409 se houver conflito de identificadores ativos."""
    use_case = RestoreEquipmentUseCase(db)
    detail_use_case = GetEquipmentDetailUseCase(db)
    try:
        use_case.execute(id)
        db.commit()
        return detail_use_case.execute(id)
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{id}/windows-key", response_model=EquipmentSecretKeyResponse)
def get_windows_key(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Retorna a chave do produto do Windows decriptografada para o técnico autenticado (Role: Técnico)."""
    use_case = GetDecryptedWindowsKeyUseCase(db)
    try:
        return use_case.execute(id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Movimentações ---

@router.post("/{id}/movements", response_model=EquipmentMovementResponse, status_code=status.HTTP_201_CREATED)
def record_movement(
    id: int,
    data: EquipmentMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Registra uma transferência de setor e auto-ajusta a cadeia cronológica (Role: Técnico)."""
    use_case = MovementsUseCase(db)
    try:
        movement = use_case.record_movement(
            equipment_id=id,
            data=data,
            performed_by_user_id=current_user.id,
        )
        db.commit()
        db.refresh(movement)
        return movement
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}/movements/{movement_id}", response_model=EquipmentMovementResponse)
def update_movement(
    id: int,
    movement_id: int,
    data: EquipmentMovementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Edita uma transferência existente e reavalia o encadeamento cronológico (Role: Técnico)."""
    use_case = MovementsUseCase(db)
    try:
        movement = use_case.update_movement(
            equipment_id=id,
            movement_id=movement_id,
            data=data,
        )
        db.commit()
        db.refresh(movement)
        return movement
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# --- Manutenções ---

@router.post("/{id}/maintenances", response_model=EquipmentMaintenanceResponse, status_code=status.HTTP_201_CREATED)
def start_maintenance(
    id: int,
    data: EquipmentMaintenanceStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Inicia uma intervenção de manutenção, alterando automaticamente a situação do bem para 'Em manutenção' (Role: Técnico)."""
    use_case = MaintenancesUseCase(db)
    try:
        maintenance = use_case.start_maintenance(
            equipment_id=id,
            data=data,
            performed_by_user_id=current_user.id,
        )
        db.commit()
        db.refresh(maintenance)
        return maintenance
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/maintenances/{maintenance_id}/complete", response_model=EquipmentMaintenanceResponse)
def complete_maintenance(
    id: int,
    maintenance_id: int,
    data: EquipmentMaintenanceComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Conclui uma manutenção em aberto exigindo a escolha da nova situação patrimonial do equipamento (Role: Técnico)."""
    use_case = MaintenancesUseCase(db)
    try:
        maintenance = use_case.complete_maintenance(
            equipment_id=id,
            maintenance_id=maintenance_id,
            data=data,
        )
        db.commit()
        db.refresh(maintenance)
        return maintenance
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{id}/maintenances/{maintenance_id}", response_model=EquipmentMaintenanceResponse)
def update_maintenance(
    id: int,
    maintenance_id: int,
    data: EquipmentMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Atualiza dados cadastrais de uma manutenção (Role: Técnico)."""
    use_case = MaintenancesUseCase(db)
    try:
        maintenance = use_case.update_maintenance(
            equipment_id=id,
            maintenance_id=maintenance_id,
            data=data,
        )
        db.commit()
        db.refresh(maintenance)
        return maintenance
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
