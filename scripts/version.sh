#!/bin/bash

# Script de Versionamento Semântico
# Uso: ./version.sh [major|minor|patch|prerelease]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arquivo de versão
VERSION_FILE="VERSION"
CURRENT_VERSION=$(cat $VERSION_FILE 2>/dev/null || echo "0.0.0")

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Versionamento Semântico${NC}"
echo -e "${YELLOW}========================================${NC}"

# Parse da versão atual
parse_version() {
    MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
    MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
    PATCH=$(echo $CURRENT_VERSION | cut -d. -f3 | cut -d- -f1)
    PRERELEASE=$(echo $CURRENT_VERSION | cut -d- -f2)
    
    # Remover prefixo 'v' se existir
    MAJOR=$(echo $MAJOR | sed 's/^v//')
}

# Calcular nova versão
calculate_new_version() {
    case $1 in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            PRERELEASE=""
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            PRERELEASE=""
            ;;
        patch)
            PATCH=$((PATCH + 1))
            PRERELEASE=""
            ;;
        prerelease)
            if [ -z "$PRERELEASE" ]; then
                PRERELEASE="rc.1"
            else
                NUM=$(echo $PRERELEASE | cut -d. -f2)
                NUM=$((NUM + 1))
                PRERELEASE="rc.$NUM"
            fi
            ;;
        *)
            echo "Uso: $0 [major|minor|patch|prerelease]"
            exit 1
            ;;
    esac
}

# Format nova versão
format_version() {
    if [ -n "$PRERELEASE" ]; then
        echo "${MAJOR}.${MINOR}.${PATCH}-${PRERELEASE}"
    else
        echo "${MAJOR}.${MINOR}.${PATCH}"
    fi
}

# Atualizar arquivo de versão
update_version_file() {
    local NEW_VERSION=$1
    echo $NEW_VERSION > $VERSION_FILE
    echo -e "${GREEN}Versão atualizada: ${CURRENT_VERSION} → ${NEW_VERSION}${NC}"
}

# Atualizar settings.py
update_settings() {
    local NEW_VERSION=$1
    
    if [ -f "core/settings.py" ]; then
        # Adicionar ou atualizar APP_VERSION
        if grep -q "APP_VERSION" core/settings.py; then
            sed -i "s/APP_VERSION = .*/APP_VERSION = '${NEW_VERSION}'/" core/settings.py
        else
            echo "" >> core/settings.py
            echo "# Versão da aplicação" >> core/settings.py
            echo "APP_VERSION = '${NEW_VERSION}'" >> core/settings.py
        fi
        echo -e "${GREEN}core/settings.py atualizado${NC}"
    fi
}

# Criar tag git
create_git_tag() {
    local NEW_VERSION=$1
    
    echo -e "${YELLOW}Criando tag git v${NEW_VERSION}...${NC}"
    
    if git rev-parse "v${NEW_VERSION}" >/dev/null 2>&1; then
        echo -e "${RED}Tag v${NEW_VERSION} já existe!${NC}"
        read -p "Deseja sobrescrever? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
            exit 1
        fi
        git tag -d "v${NEW_VERSION}"
    fi
    
    git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
    echo -e "${GREEN}Tag v${NEW_VERSION} criada${NC}"
}

# Main
main() {
    parse_version
    
    echo -e "Versão atual: ${BLUE}${CURRENT_VERSION}${NC}"
    echo -e "Tipo de bump: ${YELLOW}${1:-patch}${NC}"
    
    calculate_new_version ${1:-patch}
    NEW_VERSION=$(format_version)
    
    echo -e "Nova versão: ${GREEN}${NEW_VERSION}${NC}"
    echo ""
    
    read -p "Deseja continuar? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo -e "${YELLOW}Versionamento cancelado${NC}"
        exit 0
    fi
    
    update_version_file $NEW_VERSION
    update_settings $NEW_VERSION
    
    echo ""
    read -p "Deseja criar tag git? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        create_git_tag $NEW_VERSION
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Próximos passos:${NC}"
        echo -e "${GREEN}  git push origin v${NEW_VERSION}${NC}"
        echo -e "${GREEN}========================================${NC}"
    fi
}

main "$@"
