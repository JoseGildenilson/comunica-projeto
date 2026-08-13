"""Testes unitários para o script de seed de tags padrão e banco de dados."""
from sqlalchemy.orm import Session
from src.domain.models import EquipmentTag, User
from src.infrastructure.seed import seed_default_tags, seed_database


def test_seed_default_tags_idempotency(db_session: Session):
    """Testa a criação de tags padrão e verifica idempotência ao rodar duas vezes."""
    created = seed_default_tags(db_session)
    assert len(created) == 13

    # Segunda execução não deve criar duplicados
    second_run = seed_default_tags(db_session)
    assert len(second_run) == 0

    total_tags = db_session.query(EquipmentTag).count()
    assert total_tags == 13
