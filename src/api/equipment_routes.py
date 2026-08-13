"""Roteador HTTP do FastAPI para Gestão de Equipamentos (Patrimônio)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from src.api.dependencies import require_tecnico_role
from src.core.database import get_db
from src.domain.models import User
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
    EquipmentMaintenanceUpdate,
    EquipmentMaintenanceResponse,
    MessageResponse,
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
)

router = APIRouter(prefix="/api/v1/equipments", tags=["Equipamentos"])


@router.get("", response_model=EquipmentListResponse)
def list_equipments(
    page: int = Query(default=1, ge=1, description="Número da página"),
    limit: int = Query(default=25, ge=1, le=100, description="Itens por página"),
    equipment_type: List[str] | None = Query(default=None, alias="type"),
    location: List[str] | None = Query(default=None),
    status: List[str] | None = Query(default=None),
    patrimony_number: List[str] | None = Query(default=None),
    serial_number: List[str] | None = Query(default=None),
    product_number: List[str] | None = Query(default=None),
    search: str | None = Query(default=None, description="Busca global"),
    sort_by: str = Query(default="created_at", description="Campo para ordenação"),
    sort_dir: str = Query(default="desc", description="Direção da ordenação: asc/desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Lista equipamentos cadastrados com paginação, ordenação e múltiplos filtros combinados (Role: Técnico)."""
    use_case = ListEquipmentsUseCase(db)
    return use_case.execute(
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


@router.post("", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
def create_equipment(
    data: EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Cadastra um novo equipamento (Role: Técnico)."""
    use_case = CreateEquipmentUseCase(db)
    try:
        equipment = use_case.execute(data)
        db.commit()
        db.refresh(equipment)
        return equipment
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/tags", response_model=list[EquipmentTagResponse])
def list_tags(
    category: str | None = Query(default=None, description="Filtrar por categoria: tipo, localizacao, situacao"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Lista todas as tags dinâmicas ou filtradas por categoria (Role: Técnico)."""
    use_case = ManageTagsUseCase(db)
    return use_case.list_tags(category=category)


@router.post("/tags", response_model=EquipmentTagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    data: EquipmentTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Cria uma nova tag em tempo real (Role: Técnico)."""
    use_case = ManageTagsUseCase(db)
    tag = use_case.create_tag(data)
    db.commit()
    db.refresh(tag)
    return tag


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
    try:
        equipment = use_case.execute(id, data)
        db.commit()
        db.refresh(equipment)
        return equipment
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{id}/movements", response_model=EquipmentMovementResponse, status_code=status.HTTP_201_CREATED)
def record_movement(
    id: int,
    data: EquipmentMovementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Registra uma movimentação de localização do equipamento (Role: Técnico)."""
    use_case = RecordMovementUseCase(db)
    try:
        movement = use_case.execute(id, data)
        db.commit()
        db.refresh(movement)
        return movement
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{id}/maintenances", response_model=EquipmentMaintenanceResponse, status_code=status.HTTP_201_CREATED)
def record_maintenance(
    id: int,
    data: EquipmentMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Registra uma intervenção de manutenção no equipamento (Role: Técnico)."""
    use_case = RecordMaintenanceUseCase(db)
    try:
        maintenance = use_case.execute(id, data)
        db.commit()
        db.refresh(maintenance)
        return maintenance
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{id}/maintenances/{maintenance_id}", response_model=EquipmentMaintenanceResponse)
def update_maintenance(
    id: int,
    maintenance_id: int,
    data: EquipmentMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Atualiza os dados de uma manutenção existente (Role: Técnico)."""
    use_case = UpdateMaintenanceUseCase(db)
    try:
        maintenance = use_case.execute(
            equipment_id=id,
            maintenance_id=maintenance_id,
            maintenance_date=data.maintenance_date,
            maintenance_type=data.maintenance_type,
            description=data.description,
            notes=data.notes,
        )
        db.commit()
        db.refresh(maintenance)
        return maintenance
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{id}/maintenances/{maintenance_id}", response_model=MessageResponse)
def delete_maintenance(
    id: int,
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tecnico_role),
):
    """Exclui um registro de manutenção do histórico do equipamento (Role: Técnico)."""
    use_case = DeleteMaintenanceUseCase(db)
    try:
        use_case.execute(equipment_id=id, maintenance_id=maintenance_id)
        db.commit()
        return MessageResponse(message="Manutenção excluída com sucesso.")
    except KeyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
