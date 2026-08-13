"""Schemas Pydantic para validação e transporte de dados (DTOs)."""
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
