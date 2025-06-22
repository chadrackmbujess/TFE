# SWEEP.md - Commandes et informations utiles

## Commandes Django

### Serveur de développement
```bash
# Pour accès local uniquement
python manage.py runserver 127.0.0.1:8000

# Pour accès réseau (autres PC du réseau local)
python manage.py runserver 0.0.0.0:8000
```

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Tests
```bash
python manage.py test
```

### Shell Django
```bash
python manage.py shell
```

## Structure du projet

### Applications principales
- `apps/users/` - Gestion des utilisateurs
- `apps/tickets/` - Gestion des tickets et notifications
- `apps/machines/` - Gestion des machines
- `apps/inventory/` - Inventaire
- `desktop_app/` - Application desktop Kivy

### API Endpoints
- `/api/v1/users/` - Utilisateurs
- `/api/v1/tickets/` - Tickets
- `/api/v1/tickets/notifications/` - Notifications de tickets
- `/api/v1/machines/` - Machines

## Utilisateurs de test
- Admin: `@admin.demo.demo` / `admin123`
- Technicien: `@technicien.demo.demo` / `tech123`
- Utilisateur: `@utilisateur.demo.demo` / `user123`
- Utilisateur test: `@aa.jess.cd` / `user123`

## Scripts utiles
- `create_test_notifications.py` - Créer des notifications de test
- `test_notifications_api.py` - Tester l'API des notifications

## Génération APK Android
**Note:** Buildozer pour Android nécessite un environnement Linux
- Sur Windows : Utiliser WSL ou GitHub Actions
- Commande : `buildozer android debug` (dans mobile_app/)
- Fichier de config : `mobile_app/buildozer.spec`

## GitHub Actions
### Workflows disponibles
- `django-ci.yml` - Tests et CI/CD pour le backend Django
- `build-android.yml` - Génération automatique d'APK Android
- `desktop-app.yml` - Build des applications desktop (Windows/Linux)
- `deploy.yml` - Déploiement en production
- `release.yml` - Création automatique de releases avec assets

### Déclenchement manuel
```bash
# Via l'interface GitHub ou avec GitHub CLI
gh workflow run build-android.yml
gh workflow run desktop-app.yml
```

### Secrets requis
- `SECRET_KEY` - Clé secrète Django
- `DATABASE_URL` - URL de la base de données
- `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_KEY` - Pour le déploiement

## Style de code
- Utiliser des docstrings pour toutes les fonctions et classes
- Noms de variables en français pour les modèles métier
- Noms de variables en anglais pour le code technique
- Utiliser des emojis dans les messages de log pour la lisibilité