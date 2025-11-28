#!/bin/bash
set -e

echo "=================================================="
echo "DevFest RAG - Ubuntu Setup Script"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}This script is for Ubuntu/Linux only${NC}"
    exit 1
fi

echo -e "${YELLOW}This script will install:${NC}"
echo "  - Docker + NVIDIA Container Toolkit"
echo "  - Ollama with GPU support"
echo "  - K3D (Kubernetes)"
echo "  - Python dependencies"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "=================================================="
echo "Step 1: System Update"
echo "=================================================="
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential curl git python3-pip python3-venv
echo -e "${GREEN}✓ System updated${NC}"
echo ""

echo "=================================================="
echo "Step 2: Check NVIDIA GPU"
echo "=================================================="
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}Installing NVIDIA drivers...${NC}"
    sudo ubuntu-drivers autoinstall
    echo -e "${YELLOW}Please reboot and run this script again${NC}"
    exit 0
fi
nvidia-smi
echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
echo ""

echo "=================================================="
echo "Step 3: Install Docker"
echo "=================================================="
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✓ Docker installed${NC}"
    echo -e "${YELLOW}Please logout/login and run this script again${NC}"
    exit 0
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi
echo ""

echo "=================================================="
echo "Step 4: Install NVIDIA Container Toolkit"
echo "=================================================="
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
echo -e "${GREEN}✓ NVIDIA Container Toolkit installed${NC}"
echo ""

echo "=================================================="
echo "Step 5: Install Ollama"
echo "=================================================="
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
else
    echo -e "${GREEN}✓ Ollama already installed${NC}"
fi

echo ""
echo -e "${YELLOW}Pulling Gemma3n (this may take a few minutes)...${NC}"
ollama pull gemma3n
echo -e "${GREEN}✓ Gemma3n ready${NC}"
echo ""

echo "=================================================="
echo "Step 6: Install K3D"
echo "=================================================="
if ! command -v kubectl &> /dev/null; then
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    echo -e "${GREEN}✓ kubectl installed${NC}"
fi

if ! command -v k3d &> /dev/null; then
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    echo -e "${GREEN}✓ K3D installed${NC}"
fi
echo ""

echo "=================================================="
echo "Step 7: Setup Python Environment"
echo "=================================================="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo "=================================================="
echo "Step 8: Configure for Ubuntu"
echo "=================================================="
cp .env.ubuntu .env
echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

echo "=================================================="
echo -e "${GREEN}✓✓✓ SETUP COMPLETE! ✓✓✓${NC}"
echo "=================================================="
echo ""
echo "🎉 Your Ubuntu system is ready for DevFest RAG!"
echo ""
echo "Next steps:"
echo "  1. Test GPU: ollama run gemma3n 'Hello test'"
echo "  2. Test local app: streamlit run src/coordinator/app.py"
echo "  3. Deploy K3D: ./scripts/deploy-all.sh"
echo ""
echo "Verify GPU is used:"
echo "  watch -n 1 nvidia-smi"
echo ""
