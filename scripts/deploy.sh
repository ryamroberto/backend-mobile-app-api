#!/bin/bash

# Script de Deploy Automatizado
# Uso: ./deploy.sh [staging|production]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
ENVIRONMENT=${1:-staging}
PROJECT_NAME="backend-mobile-app"
REMOTE_USER="${DEPLOY_USERNAME:-deploy}"
REMOTE_HOST="${DEPLOY_HOST:-localhost}"
REMOTE_PATH="/opt/${PROJECT_NAME}"
REGISTRY="ghcr.io"
IMAGE_NAME="${REGISTRY}/lais-moveis/project"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Script de Deploy - ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}========================================${NC}"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" >&2
    exit 1
}

# Verificar se está logado no Docker
check_docker_login() {
    log "Verificando login no Docker Registry..."
    if ! docker info &>/dev/null; then
        error "Docker não está rodando ou usuário não tem permissão"
    fi
}

# Pull da imagem mais recente
pull_image() {
    log "Pull da imagem mais recente..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker login ${REGISTRY} -u ${GITHUB_ACTOR} -p ${GITHUB_TOKEN}
        docker pull ${IMAGE_NAME}:latest
EOF
}

# Parar containers antigos
stop_containers() {
    log "Parando containers existentes..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker compose -f docker-compose.yml -f docker-compose.prod.yml down
EOF
}

# Iniciar novos containers
start_containers() {
    log "Iniciando novos containers..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
EOF
}

# Aguardar aplicação ficar pronta
wait_healthy() {
    log "Aguardando aplicação ficar saudável..."
    MAX_ATTEMPTS=30
    ATTEMPT=1
    
    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
        if ssh "${REMOTE_USER}@${REMOTE_HOST}" "curl -sf http://localhost:8000/health/ > /dev/null 2>&1"; then
            log "Aplicação está saudável!"
            return 0
        fi
        log "Tentativa $ATTEMPT/$MAX_ATTEMPTS - aguardando..."
        sleep 5
        ATTEMPT=$((ATTEMPT + 1))
    done
    
    error "Falha no health check após $MAX_ATTEMPTS tentativas"
}

# Executar health check
run_health_check() {
    log "Executando health check completo..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        curl -sf http://localhost:8000/health/ | python3 -m json.tool
        curl -sf http://localhost:8000/ready/ | python3 -m json.tool
EOF
}

# Limpeza de imagens antigas
cleanup() {
    log "Limpando imagens antigas..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker image prune -af --filter "until=24h"
EOF
}

# Main
main() {
    check_docker_login
    pull_image
    stop_containers
    start_containers
    wait_healthy
    run_health_check
    cleanup
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deploy realizado com sucesso!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main
