#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Data Preparation"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Preparing vector store data...${NC}"
echo ""

# Create Python script to load data
python3 << 'EOF'
import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from vectorstore import ChromaManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChromaDB
chroma_manager = ChromaManager()

# Data directories
data_dir = project_root / "data"

# Load DevFest data
logger.info("Loading DevFest data...")
devfest_count = chroma_manager.load_json_data(
    collection_name="devfest_docs",
    data_dir=str(data_dir / "devfest")
)
logger.info(f"✓ DevFest: {devfest_count} documents loaded")

# Load Kimana data
logger.info("Loading Kimana data...")
kimana_count = chroma_manager.load_json_data(
    collection_name="kimana_docs",
    data_dir=str(data_dir / "kimana")
)
logger.info(f"✓ Kimana: {kimana_count} documents loaded")

# Verify
devfest_stats = chroma_manager.get_stats("devfest_docs")
kimana_stats = chroma_manager.get_stats("kimana_docs")

print("\n" + "="*50)
print("Data Preparation Complete!")
print("="*50)
print(f"DevFest Collection: {devfest_stats['count']} documents")
print(f"Kimana Collection: {kimana_stats['count']} documents")
print("="*50)

EOF

echo ""
echo -e "${GREEN}✓ Data preparation complete!${NC}"
echo ""
echo "Next step: ./scripts/3-build-deploy.sh"
echo ""
