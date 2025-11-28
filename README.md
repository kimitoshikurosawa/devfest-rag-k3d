# DevFest RAG Multi-Agent System

🤖 **Système RAG Multi-Agents déployé sur Kubernetes avec Gemma**

Démonstration live pour DevFest Abidjan 2025 - 29 Novembre 2025

---

## 🎯 Vue d'Ensemble

Ce projet démontre un système RAG (Retrieval-Augmented Generation) multi-agents orchestré sur Kubernetes, utilisant:

- **2 Agents Spécialisés** (DevFest & Kimana)
- **Gemma 2B** via Ollama (LLM local)
- **K3D** (Kubernetes in Docker)
- **ChromaDB** (Vector Store)
- **Streamlit** (Interface utilisateur)

### Architecture

```
┌─────────────────────────────────────────┐
│    Coordinator (Streamlit)              │
│    Routing intelligent                  │
└────┬─────────────────────┬──────────────┘
     │                     │
┌────▼──────┐      ┌───────▼────┐
│  DevFest  │      │   Kimana   │
│  Agent    │      │   Agent    │
│  (K3D)    │      │   (K3D)    │
└────┬──────┘      └───────┬────┘
     │                     │
     └──────────┬──────────┘
                │
    ┌───────────▼────────────┐
    │   ChromaDB             │
    │   2 Collections        │
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │   Ollama + Gemma 2B    │
    │   (Host Mac)           │
    └────────────────────────┘
```

---

## 🚀 Quick Start

### Prérequis

- Docker Desktop
- K3D
- Ollama
- Python 3.11+

### Installation

```bash
# 1. Cloner le repo
git clone <repo-url>
cd devfest-rag-k3d

# 2. Installer Ollama (si pas déjà fait)
curl -fsSL https://ollama.com/install.sh | sh

# 3. Télécharger Gemma
ollama pull gemma2:2b

# 4. Installer K3D
brew install k3d  # macOS
# ou curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# 5. Installer les dépendances Python
pip install -r requirements.txt
```

### Démarrage Rapide (Local)

```bash
# Copier le fichier d'environnement
cp .env.example .env

# Lancer Ollama
ollama serve

# Lancer l'application Streamlit
streamlit run src/coordinator/app.py
```

Ouvrir http://localhost:8501 dans votre navigateur.

---

## 🎬 Déploiement K3D (Production)

### Étape 1: Créer le Cluster K3D

```bash
./scripts/1-setup-cluster.sh
```

Cela va:
- Créer un cluster K3D avec 1 master + 2 workers
- Créer un registry local
- Configurer le namespace

### Étape 2: Préparer les Données

```bash
./scripts/2-prepare-data.sh
```

Charge les données dans ChromaDB.

### Étape 3: Build & Deploy

```bash
./scripts/3-build-deploy.sh
```

Build les images Docker et déploie sur K3D.

### Étape 4: Accéder à l'Application

```bash
# Port-forward vers Streamlit
kubectl port-forward -n devfest svc/coordinator 8501:8501

# Ouvrir dans le navigateur
open http://localhost:8501
```

---

## 📊 Monitoring & Debugging

### Vérifier les Pods

```bash
kubectl get pods -n devfest -o wide
```

### Voir les Logs

```bash
# DevFest Agent
kubectl logs -f deployment/devfest-agent -n devfest

# Kimana Agent
kubectl logs -f deployment/kimana-agent -n devfest

# Coordinator
kubectl logs -f deployment/coordinator -n devfest
```

### Dashboard K9s (Recommandé)

```bash
# Installer K9s
brew install k9s

# Lancer
k9s -n devfest
```

---

## 🎯 Démo Live - Commandes

### 1. Montrer l'Architecture

```bash
# Cluster
k3d cluster list
kubectl get nodes

# Pods
kubectl get pods -n devfest -o wide

# Services
kubectl get svc -n devfest
```

### 2. Questions Exemples

**DevFest Agent:**
- "À quelle heure commence le talk de Kimana ?"
- "Quels sont les sponsors de DevFest ?"
- "Où se déroule l'événement ?"

**Kimana Agent:**
- "Qui est Kimana Misago ?"
- "C'est quoi Ivoire.pro ?"
- "Quelle est l'expertise technique de Kimana ?"

**Questions Mixtes:**
- "Parle-moi du speaker qui présente sur Kubernetes"

### 3. Scaling Live

```bash
# Scale DevFest Agent à 4 replicas
kubectl scale deployment devfest-agent --replicas=4 -n devfest

# Watch les pods
kubectl get pods -n devfest -w

# Tester dans Streamlit pendant ce temps
```

### 4. Résilience

```bash
# Supprimer un pod
kubectl delete pod <pod-name> -n devfest

# Observer le restart automatique
kubectl get pods -n devfest -w
```

---

## 🛠️ Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Orchestration** | K3D (Kubernetes) | v5.x |
| **LLM** | Gemma 2B via Ollama | 0.1.6 |
| **Vector Store** | ChromaDB | 0.4.22 |
| **Embeddings** | sentence-transformers | 2.2.2 |
| **Framework** | LangChain | 0.1.0 |
| **UI** | Streamlit | 1.29.0 |
| **Language** | Python | 3.11+ |

---

## 📁 Structure du Projet

```
devfest-rag-k3d/
├── data/                  # Données JSON
│   ├── devfest/          # Infos événement
│   └── kimana/           # Profil Kimana
├── src/
│   ├── agents/           # Agents RAG
│   ├── coordinator/      # Routing & Streamlit
│   ├── vectorstore/      # ChromaDB
│   └── utils/            # Ollama client
├── k3d/                  # Manifests Kubernetes
├── docker/               # Dockerfiles
├── scripts/              # Scripts d'automatisation
└── requirements.txt
```

---

## 🎓 Use Cases

### 1. Assistant Événement
Base de connaissances complète sur DevFest Abidjan 2025.

### 2. Profil Professionnel
Informations détaillées sur Kimana Misago et ses projets.

### 3. Démo Technique
Showcase de RAG + Kubernetes pour production.

---

## 🔧 Configuration

### Variables d'Environnement

```bash
# Ollama
OLLAMA_HOST=http://host.docker.internal:11434
OLLAMA_MODEL=gemma2:2b

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_DEVFEST=devfest_docs
CHROMA_COLLECTION_KIMANA=kimana_docs

# Agents (K3D)
DEVFEST_AGENT_URL=http://devfest-agent:8000
KIMANA_AGENT_URL=http://kimana-agent:8000
```

---

## 🤝 Contributions

Ce projet est une démonstration pour DevFest Abidjan 2025.

**Speaker:** Kimana Misago  
**Event:** DevFest Cloud Abidjan & Cocody 2025  
**Date:** 29 Novembre 2025  
**Talk:** "De Kubernetes à Gemma : Déployer un Agent IA (RAG) en Live"

---

## 📝 License

MIT License - Voir LICENSE pour détails.

---

## 🙏 Remerciements

- **Google Developer Groups Cloud Abidjan**
- **DevFest Abidjan 2025 Organizers**
- **Sponsors:** ATOS, FATA, Dextrem
- **Communauté open source** (LangChain, ChromaDB, Ollama)

---

## 📞 Contact

**Kimana Misago**
- Blog: [kimana.ivoire.pro](https://kimana.ivoire.pro)
- LinkedIn: [kimana-misago](#)
- Twitter: [@kimana_misago](#)

---

**Made with ❤️ for DevFest Abidjan 2025** 🇨🇮
