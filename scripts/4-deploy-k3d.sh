#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Deploy to K3D"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Step 1: Applying namespace...${NC}"
kubectl apply -f k3d/namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

echo -e "${YELLOW}Step 2: Applying ConfigMap...${NC}"
kubectl apply -f k3d/configmap.yaml
echo -e "${GREEN}✓ ConfigMap applied${NC}"
echo ""

echo -e "${YELLOW}Step 3: Deploying coordinator...${NC}"
kubectl apply -f k3d/deployments/coordinator.yaml
echo -e "${GREEN}✓ Coordinator deployed${NC}"
echo ""

echo -e "${YELLOW}Step 4: Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=coordinator -n devfest --timeout=120s
echo -e "${GREEN}✓ All pods ready${NC}"
echo ""

echo "=================================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=================================================="
echo ""
echo "Deployment status:"
kubectl get pods -n devfest -o wide
echo ""
kubectl get svc -n devfest
echo ""
echo "=================================================="
echo "Access the application:"
echo "  URL: http://localhost:8501"
echo ""
echo "Or port-forward:"
echo "  kubectl port-forward -n devfest svc/coordinator 8501:8501"
echo ""
echo "Monitor pods:"
echo "  kubectl get pods -n devfest -w"
echo "  kubectl logs -f deployment/coordinator -n devfest"
echo ""
echo "Demo commands:"
echo "  # Check deployment"
echo "  kubectl get all -n devfest"
echo ""
echo "  # View logs"
echo "  kubectl logs -f deployment/coordinator -n devfest"
echo ""
echo "  # Scale (for demo)"
echo "  kubectl scale deployment coordinator --replicas=2 -n devfest"
echo ""
echo "=================================================="
