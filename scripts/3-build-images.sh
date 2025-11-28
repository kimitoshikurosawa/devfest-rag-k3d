#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Build Docker Images"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

REGISTRY="localhost:5555"
VERSION="latest"

echo -e "${YELLOW}Step 1: Building coordinator image...${NC}"
docker build \
  -f docker/coordinator.Dockerfile \
  -t ${REGISTRY}/devfest-coordinator:${VERSION} \
  .
echo -e "${GREEN}✓ Coordinator image built${NC}"
echo ""

echo -e "${YELLOW}Step 2: Pushing images to K3D registry...${NC}"
docker push ${REGISTRY}/devfest-coordinator:${VERSION}
echo -e "${GREEN}✓ Images pushed to registry${NC}"
echo ""

echo "=================================================="
echo -e "${GREEN}✓ Docker Build Complete!${NC}"
echo "=================================================="
echo ""
echo "Images built and pushed:"
echo "  - ${REGISTRY}/devfest-coordinator:${VERSION}"
echo ""
echo "Next step: ./scripts/4-deploy-k3d.sh"
echo ""
