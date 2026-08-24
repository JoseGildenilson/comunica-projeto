"""Aplicação principal do FastAPI."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from src.api.routes import router as auth_router
# pyrefly: ignore [missing-import]
from src.api.dashboard_routes import router as dashboard_router
# pyrefly: ignore [missing-import]
from src.api.equipment_routes import router as equipment_router
from src.api.import_routes import router as import_router
from src.core.config import settings
from src.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de ciclo de vida da aplicação (criação de tabelas no banco de dados)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sistema de Gestão de Patrimônio e Suporte",
    version="0.1.0",
    lifespan=lifespan,
)

# Inclui os roteadores da aplicação
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(equipment_router)
app.include_router(import_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return {"status": "ok", "app": settings.PROJECT_NAME}
