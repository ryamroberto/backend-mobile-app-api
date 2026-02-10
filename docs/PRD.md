# Product Requirement Document (PRD) - Backend Mobile App API

**Autor:** Atlas (Analyst Agent)
**Data:** 09/02/2026
**Status:** Rascunho Inicial
**Versão:** 1.0

---

## 1. Visão Geral
Desenvolvimento de um backend robusto, seguro e escalável utilizando **Django** e **Django Rest Framework (DRF)** para servir como API REST de um aplicativo mobile existente. O sistema deve priorizar a separação de responsabilidades, segurança e extensibilidade.

## 2. Objetivos
- Fornecer uma interface de comunicação (API) segura e performática para o app mobile.
- Garantir a integridade e consistência dos dados.
- Estabelecer uma arquitetura modular que facilite a manutenção e evolução futura.
- Implementar documentação automática para facilitar o consumo pelo time de frontend.

## 3. Arquitetura do Sistema

### 3.1. Tecnologias Principais
- **Linguagem:** Python 3.10+
- **Framework Web:** Django 5.x / 6.x
- **API Toolkit:** Django Rest Framework (DRF)
- **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Recomendado para Produção)
- **Autenticação:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Documentação:** Swagger/OpenAPI (via `drf-yasg` ou `drf-spectacular`)

### 3.2. Estrutura de Módulos (Apps)
A arquitetura seguirá o padrão modular do Django, onde cada domínio de responsabilidade reside em seu próprio "app". Baseado na estrutura de pastas existente:

1.  **`core`**: Configurações globais do projeto (`settings.py`, `urls.py` principal, `wsgi.py`).
2.  **`common`**: Utilitários, *mixins*, classes base abstratas e funções compartilhadas por todo o projeto (ex: modelos de `TimeStampedModel`).
3.  **`authentication`**: Lógica de login, registro, recuperação de senha e gestão de tokens JWT.
4.  **`users`**: Gerenciamento do modelo de usuário customizado (Custom User Model), focando em credenciais e acesso.
5.  **`profiles`**: Dados públicos e extendidos do usuário (foto, bio, preferências), separando a "conta" do "perfil social/funcional".
6.  **`appdata`**: Domínio principal de negócio do aplicativo (exemplo genérico para CRUD de recursos do app).

### 3.3. Padrões de Projeto
- **Service Layer (Opcional/Futuro):** Para regras de negócio complexas, separar a lógica das *Views* e *Models*.
- **Selectors:** Funções dedicadas para queries complexas (leitura).
- **Model Managers:** Encapsulamento de queries comuns no nível do modelo.

## 4. Requisitos Funcionais

### 4.1. Autenticação & Segurança (`authentication`, `users`)
- **Registro de Usuário:** Endpoint para criação de nova conta (email, senha, confirmação).
- **Login:** Autenticação via Email/Senha retornando par de tokens (Access e Refresh JWT).
- **Refresh Token:** Endpoint para renovar o Access Token expirado.
- **Logout:** Blacklist do Refresh Token (se aplicável na configuração de segurança).
- **Segurança:** Senhas devem ser armazenadas com hash (padrão Django PBKDF2).

### 4.2. Gestão de Perfil (`profiles`)
- **Criação Automática:** Um perfil deve ser criado automaticamente (via *Signals*) quando um usuário se registra.
- **Visualização:** Usuário pode ver seu próprio perfil e (opcionalmente) de outros.
- **Edição:** Usuário pode atualizar seus dados de perfil (nome, bio, avatar).

### 4.3. Funcionalidades do App (`appdata`)
*Nota: Como o domínio específico não foi informado, define-se um CRUD genérico para "Items" ou "Resources" como prova de conceito da arquitetura.*
- **Listagem:** Listar itens com paginação e filtros básicos.
- **Detalhes:** Visualizar detalhes de um item específico.
- **Criação/Edição/Remoção:** Operações protegidas (apenas usuários autenticados ou donos do recurso).

## 5. Modelo de Dados (Schema Proposto)

### `users.User` (AbstractBaseUser)
- `email` (EmailField, Unique, PK/UsernameField)
- `is_active` (Boolean)
- `is_staff` (Boolean)
- `date_joined` (DateTime)

### `profiles.Profile`
- `user` (OneToOne -> users.User)
- `full_name` (Char)
- `bio` (Text, Nullable)
- `avatar` (ImageField, Nullable)
- `created_at` (DateTime - via `common`)
- `updated_at` (DateTime - via `common`)

### `appdata.Resource` (Entidade Genérica)
- `owner` (ForeignKey -> users.User)
- `title` (Char)
- `description` (Text)
- `status` (ChoiceField: Active, Archived, etc.)
- `metadata` (JSONField - para flexibilidade futura)

## 6. API Endpoints (Esboço)

| Método | Endpoint | Descrição | Permissão |
| :--- | :--- | :--- | :--- |
| POST | `/api/v1/auth/register/` | Criar nova conta | Público |
| POST | `/api/v1/auth/login/` | Obter Token JWT | Público |
| POST | `/api/v1/auth/refresh/` | Renovar Token | Público |
| GET | `/api/v1/profile/me/` | Ver perfil logado | Autenticado |
| PATCH | `/api/v1/profile/me/` | Atualizar perfil | Autenticado |
| GET | `/api/v1/app/resources/` | Listar recursos | Autenticado |
| POST | `/api/v1/app/resources/` | Criar recurso | Autenticado |

## 7. Requisitos Não-Funcionais
- **Performance:** Respostas da API devem visar latência < 200ms para leituras simples.
- **Escalabilidade:** O código deve ser *stateless* (sessão via Token) para permitir escalabilidade horizontal.
- **Segurança:** CORS configurado restritivamente; `DEBUG=False` em produção; Validação estrita de inputs via Serializers.
- **Testes:** Cobertura de testes unitários/integração para fluxos críticos (Auth, CRUD principal) usando `pytest` ou `django.test`.

## 8. Definição de Pronto (DoD)
- [ ] Modelos criados e migrações aplicadas.
- [ ] Endpoints de autenticação funcionais (Login/Register/Refresh).
- [ ] CRUD de Perfil funcional.
- [ ] CRUD de AppData funcional.
- [ ] Testes básicos rodando e passando (`python manage.py test`).
- [ ] Swagger/Redoc acessível em `/swagger/`.
- [ ] Código lintado e seguindo PEP8.
