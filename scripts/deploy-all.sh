#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Full K3D Deployment"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v k3d &> /dev/null; then
    echo -e "${RED}✗ k3d not found${NC}"
    echo "Install: brew install k3d"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl not found${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ docker not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites OK${NC}"
echo ""

# Step 1: Setup cluster
echo "=================================================="
echo "STEP 1/4: Setting up K3D cluster"
echo "=================================================="
./scripts/1-setup-cluster.sh

# Step 2: Build images
echo ""
echo "=================================================="
echo "STEP 2/4: Building Docker images"
echo "=================================================="
./scripts/3-build-images.sh

# Step 3: Deploy to K3D
echo ""
echo "=================================================="
echo "STEP 3/4: Deploying to K3D"
echo "=================================================="
./scripts/4-deploy-k3d.sh

# Step 4: Summary
echo ""
echo "=================================================="
echo -e "${GREEN}✓✓✓ DEPLOYMENT COMPLETE! ✓✓✓${NC}"
echo "=================================================="
echo ""
echo "🎉 Your DevFest RAG system is running on K3D!"
echo ""
echo "📊 Quick Status Check:"
kubectl get all -n devfest
echo ""
echo "🌐 Access the application:"
echo "   http://localhost:8501"
echo ""
echo "📝 Useful commands:"
echo "   # Watch pods"
echo "   kubectl get pods -n devfest -w"
echo ""
echo "   # View logs"
echo "   kubectl logs -f deployment/coordinator -n devfest"
echo ""
echo "   # Port forward (if needed)"
echo "   kubectl port-forward -n devfest svc/coordinator 8501:8501"
echo ""
echo "🎬 Demo commands:"
echo "   # Scale up"
echo "   kubectl scale deployment coordinator --replicas=3 -n devfest"
echo ""
echo "   # Delete a pod (watch auto-restart)"
echo "   kubectl delete pod <pod-name> -n devfest"
echo ""
echo "=================================================="
echo -e "${GREEN}Ready for DevFest demo! 🚀${NC}"
echo "=================================================="
