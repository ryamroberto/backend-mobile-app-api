# Story 3.2: Orquestração Automática de Resolução de Casos (AI-Driven Support)

**Status**: Ready for Review

## Story
**As a** Operador de Suporte / Administrador,
**I want** disparar tarefas de automação automaticamente com base na categoria dos casos de suporte,
**so that** problemas técnicos ou de IA possam ser analisados ou resolvidos sem intervenção manual imediata.

## Acceptance Criteria
1. [x] Adicionar um campo opcional `associated_case` (ForeignKey para `support.ResolveCase`) ao modelo `AutomationTask` no app `appdata`.
2. [x] Implementar lógica de integração (via Signals ou Service Layer) que:
    - Ao criar um `ResolveCase` com categoria `TECHNICAL` ou `AI_REFINEMENT`, crie automaticamente uma `AutomationTask` relacionada.
    - O `status` do `ResolveCase` deve ser alterado para `IN_PROGRESS` assim que a tarefa for criada.
3. [x] Sincronização de Status:
    - Se a `AutomationTask` for marcada como `COMPLETED`, as `output_results` devem ser anexadas às `resolution_notes` do caso e o status do caso deve ser movido para `RESOLVED`.
    - Se a `AutomationTask` falhar (`FAILED`), o caso deve ser atualizado com o erro e o status mantido em `IN_PROGRESS` para intervenção manual (ou movido para um novo status de alerta).
4. [x] Garantir que a criação automática de tarefas não cause loops infinitos ou falhas se o app `appdata` estiver indisponível.
5. [x] REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled

### Story Type Analysis
**Primary Type**: Integration
**Secondary Type(s)**: Business Logic, Automation
**Complexity**: Medium

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @architect

**Supporting Agents**:
- @qa

## Tasks / Subtasks
- [x] **Evolução do Modelo (`appdata`)**
    - [x] Adicionar ForeignKey `associated_case` em `AutomationTask`.
    - [x] Gerar e aplicar migrações.
- [x] **Lógica de Orquestração (`support`)**
    - [x] Criar `support/signals.py` ou atualizar `case_create` service.
    - [x] Implementar trigger para `AutomationTask` baseado na categoria.
- [x] **Sincronização de Resultados**
    - [x] Implementar lógica que monitora o status da tarefa e atualiza o caso original.
- [x] **Verificação**
    - [x] Criar testes de integração que validam o fluxo: Criação de Caso -> Trigger de Tarefa -> Resolução Automática do Caso.

## Dev Notes
- Utilizar `apps.get_model` para evitar importações circulares entre `support` e `appdata`.
- Considerar o uso de `transaction.on_commit` para garantir que a tarefa só seja disparada se o caso for persistido com sucesso.
- O campo `input_params` da tarefa automática deve incluir o `id` e a `description` do caso para contexto.

### Testing
- Validar se a criação de casos em outras categorias (`BILLING`, `OTHER`) NÃO dispara automações.
- Testar falhas na automação e garantir que o caso de suporte permaneça rastreável.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 20/02/2026 | 1.0 | Rascunho inicial da integração Suporte-IA | River (SM) |
| 20/02/2026 | 1.1 | Implementação concluída e validada via testes | Dex (Dev) |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Resolvida falha de `ModuleNotFoundError: No module named 'dotenv'` via venv.
- Corrigido erro de sintaxe em f-string multi-line em `case_sync_services.py`.
- Ajustado `support/services/case_automation_services.py` para fornecer `provider_id` padrão.

### Completion Notes List
- Integração bidirecional implementada entre Support e AutomationTasks.
- Uso de `transaction.on_commit` garante consistência na criação de tarefas.
- Suíte de 31 testes passando (incluindo 5 novos testes de integração).

### File List
- appdata/models.py
- appdata/services/resource_services.py
- appdata/services/case_sync_services.py
- support/services/case_services.py
- support/services/case_automation_services.py
- support/tests_automation.py
- requirements.txt (ajustada versão django-storages)
