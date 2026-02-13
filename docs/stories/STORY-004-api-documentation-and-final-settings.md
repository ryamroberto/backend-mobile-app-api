# Story 1.4: Documentação da API (Swagger/OpenAPI) e Ajustes Globais

**Status**: Completed

## Story
**As a** Desenvolvedor de Frontend/Mobile,
**I want** acessar uma documentação interativa da API,
**so that** eu possa entender os endpoints, formatos de dados e requisitos de autenticação sem precisar ler o código-fonte.

## Acceptance Criteria
1. Documentação Swagger/OpenAPI configurada utilizando `drf-yasg`. [x]
2. A documentação deve estar acessível via `/swagger/` e `/redoc/`. [x]
3. Todos os endpoints criados (Auth, Profile, AppData) devem estar listados na documentação. [x]
4. Esquemas de segurança (JWT Bearer Token) devem estar configurados na interface do Swagger para permitir testes. [x]
5. Configuração de CORS implementada para permitir requisições do aplicativo mobile (usando `django-cors-headers`). [x]
6. REGRA OBRIGATORIO: qualquer texto exibido ao usuario deve estar em portugues (pt-br) se houver ingles, considere um erro. [x]

## 🤖 CodeRabbit Integration
> **CodeRabbit Integration**: Disabled
>
> CodeRabbit CLI is not enabled in `core-config.yaml`.
> Quality validation will use manual review process only.

### Story Type Analysis
**Primary Type**: API
**Secondary Type(s)**: Security, Deployment
**Complexity**: Low

### Specialized Agent Assignment
**Primary Agents**:
- @dev
- @architect

**Supporting Agents**:
- @qa

### Quality Gate Tasks
- [x] Pre-Commit (@dev): Run before marking story complete

## Tasks / Subtasks
- [x] **Configuração da Documentação**
    - [x] Instalar e configurar `drf-yasg`.
    - [x] Adicionar `get_schema_view` em `core/urls.py`.
    - [x] Configurar metadados da API (Título, Versão, Descrição).
- [x] **Configuração de CORS**
    - [x] Instalar `django-cors-headers`.
    - [x] Adicionar ao `INSTALLED_APPS` e `MIDDLEWARE`.
    - [x] Configurar `CORS_ALLOW_ALL_ORIGINS = True` (para dev).
- [x] **Segurança na Documentação**
    - [x] Garantir que o Swagger suporte o campo "Authorize" para incluir o token JWT.
- [x] **Verificação**
    - [x] Acessar `/swagger/` no navegador e testar um endpoint autenticado.

## Dev Notes
- A documentação automática facilita muito o handoff para o time mobile.
- Corrigido erro de geração de esquema no Swagger para views que filtram por usuário autenticado.
- Configurações de CORS habilitadas para facilitar testes com o frontend.

### Testing
- Validar se a rota `/swagger/` retorna status 200. [x]
- Validar se a definição `swagger.json` é gerada sem erros. [x]

## Change Log
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 09/02/2026 | 1.0 | Criação da história de Documentação e CORS | River (SM) |
| 09/02/2026 | 1.1 | Implementação de Swagger, ReDoc e CORS | Dex (Dev) |

## Dev Agent Record
### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Testes de documentação passaram com sucesso (3 testes).
- `drf-yasg` e `django-cors-headers` instalados.

### Completion Notes List
- Swagger UI disponível em `/swagger/`.
- ReDoc disponível em `/redoc/`.
- CORS configurado para permitir todas as origens em desenvolvimento.
- Adicionado suporte a Bearer Token no Swagger.

### File List
- core/settings.py (modificado)
- core/urls.py (modificado)
- appdata/views.py (modificado)
- profiles/views.py (modificado)
- common/tests.py (criado)

## QA Results
### QA Decision: PASS ✅

**Validação de Critérios de Aceite:**
1. [x] Documentação Swagger/OpenAPI configurada com `drf-yasg`.
2. [x] Acessível via `/swagger/` e `/redoc/`.
3. [x] Todos os endpoints (Auth, Profile, AppData) listados corretamente.
4. [x] Suporte a Bearer Token (JWT) configurado na interface do Swagger.
5. [x] CORS configurado e ativo via `django-cors-headers`.
6. [x] Regra de idioma `pt-br` respeitada nas metatags da documentação.

**Análise Técnica:**
- Integração limpa do `drf-yasg`.
- Tratamento proativo de `swagger_fake_view` nas views para evitar erros de geração de esquema em tempo de documentação.
- Configuração de CORS adequada para o ambiente de desenvolvimento.
- Suíte de testes expandida para garantir a disponibilidade das rotas de documentação.

**Evidências:**
- Execução de `python manage.py test`: 17 testes passaram (incluindo testes de auth, perfil, appdata e documentação).
- Inspeção visual das configurações em `core/settings.py` e `core/urls.py`.

— Quinn, guardião da qualidade 🛡️