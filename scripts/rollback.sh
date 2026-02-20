#!/bin/bash

# Script de Rollback Automatizado
# Uso: ./rollback.sh [versão-anterior|previous]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
TARGET_VERSION=${1:-previous}
PROJECT_NAME="backend-mobile-app"
REMOTE_USER="${DEPLOY_USERNAME:-deploy}"
REMOTE_HOST="${DEPLOY_HOST:-localhost}"
REMOTE_PATH="/opt/${PROJECT_NAME}"
REGISTRY="ghcr.io"
IMAGE_NAME="${REGISTRY}/lais-moveis/project"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Script de Rollback${NC}"
echo -e "${YELLOW}========================================${NC}"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" >&2
    exit 1
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar versão alvo
get_target_version() {
    if [ "$TARGET_VERSION" == "previous" ]; then
        log "Buscando versão anterior..."
        
        # Listar tags disponíveis
        AVAILABLE_TAGS=$(ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker images --format '{{.Tag}}' ${IMAGE_NAME} | grep -v latest" | head -n 1)
        
        if [ -z "$AVAILABLE_TAGS" ]; then
            error "Nenhuma versão anterior encontrada"
        fi
        
        TARGET_VERSION=$AVAILABLE_TAGS
        info "Versão anterior identificada: ${TARGET_VERSION}"
    else
        info "Versão alvo: ${TARGET_VERSION}"
    fi
}

# Verificar se imagem existe localmente
check_image_exists() {
    log "Verificando se imagem existe no registry..."
    
    EXISTS=$(ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker images --format '{{.Repository}}:{{.Tag}}' ${IMAGE_NAME} | grep ${TARGET_VERSION}" || true)
    
    if [ -n "$EXISTS" ]; then
        info "Imagem já existe localmente"
    else
        log "Pull da imagem ${TARGET_VERSION}..."
        ssh "${REMOTE_USER}@${REMOTE_HOST}" "docker pull ${IMAGE_NAME}:${TARGET_VERSION}"
    fi
}

# Backup do estado atual
backup_current() {
    log "Criando backup do estado atual..."
    
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        CURRENT_VERSION=\$(docker compose ps --format json | jq -r '.[0].Image' | cut -d':' -f2)
        echo "Backup da versão atual: \${CURRENT_VERSION:-unknown}"
        
        # Salvar informação do backup
        echo "{
            \"timestamp\": \"$(date -Iseconds)\",
            \"version\": \"\${CURRENT_VERSION:-unknown}\",
            \"reason\": \"Rollback para ${TARGET_VERSION}\"
        }" > backup-$(date +%Y%m%d-%H%M%S).json
EOF
}

# Parar containers atuais
stop_containers() {
    log "Parando containers atuais..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker compose -f docker-compose.yml -f docker-compose.prod.yml down
EOF
}

# Iniciar versão anterior
start_previous() {
    log "Iniciando versão ${TARGET_VERSION}..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" << EOF
        cd ${REMOTE_PATH}
        docker tag ${IMAGE_NAME}:${TARGET_VERSION} ${IMAGE_NAME}:latest
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

# Main
main() {
    echo -e "${RED}ATENÇÃO: Este script irá fazer rollback para a versão ${TARGET_VERSION}${NC}"
    read -p "Deseja continuar? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        log "Rollback cancelado"
        exit 0
    fi
    
    get_target_version
    check_image_exists
    backup_current
    stop_containers
    start_previous
    wait_healthy
    run_health_check
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Rollback realizado com sucesso!${NC}"
    echo -e "${GREEN}Versão atual: ${TARGET_VERSION}${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main
