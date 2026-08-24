"""Repositórios SQLAlchemy para persistência de dados.

Nota: Em cumprimento à Constituição, os repositórios NÃO executam commit ou rollback.
O controle de transação é feito no nível do caso de uso ou rota HTTP.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, func, or_, desc, asc
from sqlalchemy.orm import Session, selectinload
from src.domain.models import (
    User,
    LoginAttempt,
    Ticket,
    Equipment,
    EquipmentTag,
    EquipmentMovement,
    EquipmentMaintenance,
)


class DashboardRepository:
    """Repositório para consulta de métricas e indicadores do Dashboard."""

    def __init__(self, db: Session):
        self.db = db

    def count_tickets_by_status(self, status: str, user_id: int | None = None) -> int:
        """Conta a quantidade de tickets com determinado status (global ou por usuário)."""
        stmt = select(func.count(Ticket.id)).where(Ticket.status == status)
        if user_id is not None:
            stmt = stmt.where(Ticket.created_by_id == user_id)
        count = self.db.execute(stmt).scalar()
        return count or 0

    def count_total_equipments(self) -> int:
        """Conta a quantidade total de equipamentos cadastrados."""
        stmt = select(func.count(Equipment.id))
        count = self.db.execute(stmt).scalar()
        return count or 0


class UserRepository:
    """Repositório de acesso a dados da entidade User."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Busca usuário por email."""
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        """Busca usuário por ID."""
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User) -> User:
        """Adiciona novo usuário à sessão (sem commit)."""
        self.db.add(user)
        return user


class LoginAttemptRepository:
    """Repositório de registro e contagem de tentativas de login por IP."""

    def __init__(self, db: Session):
        self.db = db

    def count_recent_failed_attempts(self, ip_address: str, window_minutes: int = 15) -> int:
        """Conta tentativas malsucedidas de um IP na janela de tempo especificada."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        stmt = (
            select(func.count(LoginAttempt.id))
            .where(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.success.is_(False),
                LoginAttempt.attempted_at >= cutoff_time,
            )
        )
        count = self.db.execute(stmt).scalar()
        return count or 0

    def record_attempt(self, ip_address: str, success: bool) -> LoginAttempt:
        """Registra uma nova tentativa de login para um IP (sem commit)."""
        attempt = LoginAttempt(
            ip_address=ip_address,
            success=success,
            attempted_at=datetime.now(timezone.utc),
        )
        self.db.add(attempt)
        return attempt


class EquipmentRepository:
    """Repositório de persistência e consulta da entidade Equipment."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, equipment_id: int) -> Equipment | None:
        """Busca equipamento por ID."""
        stmt = select(Equipment).where(Equipment.id == equipment_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_serial_number(self, serial_number: str) -> Equipment | None:
        """Busca equipamento por Nº de Série."""
        stmt = select(Equipment).where(Equipment.serial_number == serial_number)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_patrimony_number(self, patrimony_number: str) -> Equipment | None:
        """Busca equipamento por Nº de Patrimônio."""
        stmt = select(Equipment).where(Equipment.patrimony_number == patrimony_number)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_hostname(self, hostname: str) -> Equipment | None:
        """Busca equipamento por Hostname."""
        stmt = select(Equipment).where(Equipment.hostname == hostname)
        return self.db.execute(stmt).scalar_one_or_none()

    def _build_filter_query(
        self,
        equipment_type: list[str] | str | None = None,
        location: list[str] | str | None = None,
        status: list[str] | str | None = None,
        patrimony_number: list[str] | str | None = None,
        serial_number: list[str] | str | None = None,
        product_number: list[str] | str | None = None,
        search: str | None = None,
    ):
        query = select(Equipment)

        def normalize_list(val: list[str] | str | None) -> list[str]:
            if val is None:
                return []
            if isinstance(val, list):
                return [v for v in val if v]
            return [val] if val else []

        types = normalize_list(equipment_type)
        if types:
            query = query.where(Equipment.equipment_type.in_(types))

        locations = normalize_list(location)
        if locations:
            query = query.where(Equipment.location.in_(locations))

        statuses = normalize_list(status)
        if statuses:
            query = query.where(Equipment.status.in_(statuses))

        patrimonies = normalize_list(patrimony_number)
        if patrimonies:
            query = query.where(or_(*[Equipment.patrimony_number.ilike(f"%{p}%") for p in patrimonies]))

        serials = normalize_list(serial_number)
        if serials:
            query = query.where(or_(*[Equipment.serial_number.ilike(f"%{s}%") for s in serials]))

        products = normalize_list(product_number)
        if products:
            query = query.where(or_(*[Equipment.product_number.ilike(f"%{pr}%") for pr in products]))

        # Busca geral em múltiplos campos
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Equipment.description.ilike(search_pattern),
                    Equipment.brand.ilike(search_pattern),
                    Equipment.patrimony_number.ilike(search_pattern),
                    Equipment.serial_number.ilike(search_pattern),
                    Equipment.product_number.ilike(search_pattern),
                    Equipment.hostname.ilike(search_pattern),
                )
            )

        return query

    def list_paginated_and_filtered(
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
    ) -> tuple[list[Equipment], int]:
        """Retorna equipamentos paginados e filtrados com o total de registros (suporta múltiplos valores por filtro)."""
        query = self._build_filter_query(
            equipment_type=equipment_type,
            location=location,
            status=status,
            patrimony_number=patrimony_number,
            serial_number=serial_number,
            product_number=product_number,
            search=search,
        )

        # Totalizador antes da paginação
        count_stmt = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        # Ordenação
        sort_column = getattr(Equipment, sort_by, Equipment.created_at)
        if sort_dir.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # Paginação
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        items = list(self.db.execute(query).scalars().all())
        return items, total

    def list_all_filtered(
        self,
        equipment_type: list[str] | str | None = None,
        location: list[str] | str | None = None,
        status: list[str] | str | None = None,
        patrimony_number: list[str] | str | None = None,
        serial_number: list[str] | str | None = None,
        product_number: list[str] | str | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> list[Equipment]:
        """Retorna todos os equipamentos filtrados sem paginação com manutenções pré-carregadas."""
        query = self._build_filter_query(
            equipment_type=equipment_type,
            location=location,
            status=status,
            patrimony_number=patrimony_number,
            serial_number=serial_number,
            product_number=product_number,
            search=search,
        ).options(selectinload(Equipment.maintenances))

        sort_column = getattr(Equipment, sort_by, Equipment.created_at)
        if sort_dir.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        return list(self.db.execute(query).scalars().all())

    def create(self, equipment: Equipment) -> Equipment:
        """Adiciona novo equipamento à sessão."""
        self.db.add(equipment)
        return equipment

    def get_distinct_values_by_prefix(
        self,
        field_name: str,
        prefix: str,
        limit: int = 10,
    ) -> list[str]:
        """Retorna valores distintos de um campo filtrados por prefixo e ordenados alfabeticamente."""
        column = getattr(Equipment, field_name, None)
        if column is None:
            return []

        stmt = (
            select(column)
            .where(column.is_not(None), column.ilike(f"{prefix}%"))
            .distinct()
            .order_by(asc(column))
            .limit(limit)
        )
        results = self.db.execute(stmt).scalars().all()
        return [r for r in results if r]



class EquipmentTagRepository:
    """Repositório para gerenciamento das tags dinâmicas."""

    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> list[EquipmentTag]:
        """Retorna todas as tags."""
        stmt = select(EquipmentTag).order_by(EquipmentTag.category, EquipmentTag.name)
        return list(self.db.execute(stmt).scalars().all())

    def list_by_category(self, category: str) -> list[EquipmentTag]:
        """Retorna tags filtradas por categoria ('tipo', 'localizacao', 'situacao')."""
        stmt = (
            select(EquipmentTag)
            .where(EquipmentTag.category == category)
            .order_by(EquipmentTag.name)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_category_and_name(self, category: str, name: str) -> EquipmentTag | None:
        """Busca tag por categoria e nome."""
        stmt = select(EquipmentTag).where(
            EquipmentTag.category == category, EquipmentTag.name == name
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, tag: EquipmentTag) -> EquipmentTag:
        """Adiciona nova tag à sessão."""
        self.db.add(tag)
        return tag

    def get_by_id(self, tag_id: int) -> EquipmentTag | None:
        """Busca tag por ID."""
        stmt = select(EquipmentTag).where(EquipmentTag.id == tag_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def delete(self, tag: EquipmentTag) -> None:
        """Remove a tag da sessão."""
        self.db.delete(tag)

    def propagate_tag_rename(self, category: str, old_name: str, new_name: str) -> None:
        """Atualiza o nome da tag em todos os equipamentos que utilizam o valor antigo."""
        if category == "tipo":
            stmt = update(Equipment).where(Equipment.equipment_type == old_name).values(equipment_type=new_name)
            self.db.execute(stmt)
        elif category == "localizacao":
            stmt = update(Equipment).where(Equipment.location == old_name).values(location=new_name)
            self.db.execute(stmt)
        elif category == "situacao":
            stmt = update(Equipment).where(Equipment.status == old_name).values(status=new_name)
            self.db.execute(stmt)


class EquipmentMovementRepository:
    """Repositório de histórico de movimentação."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, movement: EquipmentMovement) -> EquipmentMovement:
        """Adiciona nova movimentação à sessão."""
        self.db.add(movement)
        return movement

    def list_by_equipment(self, equipment_id: int) -> list[EquipmentMovement]:
        """Retorna o histórico de movimentações de um equipamento."""
        stmt = (
            select(EquipmentMovement)
            .where(EquipmentMovement.equipment_id == equipment_id)
            .order_by(desc(EquipmentMovement.movement_date))
        )
        return list(self.db.execute(stmt).scalars().all())


class EquipmentMaintenanceRepository:
    """Repositório de histórico de manutenção."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, maintenance_id: int) -> EquipmentMaintenance | None:
        """Busca registro de manutenção por ID."""
        stmt = select(EquipmentMaintenance).where(EquipmentMaintenance.id == maintenance_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, maintenance: EquipmentMaintenance) -> EquipmentMaintenance:
        """Adiciona nova manutenção à sessão."""
        self.db.add(maintenance)
        return maintenance

    def delete(self, maintenance: EquipmentMaintenance) -> None:
        """Remove registro de manutenção da sessão."""
        self.db.delete(maintenance)

    def list_by_equipment(self, equipment_id: int) -> list[EquipmentMaintenance]:
        """Retorna o histórico de manutenções de um equipamento."""
        stmt = (
            select(EquipmentMaintenance)
            .where(EquipmentMaintenance.equipment_id == equipment_id)
            .order_by(desc(EquipmentMaintenance.maintenance_date))
        )
        return list(self.db.execute(stmt).scalars().all())
