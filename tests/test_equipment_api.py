"""Testes de API HTTP para os endpoints de Gestão de Equipamentos (FastAPI)."""
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from src.core.security import create_access_token


@pytest.fixture
def test_users(create_test_user):
    tecnico = create_test_user(email="tecnico_eq@empresa.com", role="tecnico")
    colaborador = create_test_user(email="colaborador_eq@empresa.com", role="colaborador")
    return {"tecnico": tecnico, "colaborador": colaborador}


@pytest.fixture
def tecnico_cookie(test_users):
    tec = test_users["tecnico"]
    return create_access_token({"sub": str(tec.id), "email": tec.email, "role": tec.role})


@pytest.fixture
def colaborador_cookie(test_users):
    colab = test_users["colaborador"]
    return create_access_token({"sub": str(colab.id), "email": colab.email, "role": colab.role})


@pytest.mark.anyio
async def test_equipment_api_rbac_forbidden_for_colaborador(client: AsyncClient, colaborador_cookie: str):
    """Testa que colaborador recebe HTTP 403 Forbidden ao acessar rotas de Equipamentos (RN-EQ-10)."""
    client.cookies.set("access_token", colaborador_cookie)
    response = await client.get("/api/v1/equipments")
    assert response.status_code == 403
    assert "restrito" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_equipment_api_create_and_get_detail_tecnico(client: AsyncClient, tecnico_cookie: str):
    """Testa cadastro e consulta detalhada por Técnico (Cenário BDD 1 & 2)."""
    client.cookies.set("access_token", tecnico_cookie)

    payload = {
        "serial_number": "SN_API_001",
        "patrimony_number": "PAT_API_001",
        "hostname": "HOST-API-01",
        "description": "Dell OptiPlex 7090 API",
        "equipment_type": "Desktop",
        "location": "TI",
        "status": "Em uso",
        "brand": "Dell",
        "windows_key": "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
    }
    create_resp = await client.post("/api/v1/equipments", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.json()
    assert data["id"] is not None
    assert data["serial_number"] == "SN_API_001"

    # Consulta detalhada
    eq_id = data["id"]
    detail_resp = await client.get(f"/api/v1/equipments/{eq_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["description"] == "Dell OptiPlex 7090 API"


@pytest.mark.anyio
async def test_equipment_api_get_detail_404(client: AsyncClient, tecnico_cookie: str):
    """Testa HTTP 404 ao buscar equipamento inexistente."""
    client.cookies.set("access_token", tecnico_cookie)
    resp = await client.get("/api/v1/equipments/9999")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_equipment_api_duplicate_error_400(client: AsyncClient, tecnico_cookie: str):
    """Testa erro HTTP 400 em duplicidade de Nº de Série (Cenário BDD 2)."""
    client.cookies.set("access_token", tecnico_cookie)
    payload = {
        "serial_number": "SN_DUP_API",
        "description": "Primeiro",
        "equipment_type": "Notebook",
        "location": "TI",
    }
    await client.post("/api/v1/equipments", json=payload)

    # Segunda tentativa com o mesmo serial
    resp_dup = await client.post("/api/v1/equipments", json=payload)
    assert resp_dup.status_code == 400
    assert "já está cadastrado" in resp_dup.json()["detail"]


@pytest.mark.anyio
async def test_equipment_api_list_and_filters(client: AsyncClient, tecnico_cookie: str):
    """Testa listagem paginada e filtros na API HTTP."""
    client.cookies.set("access_token", tecnico_cookie)

    for i in range(1, 6):
        await client.post("/api/v1/equipments", json={
            "serial_number": f"SN_LIST_{i}",
            "patrimony_number": f"PAT_{i}",
            "description": f"Equipamento Teste {i}",
            "equipment_type": "Notebook" if i % 2 == 0 else "Desktop",
            "location": "TI" if i <= 3 else "Comunicação",
            "status": "Em uso" if i <= 3 else "Ocioso",
            "product_number": f"PROD_{i}",
        })

    response = await client.get(
        "/api/v1/equipments?page=1&limit=25&type=Notebook&location=TI&status=Em%20uso&patrimony_number=PAT_2&serial_number=SN_LIST_2&product_number=PROD_2&sort_by=serial_number&sort_dir=asc"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1


@pytest.mark.anyio
async def test_equipment_api_update_404_and_400(client: AsyncClient, tecnico_cookie: str):
    """Testa atualização de equipamento e tratamento de erros."""
    client.cookies.set("access_token", tecnico_cookie)

    res = await client.post("/api/v1/equipments", json={
        "serial_number": "SN_UPD_1",
        "description": "Original",
        "equipment_type": "Desktop",
        "location": "TI",
    })
    eq_id = res.json()["id"]

    # Atualização OK
    upd_resp = await client.put(f"/api/v1/equipments/{eq_id}", json={
        "description": "Modificado",
        "brand": "Dell",
        "product_number": "P123",
        "windows_key": "KEY123",
        "notes": "Obs editada",
    })
    assert upd_resp.status_code == 200
    assert upd_resp.json()["description"] == "Modificado"

    # Update 404
    upd_404 = await client.put("/api/v1/equipments/9999", json={"description": "Novo"})
    assert upd_404.status_code == 404

    # Update 400 (duplicidade)
    await client.post("/api/v1/equipments", json={
        "serial_number": "SN_UPD_EXISTING",
        "description": "Existe",
        "equipment_type": "Desktop",
        "location": "TI",
    })
    upd_400 = await client.put(f"/api/v1/equipments/{eq_id}", json={"serial_number": "SN_UPD_EXISTING"})
    assert upd_400.status_code == 400


@pytest.mark.anyio
async def test_equipment_api_tags(client: AsyncClient, tecnico_cookie: str, colaborador_cookie: str):
    """Testa listagem, criação, renomeação, exclusão e RBAC de tags dinâmicas."""
    client.cookies.set("access_token", tecnico_cookie)

    # 1. Criação OK
    create_resp = await client.post("/api/v1/equipments/tags", json={"category": "tipo", "name": "Servidor"})
    assert create_resp.status_code == 201
    tag_id = create_resp.json()["id"]
    assert create_resp.json()["name"] == "Servidor"

    # 2. Criação duplicada -> 400
    dup_resp = await client.post("/api/v1/equipments/tags", json={"category": "tipo", "name": "Servidor"})
    assert dup_resp.status_code == 400

    # 3. Listagem por categoria e geral
    list_resp = await client.get("/api/v1/equipments/tags?category=tipo")
    assert list_resp.status_code == 200
    assert any(t["name"] == "Servidor" for t in list_resp.json())

    list_all = await client.get("/api/v1/equipments/tags")
    assert list_all.status_code == 200

    # 4. Edição OK
    edit_resp = await client.put(f"/api/v1/equipments/tags/{tag_id}", json={"name": "Servidor Rack"})
    assert edit_resp.status_code == 200
    assert edit_resp.json()["name"] == "Servidor Rack"

    # 4.1 Edição 404
    edit_404 = await client.put("/api/v1/equipments/tags/99999", json={"name": "Novo Nome"})
    assert edit_404.status_code == 404

    # 4.2 Edição 400 (nome duplicado)
    other_tag = await client.post("/api/v1/equipments/tags", json={"category": "tipo", "name": "Switch"})
    assert other_tag.status_code == 201
    other_id = other_tag.json()["id"]
    edit_400 = await client.put(f"/api/v1/equipments/tags/{other_id}", json={"name": "Servidor Rack"})
    assert edit_400.status_code == 400

    # 5. Exclusão OK
    del_resp = await client.delete(f"/api/v1/equipments/tags/{other_id}")
    assert del_resp.status_code == 200
    assert "sucesso" in del_resp.json()["message"]

    # 5.1 Exclusão 404
    del_404 = await client.delete("/api/v1/equipments/tags/99999")
    assert del_404.status_code == 404

    # 6. Validação RBAC: colaborador não tem acesso
    client.cookies.set("access_token", colaborador_cookie)
    get_forbidden = await client.get("/api/v1/equipments/tags")
    assert get_forbidden.status_code == 403

    post_forbidden = await client.post("/api/v1/equipments/tags", json={"category": "tipo", "name": "Hack"})
    assert post_forbidden.status_code == 403

    put_forbidden = await client.put(f"/api/v1/equipments/tags/{tag_id}", json={"name": "Hack"})
    assert put_forbidden.status_code == 403

    del_forbidden = await client.delete(f"/api/v1/equipments/tags/{tag_id}")
    assert del_forbidden.status_code == 403



@pytest.mark.anyio
async def test_equipment_api_movements_and_maintenances(client: AsyncClient, tecnico_cookie: str):
    """Testa endpoints HTTP de movimentação e manutenção (Cenários BDD 3 & 4)."""
    client.cookies.set("access_token", tecnico_cookie)

    eq_resp = await client.post("/api/v1/equipments", json={
        "serial_number": "SN_HIST_01",
        "description": "Notebook para Histórico",
        "equipment_type": "Notebook",
        "location": "TI",
        "status": "Em uso",
    })
    eq_id = eq_resp.json()["id"]

    now_str = datetime.now(timezone.utc).isoformat()

    # Movimentação OK
    mov_resp = await client.post(f"/api/v1/equipments/{eq_id}/movements", json={
        "origin_location": "TI",
        "destination_location": "Rádio Produção",
        "movement_date": now_str,
        "notes": "Mudança de setor",
    })
    assert mov_resp.status_code == 201
    assert mov_resp.json()["destination_location"] == "Rádio Produção"

    # Movimentação 404
    mov_404 = await client.post("/api/v1/equipments/9999/movements", json={
        "origin_location": "TI",
        "destination_location": "Rádio Produção",
        "movement_date": now_str,
    })
    assert mov_404.status_code == 404

    # Manutenção OK
    maint_resp = await client.post(f"/api/v1/equipments/{eq_id}/maintenances", json={
        "maintenance_date": now_str,
        "maintenance_type": "Preventiva",
        "description": "Limpeza de cooler",
    })
    assert maint_resp.status_code == 201
    assert maint_resp.json()["description"] == "Limpeza de cooler"

    # Manutenção 404
    maint_404 = await client.post("/api/v1/equipments/9999/maintenances", json={
        "maintenance_date": now_str,
        "maintenance_type": "Preventiva",
        "description": "Inexistente",
    })
    assert maint_404.status_code == 404

    maint_id = maint_resp.json()["id"]

    # Edição de Manutenção OK
    maint_put = await client.put(f"/api/v1/equipments/{eq_id}/maintenances/{maint_id}", json={
        "description": "Limpeza de cooler e substituição de pasta térmica",
        "notes": "Executado com sucesso",
    })
    assert maint_put.status_code == 200
    assert maint_put.json()["description"] == "Limpeza de cooler e substituição de pasta térmica"

    # Edição de Manutenção 404
    maint_put_404 = await client.put(f"/api/v1/equipments/{eq_id}/maintenances/9999", json={
        "description": "Inexistente",
    })
    assert maint_put_404.status_code == 404

    # Exclusão de Manutenção OK
    maint_del = await client.delete(f"/api/v1/equipments/{eq_id}/maintenances/{maint_id}")
    assert maint_del.status_code == 200
    assert "sucesso" in maint_del.json()["message"]

    # Exclusão de Manutenção 404
    maint_del_404 = await client.delete(f"/api/v1/equipments/{eq_id}/maintenances/9999")
    assert maint_del_404.status_code == 404

    # Verifica atualização no objeto do equipamento
    get_resp = await client.get(f"/api/v1/equipments/{eq_id}")
    eq_data = get_resp.json()
    assert eq_data["location"] == "Rádio Produção"
    assert len(eq_data["movements"]) == 1
    assert len(eq_data["maintenances"]) == 0


@pytest.mark.anyio
async def test_equipment_api_suggestions(
    client: AsyncClient,
    colaborador_cookie: str,
    tecnico_cookie: str,
):
    """Testa endpoint GET /api/v1/equipments/suggestions."""
    # Autentica como colaborador (RBAC 403)
    client.cookies.set("access_token", colaborador_cookie)
    forbidden_resp = await client.get("/api/v1/equipments/suggestions?field=patrimony_number&prefix=PA")
    assert forbidden_resp.status_code == 403

    # Autentica como técnico
    client.cookies.set("access_token", tecnico_cookie)

    # Cria equipamentos para sugestões
    await client.post("/api/v1/equipments", json={
        "serial_number": "SN_AUTO_001",
        "patrimony_number": "PAT_AUTO_10",
        "product_number": "PROD_AUTO_A",
        "description": "Item Autocomplete 1",
        "equipment_type": "Notebook",
        "location": "TI",
        "status": "Em uso",
    })
    await client.post("/api/v1/equipments", json={
        "serial_number": "SN_AUTO_002",
        "patrimony_number": "PAT_AUTO_20",
        "product_number": "PROD_AUTO_B",
        "description": "Item Autocomplete 2",
        "equipment_type": "Notebook",
        "location": "TI",
        "status": "Em uso",
    })

    # 1. Sugestões de patrimônio com sucesso
    sug_pat = await client.get("/api/v1/equipments/suggestions?field=patrimony_number&prefix=PAT_AUTO")
    assert sug_pat.status_code == 200
    pats = sug_pat.json()
    assert len(pats) == 2
    assert "PAT_AUTO_10" in pats
    assert "PAT_AUTO_20" in pats

    # 2. Sugestões com limite
    sug_pat_lim = await client.get("/api/v1/equipments/suggestions?field=patrimony_number&prefix=PAT_AUTO&limit=1")
    assert sug_pat_lim.status_code == 200
    assert len(sug_pat_lim.json()) == 1

    # 3. Sugestões de serial
    sug_ser = await client.get("/api/v1/equipments/suggestions?field=serial_number&prefix=sn_auto")
    assert sug_ser.status_code == 200
    assert len(sug_ser.json()) == 2

    # 4. Campo inválido (400)
    sug_inv_field = await client.get("/api/v1/equipments/suggestions?field=invalid_col&prefix=abc")
    assert sug_inv_field.status_code == 400
    assert "Campo inválido" in sug_inv_field.json()["detail"]

    # 5. Prefixo curto (< 2 caracteres) (400)
    sug_short_prefix = await client.get("/api/v1/equipments/suggestions?field=patrimony_number&prefix=P")
    assert sug_short_prefix.status_code == 400
    assert "pelo menos 2 caracteres" in sug_short_prefix.json()["detail"]


@pytest.mark.anyio
async def test_equipment_api_export_all_and_filtered(client: AsyncClient, tecnico_cookie: str):
    """Testa exportação de equipamentos via GET /api/v1/equipments/export (Cenários 1, 2 e 3)."""
    client.cookies.set("access_token", tecnico_cookie)

    # Cria equipamentos para teste
    c1 = await client.post("/api/v1/equipments", json={
        "serial_number": "SN_EXPORT_001",
        "patrimony_number": "PAT_EXPORT_001",
        "product_number": "PROD_EXP_1",
        "description": "Notebook Lenovo L14",
        "equipment_type": "Notebook",
        "location": "TI",
        "status": "Em uso",
        "brand": "Lenovo",
    })
    eq1_id = c1.json()["id"]

    await client.post("/api/v1/equipments", json={
        "serial_number": "SN_EXPORT_002",
        "patrimony_number": "PAT_EXPORT_002",
        "product_number": "PROD_EXP_2",
        "description": "Desktop Dell 7090",
        "equipment_type": "Desktop",
        "location": "Financeiro",
        "status": "Disponível",
        "brand": "Dell",
    })

    # Adiciona manutenção em eq1
    await client.post(f"/api/v1/equipments/{eq1_id}/maintenances", json={
        "maintenance_date": "2026-08-20T10:00:00Z",
        "description": "Substituição de cooler",
        "notes": "Original",
    })

    # 1. Exportação sem filtros
    resp_all = await client.get("/api/v1/equipments/export")
    assert resp_all.status_code == 200
    assert resp_all.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=" in resp_all.headers["content-disposition"]
    assert resp_all.headers["content-disposition"].endswith(".xlsx\"")
    assert len(resp_all.content) > 0

    # 2. Exportação com filtros aplicados
    resp_filtered = await client.get("/api/v1/equipments/export?type=Notebook&location=TI")
    assert resp_filtered.status_code == 200
    assert len(resp_filtered.content) > 0


@pytest.mark.anyio
async def test_equipment_api_export_rbac_forbidden(client: AsyncClient, colaborador_cookie: str):
    """Testa que colaborador recebe HTTP 403 Forbidden ao tentar exportar planilha (Cenário 4)."""
    client.cookies.set("access_token", colaborador_cookie)
    response = await client.get("/api/v1/equipments/export")
    assert response.status_code == 403



