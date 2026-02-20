# Story 1.1: Configuração do Modelo de Usuário Customizado e Autenticação JWT

**Status**: Completed

## Story
**As a** Desenvolvedor,
**I want** implementar o modelo de usuário customizado e a autenticação JWT,
**so that** o sistema tenha uma base sólida e segura para gerenciar usuários e acessos.

## Acceptance Criteria
1. O modelo `User` deve ser implementado no app `users` usando `AbstractBaseUser`.
2. O campo de login deve ser o `email`.
3. Deve existir um `CustomUserManager` para lidar com a criação de usuários e superusuários.
4. A autenticação JWT deve ser configurada usando `djangorestframework-simplejwt`.
5. Endpoints de Login, Refresh e Register devem estar funcionais em `/api/v1/auth/`.
6. REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro.

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled
>
> CodeRabbit CLI is not enabled in `core-config.yaml`.
> Quality validation will use manual review process only.

### Story Type Analysis
**Primary Type**: Security
**Secondary Type(s)**: API, Database
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
- [x] **Configuração do App `users`**
    - [x] Definir `User` em `users/models.py` (email, is_active, is_staff, date_joined).
    - [x] Criar `CustomUserManager` em `users/managers.py`.
    - [x] Atualizar `AUTH_USER_MODEL` em `core/settings.py`.
- [x] **Configuração de Autenticação (SimpleJWT)**
    - [x] Adicionar `rest_framework_simplejwt` ao `INSTALLED_APPS`.
    - [x] Configurar `REST_FRAMEWORK` em `settings.py` para usar `JWTAuthentication`.
- [x] **Endpoints de Autenticação (`authentication` app)**
    - [x] Implementar Serializer de Registro.
    - [x] Configurar URLs para `token_obtain_pair`, `token_refresh` e `register`.
- [x] **Migrações e Verificação**
    - [x] Gerar e aplicar migrações iniciais.
    - [x] Criar um superusuário para testes.

## Dev Notes
- O projeto já possui a estrutura de pastas: `appdata`, `authentication`, `common`, `core`, `profiles`, `users`.
- Utilizar `uuid` como PK para o modelo User conforme sugerido na arquitetura.
- **Importante**: O app `profiles` deve ter um signal para criar um perfil automaticamente, mas isso pode ser feito na próxima story ou como subtask aqui se sobrar tempo. Focaremos no User primeiro.

### Testing
- Localização: `users/tests.py` e `authentication/tests.py`.
- Framework: Django Test / Pytest.
- Cenários: Registro com sucesso, Login com credenciais válidas/inválidas, Refresh de token.

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 09/02/2026 | 1.0 | Criação da história inicial de Autenticação | River (SM) |
| 09/02/2026 | 1.1 | Implementação concluída e testada | Dex (Dev) |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Testes de autenticação passaram com sucesso.
- Superusuário criado: admin@example.com

### Completion Notes List
- Modelo User customizado com UUID como PK.
- Autenticação JWT configurada com SimpleJWT.
- Endpoint de registro implementado com sucesso.
- Configurações de idioma ajustadas para pt-br.

### File List
- users/models.py
- users/managers.py
- users/tests.py
- core/settings.py
- core/urls.py
- authentication/serializers.py
- authentication/views.py
- authentication/urls.py
- authentication/tests.py

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Modelo `User` com `AbstractBaseUser` no app `users`.
2. [x] Login via `email` configurado.
3. [x] `CustomUserManager` funcional para User e Superuser.
4. [x] SimpleJWT configurado e ativo.
5. [x] Endpoints `/api/v1/auth/` (login, refresh, register) operacionais.
6. [x] Sistema configurado para `pt-br`.

**Análise Técnica:**
- Código segue padrões PEP8 e idiomatismo Django.
- UUID utilizado como PK conforme recomendado.
- Testes automatizados cobrem os fluxos principais de auth.

**Evidências:**
- Execução de `python manage.py test`: 5 testes passaram com sucesso.
- Verificação manual de `core/settings.py` e `users/models.py`.

— Quinn, guardião da qualidade 🛡️