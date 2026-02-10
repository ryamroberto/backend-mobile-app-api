# Arquitetura do Sistema - Backend Mobile App API

**Data:** 09/02/2026
**Autor:** Aria (Architect Agent)
**Versão:** 1.0
**Baseado em:** docs/PRD.md

---

## 1. Visão Geral
Esta arquitetura define a estrutura de um backend monolítico modular desenvolvido em **Django** e **Django Rest Framework (DRF)**. O sistema serve como a API central para um aplicativo mobile, focando em segurança (JWT), escalabilidade e separação clara de domínios através de "apps" Django.

## 2. Princípios de Design
- **DRY (Don't Repeat Yourself):** Reutilização de código através do app `common` (mixins, utilitários).
- **Separação de Preocupações:** Cada app tem responsabilidade única (Autenticação, Usuários, Perfis, Dados do App).
- **Stateless:** API RESTful pura, utilizando JWT para autenticação, permitindo escalabilidade horizontal.
- **Segurança em Camadas:** Validação forte em Serializers, permissões em Views e autenticação em nível de middleware.

## 3. Stack Tecnológico

| Camada | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | Tipagem estática (Type Hints) recomendada. |
| **Framework** | Django 5.x / 6.x | Framework web de alto nível ("baterias inclusas"). |
| **API** | Django Rest Framework (DRF) | Toolkit para construção de APIs Web. |
| **Auth** | SimpleJWT | Autenticação via JSON Web Token (Access/Refresh). |
| **DB (Dev)** | SQLite | Banco leve para desenvolvimento local. |
| **DB (Prod)** | PostgreSQL | Banco relacional robusto para produção. |
| **Docs** | drf-yasg / drf-spectacular | Documentação automática (Swagger/OpenAPI). |
| **Testes** | Pytest / Django Test | Testes unitários e de integração. |

## 4. Estrutura do Projeto e Módulos

A estrutura de diretórios reflete a separação de domínios. A raiz do projeto contém o `manage.py` e a pasta de configuração `core`.

```text
/
├── core/                   # Configurações globais (settings, urls, wsgi)
├── common/                 # Utilitários compartilhados e modelos abstratos
│   ├── models.py           # Ex: TimeStampedModel
│   └── permissions.py      # Permissões customizadas globais
├── users/                  # Custom User Model (Autenticação e Credenciais)
│   ├── models.py           # User (AbstractBaseUser)
│   └── managers.py         # CustomUserManager
├── profiles/               # Dados extendidos do usuário (Social)
│   ├── models.py           # Profile (OneToOne com User)
│   └── signals.py          # Auto-create profile on user creation
├── authentication/         # Lógica de Auth (Login, Register, Reset)
│   ├── views.py            # Endpoints de JWT
│   └── serializers.py      # Validação de credenciais
├── appdata/                # Domínio principal do negócio (Recursos do App)
│   ├── models.py           # Modelos de negócio
│   └── views.py            # ViewSets para CRUD
├── docs/                   # Documentação (PRD, Arquitetura)
└── manage.py               # Entrypoint do Django
```

## 5. Modelagem de Dados (ERD Textual)

### 5.1. Users & Authentication
*   **User (users.models)**
    *   `id`: UUID (Primary Key)
    *   `email`: EmailField (Unique, Username)
    *   `password`: CharField (Hashed)
    *   `is_active`: Boolean
    *   `is_staff`: Boolean
    *   `date_joined`: DateTime

### 5.2. Profiles
*   **Profile (profiles.models)**
    *   `id`: UUID
    *   `user_id`: ForeignKey (OneToOne) -> User
    *   `full_name`: CharField
    *   `bio`: TextField
    *   `avatar`: ImageField
    *   *Herda de TimeStampedModel (created_at, updated_at)*

### 5.3. App Business Logic
*   **Resource (appdata.models)**
    *   `id`: UUID
    *   `owner_id`: ForeignKey -> User
    *   `title`: CharField
    *   `description`: TextField
    *   `status`: CharField (Enum: ACTIVE, ARCHIVED)
    *   `metadata`: JSONField
    *   *Herda de TimeStampedModel*

## 6. Fluxos de Dados e Padrões de API

### 6.1. Autenticação (JWT Flow)
1.  **Login:** Client envia `email` + `password` para `/api/auth/login/`.
2.  **Token:** Server valida e retorna `access_token` (curta duração) e `refresh_token` (longa duração).
3.  **Request:** Client envia `Authorization: Bearer <access_token>` em requests subsequentes.
4.  **Refresh:** Quando `access_token` expira (401), Client envia `refresh_token` para `/api/auth/refresh/` para obter novo par.

### 6.2. Padrão de ViewSets e Serializers
*   **ModelViewSet:** Utilizado para CRUD padrão (Create, Retrieve, Update, Delete, List).
*   **Serializers:**
    *   Responsáveis por validação de entrada (Input) e formatação de saída (Output).
    *   Uso de `ModelSerializer` para mapeamento direto.
    *   Uso de `NestedSerializers` com cuidado para performance (preferir links ou IDs para relações profundas).

## 7. Segurança

*   **Autenticação:** Obrigatória para todos os endpoints exceto `/auth/` e documentação.
*   **Permissões:**
    *   `IsAuthenticated`: Padrão global.
    *   `IsOwnerOrReadOnly`: Custom permission para garantir que usuários só editem seus próprios dados (`appdata` e `profiles`).
*   **Throttling:** Limitação de taxa de requisições (AnonRateThrottle, UserRateThrottle) para prevenir abuso.
*   **CORS:** Configurado para permitir apenas origens confiáveis (ex: domínio do app mobile, localhost em dev).

## 8. Considerações de Infraestrutura

*   **Gerenciamento de Dependências:** `pip` com `requirements.txt` ou `poetry`.
*   **Variáveis de Ambiente:** `.env` (python-dotenv) para segredos (SECRET_KEY, DB_URL). **NUNCA comitar .env**.
*   **Static Files:** `Whitenoise` para servir arquivos estáticos em produção se não houver CDN.
*   **Media Files:** Armazenamento em S3/Cloud Storage recomendado para produção (AWS/GCP/Azure).

## 9. Próximos Passos (Roadmap Técnico)

1.  **Setup Inicial:** Configurar projeto Django e apps.
2.  **Core & Common:** Definir modelos base e configurações.
3.  **Users & Auth:** Implementar Custom User Model e JWT.
4.  **Profiles:** Criar modelo de perfil e signals.
5.  **AppData:** Implementar CRUD de recursos de exemplo.
6.  **Docs:** Configurar Swagger/OpenAPI.
