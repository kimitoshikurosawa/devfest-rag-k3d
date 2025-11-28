#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG K3D - Cluster Setup"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CLUSTER_NAME="devfest-rag"
REGISTRY_NAME="devfest-registry"
REGISTRY_PORT="5555"

echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"

# Check if k3d is installed
if ! command -v k3d &> /dev/null; then
    echo "Error: k3d is not installed"
    echo "Install with: brew install k3d (macOS) or curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

echo -e "${YELLOW}Step 2: Cleaning up existing cluster (if any)...${NC}"
k3d cluster delete $CLUSTER_NAME 2>/dev/null || true
k3d registry delete $REGISTRY_NAME 2>/dev/null || true
echo -e "${GREEN}✓ Cleanup done${NC}"
echo ""

echo -e "${YELLOW}Step 3: Creating local registry...${NC}"
k3d registry create $REGISTRY_NAME --port $REGISTRY_PORT
echo -e "${GREEN}✓ Registry created at localhost:$REGISTRY_PORT${NC}"
echo ""

echo -e "${YELLOW}Step 4: Creating K3D cluster...${NC}"
k3d cluster create $CLUSTER_NAME \
  --agents 2 \
  --registry-use k3d-$REGISTRY_NAME:$REGISTRY_PORT \
  --port "8501:30850@loadbalancer" \
  --api-port 6550 \
  --k3s-arg "--disable=traefik@server:0"

echo -e "${GREEN}✓ Cluster created${NC}"
echo ""

echo -e "${YELLOW}Step 5: Waiting for cluster to be ready...${NC}"
kubectl wait --for=condition=Ready nodes --all --timeout=120s
echo -e "${GREEN}✓ Cluster ready${NC}"
echo ""

echo -e "${YELLOW}Step 6: Creating namespace...${NC}"
kubectl create namespace devfest --dry-run=client -o yaml | kubectl apply -f -
kubectl config set-context --current --namespace=devfest
echo -e "${GREEN}✓ Namespace 'devfest' created and set as default${NC}"
echo ""

echo -e "${YELLOW}Step 7: Cluster info...${NC}"
echo ""
kubectl cluster-info
echo ""
kubectl get nodes
echo ""

echo "=================================================="
echo -e "${GREEN}✓ K3D Cluster Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Cluster: $CLUSTER_NAME"
echo "Registry: localhost:$REGISTRY_PORT"
echo "Namespace: devfest"
echo ""
echo "Next steps:"
echo "  1. Run: ./scripts/2-prepare-data.sh"
echo "  2. Run: ./scripts/3-build-deploy.sh"
echo ""
