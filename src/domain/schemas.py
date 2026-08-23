"""Schemas Pydantic para validação e transporte de dados (DTOs)."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema para requisição de login."""
    email: EmailStr = Field(..., description="Endereço de email do usuário")
    password: str = Field(..., min_length=1, description="Senha do usuário")


class UserResponse(BaseModel):
    """Schema de resposta representando os dados públicos do usuário."""
    id: int
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema para resposta de autenticação com token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Schema genérico para respostas de mensagem ou erro."""
    message: str


class DashboardMetricsResponse(BaseModel):
    """Schema para resposta dos indicadores do Dashboard."""
    tickets_pending: int
    tickets_in_progress: int
    equipments_total: int | None = None


# --- Schemas de Equipamentos (Patrimônio) ---

class EquipmentTagCreate(BaseModel):
    """Schema para criação de nova Tag."""
    category: str = Field(..., min_length=1, description="Categoria: 'tipo', 'localizacao' ou 'situacao'")
    name: str = Field(..., min_length=1, description="Nome da tag")


class EquipmentTagResponse(BaseModel):
    """Schema de resposta para Tag."""
    id: int
    category: str
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentTagUpdate(BaseModel):
    """Schema para atualização/renomeação de Tag."""
    name: str = Field(..., min_length=1, description="Novo nome da tag")


class EquipmentMovementCreate(BaseModel):
    """Schema para registro de movimentação de localização."""
    origin_location: str = Field(..., min_length=1, description="Localização de origem")
    destination_location: str = Field(..., min_length=1, description="Localização de destino")
    movement_date: datetime = Field(..., description="Data da movimentação")
    notes: str | None = Field(default=None, description="Observação opcional")


class EquipmentMovementResponse(BaseModel):
    """Schema de resposta para movimentação."""
    id: int
    equipment_id: int
    origin_location: str
    destination_location: str
    movement_date: datetime
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentMaintenanceCreate(BaseModel):
    """Schema para registro de manutenção."""
    maintenance_date: datetime = Field(..., description="Data da manutenção")
    maintenance_type: str = Field(default="Manutenção", description="Tipo ou título da manutenção")
    description: str = Field(..., min_length=1, description="Descrição ou lista de itens da intervenção")
    notes: str | None = Field(default=None, description="Observações técnicas adicionais")


class EquipmentMaintenanceUpdate(BaseModel):
    """Schema para edição de manutenção."""
    maintenance_date: datetime | None = Field(default=None, description="Data da manutenção")
    maintenance_type: str | None = Field(default=None, description="Tipo ou título da manutenção")
    description: str | None = Field(default=None, description="Descrição ou lista de itens da intervenção")
    notes: str | None = Field(default=None, description="Observações técnicas adicionais")


class EquipmentMaintenanceResponse(BaseModel):
    """Schema de resposta para manutenção."""
    id: int
    equipment_id: int
    maintenance_date: datetime
    maintenance_type: str
    description: str
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentCreate(BaseModel):
    """Schema para cadastro de equipamento."""
    serial_number: str = Field(..., min_length=1, description="Nº de Série (Obrigatório e único)")
    description: str = Field(..., min_length=1, description="Descrição do equipamento")
    equipment_type: str = Field(..., min_length=1, description="Tipo (Tag)")
    location: str = Field(..., min_length=1, description="Localização (Tag)")
    status: str = Field(default="Em uso", min_length=1, description="Situação (Tag)")
    patrimony_number: str | None = Field(default=None, description="Nº de Patrimônio (Opcional, mas único)")
    hostname: str | None = Field(default=None, description="Hostname (Opcional, mas único)")
    brand: str | None = Field(default=None, description="Marca")
    product_number: str | None = Field(default=None, description="Nº do Produto")
    windows_key: str | None = Field(default=None, description="Chave Windows")
    last_maintenance_at: datetime | None = Field(default=None, description="Data da última manutenção")
    notes: str | None = Field(default=None, description="Observações")


class EquipmentUpdate(BaseModel):
    """Schema para atualização parcial/total de equipamento."""
    serial_number: str | None = None
    description: str | None = None
    equipment_type: str | None = None
    location: str | None = None
    status: str | None = None
    patrimony_number: str | None = None
    hostname: str | None = None
    brand: str | None = None
    product_number: str | None = None
    windows_key: str | None = None
    last_maintenance_at: datetime | None = None
    notes: str | None = None


class EquipmentResponse(BaseModel):
    """Schema de resposta completo do equipamento."""
    id: int
    serial_number: str
    patrimony_number: str | None = None
    hostname: str | None = None
    description: str
    brand: str | None = None
    product_number: str | None = None
    equipment_type: str
    location: str
    status: str
    windows_key: str | None = None
    last_maintenance_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    movements: list[EquipmentMovementResponse] = []
    maintenances: list[EquipmentMaintenanceResponse] = []

    model_config = ConfigDict(from_attributes=True)


class EquipmentListResponse(BaseModel):
    """Schema para resposta paginada de equipamentos."""
    items: list[EquipmentResponse]
    total: int
    page: int
    limit: int
    pages: int
