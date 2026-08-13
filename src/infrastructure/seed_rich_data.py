"""Script para popular o banco de dados com 35+ equipamentos e históricos para testes visuais em navegador."""
from datetime import datetime, timedelta, timezone
from src.core.database import SessionLocal, Base, engine
from src.core.security import hash_password
from src.domain.models import User, Equipment, EquipmentTag, EquipmentMovement, EquipmentMaintenance, Ticket
from src.infrastructure.seed import seed_default_tags


def seed_rich_equipments():
    """Garante que as tabelas existam e popula 35 equipamentos variados com movimentações e manutenções."""
    # Recria as tabelas no SQLite local para garantir o schema atualizado sem erros de ALTER TABLE
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # 1. Seed Tags
        seed_default_tags(db)

        # 2. Seed Usuários
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

        now = datetime.now(timezone.utc)

        # 3. Criar 35 Equipamentos
        equipment_templates = [
            # Desktops
            ("Dell OptiPlex 7090 Core i7 16GB SSD 512GB", "Desktop", "TI", "Em uso", "Dell", "7090-OPT", "DESK-TI-01", "VK9X2-N8Y4R-W3M2T-K7P1Q-L9Z0A"),
            ("Lenovo ThinkCentre M70q Tiny Core i5 16GB", "Desktop", "Comunicação", "Em uso", "Lenovo", "11DT0025BP", "DESK-COM-01", "WM8R9-B2V4C-N5X7Z-K3P1L-J9Q0W"),
            ("HP EliteDesk 800 G6 Small Form Factor Core i7", "Desktop", "Rádio Produção", "Em uso", "HP", "800G6-SFF", "DESK-RAD-01", None),
            ("Apple Mac Mini M2 16GB SSD 512GB", "Desktop", "Diretoria", "Em uso", "Apple", "MM2-2023", "MAC-DIR-01", None),
            ("Dell Vostro 3710 Small Desktop Core i5", "Desktop", "TI", "Ocioso", "Dell", "V3710", "DESK-TI-02", "P9Z0X-L8W7V-K6J5H-G4F3D-S2A1Q"),
            ("Lenovo ThinkCentre M90q Gen 3 Tiny i9", "Desktop", "Rádio Produção", "Em uso", "Lenovo", "11Q70001BR", "DESK-RAD-02", None),
            ("HP ProDesk 400 G7 Microtower i5 8GB", "Desktop", "Comunicação", "Aguardando recolhimento", "HP", "400G7-MT", "DESK-COM-02", None),
            ("Dell OptiPlex 3080 Tower Core i3", "Desktop", "TI", "Baixado", "Dell", "3080-TWR", "DESK-TI-03", None),

            # Notebooks
            ("Lenovo ThinkPad T480 Core i5 16GB SSD 256GB", "Notebook", "TI", "Em uso", "Lenovo", "20L50001BR", "NOTE-TI-01", "TX9N8-B7V6C-X5Z4M-L3K2J-H1G0F"),
            ("Dell Latitude 3420 Core i5 16GB SSD 512GB", "Notebook", "Comunicação", "Em uso", "Dell", "LAT3420", "NOTE-COM-01", "W8R7V-6C5X4-Z3ML2-K1JH0-GF9ED"),
            ("Apple MacBook Pro M2 14' 16GB SSD 512GB", "Notebook", "Diretoria", "Em uso", "Apple", "MBP14-M2", "MACBOOK-DIR-01", None),
            ("HP ProBook 450 G8 Core i7 16GB SSD 512GB", "Notebook", "Rádio Produção", "Em uso", "HP", "PB450G8", "NOTE-RAD-01", "K9J8H-7G6F5-D4S3A-2Q1WE-R8TY9"),
            ("Lenovo ThinkPad X1 Carbon Gen 10 i7 32GB", "Notebook", "Diretoria", "Em uso", "Lenovo", "21CB0001BR", "NOTE-DIR-02", "M9N8B-7V6C5-X4Z3L-2K1JH-GF0ED"),
            ("Dell Latitude 5430 Core i7 16GB", "Notebook", "TI", "Em manutenção", "Dell", "LAT5430", "NOTE-TI-02", None),
            ("Asus ZenBook 14 Core i7 16GB SSD 512GB", "Notebook", "Comunicação", "Ocioso", "Asus", "UX3402", "NOTE-COM-02", None),
            ("Acer Aspire 5 Core i5 8GB SSD 256GB", "Notebook", "TI", "Baixado", "Acer", "A515-56", "NOTE-TI-03", None),
            ("Lenovo ThinkPad L14 Gen 2 Core i5", "Notebook", "Rádio Produção", "Em uso", "Lenovo", "20X10001BR", "NOTE-RAD-02", None),
            ("Dell Vostro 3510 Core i5 8GB", "Notebook", "Comunicação", "Ocioso", "Dell", "V3510", "NOTE-COM-03", None),

            # Monitores
            ("Monitor LG 29' Ultrawide IPS 75Hz Full HD", "Monitor", "Comunicação", "Em uso", "LG", "29WK600", None, None),
            ("Monitor Dell UltraSharp 27' 4K USB-C U2723QE", "Monitor", "Diretoria", "Em uso", "Dell", "U2723QE", None, None),
            ("Monitor Samsung 24' IPS 75Hz Borderless", "Monitor", "TI", "Em uso", "Samsung", "T350", None, None),
            ("Monitor AOC 24' HERO 144Hz 1ms Gaming/Edição", "Monitor", "Rádio Produção", "Em uso", "AOC", "24G2", None, None),
            ("Monitor Dell 23.8' P2422H Ergostand", "Monitor", "TI", "Ocioso", "Dell", "P2422H", None, None),
            ("Monitor LG 24' Full HD HDMI 75Hz", "Monitor", "Comunicação", "Em uso", "LG", "24MK430H", None, None),
            ("Monitor Philips 21.5' Full HD VGA/HDMI", "Monitor", "Rádio Produção", "Ocioso", "Philips", "221V8", None, None),
            ("Monitor BenQ 27' EW2780 Eye-Care", "Monitor", "Diretoria", "Em uso", "BenQ", "EW2780", None, None),
            ("Monitor Samsung 27' Curved 1800R", "Monitor", "TI", "Aguardando recolhimento", "Samsung", "CF390", None, None),

            # Impressoras
            ("Impressora HP LaserJet Pro M404dw Laser Mono", "Impressora", "TI", "Em uso", "HP", "M404DW", "PRN-TI-01", None),
            ("Impressora Epson EcoTank L3250 Tanque de Tinta", "Impressora", "Comunicação", "Em uso", "Epson", "L3250", "PRN-COM-01", None),
            ("Impressora Brother HL-L2360DW Laser Duplex", "Impressora", "Rádio Produção", "Em uso", "Brother", "HLL2360DW", "PRN-RAD-01", None),
            ("Impressora Canon Mega Tank G3110 Wi-Fi", "Impressora", "Diretoria", "Em uso", "Canon", "G3110", "PRN-DIR-01", None),
            ("Impressora Zebra ZT230 Térmica Etiquetas", "Impressora", "TI", "Em uso", "Zebra", "ZT230", "PRN-LABEL-01", None),
            ("Impressora HP DeskJet Ink Advantage 2776", "Impressora", "Comunicação", "Em manutenção", "HP", "DJ2776", "PRN-COM-02", None),
            ("Impressora Kyocera Ecosys P2040dn Laser", "Impressora", "Rádio Produção", "Ocioso", "Kyocera", "P2040DN", "PRN-RAD-02", None),
        ]

        created_equipments = []
        for i, (desc, etype, loc, stat, brand, prod, host, win_key) in enumerate(equipment_templates, start=1001):
            eq = Equipment(
                description=desc,
                equipment_type=etype,
                location=loc,
                status=stat,
                brand=brand,
                product_number=prod,
                hostname=host,
                patrimony_number=f"PAT-{i}",
                serial_number=f"SN-PATR-{i:04d}",
                windows_key=win_key,
                last_maintenance_at=now - timedelta(days=(i % 40) + 5) if i % 3 == 0 else None,
                notes=f"Equipamento cadastrado para uso do setor de {loc}.",
                created_at=now - timedelta(days=(i % 100)),
            )
            db.add(eq)
            created_equipments.append(eq)

        db.flush()

        # 4. Inserir Históricos de Movimentação e Manutenção para alguns equipamentos
        for eq in created_equipments[:12]:
            # Movimentação
            mov = EquipmentMovement(
                equipment_id=eq.id,
                origin_location="Estoque TI",
                destination_location=eq.location,
                movement_date=now - timedelta(days=15),
                notes="Instalação inicial e alocação da máquina.",
                created_at=now - timedelta(days=15),
            )
            db.add(mov)

            # Manutenção (se tiver)
            if eq.last_maintenance_at:
                maint = EquipmentMaintenance(
                    equipment_id=eq.id,
                    maintenance_date=eq.last_maintenance_at,
                    maintenance_type="Preventiva" if eq.id % 2 == 0 else "Corretiva",
                    description="Limpeza preventiva de ventoinha e substituição de pasta térmica.",
                    notes="Serviço concluído com sucesso e testes executados.",
                    created_at=eq.last_maintenance_at,
                )
                db.add(maint)

        # 5. Seed de alguns tickets fictícios para o Dashboard
        tickets = [
            Ticket(title="Troca de teclado quebrada", description="Tecla barra de espaço afundou", status="pendente", created_by_id=colaborador.id),
            Ticket(title="Lente do monitor piscando", description="Pisca aleatoriamente durante o dia", status="em_andamento", created_by_id=colaborador.id),
            Ticket(title="Upgrade de memória ram", description="Solicitação de +16GB para virtualização", status="pendente", created_by_id=tecnico.id),
            Ticket(title="Instalação de software VPN", description="Necessário para home office", status="resolvido", created_by_id=colaborador.id),
        ]
        db.add_all(tickets)

        db.commit()
        print(f"Sucesso! {len(created_equipments)} equipamentos injetados no banco de dados com histórico completo!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao injetar equipamentos: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_rich_equipments()
