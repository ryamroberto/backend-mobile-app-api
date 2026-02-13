# Story 2.3: Implementação do Domínio de Orquestração (Automation Tasks)

**Status**: Completed

## Story
**As a** Desenvolvedor/Operador de IA,
**I want** gerenciar tarefas de automação (Bedrock, Step Functions, ECS),
**so that** eu possa orquestrar execuções de IA e infraestrutura de forma centralizada e rastreável.

## Acceptance Criteria
1. [x] Refatorar o modelo `Resource` (ou criar `AutomationTask`) no app `appdata` com os campos:
    - `task_type`: Choices (BEDROCK, STEP_FUNCTION, ECS, CUSTOM).
    - `provider_id`: String (para armazenar ARN ou ID externo).
    - `execution_status`: Choices (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED).
    - `input_params`: JSONField (parâmetros de entrada da tarefa).
    - `output_results`: JSONField (resultados ou logs da execução).
2. [x] Atualizar o `ResourceViewSet` (renomear para `AutomationTaskViewSet`) e as URLs para `/api/v1/app/tasks/`.
3. [x] Adaptar a `Service Layer` e os `Selectors` para as novas regras de negócio da entidade `AutomationTask`.
4. [x] Implementar validação para garantir que o `provider_id` seja obrigatório para tarefas que não sejam `CUSTOM`.
5. [x] REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled

### Story Type Analysis
**Primary Type**: Business Logic
**Secondary Type(s)**: API, Database
**Complexity**: Medium

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @architect

**Supporting Agents**:
- @qa

## Tasks / Subtasks
- [x] **Modelagem e Migração**
    - [x] Renomear/Atualizar `Resource` para `AutomationTask` em `appdata/models.py`.
    - [x] Gerar e aplicar migrações.
- [x] **Refatoração da Camada de Domínio**
    - [x] Atualizar `appdata/services/resource_services.py` para as novas lógicas de `AutomationTask`.
    - [x] Atualizar `appdata/selectors/resource_selectors.py`.
- [x] **Interface de API**
    - [x] Atualizar Serializers em `appdata/serializers.py`.
    - [x] Atualizar ViewSet em `appdata/views.py`.
    - [x] Atualizar URLs em `appdata/urls.py`.
- [x] **Verificação**
    - [x] Atualizar e rodar testes em `appdata/tests.py`.

## Dev Notes
- Modelo `Resource` foi substituído por `AutomationTask`.
- `Service Layer` agora utiliza os nomes `task_create`, `task_update`, etc.
- Endpoint alterado de `/resources/` para `/tasks/`.

### Testing
- Executados 18 testes via `venv\Scripts\python manage.py test`. Todos passaram com sucesso.
- Novos casos de teste adicionados para validar obrigatoriedade de `provider_id`.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 13/02/2026 | 1.0 | Implementação do domínio de Automação de IA | Dex (Dev) |

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Transformação do modelo genérico `Resource` em `AutomationTask` concluída com sucesso.
2. [x] Inclusão de campos específicos para orquestração: `task_type`, `provider_id`, `execution_status`, `input_params` e `output_results`.
3. [x] API exposta em `/api/v1/app/tasks/` via `AutomationTaskViewSet`.
4. [x] Lógica de validação robusta: `provider_id` é obrigatório para integrações externas (AWS), prevenindo registros inconsistentes.
5. [x] Conformidade total com a regra de idioma `pt-br` em campos e mensagens.

**Análise Técnica:**
- Refatoração limpa da camada de domínio (Services/Selectors).
- Testes automatizados validam o fluxo feliz e as restrições de validação de dados.
- Migrações aplicadas e consistentes.

— Quinn, guardião da qualidade 🛡️
