"""Modelos ORM de domínio para o SQLAlchemy 2.0."""
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


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


class LoginAttempt(Base):
    """Modelo ORM registrando tentativas de login por IP para controle de rate limit."""
    __tablename__ = "login_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(String(45), index=True, nullable=False)
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
    description: Mapped[str] = mapped_column(Text, nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    patrimony_number: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    equipment_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(100), index=True, nullable=False, default="Em uso")
    windows_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_maintenance_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    movements: Mapped[list["EquipmentMovement"]] = relationship(
        "EquipmentMovement", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(EquipmentMovement.movement_date)"
    )
    maintenances: Mapped[list["EquipmentMaintenance"]] = relationship(
        "EquipmentMaintenance", back_populates="equipment", cascade="all, delete-orphan", order_by="desc(EquipmentMaintenance.maintenance_date)"
    )


class EquipmentTag(Base):
    """Modelo ORM representando tags dinâmicas (Tipo, Localização, Situação)."""
    __tablename__ = "equipment_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("category", "name", name="uq_equipment_tag_category_name"),
    )


class EquipmentMovement(Base):
    """Modelo ORM registrando histórico imutável de movimentação de localização."""
    __tablename__ = "equipment_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), index=True, nullable=False)
    origin_location: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_location: Mapped[str] = mapped_column(String(100), nullable=False)
    movement_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="movements")


class EquipmentMaintenance(Base):
    """Modelo ORM registrando histórico imutável de manutenção."""
    __tablename__ = "equipment_maintenances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipments.id"), index=True, nullable=False)
    maintenance_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="maintenances")



class Ticket(Base):
    """Modelo ORM representando um chamado/ticket de suporte."""
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pendente")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    created_by: Mapped["User"] = relationship("User", backref="tickets")
