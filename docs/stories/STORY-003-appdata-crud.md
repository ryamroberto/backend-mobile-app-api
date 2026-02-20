# Story 1.3: Implementação do Domínio de Negócio (AppData) e CRUD de Recursos

**Status**: Completed

## Story
**As a** Usuário Autenticado,
**I want** gerenciar meus recursos (criar, visualizar, editar e excluir),
**so that** eu possa organizar meus dados dentro do aplicativo.

## Acceptance Criteria
1. O modelo `Resource` deve ser implementado no app `appdata` com os campos: `id` (UUID), `owner` (FK -> User), `title`, `description`, `status` (Choices: ACTIVE, ARCHIVED) e `metadata` (JSONField).
2. O modelo deve herdar de `TimeStampedModel` do app `common`.
3. Deve ser implementado um `ModelViewSet` para `Resource` no app `appdata`.
4. O endpoint `/api/v1/app/resources/` deve listar apenas os recursos pertencentes ao usuário autenticado.
5. O usuário só pode visualizar, editar ou excluir seus próprios recursos (`IsOwner` permission).
6. A listagem deve suportar paginação básica (padrão do DRF).
7. REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled
>
> CodeRabbit CLI is not enabled in `core-config.yaml`.
> Quality validation will use manual review process only.

### Story Type Analysis
**Primary Type**: API
**Secondary Type(s)**: Database
**Complexity**: Medium

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @architect

**Supporting Agents**:
- @qa

### Quality Gate Tasks
- [x] Pre-Commit (@dev): Run before marking story complete

## Tasks / Subtasks
- [x] **Modelagem de Dados (`appdata` app)**
    - [x] Definir `Resource` em `appdata/models.py`.
    - [x] Criar migrações e aplicar ao banco.
- [x] **Serializers e Permissões**
    - [x] Criar `ResourceSerializer` em `appdata/serializers.py`.
    - [x] Implementar permissão customizada `IsOwner` em `common/permissions.py`.
- [x] **Views e ViewSets**
    - [x] Implementar `ResourceViewSet` em `appdata/views.py`.
    - [x] Sobrescrever `get_queryset` para filtrar por `request.user`.
    - [x] Sobrescrever `perform_create` para associar o `owner` automaticamente.
- [x] **Configuração de URLs**
    - [x] Criar `appdata/urls.py` e registrar o ViewSet usando um `DefaultRouter`.
    - [x] Incluir as URLs no `core/urls.py` sob o prefixo `/api/v1/app/`.
- [x] **Verificação**
    - [x] Validar CRUD completo via testes automatizados.

## Dev Notes
- O campo `owner` é preenchido automaticamente no `perform_create` da View.
- Implementada permissão `IsOwner` em `common/permissions.py` para reuso.
- Modelo `Resource` utiliza `UUID` como chave primária.

### Testing
- Localização: `appdata/tests.py`.
- Framework: Django Test / Pytest.
- Cenários: Criar recurso com sucesso, Listar apenas meus recursos, Tentar acessar recurso de outro usuário (404), Atualizar e Deletar recurso.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 09/02/2026 | 1.0 | Criação da história de CRUD de Recursos | River (SM) |
| 09/02/2026 | 1.1 | Implementação do modelo e endpoints de Resource | Dex (Dev) |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Testes de appdata passaram com sucesso (5 testes).
- Migrações aplicadas corretamente.

### Completion Notes List
- Modelo Resource implementado com herança de TimeStampedModel.
- ViewSet configurado com permissões de dono e filtragem de queryset.
- Endpoints registrados em `/api/v1/app/resources/`.

### File List
- common/permissions.py (criado)
- appdata/models.py (modificado)
- appdata/serializers.py (criado)
- appdata/views.py (modificado)
- appdata/urls.py (criado)
- core/urls.py (modificado)
- appdata/tests.py (modificado)

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Modelo `Resource` com UUID, FK para User, Choices de status e JSONField.
2. [x] Herança de `TimeStampedModel` confirmada.
3. [x] `ModelViewSet` implementado para CRUD completo.
4. [x] Filtragem de queryset por usuário autenticado funcional.
5. [x] Permissão `IsOwner` aplicada e validada em todos os métodos de detalhe.
6. [x] Paginação padrão do DRF ativa.
7. [x] Textos de interface e nomes de campos seguindo `pt-br`.

**Análise Técnica:**
- Uso correto de `perform_create` para injeção de dependência do `owner`.
- Isolamento de dados entre usuários garantido tanto pelo `get_queryset` quanto pela permissão `IsOwner`.
- Flexibilidade garantida pelo uso de `JSONField` em `metadata`.
- Testes automatizados robustos cobrindo fluxos felizes e de exceção (acesso não autorizado).

**Evidências:**
- Execução de `python manage.py test appdata`: 5 testes passaram com sucesso.
- Verificação manual de `appdata/views.py` e `common/permissions.py`.

— Quinn, guardião da qualidade 🛡️