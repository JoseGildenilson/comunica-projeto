# Plano de Tarefas: Dashboard

Este documento especifica o plano detalhado de implementação para a funcionalidade de **Dashboard**, mapeando cada requisito da especificação [`spec.md`](file:///home/gil/code/internal_management/spec/features/dashboard/spec.md) e cumprindo os princípios da [`constituicao.md`](file:///home/gil/code/internal_management/spec/constituicao.md).

---

## Mapeamento de Requisitos da Especificação

| Requisito / Regra | Descrição | Tarefa Correspondente |
|---|---|---|
| **Visão Geral / RN-02** | Técnico vê global e equipamentos; Colaborador vê apenas seus tickets. | **TASK-02**, **TASK-03**, **TASK-04**, **TASK-06** |
| **RN-01** | Menu lateral à esquerda, ocultável, oculto por padrão ao iniciar. | **TASK-05** |
| **RN-03 / RN-05** | Dashboard intuitivo; Valores numéricos crescentes, blocos com fade-in/slide-in. | **TASK-07** |
| **RN-04** | "Painel de Patrimônio" no menu exclusivo para Técnico. Colaborador não vê. | **TASK-05** |
| **Cenário 1** | Animações (números e blocos) aplicadas após login bem-sucedido. | **TASK-07** |
| **Cenário 2** | Acesso ao Painel de Patrimônio por clique no Card ou Menu (Role: Técnico). | **TASK-05**, **TASK-06** |
| **Cenário 3** | Visão limitada do Colaborador (somente seus tickets, sem equipamentos/menu). | **TASK-03**, **TASK-05**, **TASK-06** |
| **Invariante** | Acesso às métricas e rotas de patrimônio bloqueado para não-técnicos. | **TASK-03**, **TASK-04**, **TASK-05** |

---

## Lista de Tarefas de Implementação

### Fase 1: Serviços de Domínio e Banco de Dados (Backend)
- [x] **TASK-01: Preparação de Dados e Modelos Base**
  - [x] Garantir/verificar que os modelos SQLAlchemy para `Ticket` e `Equipment` (ou similares) existam ou criá-los de forma base, mapeando corretamente o relacionamento com o usuário criador do ticket.
- [x] **TASK-02: Consultas ao Banco de Dados (Repository)**
  - [x] Criar query para total de tickets globais (agrupados por status: pendente/andamento).
  - [x] Criar query para total de tickets filtrados pelo ID do usuário (`user_id`).
  - [x] Criar query para total de equipamentos cadastrados.
  - [x] **Testes de Integração:** Cobertura de 100% utilizando uma instância isolada do PostgreSQL, confirmando as contagens corretas.

---

### Fase 2: Regras de Negócio e Casos de Uso (Backend)
- [x] **TASK-03: Caso de Uso do Dashboard (`GetDashboardMetrics`)**
  - [x] Orquestrar a chamada ao banco baseado na role do usuário (injetada a partir do token JWT).
  - [x] Aplicar regra para `tecnico`: buscar totais globais e total de equipamentos.
  - [x] Aplicar regra para `colaborador`: buscar totais filtrados pelo próprio `user_id` e zerar/omitir contagem de equipamentos.
  - [x] **Testes Unitários:** 100% de cobertura nos ramos condicionais para cada role.

---

### Fase 3: Interface de API HTTP (FastAPI)
- [x] **TASK-04: Endpoints HTTP de Métricas (`/api/v1/dashboard/metrics`)**
  - [x] Criar Pydantic schema de resposta (`DashboardMetricsResponse`).
  - [x] Implementar a rota GET protegida pela dependência de autenticação atual (`get_current_user`).
  - [x] Tratar injeção do usuário autenticado no Caso de Uso.
  - [x] **Testes de API:** 100% de cobertura realizando requisições com tokens simulados de Técnico e Colaborador, verificando a estrutura e os dados do JSON.

---

### Fase 4: Frontend (React.js)
- [x] **TASK-05: Componente de Menu Lateral (RN-01, RN-04, Cenário 3)**
  - [x] Criar componente genérico `SideMenu`, iniciando em estado oculto (`collapsed`).
  - [x] Inserir lógica para exibir o e-mail do usuário obtido do estado de autenticação.
  - [x] Renderizar condicionalmente a opção "Painel de Patrimônio", garantindo que só seja montada se a role do usuário for `tecnico`.
  - [x] **Testes de Componente:** Validar renderização das opções de menu dependendo da role logada.
- [x] **TASK-06: Página Principal do Dashboard e Integração**
  - [x] Criar componente da página de Dashboard e efetuar chamada para `GET /api/v1/dashboard/metrics`.
  - [x] Mapear dados da API para blocos informativos (Cards de "Tickets Pendentes", "Tickets em Andamento").
  - [x] Renderizar condicionalmente o Card de "Equipamentos Cadastrados" e seu link de redirecionamento apenas se for `tecnico` (Cenário 2).
  - [x] **Testes de Integração:** Simular a resposta da API com mock e verificar se a renderização restringe corretamente a visão do colaborador.
- [x] **TASK-07: Micro-animações e Design Vibrante (Cenário 1, RN-03, RN-05)**
  - [x] Implementar transição CSS/framer-motion para os blocos surgirem na tela com *fade-in* ou *slide-in*.
  - [x] Desenvolver hook/lógica (ex. *CountUp*) para que os valores numéricos cresçam progressivamente de 0 até o valor retornado pela API.

---

### Fase 5: Validação Final
- [x] **TASK-08: Auditoria de Cobertura de Testes (100% Lines e Branches)**
  - [x] Executar suíte de testes do backend (`uv run pytest --cov=src --cov-branch --cov-report=term-missing`).
  - [x] Assegurar 100% de cobertura em todo código executável modificado ou criado para esta feature, conforme a Constituição do Projeto.
