# 🏗️ Architecture du Système ITSM

## Vue d'Ensemble

Le système ITSM est conçu avec une architecture modulaire basée sur Django pour le backend et Kivy pour l'application desktop client.

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTÈME ITSM                            │
├─────────────────────────────────────────────────────────────┤
│  🖥️ Application Desktop (Kivy)                             │
│  ├── Interface utilisateur moderne                         │
│  ├── Synchronisation automatique                           │
│  ├── Collecte d'informations système                       │
│  └── Fonctionnalités hors ligne                           │
├─────────────────────────────────────────────────────────────┤
│  🌐 Interface Web (Django + Tailwind)                      │
│  ├── Administration système                                │
│  ├── Tableau de bord                                       │
│  ├── Rapports et statistiques                             │
│  └── Interface responsive                                  │
├─────────────────────────────────────────────────────────────┤
│  🔌 API REST (Django REST Framework)                       │
│  ├── Authentification par token                           │
│  ├── Endpoints CRUD complets                              │
│  ├── Permissions granulaires                              │
│  └── Documentation automatique                            │
├─────────────────────────────────────────────────────────────┤
│  ⚙️ Backend Django                                         │
│  ├── Modèles de données                                   │
│  ├── Logique métier                                       │
│  ├── Tâches asynchrones                                   │
│  └── Intégrations externes                                │
├─────────────────────────────────────────────────────────────┤
│  🗄️ Base de Données                                        │
│  ├── SQLite (développement)                               │
│  ├── PostgreSQL (production)                              │
│  └── Migrations automatiques                              │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Modules Applicatifs

### 👥 Users (Gestion des Utilisateurs)
- **Modèles** : User, Structure, Groupe, Site, JournalConnexion
- **Fonctionnalités** :
  - Authentification avec format @prenom.nom.entreprise
  - Gestion des rôles (Admin, Technicien, Utilisateur)
  - Journalisation des connexions
  - Gestion des structures organisationnelles

### 💻 Machines (Gestion des Machines)
- **Modèles** : Machine, InformationSysteme, InterfaceReseau, LogicielInstalle, HistoriqueMachine
- **Fonctionnalités** :
  - Inventaire automatique du matériel
  - Suivi des informations système
  - Gestion des interfaces réseau
  - Historique des modifications

### 🎫 Tickets (Support Technique)
- **Modèles** : Ticket, CategorieTicket, CommentaireTicket, PieceJointeTicket, SLA
- **Fonctionnalités** :
  - Système de tickets complet
  - Gestion des SLA
  - Escalades automatiques
  - Suivi de satisfaction

### 📦 Inventory (Inventaire)
- **Modèles** : Equipement, CategorieEquipement
- **Fonctionnalités** :
  - Gestion des équipements
  - Suivi du cycle de vie
  - Gestion des garanties

### 📊 Monitoring (Supervision)
- **Fonctionnalités prévues** :
  - Surveillance en temps réel
  - Alertes automatiques
  - Métriques de performance

### 🔧 Maintenance (Maintenance)
- **Fonctionnalités prévues** :
  - Maintenance préventive
  - Planification des interventions
  - Suivi des réparations

### 🖥️ Remote Control (Contrôle Distant)
- **Fonctionnalités prévues** :
  - Contrôle à distance
  - Capture d'écran
  - Gestion des processus

### 📚 Knowledge Base (Base de Connaissances)
- **Fonctionnalités prévues** :
  - Articles de support
  - FAQ automatique
  - Recherche intelligente

### 📈 Reports (Rapports)
- **Fonctionnalités prévues** :
  - Rapports personnalisables
  - Exports multiples formats
  - Tableaux de bord

## 🔐 Sécurité

### Authentification
- **Token-based authentication** pour l'API
- **Session authentication** pour l'interface web
- **Permissions granulaires** par rôle et structure

### Permissions
```python
# Hiérarchie des rôles
Admin > Technicien > Utilisateur

# Permissions par structure
- Admin : Accès global
- Technicien : Accès à sa structure
- Utilisateur : Accès à ses données
```

### Journalisation
- **Connexions utilisateurs** avec IP et User-Agent
- **Actions sensibles** avec traçabilité complète
- **Modifications de données** avec historique

## 🔄 Flux de Données

### Synchronisation Desktop ↔ Backend
```
Desktop App (Kivy)
    ↓ Collecte des données système
    ↓ Envoi via API REST
Backend (Django)
    ↓ Traitement et stockage
    ↓ Réponse avec instructions
Desktop App
    ↓ Application des actions
```

### Gestion des Tickets
```
Utilisateur → Création ticket → Assignation automatique
    ↓
Technicien → Traitement → Résolution
    ↓
Utilisateur → Validation → Fermeture
```

## 🛠️ Technologies

### Backend
- **Django 4.2** - Framework web Python
- **Django REST Framework** - API REST
- **django-cors-headers** - Gestion CORS
- **django-filter** - Filtrage avancé
- **Pillow** - Traitement d'images
- **python-decouple** - Configuration

### Frontend Desktop
- **Kivy** - Framework GUI Python
- **KivyMD** - Material Design
- **plyer** - Accès aux APIs système
- **psutil** - Informations système

### Base de Données
- **SQLite** - Développement
- **PostgreSQL** - Production recommandée

### Outils de Développement
- **pytest** - Tests unitaires
- **django-extensions** - Outils de développement

## 📊 Modèle de Données

### Relations Principales
```
Structure (1) ←→ (N) User
Structure (1) ←→ (N) Machine
User (1) ←→ (N) Ticket
Machine (1) ←→ (N) Ticket
User (1) ←→ (N) Machine
```

### Contraintes d'Intégrité
- **Unicité** des usernames, numéros de série, etc.
- **Références** avec CASCADE/SET_NULL selon le contexte
- **Validation** des données au niveau modèle et API

## 🚀 Déploiement

### Environnement de Développement
```bash
# Configuration locale
DEBUG=True
DATABASE=SQLite
CORS_ALLOW_ALL=True
```

### Environnement de Production
```bash
# Configuration sécurisée
DEBUG=False
DATABASE=PostgreSQL
HTTPS=True
CORS_RESTRICTED=True
```

## 🔮 Évolutions Futures

### Phase 1 (Actuelle)
- ✅ Backend Django complet
- ✅ API REST fonctionnelle
- ✅ Interface web basique
- 🔄 Application desktop Kivy

### Phase 2
- 🔄 Contrôle distant avancé
- 🔄 Intelligence artificielle
- 🔄 Application mobile
- 🔄 Intégrations externes

### Phase 3
- 🔄 Clustering et haute disponibilité
- 🔄 Analytics avancés
- 🔄 Automatisation complète
- 🔄 API publique

## 📝 Conventions de Code

### Nommage
- **Modèles** : PascalCase (ex: `User`, `CategorieTicket`)
- **Champs** : snake_case (ex: `date_creation`, `nom_complet`)
- **Méthodes** : snake_case (ex: `get_tickets_ouverts()`)
- **URLs** : kebab-case (ex: `/api/v1/remote-control/`)

### Structure des Fichiers
```
apps/nom_app/
├── __init__.py
├── models.py          # Modèles de données
├── serializers.py     # Sérialiseurs API
├── views.py           # Vues et ViewSets
├── urls.py            # Configuration URLs
├── admin.py           # Interface admin
├── permissions.py     # Permissions personnalisées
├── filters.py         # Filtres personnalisés
└── tests.py           # Tests unitaires
```

Cette architecture modulaire permet une maintenance facile, une évolutivité optimale et une séparation claire des responsabilités.