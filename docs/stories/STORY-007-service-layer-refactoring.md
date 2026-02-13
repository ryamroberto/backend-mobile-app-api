# Story 2.1: Refatoração para Service Layer e Selectors

**Status**: Ready for Review

## Story
**As a** Arquiteto de Software,
**I want** desacoplar a lógica de negócio das Views utilizando os padrões Service Layer e Selectors,
**so that** o código seja mais fácil de testar, reutilizar e manter à medida que o sistema cresce.

## Acceptance Criteria
1. Criar uma estrutura de pastas `services/` e `selectors/` dentro de cada app relevante (`appdata`, `profiles`).
2. Mover a lógica de criação e atualização de `Resource` para `appdata/services/resource_services.py`.
3. Mover queries complexas ou filtros de `Resource` para `appdata/selectors/resource_selectors.py`.
4. As Views devem apenas chamar os Services/Selectors e lidar com o status HTTP.
5. Manter 100% de cobertura de testes nos novos Services.
6. REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled

### Story Type Analysis
**Primary Type**: Refactoring
**Secondary Type(s)**: Architecture, Quality
**Complexity**: Medium

### Specialized Agent Assignment
**Primary Agents**:
- @architect
- @dev

### Quality Gate Tasks
- [x] Unit Tests for Services
- [x] Integration Tests for Views (Regression)

## Tasks / Subtasks
- [x] **Preparação da Estrutura**
    - [x] Criar diretórios `services` e `selectors` nos apps.
- [x] **Refatoração AppData**
    - [x] Criar `create_resource_service`.
    - [x] Criar `update_resource_service`.
    - [x] Atualizar `ResourceViewSet` para usar os novos services.
- [x] **Refatoração Profiles**
    - [x] Mover lógica de atualização de perfil para um service dedicado.
- [x] **Verificação**
    - [x] Rodar suíte de testes existente para garantir que não houve quebras (Regressão).

## Dev Notes
- O padrão Service Layer ajuda a evitar o "Fat Model" ou "Fat View".
- Selectors são funções puras que retornam QuerySets ou dados filtrados.
- Refatoração concluída mantendo total compatibilidade com a suíte de testes existente.

### Testing
- Executados 18 testes via `venv\Scripts\python manage.py test`. Todos passaram com sucesso.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 13/02/2026 | 1.0 | Implementação da Service Layer e Selectors | Dex (Dev) |

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Estrutura de pastas `services/` e `selectors/` criada corretamente em `appdata` e `profiles`.
2. [x] Lógica de criação, atualização e deleção de recursos isolada em `resource_services.py`.
3. [x] Consultas e filtros de recursos isolados em `resource_selectors.py`.
4. [x] ViewSets e Views refatoradas para utilizar a camada de domínio, mantendo a responsabilidade da View apenas sobre o protocolo HTTP.
5. [x] Regressão automatizada confirmada: 18 testes aprovados.
6. [x] Mensagens, docstrings e comentários em conformidade com a regra `pt-br`.

**Análise Técnica:**
- Implementação robusta com uso de `transaction.atomic` e `full_clean()`.
- Resolução correta de dependências circulares e imports relativos.
- Código limpo, seguindo padrões PEP8 e arquitetura modular.

— Quinn, guardião da qualidade 🛡️
