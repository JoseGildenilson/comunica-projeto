# Original User Request

## 2026-10-13T15:55:26Z

Auditar e verificar a conformidade de 100% das especificações presentes em `spec/features/` contra a implementação atual da base de código (backend em `src/`, frontend em `frontend/` e testes em `tests/`), gerando um relatório detalhado de rastreabilidade que aponte exatamente o que está conforme, parcial ou pendente, além de validar a aderência à Constituição do projeto.

Working directory: C:/Users/70486375447/orca/comunica-projeto
Integrity mode: development

## Requirements

### R1. Auditoria e Rastreabilidade Exaustiva de Especificações
Realizar o cruzamento detalhado de cada requisito, cenário BDD e tarefa descritos nas pastas de especificações (`spec/features/*`) contra o código existente no backend (`src/`), frontend (`frontend/`) e testes (`tests/`). Para cada requisito/cenário, identificar com precisão o status:
- Conforme (implementado com teste correspondente)
- Parcial (implementação incompleta ou sem testes adequados)
- Não Implementado (ausente no código ou no frontend)

### R2. Checagem de Cobertura e Aderência à Constituição do Projeto
Executar e analisar os testes automatizados existentes (`pytest`) e verificar a aderência aos princípios da Constituição definidos em `GEMINI.md`:
- Cobertura de testes automatizados do código executável (meta de 100% em linhas e branches).
- Separação arquitetural, uso de SQLAlchemy 2.0 (sem raw SQL), controle transacional no nível de caso de uso/operação.
- Validação se alterações de spec possuem testes correspondentes.

### R3. Elaboração de Relatório Executivo e Técnico de Conformidade
Consolidar todos os achados em um relatório estruturado em Markdown (`audit_spec_compliance.md` na raiz do projeto), contendo:
- Sumário executivo com o percentual global de conformidade das specs.
- Tabela de rastreabilidade por feature com status e links/caminhos para os arquivos que atendem (ou deveriam atender) cada item.
- Lista prioritária de pendências e débitos técnicos encontrados, sugerindo as ações necessárias para atingir 100% de conformidade.

## Acceptance Criteria

### Cobertura de Auditoria das Features
- [ ] Todas as 8 pastas em `spec/features/` são analisadas e documentadas no relatório:
  - `equipamentos` (incluindo `autocomplete-filtros` e `spec-corretion.md`)
  - `tags-crud`
  - `tela-de-login`
  - `exportacao-planilha`
  - `importacao-planilha`
  - `documentacao`
  - `gitignore`
  - `UI`
- [ ] Cada cenário BDD em cada `spec.md` possui indicação explícita do arquivo/componente que o implementa ou justificativa de pendência.
- [ ] Cada tarefa em cada `tasks.md` tem seu status de conclusão verificado na base de código.

### Verificação de Testes e Constituição
- [ ] A suíte de testes unitários e de integração (`pytest`) é executada e o resultado (pass/fail e percentual de cobertura) é documentado no relatório.
- [ ] Violações aos princípios da Constituição (ex: raw SQL, transações em repositórios, falta de cobertura) são explicitamente apontadas se existirem.

### Entregável
- [ ] O relatório `audit_spec_compliance.md` é gerado na raiz do repositório, com formatação clara e tabela de rastreabilidade.
