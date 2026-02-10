# Story 1.2: Gestão de Perfil de Usuário e Criação Automática

**Status**: Ready for Review

## Story
**As a** Usuário do Sistema,
**I want** que meu perfil seja criado automaticamente e que eu possa editá-lo,
**so that** minhas informações personalizadas sejam mantidas separadas das minhas credenciais de acesso.

## Acceptance Criteria
1. O modelo `Profile` deve ser implementado no app `profiles` com campos: `user` (OneToOne), `full_name`, `bio`, `avatar`, `created_at` e `updated_at`.
2. Deve ser implementado um *Signal* (`post_save`) no app `profiles` para criar automaticamente um `Profile` sempre que um novo `User` for registrado.
3. O endpoint `/api/v1/profile/me/` deve permitir que o usuário logado visualize seus próprios dados.
4. O endpoint `/api/v1/profile/me/` deve permitir que o usuário logado atualizar seus dados (PATCH).
5. O acesso aos endpoints de perfil deve ser restrito a usuários autenticados.
6. REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled
>
> CodeRabbit CLI is not enabled in `core-config.yaml`.
> Quality validation will use manual review process only.

### Story Type Analysis
**Primary Type**: API
**Secondary Type(s)**: Database, Architecture
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
- [x] **Modelagem de Perfil (`profiles` app)**
    - [x] Definir `Profile` em `profiles/models.py`.
    - [x] Garantir que o modelo herda de um modelo base de timestamp ou tenha os campos `created_at`/`updated_at`.
- [x] **Implementação de Signals**
    - [x] Criar `profiles/signals.py` com a lógica de criação automática.
    - [x] Conectar o signal no `profiles/apps.py` (método `ready`).
- [x] **Serializers e Views**
    - [x] Criar `ProfileSerializer` em `profiles/serializers.py`.
    - [x] Implementar `ProfileView` (ou ViewSet) em `profiles/views.py` para o endpoint `/me/`.
- [x] **Configuração de URLs**
    - [x] Criar `profiles/urls.py` e incluí-lo no `core/urls.py` sob o prefixo `/api/v1/profile/`.
- [x] **Migrações e Verificação**
    - [x] Gerar e aplicar migrações para o app `profiles`.
    - [x] Validar a criação automática criando um usuário via endpoint de registro.

## Dev Notes
- Utilize `OneToOneField` com `related_name='profile'` para ligar o Perfil ao Usuário.
- Para o campo de `avatar`, use `ImageField`. Certifique-se de que o `Pillow` esteja disponível se for testar o upload de imagem.
- O endpoint `/me/` deve retornar o perfil do `request.user`.
- Adicionado `TimeStampedModel` em `common/models.py` para reutilização.

### Testing
- Localização: `profiles/tests.py`.
- Framework: Django Test / Pytest.
- Cenários: Criação automática de perfil após registro, Visualização do perfil (/me/), Atualização de nome e bio.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 09/02/2026 | 1.0 | Criação da história de Gestão de Perfil | River (SM) |
| 09/02/2026 | 1.1 | Implementação de Perfil e Signals | Dex (Dev) |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Testes de perfil passaram com sucesso (4 testes).
- Signal de criação automática verificado via teste unitário.

### Completion Notes List
- Modelo Profile criado com OneToOne para User.
- TimeStampedModel implementado em `common`.
- Signals configurados para criar perfil no registro do usuário.
- Endpoint `/api/v1/profile/me/` funcional para GET e PATCH.

### File List
- common/models.py (modificado)
- profiles/models.py (modificado)
- profiles/signals.py (criado)
- profiles/apps.py (modificado)
- profiles/serializers.py (criado)
- profiles/views.py (modificado)
- profiles/urls.py (criado)
- core/urls.py (modificado)
- profiles/tests.py (modificado)

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Modelo `Profile` implementado com campos user (OneToOne), full_name, bio, avatar, created_at e updated_at.
2. [x] Signal `post_save` funcional para criação automática de perfil.
3. [x] Endpoint `/api/v1/profile/me/` para visualização dos dados do próprio usuário.
4. [x] Endpoint `/api/v1/profile/me/` para atualização (PATCH) dos dados do próprio usuário.
5. [x] Acesso restrito a usuários autenticados garantido via `IsAuthenticated`.
6. [x] Mensagens de erro e interface seguindo padrão `pt-br`.

**Análise Técnica:**
- Implementação limpa utilizando `TimeStampedModel` para reutilização de campos de data.
- Signal corretamente configurado no `apps.py` (método `ready`).
- Serializer expõe apenas os campos necessários, mantendo o e-mail como `read_only`.
- Testes automatizados cobrem criação automática, CRUD e segurança.

**Evidências:**
- Execução de `python manage.py test profiles`: 4 testes passaram com sucesso.
- Inspeção de código confirma o uso de `related_name='profile'` e `OneToOneField`.

— Quinn, guardião da qualidade 🛡️