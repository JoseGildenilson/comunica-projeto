"""Modelos ORM de domínio para o SQLAlchemy 2.0."""
from datetime import datetime, timezone
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import INET, MACADDR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class EquipmentType(Base):
    """Modelo ORM representando o catálogo de tipos de equipamentos."""
    __tablename__ = "equipment_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class Sector(Base):
    """Modelo ORM representando o catálogo de setores / localizações."""
    __tablename__ = "sectors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class EquipmentStatus(Base):
    """Modelo ORM representando o catálogo de situações patrimoniais."""
    __tablename__ = "equipment_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class MaintenanceType(Base):
    """Modelo ORM representando o catálogo de tipos de manutenção."""
    __tablename__ = "maintenance_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class User(Base):
    """Modelo ORM representando um usuário registrado no sistema."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="tecnico")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        CheckConstraint("role = 'tecnico'", name="chk_users_role_tecnico"),
    )


class LoginAttempt(Base):
    """Modelo ORM registrando tentativas de login por IP para controle de rate limit e auditoria."""
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_attempted: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(INET, nullable=False)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Equipment(Base):
    """Modelo ORM representando um equipamento de TI (Patrimônio)."""
    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patrimony_number: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)

    equipment_type_id: Mapped[int] = mapped_column(ForeignKey("equipment_types.id"), nullable=False)
    sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id"), nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("equipment_statuses.id"), nullable=False)

    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(MACADDR, nullable=True)
    printer_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    windows_product_key_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    __table_args__ = (
        CheckConstraint(
            "ip_address IS NULL OR (family(ip_address) = 4 AND masklen(ip_address) = 32) OR (family(ip_address) = 6 AND masklen(ip_address) = 128)",
            name="chk_equipments_ip_host_only",
        ),
    )

    equipment_type: Mapped["EquipmentType"] = relationship("EquipmentType")
    sector: Mapped["Sector"] = relationship("Sector")
    status: Mapped["EquipmentStatus"] = relationship("EquipmentStatus")

    movements: Mapped[list["EquipmentMovement"]] = relationship(
        "EquipmentMovement",
        back_populates="equipment",
        cascade="all, delete-orphan",
        order_by="asc(EquipmentMovement.movement_date), asc(EquipmentMovement.id)",
    )
    maintenances: Mapped[list["EquipmentMaintenance"]] = relationship(
        "EquipmentMaintenance",
        back_populates="equipment",
        cascade="all, delete-orphan",
        order_by="desc(EquipmentMaintenance.started_at)",
    )


class EquipmentMovement(Base):
    """Modelo ORM registrando histórico imutável de transferências de setor."""
    __tablename__ = "equipment_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), index=True, nullable=False)
    origin_sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id"), nullable=False)
    destination_sector_id: Mapped[int] = mapped_column(ForeignKey("sectors.id"), nullable=False)
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    performed_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("origin_sector_id <> destination_sector_id", name="chk_movement_different_sectors"),
        CheckConstraint("movement_date <= (now() + interval '5 minutes')", name="chk_movement_date_not_future"),
    )

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="movements")
    origin_sector: Mapped["Sector"] = relationship("Sector", foreign_keys=[origin_sector_id])
    destination_sector: Mapped["Sector"] = relationship("Sector", foreign_keys=[destination_sector_id])
    performed_by_user: Mapped["User"] = relationship("User", foreign_keys=[performed_by_user_id])


class EquipmentMaintenance(Base):
    """Modelo ORM registrando intervenção e ciclo de vida de manutenção."""
    __tablename__ = "equipment_maintenances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), index=True, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    maintenance_type_id: Mapped[int] = mapped_column(ForeignKey("maintenance_types.id"), nullable=False)
    performed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("completed_at IS NULL OR completed_at >= started_at", name="chk_maintenance_completion_after_start"),
    )

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="maintenances")
    maintenance_type: Mapped["MaintenanceType"] = relationship("MaintenanceType")
    performed_by_user: Mapped["User | None"] = relationship("User", foreign_keys=[performed_by_user_id])
