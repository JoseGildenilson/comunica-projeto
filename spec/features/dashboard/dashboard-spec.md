# Especificação: Dashboard

## Visão Geral
Após o login, o sistema deve redirecionar para a tela de dashboard, onde o usuário terá visão dos números de tickets (pendentes e em andamento).
- O **Técnico** verá o total global de tickets e também o bloco de Equipamentos Cadastrados.
- O **Colaborador** verá apenas os números referentes aos tickets que ele mesmo criou, e não terá acesso ao bloco de Equipamentos Cadastrados.

## Regras de Negócio & Restrições
- **RN-01:** Deverá ter um menu lateral à esquerda, que pode ser ocultado, e ao abrir o dashboard ele deve estar oculto por padrão.
- **RN-02:** Um usuário deverá ver apenas as informações pertinentes ao seu cargo/role (Técnico vs Colaborador). As informações de e-mail ficam disponíveis ao clicar no menu lateral.
- **RN-03:** O dashboard deve ser intuitivo.
- **RN-04:** O menu lateral, por enquanto, conterá apenas a opção "Painel de Patrimônio" exclusiva para a role Técnico. Para o colaborador, não haverá opções adicionais de navegação por enquanto.
- **RN-05:** Os valores (números) e blocos de informações devem ser animados ao carregar a tela (ex: valores crescendo, blocos surgindo com fade-in), mantendo o padrão dinâmico da tela de login.

## Cenários de Aceitação (BDD)

### Cenário 1: Acesso Inicial e Animações (Técnico e Colaborador)
- **Dado** que o login foi um sucesso
- **Quando** for feito o redirecionamento para o dashboard
- **Então** os valores numéricos devem crescer gradativamente até o valor real
- **E** os blocos de informações devem surgir na tela de forma fluida (fade-in/slide-in)

### Cenário 2: Acesso ao Painel de Patrimônio (Role: Técnico)
- **Dado** que o usuário (Técnico) esteja na tela de dashboard
- **Quando** ele efetuar um clique no bloco de Equipamentos Cadastrados ou no menu "Painel de Patrimônio"
- **Então** o usuário será redirecionado para o painel de equipamentos

### Cenário 3: Visão Limitada (Role: Colaborador)
- **Dado** que um usuário com a role "Colaborador" entra na tela de dashboard
- **Quando** ele visualiza a tela
- **Então** ele deve ver apenas os números dos tickets criados por ele
- **E** não deve visualizar o bloco de Equipamentos Cadastrados
- **E** não deve haver a opção "Painel de Patrimônio" no menu lateral

## Considerações de Borda & Invariantes
- Nunca deve ser possível o acesso de um usuário sem a role técnico ao painel de controle de patrimônio.
