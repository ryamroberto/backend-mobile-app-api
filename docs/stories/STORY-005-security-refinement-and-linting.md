# Story 1.5: Refinamento de Segurança, Throttling e Qualidade de Código

**Status**: Ready for Review

## Story
**As a** Administrador do Sistema,
**I want** garantir que a API seja protegida contra abusos, permita o encerramento seguro de sessões e siga padrões rigorosos de código,
**so that** o sistema seja estável, seguro e fácil de manter.

## Acceptance Criteria
1. [x] Implementar endpoint de Logout que coloca o Refresh Token na Blacklist (usando `rest_framework_simplejwt.token_blacklist`).
2. [x] Configurar Throttling global para usuários autenticados (ex: 1000 req/dia) e anônimos (ex: 100 req/dia).
3. [x] Configurar Throttling específico para endpoints de autenticação (Login/Register) para prevenir força bruta.
4. [x] O código deve passar 100% no linter (Ruff ou Flake8) seguindo o PEP8.
5. [x] REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled
> Quality validation will use manual review process only.

### Story Type Analysis
**Primary Type**: Security
**Secondary Type(s)**: Quality, DevOps
**Complexity**: Medium

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @devops

**Supporting Agents**:
- @qa

### Quality Gate Tasks
- [x] Pre-Commit (@dev): Run before marking story complete
- [x] Lint Check: `ruff check .` ou similar

## Tasks / Subtasks
- [x] **Segurança (Logout)**
    - [x] Adicionar `rest_framework_simplejwt.token_blacklist` ao `INSTALLED_APPS`.
    - [x] Criar View de Logout no app `authentication`.
- [x] **Segurança (Throttling)**
    - [x] Configurar `DEFAULT_THROTTLE_CLASSES` e `DEFAULT_THROTTLE_RATES` em `settings.py`.
    - [x] Aplicar throttles específicos em views críticas.
- [x] **Qualidade de Código**
    - [x] Instalar `ruff` ou `flake8`.
    - [x] Corrigir eventuais violações de PEP8 no projeto.
- [x] **Verificação**
    - [x] Testar blacklist do token após logout.
    - [x] Validar bloqueio de requisições excedentes (Throttling).

## Dev Notes
- O logout no JWT exige que o cliente descarte o Access Token, mas o servidor deve invalidar o Refresh Token.
- Throttling é essencial para evitar ataques de DoS básicos e brute force.
- Adicionado `ruff` ao projeto e corrigidos 12 avisos de linter.
- Testes automatizados adicionados em `authentication/tests.py` cobrindo Logout/Blacklist e Throttling.

## QA Results
- [x] **Logout com Blacklist**: Verificado em `authentication/views.py` e confirmado com testes em `authentication/tests.py`.
- [x] **Throttling**: Configurações globais e específicas de autenticação validadas em `settings.py` e testadas com sucesso.
- [x] **Linter**: Executado `ruff check .` via venv e todos os testes passaram (All checks passed!).
- [x] **Regra PT-BR**: Todas as mensagens personalizadas nas views utilizam chaves e textos em português.
- **Decisão**: PASS ✅

— Quinn, guardião da qualidade 🛡️