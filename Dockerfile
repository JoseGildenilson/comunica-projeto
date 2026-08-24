# ==========================================
# Multi-stage Dockerfile para Backend FastAPI
# ==========================================

# Estágio Base com dependências e uv
FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

WORKDIR /app

# Instala dependências de sistema mínimas para compilação e PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalação do binário do uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia arquivos de definição de dependência
COPY pyproject.toml uv.lock ./

# Instala dependências do projeto no ambiente virtual
RUN uv sync --frozen --no-cache

# Copia script de entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copia código-fonte e configurações
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini
COPY spec/ /app/spec/

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Modo Desenvolvimento padrão (com reload)
FROM base AS development
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Modo Produção (workers otimizados)
FROM base AS production
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
