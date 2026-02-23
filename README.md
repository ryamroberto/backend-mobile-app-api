# Backend Mobile App API

API RESTful desenvolvida em Django e Django Rest Framework para servir como backend de um aplicativo mobile.

## 🚀 Visão Geral

Este projeto fornece uma API segura, escalável e performática para comunicação com aplicativos móveis, implementando:

- **Autenticação JWT** com refresh de tokens
- **Gestão de perfis** de usuário
- **CRUD de recursos** com permissões granulares
- **Sistema de suporte** com automação por IA
- **Monitoramento e observabilidade** com Sentry e logs estruturados

## 📋 Índice

- [Tecnologias](#tecnologias)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [API Endpoints](#api-endpoints)
- [CI/CD](#cicd)
- [Deploy](#deploy)
- [Testes](#testes)
- [Documentação](#documentação)

## 🛠 Tecnologias

| Tecnologia | Versão | Descrição |
|------------|--------|-----------|
| Python | 3.10+ | Linguagem principal |
| Django | 6.x | Framework web |
| Django Rest Framework | 3.16.x | Toolkit para APIs |
| PostgreSQL | 15 | Banco de dados (produção) |
| SQLite | - | Banco de dados (desenvolvimento) |
| Docker | 20+ | Containerização |
| GitHub Actions | - | CI/CD |

## 📦 Requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Docker e Docker Compose (para ambiente containerizado)
- Git (controle de versão)

## 🔧 Instalação

### Desenvolvimento Local

```bash
# Clonar repositório
git clone <repository-url>
cd project

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de ambiente
cp .env.example .env

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Docker (Recomendado)

```bash
# Build e execução
docker compose up --build

# Ou apenas execução (se já tiver build)
docker compose up
```

## ⚙️ Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste as variáveis:

```bash
# Django
SECRET_KEY=sua-secret-key-segura
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados
DB_TYPE=postgres  # ou 'sqlite'
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=sua-senha
DB_HOST=db
DB_PORT=5432

# Sentry (Opcional)
SENTRY_DSN=
SENTRY_ENVIRONMENT=development

# Storage (Opcional - AWS S3)
AWS_STORAGE_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_REGION_NAME=us-east-1
```

## 🏃 Execução

### Desenvolvimento

```bash
python manage.py runserver
```

### Produção (Docker)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🌐 API Endpoints

### Autenticação

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| POST | `/api/v1/auth/register/` | Criar conta | Público |
| POST | `/api/v1/auth/login/` | Obter tokens JWT | Público |
| POST | `/api/v1/auth/refresh/` | Renovar token | Público |
| POST | `/api/v1/auth/logout/` | Invalidar token | Autenticado |

### Perfil

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/api/v1/profile/me/` | Ver perfil | Autenticado |
| PATCH | `/api/v1/profile/me/` | Atualizar perfil | Autenticado |

### Recursos (AppData)

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/api/v1/app/resources/` | Listar recursos | Autenticado |
| POST | `/api/v1/app/resources/` | Criar recurso | Autenticado |
| GET | `/api/v1/app/resources/{id}/` | Detalhes | Autenticado |
| PUT | `/api/v1/app/resources/{id}/` | Atualizar | Dono |
| DELETE | `/api/v1/app/resources/{id}/` | Remover | Dono |

### Suporte

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/api/v1/support/cases/` | Listar casos | Autenticado |
| POST | `/api/v1/support/cases/` | Criar caso | Autenticado |
| GET | `/api/v1/support/cases/{id}/` | Detalhes | Autenticado |

### Health Check

| Método | Endpoint | Descrição | Permissão |
|--------|----------|-----------|-----------|
| GET | `/health/` | Status da aplicação | Público |
| GET | `/ready/` | Pronto para tráfego | Público |

### Documentação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/swagger/` | Swagger UI |
| GET | `/redoc/` | ReDoc UI |
| GET | `/swagger.json` | OpenAPI Schema |

## 🔄 CI/CD

### Fluxo de Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Push/PR   │ ──→ │  CI Build   │ ──→ │   Tests     │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Production │ ←── │   Staging   │ ←── │  Docker     │
│   Deploy    │     │   Deploy    │     │   Publish   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Workflows GitHub Actions

| Workflow | Arquivo | Gatilho | Descrição |
|----------|---------|---------|-----------|
| CI | `.github/workflows/ci.yml` | Push/PR | Lint, testes, build |
| Docker Publish | `.github/workflows/docker-publish.yml` | Push tag/master | Build e push Docker |
| CD Deploy | `.github/workflows/deploy.yml` | Push master | Deploy staging/prod |

### Secrets Necessários

Configure no GitHub Settings → Secrets and variables → Actions:

| Secret | Descrição | Obrigatório |
|--------|-----------|-------------|
| `GHCR_TOKEN` | Token para GitHub Container Registry | Sim (CD) |
| `DEPLOY_SSH_KEY` | Chave SSH para servidor | Sim (CD) |
| `DEPLOY_HOST` | Host do servidor de produção | Sim (CD) |
| `DEPLOY_USERNAME` | Username do servidor | Sim (CD) |
| `SECRET_KEY` | Django secret key | Sim |
| `DB_PASSWORD` | Senha do banco de dados | Sim |

### Comandos de Versionamento

```bash
# Tornar scripts executáveis
chmod +x scripts/*.sh

# Versionar (major|minor|patch|prerelease)
./scripts/version.sh patch

# Fazer deploy
./scripts/deploy.sh staging
./scripts/deploy.sh production

# Rollback
./scripts/rollback.sh previous
./scripts/rollback.sh v1.2.3
```

## 🚀 Deploy

### Pré-requisitos

1. Servidor com Docker e Docker Compose instalados
2. SSH configurado com chave pública
3. Secrets do GitHub configurados

### Estrutura do Servidor

```bash
/opt/backend-mobile-app/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env
└── nginx/
    ├── nginx.conf
    └── ssl/
```

### Deploy Manual

```bash
# No servidor
cd /opt/backend-mobile-app
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Rollback

```bash
# Listar versões disponíveis
docker images ghcr.io/lais-moveis/project

# Rollback para versão específica
docker tag ghcr.io/lais-moveis/project:v1.2.3 ghcr.io/lais-moveis/project:latest
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🧪 Testes

```bash
# Testes unitários
python manage.py test

# Com coverage
coverage run manage.py test
coverage report

# Linting
python -m ruff check .

# Type checking
python -m py_compile $(git ls-files '*.py')
```

## 📚 Documentação

A documentação da API está disponível em:

- **Swagger UI**: `http://localhost:8000/swagger/`
- **ReDoc**: `http://localhost:8000/redoc/`
- **OpenAPI JSON**: `http://localhost:8000/swagger.json`

## 📁 Estrutura do Projeto

```
project/
├── core/                 # Configurações globais
│   ├── settings.py
│   ├── urls.py
│   └── views.py         # Health checks
├── authentication/       # Autenticação e JWT
├── users/               # Modelo de usuário
├── profiles/            # Perfis de usuário
├── appdata/             # Recursos do app
├── support/             # Sistema de suporte
├── common/              # Utilitários compartilhados
├── scripts/             # Scripts de deploy
│   ├── deploy.sh
│   ├── rollback.sh
│   └── version.sh
├── .github/workflows/   # CI/CD
│   ├── ci.yml
│   ├── cd.yml
│   └── docker-publish.yml
└── docs/                # Documentação
    ├── stories/         # Histórias de usuário
    └── PRD.md           # Product Requirements
```



