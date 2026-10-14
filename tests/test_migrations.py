"""Testes de integridade das migrações do Alembic (TASK-QA-14 / CRIT-01)."""
import os
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_migrations_lifecycle(tmp_path):
    """Testa o ciclo de vida completo das migrações: upgrade head -> downgrade base -> upgrade head."""
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if test_db_url:
        db_url = test_db_url
    else:
        db_file = tmp_path / "test_migration.db"
        db_url = f"sqlite:///{db_file}"

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", db_url)

    # 1. Aplica todas as migrações (upgrade head)
    command.upgrade(cfg, "head")

    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "equipments" in tables
    assert "equipment_tags" in tables
    assert "equipment_movements" in tables
    assert "equipment_maintenances" in tables
    assert "alembic_version" in tables

    # 2. Reverte todas as migrações (downgrade base)
    command.downgrade(cfg, "base")

    inspector = inspect(engine)
    remaining_tables = [t for t in inspector.get_table_names() if t != "alembic_version"]
    assert len(remaining_tables) == 0

    # 3. Reaplica todas as migrações (upgrade head)
    command.upgrade(cfg, "head")

    inspector = inspect(engine)
    reapplied_tables = inspector.get_table_names()
    assert "users" in reapplied_tables
    assert "equipments" in reapplied_tables
    assert "equipment_tags" in reapplied_tables
    assert "equipment_movements" in reapplied_tables
    assert "equipment_maintenances" in reapplied_tables
    engine.dispose()

