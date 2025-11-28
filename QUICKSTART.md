# 🚀 QUICK START GUIDE

## ⚡ Test Local MAINTENANT (5 minutes)

### Étape 1: Vérifier les prérequis

```bash
# Aller dans le projet
cd /path/to/devfest-rag-k3d

# Vérifier Ollama
ollama --version

# Si pas installé:
curl -fsSL https://ollama.com/install.sh | sh
```

### Étape 2: Lancer Ollama

```bash
# Dans un terminal séparé
ollama serve
```

### Étape 3: Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### Étape 4: Copier les variables d'environnement

```bash
cp .env.example .env
```

### Étape 5: LANCER L'APP ! 🎉

```bash
./scripts/0-test-local.sh
```

Ouvre http://localhost:8501 dans ton navigateur !

---

## 🎯 Questions à Tester

### Agent DevFest
- "À quelle heure commence le talk de Kimana ?"
- "Quels sont les sponsors de DevFest ?"
- "Où se déroule l'événement ?"

### Agent Kimana  
- "Qui est Kimana Misago ?"
- "C'est quoi Ivoire.pro ?"
- "Parle-moi d'IvoryGuards"

### Questions Mixtes (routing intelligent)
- "Quel est le talk du speaker qui est CTO d'Ivoire.pro ?"

---

## 🐛 Troubleshooting

### Ollama ne répond pas
```bash
# Vérifier
curl http://localhost:11434/api/tags

# Si erreur, redémarrer
killall ollama
ollama serve
```

### Erreur d'import Python
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### ChromaDB vide
```bash
# Recharger les données
./scripts/2-prepare-data.sh
```

---

## 📦 Pour K3D (Après avoir testé en local)

```bash
# 1. Setup cluster
./scripts/1-setup-cluster.sh

# 2. Build & Deploy (TODO: à créer)
# Docker + K8s manifests

# 3. Access
kubectl port-forward -n devfest svc/coordinator 8501:8501
```

---

## ⏱️ Timeline Ce Soir

- [x] Structure projet ✅
- [x] Code agents ✅  
- [x] Interface Streamlit ✅
- [x] Données JSON ✅
- [x] Scripts setup ✅
- [ ] **TEST LOCAL** ← TU ES ICI
- [ ] Dockerfiles
- [ ] K8s manifests
- [ ] Test K3D
- [ ] Polish démo

**Priorité #1: Tester en local MAINTENANT !**

Ensuite on fait Docker + K8s si temps.

---

## 📞 Checklist Avant Démo Demain

- [ ] App Streamlit fonctionne
- [ ] Les 2 agents répondent correctement
- [ ] Routing intelligent marche
- [ ] Sources s'affichent
- [ ] K3D cluster démarre
- [ ] kubectl scale fonctionne
- [ ] Slides à jour (Ollama au lieu de LM Studio)

---

**COMMENCE PAR TESTER EN LOCAL ! 🎯**
