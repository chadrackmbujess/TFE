# 🚀 Guide de Démarrage Rapide - Système ITSM

## Démarrage Automatique (Recommandé)

Pour démarrer rapidement le projet avec la configuration automatique :

```bash
python start.py
```

Ce script va :
- ✅ Vérifier les prérequis
- 📦 Installer les dépendances
- ⚙️ Configurer la base de données
- 👥 Créer les utilisateurs de démonstration
- 🌐 Démarrer le serveur de développement

## Démarrage Manuel

### 1. Installation des dépendances

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer le fichier .env selon vos besoins
```

### 3. Base de données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Configuration initiale (optionnel)
python scripts/setup.py
```

### 4. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 5. Démarrer le serveur

```bash
python manage.py runserver
```

## 🔗 Accès aux Interfaces

- **Interface Web**: http://127.0.0.1:8000
- **Administration Django**: http://127.0.0.1:8000/admin
- **API REST**: http://127.0.0.1:8000/api/v1/

## 👥 Comptes de Démonstration

Si vous avez exécuté le script de configuration, vous pouvez utiliser :

| Rôle | Username | Mot de passe |
|------|----------|--------------|
| Administrateur | @admin.demo.demo | admin123 |
| Technicien | @technicien.demo.demo | tech123 |
| Utilisateur | @utilisateur.demo.demo | user123 |

## 📚 Structure du Projet

```
itsm-system/
├── itsm_backend/           # Configuration Django
├── apps/                   # Applications Django
│   ├── users/             # 👥 Gestion des utilisateurs
│   ├── machines/          # 💻 Gestion des machines
│   ├── tickets/           # 🎫 Système de tickets
│   ├── inventory/         # 📦 Inventaire
│   ├── monitoring/        # 📊 Monitoring
│   ├── maintenance/       # 🔧 Maintenance
│   ├── remote_control/    # 🖥️ Contrôle distant
│   ├── knowledge_base/    # 📚 Base de connaissances
│   ├── reports/           # 📈 Rapports
│   └── web/               # 🌐 Interface web
├── templates/             # Templates HTML
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
└── scripts/               # Scripts utilitaires
```

## 🔧 Développement

### Commandes utiles

```bash
# Créer une nouvelle migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Lancer les tests
python manage.py test

# Shell Django
python manage.py shell
```

### Ajout d'une nouvelle application

```bash
# Créer l'application
python manage.py startapp nouvelle_app

# Ajouter dans INSTALLED_APPS (settings.py)
# Créer les modèles, vues, URLs...
```

## 🐛 Dépannage

### Erreur de base de données
```bash
# Supprimer la base de données et recommencer
rm db.sqlite3
python manage.py migrate
python scripts/setup.py
```

### Erreur de dépendances
```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt
```

### Port déjà utilisé
```bash
# Utiliser un autre port
python manage.py runserver 8001
```

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la documentation dans le dossier `docs/`
2. Consultez les logs dans le dossier `logs/`
3. Ouvrez une issue sur le repository

## 🎯 Prochaines Étapes

1. **Application Desktop Kivy** - Développement de l'interface client
2. **Modules Avancés** - Contrôle distant, IA, monitoring
3. **Tests** - Tests unitaires et d'intégration
4. **Documentation** - Documentation complète de l'API
5. **Déploiement** - Configuration pour la production