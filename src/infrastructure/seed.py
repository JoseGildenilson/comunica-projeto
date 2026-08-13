"""Script para popular o banco de dados com dados iniciais (seed) e fictícios para testes."""
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.core.security import hash_password
from src.domain.models import User, Equipment, EquipmentTag, Ticket

DEFAULT_TAGS = [
    # Tipos
    ("tipo", "Desktop"),
    ("tipo", "Notebook"),
    ("tipo", "Monitor"),
    ("tipo", "Impressora"),
    # Localizações
    ("localizacao", "TI"),
    ("localizacao", "Comunicação"),
    ("localizacao", "Rádio Produção"),
    ("localizacao", "Diretoria"),
    # Situações
    ("situacao", "Em uso"),
    ("situacao", "Ocioso"),
    ("situacao", "Em manutenção"),
    ("situacao", "Aguardando recolhimento"),
    ("situacao", "Baixado"),
]


def seed_default_tags(db: Session) -> list[EquipmentTag]:
    """Insere as tags padrão no banco de dados se ainda não existirem."""
    created_tags = []
    for category, name in DEFAULT_TAGS:
        existing = (
            db.query(EquipmentTag)
            .filter(EquipmentTag.category == category, EquipmentTag.name == name)
            .first()
        )
        if not existing:
            tag = EquipmentTag(category=category, name=name)
            db.add(tag)
            created_tags.append(tag)
    if created_tags:
        db.flush()
    return created_tags


def seed_database():
    """Insere dados fictícios no banco de dados se ainda não existirem."""
    db = SessionLocal()
    try:
        # Seed tags primeiro
        seed_default_tags(db)

        tecnico = db.query(User).filter(User.email == "tecnico@empresa.com").first()
        if not tecnico:
            tecnico = User(
                email="tecnico@empresa.com",
                hashed_password=hash_password("senha123"),
                role="tecnico",
                is_active=True,
            )
            db.add(tecnico)

        colaborador = db.query(User).filter(User.email == "colaborador@empresa.com").first()
        if not colaborador:
            colaborador = User(
                email="colaborador@empresa.com",
                hashed_password=hash_password("senha123"),
                role="colaborador",
                is_active=True,
            )
            db.add(colaborador)

        db.flush()

        # Equipamentos
        if db.query(Equipment).count() == 0:
            equipments = [
                Equipment(
                    description="Notebook Dell Latitude 3420 Core i5, 16GB RAM",
                    serial_number="SN-DELL-3420",
                    patrimony_number="PAT-1001",
                    hostname="NOTE-TI-01",
                    brand="Dell",
                    equipment_type="Notebook",
                    location="TI",
                    status="Em uso",
                ),
                Equipment(
                    description="Monitor LG 29' Ultrawide IPS 75Hz",
                    serial_number="SN-LG-29-001",
                    patrimony_number="PAT-1002",
                    brand="LG",
                    equipment_type="Monitor",
                    location="Comunicação",
                    status="Ocioso",
                ),
                Equipment(
                    description="Desktop OptiPlex 7090",
                    serial_number="SN-DELL-7090",
                    patrimony_number="PAT-1003",
                    hostname="DESK-RADIO-01",
                    brand="Dell",
                    equipment_type="Desktop",
                    location="Rádio Produção",
                    status="Em uso",
                ),
                Equipment(
                    description="MacBook Pro M2 14' 16GB RAM",
                    serial_number="SN-MAC-M2-01",
                    patrimony_number="PAT-1004",
                    brand="Apple",
                    equipment_type="Notebook",
                    location="Diretoria",
                    status="Em manutenção",
                ),
            ]
            db.add_all(equipments)

        # Tickets
        if db.query(Ticket).count() == 0:
            tickets = [
                Ticket(title="Troca de teclado quebrada", description="Tecla barra de espaço afundou", status="pendente", created_by_id=colaborador.id),
                Ticket(title="Lente do monitor piscando", description="Pisca aleatoriamente durante o dia", status="em_andamento", created_by_id=colaborador.id),
                Ticket(title="Upgrade de memória ram", description="Solicitação de +16GB para virtualização", status="pendente", created_by_id=tecnico.id),
                Ticket(title="Instalação de software VPN", description="Necessário para home office", status="resolvido", created_by_id=colaborador.id),
            ]
            db.add_all(tickets)

        db.commit()
        print("Banco de dados semeado com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao semear banco de dados: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
