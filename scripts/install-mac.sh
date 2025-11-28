#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Installation pour Mac"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Detect Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo -e "${YELLOW}Python version détectée: $PYTHON_VERSION${NC}"
echo ""

# Check architecture
ARCH=$(uname -m)
echo -e "${YELLOW}Architecture: $ARCH${NC}"
echo ""

echo -e "${YELLOW}Installation des dépendances...${NC}"
echo ""

# Option 1: Minimal (recommandé pour démarrage rapide)
echo "Choisissez le mode d'installation:"
echo "1) Minimal (rapide, sans ChromaDB)"
echo "2) Complet (avec ChromaDB, plus long)"
read -p "Votre choix [1/2]: " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo -e "${YELLOW}Installation minimale...${NC}"
    
    # Upgrade pip
    pip3 install --upgrade pip setuptools wheel
    
    # Install minimal requirements
    pip3 install -r requirements-minimal.txt
    
    # Use simple vector store
    echo ""
    echo -e "${GREEN}✓ Installation minimale terminée${NC}"
    echo ""
    echo "Note: Utilise SimpleVectorStore (recherche par mots-clés)"
    echo ""
else
    echo ""
    echo -e "${YELLOW}Installation complète...${NC}"
    
    # Upgrade pip
    pip3 install --upgrade pip setuptools wheel
    
    # Try full installation
    if pip3 install -r requirements.txt; then
        echo -e "${GREEN}✓ Installation complète réussie${NC}"
    else
        echo -e "${RED}! Erreur avec installation complète${NC}"
        echo ""
        echo "Tentative avec versions alternatives..."
        
        # Install packages individually
        pip3 install streamlit
        pip3 install ollama
        pip3 install requests
        pip3 install python-dotenv
        pip3 install pydantic
        
        # Try chromadb alternatives
        if pip3 install chromadb; then
            echo -e "${GREEN}✓ ChromaDB installé${NC}"
        elif pip3 install chromadb-client; then
            echo -e "${GREEN}✓ ChromaDB client installé${NC}"
        else
            echo -e "${YELLOW}! ChromaDB non disponible, utilisation de SimpleVectorStore${NC}"
        fi
        
        # LangChain
        pip3 install langchain langchain-community || echo "LangChain optionnel non installé"
    fi
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Installation terminée !${NC}"
echo "=================================================="
echo ""
echo "Prochaines étapes:"
echo "  1. cp .env.example .env"
echo "  2. ollama serve (dans un autre terminal)"
echo "  3. ./scripts/0-test-local.sh"
echo ""
