"""Script para popular o banco de dados com dados fictícios para testes."""
from src.core.database import SessionLocal
from src.core.security import hash_password
from src.domain.models import User, Equipment, Ticket


def seed_database():
    """Insere dados fictícios no banco de dados se ainda não existirem."""
    db = SessionLocal()
    try:
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
                Equipment(name="Notebook Dell Latitude 3420", description="Core i5, 16GB RAM, SSD 512GB", status="em_uso"),
                Equipment(name="Monitor LG 29' Ultrawide", description="IPS 75Hz Full HD", status="disponível"),
                Equipment(name="Teclado Mecânico Keychron K2", description="Wireless RGB Red Switch", status="disponível"),
                Equipment(name="MacBook Pro M2 14'", description="16GB RAM, SSD 512GB", status="manutenção"),
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
