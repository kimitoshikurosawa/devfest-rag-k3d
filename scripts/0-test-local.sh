#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Local Test"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Ollama
echo -e "${YELLOW}Checking Ollama...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}✗ Ollama is not running!${NC}"
    echo ""
    echo "Please start Ollama:"
    echo "  ollama serve"
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Ollama is running${NC}"
echo ""

# Check if Gemma is available
echo -e "${YELLOW}Checking Gemma model...${NC}"
if ! ollama list | grep -q "gemma2:2b"; then
    echo -e "${YELLOW}! Gemma 2B not found, pulling...${NC}"
    ollama pull gemma2:2b
fi
echo -e "${GREEN}✓ Gemma 2B available${NC}"
echo ""

# Prepare data if not done
echo -e "${YELLOW}Checking vector store...${NC}"
if [ ! -d "./chroma_db" ] || [ -z "$(ls -A ./chroma_db 2>/dev/null)" ]; then
    echo "Vector store empty, preparing data..."
    ./scripts/2-prepare-data.sh
else
    echo -e "${GREEN}✓ Vector store ready${NC}"
fi
echo ""

# Launch Streamlit
echo "=================================================="
echo -e "${GREEN}Launching Streamlit App...${NC}"
echo "=================================================="
echo ""
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")/.."
streamlit run src/coordinator/app.py
