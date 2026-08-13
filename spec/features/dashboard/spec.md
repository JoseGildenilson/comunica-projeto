# Especificação: Dashboard

## Visão Geral
Após o login, o sistema deve redirecionar para a tela de dashboard, onde o usuário terá visão dos principais indicadores do sistema.
- O **Técnico** verá os indicadores de Equipamentos Cadastrados e o total global do sistema.
- O **Colaborador** verá apenas os números referentes aos seus equipamentos e solicitações atribuídas.
- **Nota de Fase 1 (MVP - Foco em Patrimônio):** O módulo de chamados/tickets pertence à Fase 2. Na Fase 1, a tela apresentará os dados reais de **Patrimônio/Equipamentos**, enquanto eventuais blocos visuais de tickets funcionarão como placeholders/zerados para preenchimento de layout.

## Regras de Negócio & Restrições
- **RN-01:** Deverá ter um menu lateral à esquerda, que pode ser ocultado, e ao abrir o dashboard ele deve estar oculto por padrão.
- **RN-02:** Um usuário deverá ver apenas as informações pertinentes ao seu cargo/role (Técnico vs Colaborador). As informações de e-mail do usuário ficam disponíveis ao clicar/expandir o menu lateral.
- **RN-03:** O dashboard deve ser intuitivo, dinâmico e de fácil visualização.
- **RN-04:** O menu lateral conterá a opção "Painel de Patrimônio" (exclusiva para a role Técnico). Para o colaborador, não haverá opções adicionais de navegação por enquanto.
- **RN-05:** Os valores (números) e blocos de informações devem ser animados ao carregar a tela (ex: valores crescendo com efeito CountUp, blocos surgindo com fade-in/slide-in), mantendo o padrão dinâmico da aplicação.

## Cenários de Aceitação (BDD)

### Cenário 1: Acesso Inicial e Animações (Técnico e Colaborador)
- **Dado** que o login foi realizado com sucesso
- **Quando** for feito o redirecionamento para o dashboard
- **Então** os valores numéricos dos blocos devem crescer gradativamente (*CountUp*) até o valor real
- **E** os blocos de informações devem surgir na tela de forma fluida (*fade-in / slide-in*).

### Cenário 2: Acesso ao Painel de Patrimônio (Role: Técnico)
- **Dado** que o usuário (Técnico) esteja na tela de dashboard
- **Quando** ele efetuar um clique no bloco de Equipamentos Cadastrados ou no menu "Painel de Patrimônio"
- **Então** o usuário será redirecionado para a tela de listagem de equipamentos (`/equipamentos`).

### Cenário 3: Visão Limitada (Role: Colaborador)
- **Dado** que um usuário com a role "Colaborador" entra na tela de dashboard
- **Quando** ele visualiza a tela
- **Então** ele deve ver apenas os números das suas solicitações/equipamentos vinculados
- **E** não deve visualizar o bloco de controle global de Equipamentos Cadastrados
- **E** não deve haver a opção "Painel de Patrimônio" no menu lateral.

## Considerações de Borda & Invariantes
- Nunca deve ser possível o acesso de um usuário sem a role técnico ao painel de controle de patrimônio.
