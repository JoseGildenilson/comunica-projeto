# Relatório de Análise e Auditoria de Conformidade — Grupo A (Specs)

**Data da Auditoria:** 2026-10-13  
**Auditor:** Explorer M1 (`teamwork_preview_explorer_m1_1`)  
**Escopo Atribuído:** Grupo A de Especificações em `spec/features/`:
1. `spec/features/equipamentos/` (`spec.md`, `tasks.md`, `autocomplete-filtros/spec.md`, `autocomplete-filtros/tasks.md`, `spec-corretion.md`)
2. `spec/features/tags-crud/` (`spec.md`, `tasks.md`)
3. `spec/features/tela-de-login/` (`spec.md`, `tasks.md`)

---

## 1. Sumário Executivo do Grupo A

| Módulo / Especificação | Total de Cenários BDD | Conforme | Parcial | Não Implementado | % Conformidade |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Equipamentos (`spec.md`)** | 8 | 7 | 1 | 0 | 87.5% |
| **1.1. Equipamentos — Correções (`spec-corretion.md`)** | 16 | 15 | 1 | 0 | 93.8% |
| **1.2. Equipamentos — Autocomplete Filtros (`spec.md`)** | 7 | 7 | 0 | 0 | 100.0% |
| **2. Tags CRUD (`spec.md`)** | 7 | 7 | 0 | 0 | 100.0% |
| **3. Tela de Login (`spec.md`)** | 6 | 6 | 0 | 0 | 100.0% |
| **TOTAL CONSOLIDADO (Cenários Únicos)** | **28** | **27** | **1** | **0** | **96.4%** |

*(Nota: Os 16 cenários de `spec-corretion.md` refinam os cenários gerais de `spec.md`; considerando a base de cenários formais da versão final de `spec.md` + `autocomplete` + `tags-crud` + `tela-de-login` = 28 cenários).*

### Sumário de Tarefas dos `tasks.md`

| Módulo / Arquivo de Tarefas | Total de Tarefas | Concluído no Código | Parcial | Pendente |
|---|:---:|:---:|:---:|:---:|
| `equipamentos/tasks.md` | 9 | 8 | 1 | 0 |
| `autocomplete-filtros/tasks.md` | 7 | 7 | 0 | 0 |
| `tags-crud/tasks.md` | 13 | 13 | 0 | 0 |
| `tela-de-login/tasks.md` | 6 | 6 | 0 | 0 |
| **TOTAL DE TAREFAS** | **35** | **34** | **1** | **0** |

---

## 2. Auditoria Detalhada: `spec/features/equipamentos/`

### 2.1. Cenários BDD em `spec/features/equipamentos/spec.md`

#### Cenário 1: Selecionar múltiplos valores em um filtro com busca interna
- **Critérios (Given/When/Then):**
  - *Dado* que o técnico abra o painel do filtro de `Nº Série`;
  - *Quando* pesquisar pelo valor `123` e selecioná-lo, e pesquisar por `432` e selecioná-lo;
  - *Então* o filtro deve exibir o indicador visual `Nº Série (2)`;
  - *E* a lista deve exibir equipamentos que possuam o Nº Série `123` OU `432`.
- **Rastreabilidade de Implementação:**
  - **Backend:** `src/api/equipment_routes.py` (linhas 49, 58-71) aceita `serial_number: List[str] | None = Query(default=None)`.
  - **Repositório:** `src/infrastructure/repositories.py` (linhas 155-158): `query.where(or_(*[Equipment.serial_number.ilike(f"%{s}%") for s in serials]))`.
  - **Frontend:** `frontend/src/components/AutocompleteFilterInput.tsx` (linhas 109-117) exibe badge com a contagem de selecionados; `frontend/src/pages/EquipmentListPage.tsx` (linhas 49-51, 95-107, 369-376) gerencia a lista de chips e parâmetros.
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_list_and_filters`, `tests/test_equipment_repositories.py::test_equipment_repository_list_paginated_filtered_and_search`.
  - **Testes Frontend:** `frontend/src/__tests__/EquipmentPage.test.tsx` (linhas 93-109), `frontend/src/__tests__/AutocompleteFilterInput.test.tsx`.
- **Status:** **Conforme**

---

#### Cenário 2: Utilizar múltiplos filtros simultaneamente (Lógica OR e AND)
- **Critérios (Given/When/Then):**
  - *Dado* que o técnico selecione `Notebook` e `Desktop` em Tipo;
  - *E* selecione `Comunicação` e `Rádio Produção` em Localização;
  - *Então* o sistema deve retornar equipamentos que sejam `(Notebook OU Desktop) E (Comunicação OU Rádio Produção)`.
- **Rastreabilidade de Implementação:**
  - **Backend:** `src/infrastructure/repositories.py` (linhas 139-150): cláusulas independentes `query.where(Equipment.equipment_type.in_(types))` e `query.where(Equipment.location.in_(locations))` combinadas com AND nativo pelo SQLAlchemy, com OR interno (`in_`).
  - **Frontend:** `frontend/src/pages/EquipmentListPage.tsx` (linhas 98-107, 332-358) integra `MultiSelectFilterDropdown` para Tipo e Localização.
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_list_and_filters`, `tests/test_equipment_use_cases.py::test_list_and_get_equipment_detail_use_cases` (linhas 95-100).
  - **Testes Frontend:** `frontend/src/__tests__/EquipmentPage.test.tsx`.
- **Status:** **Conforme**

---

#### Cenário 3: Desmarcar filtro individual
- **Critérios (Given/When/Then):**
  - *Dado* que o filtro de `Tipo` possua 3 opções selecionadas;
  - *Quando* o técnico clicar em `Desmarcar tudo` dentro do dropdown de `Tipo`;
  - *Então* todas as seleções de `Tipo` devem ser removidas;
  - *E* os demais filtros (ex: `Localização`) devem permanecer intactos.
- **Rastreabilidade de Implementação:**
  - **Frontend Componente:** `frontend/src/components/MultiSelectFilterDropdown.tsx` (linhas 48-50, 131-144): botão "Desmarcar tudo" aciona `handleClearAll` limpando apenas `selectedValues` daquele dropdown sem alterar o estado de outros filtros.
  - **Frontend Página:** `frontend/src/pages/EquipmentListPage.tsx` (linhas 334-340): cada dropdown possui estado isolado (`setFilterTypes`, `setFilterLocations`, etc.).
  - **Testes Frontend:** `frontend/src/__tests__/EquipmentPage.test.tsx` (linhas 103-110 testa limpeza de filtros).
- **Status:** **Conforme**

---

#### Cenário 4: Visualização limpa com nomes proporcionais, respiro interno e alto contraste
- **Critérios (Given/When/Then):**
  - *Dado* que a listagem seja carregada;
  - *Quando* os blocos de equipamentos forem exibidos;
  - *Então* cada bloco deve apresentar layout horizontal com nomes em tamanho proporcional (`text-sm sm:text-base font-bold`), respiro interno em relação às bordas (`p-5 sm:px-6 sm:py-5`), alto contraste com o fundo escuro (`border-2 border-slate-700/90`) e cores alternadas (*zebra striping*).
- **Rastreabilidade de Implementação:**
  - **Frontend:** `frontend/src/pages/EquipmentListPage.tsx` (linhas 472-536).
  - *O que está implementado:*
    - Layout horizontal limpo (Ícone + Descrição + Marca + Tipo + Metadados Inline + Última Manutenção no canto direito);
    - Animação staggered slide-in (linhas 477-479: `style={{ animationDelay: `${index * 20}ms` }}` e `animate-slide-in-right`);
    - Tipografia de nomes em tamanho proporcional (`text-base font-medium text-white`);
    - Navegação ao clicar no bloco (linha 476: `onClick={() => navigate(`/equipamentos/${item.id}`)}`).
  - *Gap Técnico Encontrado (Divergência da Spec):*
    - **Zebra striping:** Não implementado na listagem. Todos os blocos usam classe fixa `bg-[#1E1E1E]` (linha 479), sem alternância par/ímpar (`index % 2 === 0` não é utilizado);
    - **Bordas duplas e cores especificadas:** A spec exige `border-2 border-slate-700/90` e fundo `bg-slate-900` / `bg-slate-900/60`, mas o código utiliza `border border-[#333333]` e `bg-[#1E1E1E]`;
    - **Padding/Respiro:** A spec exige `p-5 sm:px-6 sm:py-5`, mas o código utiliza `p-4`.
- **Status:** **Parcial**
- **Justificativa do Gap:** A funcionalidade de apresentação em blocos empilhados horizontais, animação staggered de entrada e dados essenciais inline está presente e operacional, mas o design visual refinado estipulado na RN-EQ-02 e Cenário 4 (cores intercaladas *zebra striping*, bordas reforçadas `border-2` e espaçamento interno generoso) não foi aplicado no componente `EquipmentListPage.tsx`.

---

#### Cenário 5: Edição completa em modo único na tela de detalhes
- **Critérios (Given/When/Then):**
  - *Dado* que o técnico esteja visualizando os detalhes de um equipamento em tela única;
  - *Quando* clicar em `Editar equipamento`;
  - *Então* todos os campos editáveis devem entrar em modo de edição simultaneamente;
  - *E* ao clicar em `Salvar alterações`, os novos dados devem ser persistidos e a tela voltar ao modo de visualização.
- **Rastreabilidade de Implementação:**
  - **Backend:** `src/api/equipment_routes.py` (linhas 226-246: `PUT /api/v1/equipments/{id}`); `src/use_cases/equipment_use_cases.py` (linhas 126-175: `UpdateEquipmentUseCase`).
  - **Frontend:** `frontend/src/pages/EquipmentDetailPage.tsx` (linhas 69-84, 122-139, 163-211): botão `Editar equipamento` ativa `isEditing`, abrindo todos os inputs; ao clicar em `Salvar alterações` chama `equipmentApi.updateEquipment`, atualiza o estado e desativa a edição. Ao clicar em `Cancelar`, reverte para os valores originais.
  - **Testes Backend:** `tests/test_equipment_use_cases.py::test_update_equipment_use_case`, `tests/test_equipment_api.py::test_equipment_api_update_404_and_400`.
  - **Testes Frontend:** `frontend/src/__tests__/EquipmentPage.test.tsx` (linhas 183-199).
- **Status:** **Conforme**

---

#### Cenário 6: Registrar manutenção com múltiplos itens agrupados
- **Critérios (Given/When/Then):**
  - *Dado* que o técnico cadastre uma manutenção para o equipamento;
  - *Quando* inserir a data `18/09/2026` e a lista de itens `Troca de SSD`, `Limpeza interna` e `Troca de pasta térmica`;
  - *Então* deve ser criado um único registro no histórico agrupando todos os itens;
  - *E* a data de "Última manutenção" do equipamento deve ser atualizada para `18/09/2026`.
- **Rastreabilidade de Implementação:**
  - **Backend:** `src/api/equipment_routes.py` (linhas 267-283); `src/use_cases/equipment_use_cases.py` (linhas 206-232: `RecordMaintenanceUseCase`); `src/domain/schemas.py` (linhas 85-91: campo `description` recebe texto livre com múltiplos itens).
  - **Atualização Automática de Data:** `src/use_cases/equipment_use_cases.py` (linha 229: `equipment.last_maintenance_at = data.maintenance_date`).
  - **Frontend:** `frontend/src/components/MaintenanceModal.tsx` (linhas 37-44, 87-97: input de descrição com placeholder de múltiplos itens).
  - **Testes Backend:** `tests/test_equipment_use_cases.py::test_record_maintenance_use_case_updates_last_maintenance_date_without_changing_status`, `tests/test_equipment_api.py::test_equipment_api_movements_and_maintenances`.
- **Status:** **Conforme**

---

#### Cenário 7: Editar e excluir registro de manutenção no histórico
- **Critérios (Given/When/Then):**
  - *Dado* que exista uma manutenção cadastrada no histórico do equipamento;
  - *Quando* o técnico clicar em `Editar` naquele registro, deve poder alterar os itens e a data da manutenção;
  - *E* ao clicar em `Excluir`, o registro deve ser removido do histórico do equipamento.
- **Rastreabilidade de Implementação:**
  - **Backend Endpoints:**
    - `PUT /api/v1/equipments/{id}/maintenances/{maintenance_id}` (`src/api/equipment_routes.py:286-312`);
    - `DELETE /api/v1/equipments/{id}/maintenances/{maintenance_id}` (`src/api/equipment_routes.py:313-329`).
  - **Casos de Uso:** `src/use_cases/equipment_use_cases.py`:
    - `UpdateMaintenanceUseCase` (linhas 234-273);
    - `DeleteMaintenanceUseCase` (linhas 275-300).
    - Ambos recalculam `equipment.last_maintenance_at` com base no `max(maintenance_date)` das manutenções restantes.
  - **Frontend:**
    - `frontend/src/pages/EquipmentDetailPage.tsx` (linhas 213-223: exclusão com confirmação; modal de edição vinculado a `editingMaintenance`);
    - `frontend/src/components/EditMaintenanceModal.tsx` (linhas 42-66);
    - `frontend/src/api/equipmentApi.ts` (linhas 80-96: `updateMaintenance` e `deleteMaintenance`).
  - **Testes Backend:** `tests/test_equipment_use_cases.py::test_update_and_delete_maintenance_use_cases`, `tests/test_equipment_api.py::test_equipment_api_movements_and_maintenances` (linhas 273-302).
- **Status:** **Conforme**

---

#### Cenário 8: Navegação explícita
- **Critérios (Given/When/Then):**
  - *Dado* que o técnico esteja na tela de equipamentos, ao clicar em `← Voltar ao Dashboard` deve navegar para `/dashboard`;
  - *Dado* que o técnico esteja na tela de detalhes, ao clicar em `← Voltar para equipamentos` deve navegar para `/equipamentos`.
- **Rastreabilidade de Implementação:**
  - **Frontend Listagem:** `frontend/src/pages/EquipmentListPage.tsx` (linhas 253-261: botão `data-testid="back-to-dashboard-btn"` executando `navigate('/dashboard')`).
  - **Frontend Detalhes:** `frontend/src/pages/EquipmentDetailPage.tsx` (botão `data-testid="back-to-equipments-btn"` executando `navigate('/equipamentos')`).
  - **Testes Frontend:** `frontend/src/__tests__/EquipmentPage.test.tsx` (linhas 111-118 e 200-207).
- **Status:** **Conforme**

---

### 2.2. Cruzamento com `spec-corretion.md` (16 Cenários)

`spec-corretion.md` serviu como especificação detalhada de refinamento da tela de equipamentos. Todos os 16 cenários mapeiam diretamente para a implementação:
- **Cenários 1, 2, 3 (Filtros Múltiplos, Google Sheets, Desmarcar tudo):** Conforme (ver Cenários 1, 2 e 3 acima).
- **Cenário 4 (Blocos empilhados & estrutura):** **Parcial** (estrutura em blocos ok, zebra striping e borda dupla ausentes).
- **Cenário 5 (Abrir detalhes):** Conforme (`EquipmentListPage.tsx:476`).
- **Cenários 6, 7, 8 (Editar equipamento, Cancelar, Salvar):** Conforme (`EquipmentDetailPage.tsx:163-211`).
- **Cenários 9, 10 (Manutenção vários itens & Atualizar última manutenção):** Conforme (`RecordMaintenanceUseCase`).
- **Cenários 11, 12 (Editar e Excluir manutenção):** Conforme (`UpdateMaintenanceUseCase`, `DeleteMaintenanceUseCase`).
- **Cenário 13 (Situação não alterada automaticamente):** Conforme (`RecordMovementUseCase` e `RecordMaintenanceUseCase` não alteram status; testado em `tests/test_equipment_use_cases.py:test_record_movement_use_case_updates_location_without_changing_status` e `test_record_maintenance_use_case_updates_last_maintenance_date_without_changing_status`).
- **Cenários 14, 15 (Voltar para equipamentos / Voltar ao Dashboard):** Conforme (`EquipmentDetailPage.tsx` e `EquipmentListPage.tsx`).
- **Cenário 16 (Entrada dos equipamentos com slide-in):** Conforme (`EquipmentListPage.tsx:477-479` com animação suave e delay staggered).

---

### 2.3. Especificação: Autocomplete nos Filtros (`spec/features/equipamentos/autocomplete-filtros/spec.md`)

#### Cenário 1: Exibir sugestões ao digitar no filtro de Patrimônio
- **Critérios:** Digitar prefixo `PA` exibe `PAT001`, `PAT002`, `PAT100` e não exibe `SER001`.
- **Rastreabilidade:** `GET /api/v1/equipments/suggestions?field=patrimony_number&prefix=PA`; `EquipmentRepository.get_distinct_values_by_prefix` (`src/infrastructure/repositories.py:270-305`); `AutocompleteFilterInput.tsx` (linhas 36-68).
- **Testes:** `tests/test_equipment_api.py::test_equipment_api_suggestions` (linhas 339-346); `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` (linhas 42-84).
- **Status:** **Conforme**

#### Cenário 2: Não exibir sugestões com menos de 2 caracteres
- **Critérios:** Digitar apenas 1 caractere (`S`) não dispara sugestões.
- **Rastreabilidade:** `AutocompleteFilterInput.tsx` (linhas 42-47: se `clean.length < 2` limpa sugestões); `GetSuggestionsUseCase` (`src/use_cases/equipment_use_cases.py:378-379: len(prefix.strip()) < 2`).
- **Testes:** `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` (linhas 12-40); `tests/test_equipment_api.py::test_equipment_api_suggestions` (linhas 362-366).
- **Status:** **Conforme**

#### Cenário 3: Adicionar sugestão como chip ao clicar
- **Critérios:** Clicar na sugestão adiciona como chip, limpa o input e filtra a lista.
- **Rastreabilidade:** `AutocompleteFilterInput.tsx` (linhas 70-75: `handleSelectSuggestion`); `EquipmentListPage.tsx` (linhas 365, 373, 381: `handleAddTextFilter`).
- **Testes:** `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` (linhas 78-83).
- **Status:** **Conforme**

#### Cenário 4: Ocultar valores já selecionados nas sugestões
- **Critérios:** Valores já ativos como chips não aparecem na lista de sugestões.
- **Rastreabilidade:** `AutocompleteFilterInput.tsx` (linha 53: `results.filter((item) => !selectedValues.includes(item))`).
- **Testes:** `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` (linhas 50, 73-76).
- **Status:** **Conforme**

#### Cenário 5: Manter entrada livre via Enter
- **Critérios:** Pressionar Enter em texto livre adiciona como chip mesmo sem sugestões.
- **Rastreabilidade:** `AutocompleteFilterInput.tsx` (linhas 77-87: `handleKeyDown` no Enter).
- **Testes:** `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` (linhas 86-108); `frontend/src/__tests__/EquipmentPage.test.tsx` (linhas 93-102).
- **Status:** **Conforme**

#### Cenário 6: Backend retorna erro para campo inválido
- **Critérios:** `GET /api/v1/equipments/suggestions?field=invalid_field&prefix=AB` retorna HTTP 400.
- **Rastreabilidade:** `src/use_cases/equipment_use_cases.py` (linhas 374-376); `src/api/equipment_routes.py` (linhas 173-174).
- **Testes:** `tests/test_equipment_api.py::test_equipment_api_suggestions` (linhas 357-360); `tests/test_equipment_use_cases.py::test_get_suggestions_use_case`.
- **Status:** **Conforme**

#### Cenário 7: Backend retorna erro para prefixo curto
- **Critérios:** `GET /api/v1/equipments/suggestions?field=serial_number&prefix=A` retorna HTTP 400.
- **Rastreabilidade:** `src/use_cases/equipment_use_cases.py` (linhas 378-380); `src/api/equipment_routes.py` (linhas 173-174).
- **Testes:** `tests/test_equipment_api.py::test_equipment_api_suggestions` (linhas 362-366).
- **Status:** **Conforme**

---

### 2.4. Auditoria de Tarefas: `spec/features/equipamentos/tasks.md`

| Tarefa | Status no Checklist | Status no Código | Evidências / Arquivos no Código | Observações |
|---|:---:|:---:|---|---|
| **TASK-EQ-10** | [x] | **Concluído** | `src/api/equipment_routes.py:45-50`, `src/infrastructure/repositories.py:120-177` | Rota aceita `List[str] = Query(None)` e repositório constrói cláusulas OR/AND. |
| **TASK-EQ-10-TEST** | [x] | **Concluído** | `tests/test_equipment_api.py:94-115`, `tests/test_equipment_repositories.py:46-77` | Testes de integração cobrindo múltiplos filtros combinados. |
| **TASK-EQ-11** | [x] | **Concluído** | `src/domain/schemas.py:85-110`, `src/use_cases/equipment_use_cases.py:206-300`, `src/api/equipment_routes.py:286-329` | Endpoints PUT e DELETE de manutenção e atualização de `last_maintenance_at`. |
| **TASK-EQ-11-TEST** | [x] | **Concluído** | `tests/test_equipment_use_cases.py:test_update_and_delete_maintenance_use_cases`, `tests/test_equipment_api.py:273-302` | Testes com 100% de cobertura no backend. |
| **TASK-EQ-12** | [x] | **Concluído** | `frontend/src/components/MultiSelectFilterDropdown.tsx`, `frontend/src/pages/EquipmentListPage.tsx:332-358` | Componente Google Sheets funcional, com busca interna e botão Voltar ao Dashboard. |
| **TASK-EQ-13** | [x] | **Parcial** | `frontend/src/pages/EquipmentListPage.tsx:472-536` | **Divergência:** Cards com layout horizontal e metadados inline estão presentes, mas **zebra striping** e bordas duplas espessas (`border-2 border-slate-700/80`) não foram implementados. |
| **TASK-EQ-14** | [x] | **Concluído** | `frontend/src/pages/EquipmentDetailPage.tsx:163-211` | Tela única sem abas, modo de edição em lote com Salvar/Cancelar e retorno à listagem. |
| **TASK-EQ-15** | [x] | **Concluído** | `frontend/src/components/MaintenanceModal.tsx`, `frontend/src/components/EditMaintenanceModal.tsx`, `frontend/src/pages/EquipmentDetailPage.tsx:213-223` | Edição e exclusão de manutenções no frontend com múltiplos itens. |
| **TASK-EQ-16** | [x] | **Concluído** | `frontend/src/components/NewEquipmentModal.tsx` | Formulário amplo organizado por seções lógicas. |
| **TASK-EQ-17** | [x] | **Concluído** | `frontend/src/__tests__/EquipmentPage.test.tsx`, `frontend/src/__tests__/equipmentApi.test.ts` | Testes frontend aprovados. |
| **TASK-EQ-18** | [x] | **Concluído** | `pytest tests/`, `npm test -- --run`, `npx tsc --noEmit` | 104 testes backend passando (100% de cobertura nos arquivos do módulo), 57 testes frontend passando, zero erros TypeScript. |

---

### 2.5. Auditoria de Tarefas: `spec/features/equipamentos/autocomplete-filtros/tasks.md`

| Tarefa | Status no Checklist | Status no Código | Evidências / Arquivos no Código | Observações |
|---|:---:|:---:|---|---|
| **TASK-AC-01** | [x] | **Concluído** | `src/infrastructure/repositories.py:270-305` | Método `get_distinct_values_by_prefix` implementado com ILIKE e DISTINCT. |
| **TASK-AC-01-TEST** | [x] | **Concluído** | `tests/test_equipment_repositories.py:202-235` | Testes de integração de busca por prefixo, case-insensitivity e ordenação. |
| **TASK-AC-02** | [x] | **Concluído** | `src/use_cases/equipment_use_cases.py:361-395` | `GetSuggestionsUseCase` valida campos permitidos e prefixo >= 2 chars. |
| **TASK-AC-02-TEST** | [x] | **Concluído** | `tests/test_equipment_use_cases.py:test_get_suggestions_use_case` | Testes unitários do caso de uso. |
| **TASK-AC-03** | [x] | **Concluído** | `src/api/equipment_routes.py:161-175` | `GET /api/v1/equipments/suggestions` protegido por role técnico. |
| **TASK-AC-03-TEST** | [x] | **Concluído** | `tests/test_equipment_api.py:305-367` | Testes de API cobrindo 200, 400 (campo e prefixo inválidos) e 403 (RBAC). |
| **TASK-AC-04** | [x] | **Concluído** | `frontend/src/api/equipmentApi.ts:135-144` | Função `getSuggestions` adicionada no cliente HTTP. |
| **TASK-AC-04-TEST** | [x] | **Concluído** | `frontend/src/__tests__/equipmentApi.test.ts` | Teste unitário de chamada de API. |
| **TASK-AC-05** | [x] | **Concluído** | `frontend/src/components/AutocompleteFilterInput.tsx` | Componente reutilizável com debounce de 300ms, limite de 10 e suporte a Enter. |
| **TASK-AC-05-TEST** | [x] | **Concluído** | `frontend/src/__tests__/AutocompleteFilterInput.test.tsx` | 5 testes cobrindo todos os cenários com Vitest + RTL. |
| **TASK-AC-06** | [x] | **Concluído** | `frontend/src/pages/EquipmentListPage.tsx:361-384` | Substituição dos inputs de patrimônio, série e produto pelo componente. |
| **TASK-AC-06-TEST** | [x] | **Concluído** | `frontend/src/__tests__/EquipmentPage.test.tsx:93-102` | Integração na página validada. |
| **TASK-AC-07** | [x] | **Concluído** | `pytest`, `npx tsc --noEmit`, `vitest` | Verificação geral realizada com sucesso. |

---

## 3. Auditoria Detalhada: `spec/features/tags-crud/`

### 3.1. Cenários BDD em `spec/features/tags-crud/spec.md`

#### Cenário 1: Listar tags filtradas por categoria
- **Critérios:** Selecionar aba "Localização" lista apenas tags da categoria `localizacao`.
- **Rastreabilidade:**
  - **Backend:** `GET /api/v1/equipments/tags?category=localizacao` (`src/api/equipment_routes.py:92-100`); `EquipmentTagRepository.list_by_category` (`src/infrastructure/repositories.py:328-331`).
  - **Frontend:** `frontend/src/components/ManageTagsModal.tsx` (linhas 195-226: abas de categoria filtram `tags.filter(t => t.category === activeCategory)`).
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 171-178).
  - **Testes Frontend:** `frontend/src/__tests__/ManageTagsModal.test.tsx` (linhas 40-58).
- **Status:** **Conforme**

---

#### Cenário 2: Criar nova tag com sucesso
- **Critérios:** Preencher nome `"Tablet"` na categoria `"tipo"` e adicionar: tag é persistida e exibida nos dropdowns e listas.
- **Rastreabilidade:**
  - **Backend:** `POST /api/v1/equipments/tags` (`src/api/equipment_routes.py:103-119`); `ManageTagsUseCase.create_tag` (`src/use_cases/equipment_use_cases.py:314-328`).
  - **Frontend:** `frontend/src/components/ManageTagsModal.tsx` (linhas 81-100); dispara `onTagsUpdated` recarregando tags em `EquipmentListPage.tsx`.
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 161-166); `tests/test_equipment_use_cases.py::test_manage_tags_use_case`.
  - **Testes Frontend:** `frontend/src/__tests__/ManageTagsModal.test.tsx` (linhas 60-86).
- **Status:** **Conforme**

---

#### Cenário 3: Impedir criação de tag duplicada na mesma categoria
- **Critérios:** Tentar cadastrar `"TI"` na categoria `localizacao` quando já existe retorna `HTTP 400 Bad Request`.
- **Rastreabilidade:**
  - **Backend:** `ManageTagsUseCase.create_tag` (`src/use_cases/equipment_use_cases.py:320-322: ValueError("Tag já está cadastrada...")`); rota mapeia `ValueError` para `HTTP 400 Bad Request` (`src/api/equipment_routes.py:116-118`).
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 167-170); `tests/test_equipment_use_cases.py::test_manage_tags_use_case`.
- **Status:** **Conforme**

---

#### Cenário 4: Renomear tag existente com propagação para os equipamentos
- **Critérios:** Renomear `"TI"` para `"Tecnologia da Informação"` atualiza a tag e todos os equipamentos vinculados na mesma transação.
- **Rastreabilidade:**
  - **Backend:** `PUT /api/v1/equipments/tags/{id}` (`src/api/equipment_routes.py:121-141`); `ManageTagsUseCase.update_tag` (`src/use_cases/equipment_use_cases.py:329-350`); `EquipmentTagRepository.propagate_tag_rename` (`src/infrastructure/repositories.py:350-379: UPDATE equipment SET location = :new_name WHERE location = :old_name`).
  - **Frontend:** `frontend/src/components/ManageTagsModal.tsx` (linhas 102-136: modo de edição inline com salvar/cancelar); `equipmentApi.updateTag`.
  - **Testes Backend:** `tests/test_equipment_repositories.py::test_equipment_tag_repository` (linhas 96-117); `tests/test_equipment_use_cases.py::test_manage_tags_use_case`; `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 179-183).
  - **Testes Frontend:** `frontend/src/__tests__/ManageTagsModal.test.tsx` (linhas 88-118).
- **Status:** **Conforme**

---

#### Cenário 5: Excluir tag existente
- **Critérios:** Excluir `"Ocioso"` remove a tag da tabela de tags, mas preserva os equipamentos previamente cadastrados com esse valor.
- **Rastreabilidade:**
  - **Backend:** `DELETE /api/v1/equipments/tags/{id}` (`src/api/equipment_routes.py:143-158`); `ManageTagsUseCase.delete_tag` (`src/use_cases/equipment_use_cases.py:351-359`) executa `tag_repo.delete(tag)` sem alterar a tabela de equipamentos.
  - **Frontend:** `frontend/src/components/ManageTagsModal.tsx` (linhas 138-151: exclusão com confirmação); `equipmentApi.deleteTag`.
  - **Testes Backend:** `tests/test_equipment_repositories.py::test_equipment_tag_repository` (linhas 118-122); `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 195-199).
  - **Testes Frontend:** `frontend/src/__tests__/ManageTagsModal.test.tsx` (linhas 120-143).
- **Status:** **Conforme**

---

#### Cenário 6: Criar nova tag inline no modal de movimentação
- **Critérios:** No modal de movimentação, clicar em "Criar local", preencher `"Almoxarifado B"` e confirmar: tag é persistida e selecionada automaticamente como destino.
- **Rastreabilidade:**
  - **Frontend Componente:** `frontend/src/components/MovementModal.tsx` (linhas 39-53: `handleCreateLocation` chama `equipmentApi.createTag('localizacao', ...)`, atualiza lista local e define `destinationLocation = created.name`).
  - **Testes Frontend:** `frontend/src/__tests__/MovementModal.test.tsx` (linhas 42-83: verifica criação inline com valor `"Almoxarifado B"` e ausência de duplo "+").
- **Status:** **Conforme**

---

#### Cenário 7: Bloqueio de acesso para colaborador (RBAC)
- **Critérios:** Colaborador tentando acessar criação, edição ou exclusão de tags recebe `HTTP 403 Forbidden`.
- **Rastreabilidade:**
  - **Backend:** Todas as rotas de tags dependem de `current_user: User = Depends(require_tecnico_role)` (`src/api/equipment_routes.py:96, 107, 126, 147`).
  - **Testes Backend:** `tests/test_equipment_api.py::test_equipment_api_tags` (linhas 204-217).
- **Status:** **Conforme**

---

### 3.2. Auditoria de Tarefas: `spec/features/tags-crud/tasks.md`

| Tarefa | Status Checklist | Status Código | Evidências / Arquivos | Observações |
|---|:---:|:---:|---|---|
| **1.1 DTOs / Schemas Pydantic** | [x] | **Concluído** | `src/domain/schemas.py:59-62` | `EquipmentTagUpdate` com `name: str = Field(..., min_length=1)`. |
| **1.2 Repositório de Tags** | [x] | **Concluído** | `src/infrastructure/repositories.py:313-384` | Métodos `get_by_id`, `delete`, `propagate_tag_rename` implementados. |
| **1.3 Casos de Uso (`ManageTagsUseCase`)** | [x] | **Concluído** | `src/use_cases/equipment_use_cases.py:301-360` | Métodos `create_tag`, `update_tag`, `delete_tag` implementados. |
| **1.4 Roteador HTTP** | [x] | **Concluído** | `src/api/equipment_routes.py:92-159` | Rotas GET, POST, PUT, DELETE com tratamento de 400, 404 e 403. |
| **1.5 Testes Automatizados Backend** | [x] | **Concluído** | `tests/test_equipment_api.py:156-218`, `tests/test_equipment_use_cases.py`, `tests/test_equipment_repositories.py` | 100% de cobertura no Pytest. |
| **2.1 Cliente de API Frontend** | [x] | **Concluído** | `frontend/src/api/equipmentApi.ts:98-112` | Métodos `updateTag` e `deleteTag` implementados. |
| **2.2 Modal ManageTagsModal** | [x] | **Concluído** | `frontend/src/components/ManageTagsModal.tsx` | Abas por categoria, contador, edição inline e confirmação de exclusão. |
| **2.3 Ponto no SideMenu** | [x] | **Concluído** | `frontend/src/components/SideMenu.tsx:125-135` | Item "Gerenciar Tags" com ícone de Tag, restrito a técnico. |
| **2.4 Ponto no Header de Equipamentos** | [x] | **Concluído** | `frontend/src/pages/EquipmentListPage.tsx:290-297` | Botão "Gerenciar Tags" abre o modal com callback de reload. |
| **2.5 Criação Rápida no MovementModal** | [x] | **Concluído** | `frontend/src/components/MovementModal.tsx:39-53, 113-145` | Botão "Criar local" sem duplo "+". |
| **2.6 Criação Rápida nos Detalhes/Criação** | [x] | **Concluído** | `frontend/src/pages/EquipmentDetailPage.tsx:141-160`, `frontend/src/components/NewEquipmentModal.tsx:75-125` | Botões "Criar tipo", "Criar local", "Criar situação" sem duplo "+". |
| **2.7 Testes Automatizados Frontend** | [x] | **Concluído** | `frontend/src/__tests__/ManageTagsModal.test.tsx`, `MovementModal.test.tsx` | Testes completos com Vitest + RTL. |
| **3 Validação e Conclusão** | [x] | **Concluído** | Pytest e Vitest | Todas as suítes passam com 100% de cobertura. |

---

## 4. Auditoria Detalhada: `spec/features/tela-de-login/`

### 4.1. Cenários BDD em `spec/features/tela-de-login/spec.md`

#### Cenário 1: Renderização inicial e animação da tela de login
- **Critérios:** Rota `/login` surge com animação (*fade-in / scale-up*), formulário centralizado, campos limpos e foco no Email.
- **Rastreabilidade:**
  - **Frontend:** `frontend/src/pages/LoginPage.tsx` (linhas 28-55: classe `animate-fade-in-scale`, container centralizado `my-auto`, elementos da marca `Gestão de Patrimônio`).
  - **CSS:** `frontend/tailwind.config.js` (linhas 25-32: keyframe `fadeInScale` e animação `fade-in-scale`).
  - **Testes Frontend:** `frontend/src/__tests__/LoginPage.test.tsx` (linhas 40-50); `frontend/src/__tests__/LoginForm.test.tsx` (linhas 40-50).
- **Status:** **Conforme**

---

#### Cenário 2: Validação de campos obrigatórios no frontend
- **Critérios:** Tentar submeter sem email ou senha bloqueia o envio e exibe mensagens "Email é obrigatório." e "Senha é obrigatória.". Formato de email inválido também é validado.
- **Rastreabilidade:**
  - **Frontend:** `frontend/src/components/LoginForm.tsx` (linhas 20-35: função `validate`; linhas 91-93 e 133-135: mensagens de erro visuais).
  - **Testes Frontend:** `frontend/src/__tests__/LoginForm.test.tsx` (linhas 52-71); `frontend/src/__tests__/LoginPage.test.tsx` (linhas 52-64).
- **Status:** **Conforme**

---

#### Cenário 3: Interação visual no hover do botão de login
- **Critérios:** Ponteiro do mouse sobre o botão "Entrar" causa transição suave de tom, elevação sutil e brilho (*glow*).
- **Rastreabilidade:**
  - **Frontend:** `frontend/src/components/LoginForm.tsx` (linhas 139-156: `className="... bg-zinc-100 hover:bg-white text-zinc-950 text-xs font-semibold rounded-xl transition-all duration-150 active:scale-[0.99] focus:outline-none focus:ring-2 focus:ring-zinc-400/50 shadow-sm cursor-pointer"`).
  - **CSS Base:** `frontend/src/index.css` (linhas 15-17: `.btn-transition`).
  - **Testes Frontend:** `frontend/src/__tests__/LoginForm.test.tsx`.
- **Status:** **Conforme**

---

#### Cenário 4: Submissão bem-sucedida de login
- **Critérios:** Preenchimento de credenciais válidas ativa `isSubmitting`, desabilita campos, exibe spinner (`Validando credenciais...`); recebendo HTTP 200, atualiza `AuthContext` e redireciona para `/dashboard`.
- **Rastreabilidade:**
  - **Frontend Componente:** `frontend/src/components/LoginForm.tsx` (linhas 37-53: `setIsSubmitting(true)` e renderização condicional de `<Loader2 className="animate-spin" />`).
  - **Contexto:** `frontend/src/context/AuthContext.tsx` (linhas 46-73: `login` chama `authApi.login` com `withCredentials: true`, gravando os Cookies HttpOnly e setando `user`).
  - **Redirecionamento:** `frontend/src/pages/LoginPage.tsx` (linhas 11-15 e 46: `onSuccess={() => navigate('/dashboard', { replace: true })}`).
  - **Testes Frontend:** `frontend/src/__tests__/LoginPage.test.tsx` (linhas 137-156); `frontend/src/__tests__/LoginForm.test.tsx`.
- **Status:** **Conforme**

---

#### Cenário 5: Exibição de erro por credenciais inválidas (HTTP 401)
- **Critérios:** Resposta HTTP 401 da API reabilita o formulário e exibe mensagem amigável: `"Credenciais inválidas. Verifique seu email e senha."`.
- **Rastreabilidade:**
  - **Contexto:** `frontend/src/context/AuthContext.tsx` (linhas 60-62: se `status === 401`, seta `setError('Credenciais inválidas. Verifique seu email e senha.')` e `rateLimitBlocked: false`).
  - **Componente Banner:** `frontend/src/components/AlertBanner.tsx` (linhas 24, 31: ícone `AlertCircle` e fundo vermelho).
  - **Formulário:** `frontend/src/components/LoginForm.tsx` (linhas 57-63: renderiza `<AlertBanner />` e reabilita campos no bloco `finally`).
  - **Testes Frontend:** `frontend/src/__tests__/LoginPage.test.tsx` (linhas 87-110); `frontend/src/__tests__/LoginForm.test.tsx` (linhas 94-117); `frontend/src/__tests__/AlertBanner.test.tsx`.
- **Status:** **Conforme**

---

#### Cenário 6: Exibição de alerta de bloqueio por força bruta (HTTP 429)
- **Critérios:** Quando o IP atinge o limite e a API retorna HTTP 429, o formulário é reabilitado e um banner de alerta em destaque (âmbar/amarelo com ícone `ShieldAlert`) avisa sobre o bloqueio por segurança (tentar em 15 minutos).
- **Rastreabilidade:**
  - **Backend:** `src/use_cases/authenticate_user.py` (linhas 46-55: validação de taxa de 10 tentativas em 15 minutos); `src/api/routes.py` (linhas 52-53: retorna HTTP 429).
  - **Contexto:** `frontend/src/context/AuthContext.tsx` (linhas 57-59: se `status === 429`, seta `rateLimitBlocked: true` e mensagem de bloqueio por 15 minutos).
  - **Componente Banner:** `frontend/src/components/AlertBanner.tsx` (linhas 22-23, 28-29: renderiza `isRateLimit` com `bg-amber-950/70 border-amber-500/40 text-amber-200` e ícone `ShieldAlert`).
  - **Testes Frontend:** `frontend/src/__tests__/LoginPage.test.tsx` (linhas 112-135); `frontend/src/__tests__/LoginForm.test.tsx` (linhas 119-142); `frontend/src/__tests__/AlertBanner.test.tsx`.
  - **Testes Backend:** `tests/test_use_case.py::test_authenticate_user_rate_limit_exceeded`, `tests/test_rate_limit.py`.
- **Status:** **Conforme**

---

### 4.2. Auditoria de Tarefas: `spec/features/tela-de-login/tasks.md`

| Tarefa | Status Checklist | Status Código | Evidências / Arquivos | Observações |
|---|:---:|:---:|---|---|
| **TASK-UI-01** | [x] | **Concluído** | `frontend/src/index.css`, `frontend/tailwind.config.js` | Configuração de Tailwind, tokens de cores, animações `fadeInScale`, fonte Inter. |
| **TASK-UI-02** | [x] | **Concluído** | `frontend/src/api/authApi.ts`, `frontend/src/context/AuthContext.tsx`, `frontend/src/hooks/useAuth.ts` | Cliente Axios com `withCredentials: true`, gerenciamento de Cookies HttpOnly e sessão. |
| **TASK-UI-03** | [x] | **Concluído** | `frontend/src/components/LoginForm.tsx` | Formulário com anel de foco, micro-interações, validações client-side e `isSubmitting`. |
| **TASK-UI-04** | [x] | **Concluído** | `frontend/src/components/AlertBanner.tsx` | Banner para 401 (vermelho) e 429 (âmbar com `ShieldAlert`). |
| **TASK-UI-05** | [x] | **Concluído** | `frontend/src/pages/LoginPage.tsx` | Layout centralizado responsivo com animação de entrada e redirecionamento. |
| **TASK-UI-06** | [x] | **Concluído** | `frontend/src/__tests__/LoginPage.test.tsx`, `LoginForm.test.tsx`, `AlertBanner.test.tsx` | Suíte RTL / Vitest cobrindo os 6 cenários BDD com 100% de sucesso. |

---

## 5. Auditoria de Aderência à Constituição do Projeto (`GEMINI.md`)

### 5.1. Cobertura de Testes Automatizados (Meta: 100% Linhas e Branches)
- **Backend (Pytest):**
  - Execução: `pytest --cov=src --cov-branch` -> **104 testes aprovados** (100% de sucesso).
  - Cobertura nos módulos do Grupo A:
    - `src/api/equipment_routes.py`: **100% linhas / 100% branches** (139 stmts);
    - `src/api/routes.py` (auth): **100% linhas / 100% branches** (62 stmts);
    - `src/use_cases/equipment_use_cases.py`: **100% linhas / 100% branches** (209 stmts, 80 branches);
    - `src/use_cases/authenticate_user.py`: **100% linhas / 100% branches** (34 stmts, 4 branches);
    - `src/infrastructure/repositories.py`: **100% linhas / 100% branches** (168 stmts, 32 branches);
    - `src/domain/models.py`: **100%** (72 stmts);
    - `src/domain/schemas.py`: **100%** (145 stmts);
    - `src/core/security.py`: **100%** (60 stmts, 8 branches);
    - `src/core/database.py`: **100%** (14 stmts).
  - *Nota:* O único arquivo com 98% no backend geral é `src/infrastructure/spreadsheet_parser.py` (pertencente ao Grupo B / Importação).
- **Frontend (Vitest):**
  - Execução: `vitest run` -> **57 testes aprovados** em 15 arquivos de teste (100% de sucesso).
  - Compilação TypeScript: `tsc --noEmit` -> **0 erros de compilação**.

### 5.2. Princípios de Banco de Dados e SQLAlchemy 2.0
- **SQLAlchemy 2.0:** Todo acesso ao banco em `src/infrastructure/repositories.py` utiliza exclusivamente a sintaxe do SQLAlchemy 2.0 (`select(...)`, `update(...)`, `delete(...)`, `.scalar_one_or_none()`, etc.).
- **Ausência de Raw SQL:** Verificado via busca de padrões (`text(`, `execute("SELECT...`) — **zero instâncias de raw SQL**. Totalmente aderente.
- **Controle Transacional:**
  - Repositórios **não** realizam `db.commit()` nem `db.rollback()`. Eles executam apenas `.add()`, `.flush()` ou manipulação de objetos.
  - O commit e rollback são executados estritamente na borda da operação/caso de uso nos roteadores (`equipment_routes.py` e `routes.py`), garantindo que operações que compartilham o mesmo caso de uso sejam comitadas ou revertidas conjuntamente.

### 5.3. Controle de Acesso (RBAC)
- Todas as rotas de equipamentos (`/api/v1/equipments/*`), tags (`/api/v1/equipments/tags/*`) e sugestões (`/api/v1/equipments/suggestions`) exigem a dependência `current_user: User = Depends(require_tecnico_role)`.
- Usuários autenticados com a role `colaborador` recebem estritamente `HTTP 403 Forbidden`. Testado e validado em `test_equipment_api.py::test_equipment_api_rbac_forbidden_for_colaborador` e `test_equipment_api_tags`.

---

## 6. Matriz Consolidada de Rastreabilidade e Conformidade (Grupo A)

| ID do Cenário | Nome do Requisito / Cenário | Módulo / Spec | Backend (`src/`) | Frontend (`frontend/`) | Testes (`tests/` e Vitest) | Status | Detalhes do Gap |
|---|---|---|---|---|---|:---:|---|
| **EQ-BDD-01** | Filtro múltiplos valores (Nº Série OR) | Equipamentos | `equipment_routes.py:49`, `repositories.py:155` | `EquipmentListPage.tsx`, `AutocompleteFilterInput.tsx` | `test_equipment_api.py:94`, `EquipmentPage.test.tsx` | **Conforme** | - |
| **EQ-BDD-02** | Filtros combinados (OR interno, AND externo) | Equipamentos | `repositories.py:139-161` | `EquipmentListPage.tsx:332-358` | `test_equipment_api.py:94`, `test_equipment_use_cases.py:95` | **Conforme** | - |
| **EQ-BDD-03** | Desmarcar filtro individual | Equipamentos | - | `MultiSelectFilterDropdown.tsx:48-50` | `EquipmentPage.test.tsx:103` | **Conforme** | - |
| **EQ-BDD-04** | Visualização de cards e zebra striping | Equipamentos | `equipment_routes.py:41` | `EquipmentListPage.tsx:472-536` | `EquipmentPage.test.tsx:43` | **Parcial** | Falta zebra striping (pares/ímpares), borda dupla `border-2 border-slate-700/80` e padding `p-5.5`. |
| **EQ-BDD-05** | Edição completa em lote na tela de detalhes | Equipamentos | `equipment_routes.py:226`, `equipment_use_cases.py:126` | `EquipmentDetailPage.tsx:163-211` | `test_equipment_use_cases.py:102`, `EquipmentPage.test.tsx:183` | **Conforme** | - |
| **EQ-BDD-06** | Manutenção com múltiplos itens e data | Equipamentos | `equipment_routes.py:267`, `equipment_use_cases.py:206` | `MaintenanceModal.tsx:37-44` | `test_equipment_use_cases.py:test_record_maintenance...` | **Conforme** | - |
| **EQ-BDD-07** | Editar e excluir manutenção no histórico | Equipamentos | `equipment_routes.py:286-329`, `equipment_use_cases.py:234` | `EditMaintenanceModal.tsx`, `EquipmentDetailPage.tsx:213` | `test_equipment_use_cases.py:test_update_and_delete...` | **Conforme** | - |
| **EQ-BDD-08** | Navegação explícita (Dashboard / Equipamentos) | Equipamentos | - | `EquipmentListPage.tsx:253`, `EquipmentDetailPage.tsx` | `EquipmentPage.test.tsx:111, 200` | **Conforme** | - |
| **AC-BDD-01** | Sugestões com prefixo >= 2 chars | Autocomplete | `equipment_routes.py:161`, `repositories.py:270` | `AutocompleteFilterInput.tsx:36-68` | `test_equipment_api.py:305`, `AutocompleteFilterInput.test.tsx:42` | **Conforme** | - |
| **AC-BDD-02** | Bloqueio de busca com < 2 chars | Autocomplete | `equipment_use_cases.py:378` | `AutocompleteFilterInput.tsx:42-47` | `AutocompleteFilterInput.test.tsx:12`, `test_equipment_api.py:362` | **Conforme** | - |
| **AC-BDD-03** | Adicionar sugestão como chip ao clicar | Autocomplete | - | `AutocompleteFilterInput.tsx:70-75` | `AutocompleteFilterInput.test.tsx:78` | **Conforme** | - |
| **AC-BDD-04** | Ocultar valores já selecionados | Autocomplete | - | `AutocompleteFilterInput.tsx:53` | `AutocompleteFilterInput.test.tsx:50` | **Conforme** | - |
| **AC-BDD-05** | Entrada livre via tecla Enter | Autocomplete | - | `AutocompleteFilterInput.tsx:77-87` | `AutocompleteFilterInput.test.tsx:86` | **Conforme** | - |
| **AC-BDD-06** | Erro 400 para campo inválido | Autocomplete | `equipment_routes.py:173`, `equipment_use_cases.py:374` | - | `test_equipment_api.py:357`, `test_equipment_use_cases.py` | **Conforme** | - |
| **AC-BDD-07** | Erro 400 para prefixo curto | Autocomplete | `equipment_routes.py:173`, `equipment_use_cases.py:378` | - | `test_equipment_api.py:362` | **Conforme** | - |
| **TAG-BDD-01** | Listar tags filtradas por categoria | Tags CRUD | `equipment_routes.py:92`, `repositories.py:328` | `ManageTagsModal.tsx:195-226` | `test_equipment_api.py:171`, `ManageTagsModal.test.tsx:40` | **Conforme** | - |
| **TAG-BDD-02** | Criar nova tag com sucesso | Tags CRUD | `equipment_routes.py:103`, `equipment_use_cases.py:314` | `ManageTagsModal.tsx:81-100` | `test_equipment_api.py:161`, `ManageTagsModal.test.tsx:60` | **Conforme** | - |
| **TAG-BDD-03** | Impedir criação de tag duplicada (400) | Tags CRUD | `equipment_use_cases.py:320`, `equipment_routes.py:116` | `ManageTagsModal.tsx` | `test_equipment_api.py:167`, `test_equipment_use_cases.py` | **Conforme** | - |
| **TAG-BDD-04** | Renomear tag e propagar para equipamentos | Tags CRUD | `equipment_routes.py:121`, `repositories.py:350` | `ManageTagsModal.tsx:102-136` | `test_equipment_repositories.py:96`, `ManageTagsModal.test.tsx:88` | **Conforme** | - |
| **TAG-BDD-05** | Excluir tag preservando histórico de ativos | Tags CRUD | `equipment_routes.py:143`, `equipment_use_cases.py:351` | `ManageTagsModal.tsx:138-151` | `test_equipment_api.py:195`, `ManageTagsModal.test.tsx:120` | **Conforme** | - |
| **TAG-BDD-06** | Criar nova tag inline na movimentação | Tags CRUD | `equipment_routes.py:103` | `MovementModal.tsx:39-53` | `MovementModal.test.tsx:42` | **Conforme** | - |
| **TAG-BDD-07** | RBAC: Bloqueio 403 para colaboradores | Tags CRUD | `equipment_routes.py:96, 107, 126, 147` | `SideMenu.tsx:125` | `test_equipment_api.py:204-217` | **Conforme** | - |
| **LOG-BDD-01** | Renderização inicial e animação de login | Tela de Login | - | `LoginPage.tsx:28-55`, `LoginForm.tsx` | `LoginPage.test.tsx:40`, `LoginForm.test.tsx:40` | **Conforme** | - |
| **LOG-BDD-02** | Validação client-side (Email/Senha) | Tela de Login | - | `LoginForm.tsx:20-35, 91-93` | `LoginPage.test.tsx:52`, `LoginForm.test.tsx:52` | **Conforme** | - |
| **LOG-BDD-03** | Interação visual no hover do botão | Tela de Login | - | `LoginForm.tsx:139-156`, `index.css` | `LoginForm.test.tsx` | **Conforme** | - |
| **LOG-BDD-04** | Submissão bem-sucedida e redirect dashboard | Tela de Login | `routes.py:30-58` | `LoginForm.tsx:37-53`, `LoginPage.tsx:11` | `LoginPage.test.tsx:137`, `LoginForm.test.tsx` | **Conforme** | - |
| **LOG-BDD-05** | Mensagem amigável para HTTP 401 | Tela de Login | `routes.py:54-55` | `AuthContext.tsx:60-62`, `AlertBanner.tsx` | `LoginPage.test.tsx:87`, `LoginForm.test.tsx:94` | **Conforme** | - |
| **LOG-BDD-06** | Alerta visual de destaque para HTTP 429 | Tela de Login | `routes.py:52-53`, `authenticate_user.py:46` | `AuthContext.tsx:57-59`, `AlertBanner.tsx` | `LoginPage.test.tsx:112`, `test_rate_limit.py` | **Conforme** | - |

---

## 7. Recomendações e Plano de Ação para o Grupo A

1. **Ajuste Visual nos Cards de Equipamentos (`EquipmentListPage.tsx`):**
   - **Ação:** No mapeamento de itens da lista (`equipments.map((item, index) => ...)`), aplicar estilização com alternância de cores para itens pares e ímpares (*zebra striping*):
     - Par: `bg-slate-900 border-2 border-slate-700/80`
     - Ímpar: `bg-slate-950/80 border-2 border-slate-800/80`
     - Ajustar o padding interno para `p-5 sm:px-6 sm:py-5`.
   - **Impacto:** Eleva a conformidade do Cenário EQ-BDD-04 e TASK-EQ-13 de **Parcial** para **100% Conforme**.
