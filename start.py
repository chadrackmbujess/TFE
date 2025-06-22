#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de démarrage rapide pour le système ITSM
"""
import os
import sys
import subprocess

# Configuration de l'encodage pour Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}")
        print(f"Erreur: {e.stderr}")
        return False

def main():
    print("🚀 Démarrage du système ITSM")
    print("=" * 50)
    
    # Vérifier si Python est installé
    try:
        python_version = subprocess.check_output([sys.executable, '--version'], text=True)
        print(f"✅ Python détecté: {python_version.strip()}")
    except:
        print("❌ Python non trouvé")
        return
    
    # Vérifier si les dépendances sont installées
    try:
        import django
        print(f"✅ Django détecté: {django.get_version()}")
    except ImportError:
        print("📦 Installation des dépendances...")
        if not run_command("pip install -r requirements.txt", "Installation des dépendances"):
            return
    
    # Créer le fichier .env s'il n'existe pas
    if not os.path.exists('.env'):
        print("📝 Création du fichier .env...")
        with open('.env', 'w') as f:
            f.write("""# Configuration Django
SECRET_KEY=django-insecure-demo-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration ITSM
COMPANY_DOMAIN=demo.local
AUTO_SYNC_INTERVAL=300
ENABLE_AI_ASSISTANCE=False
""")
        print("✅ Fichier .env créé")
    
    # Créer les dossiers nécessaires
    os.makedirs('logs', exist_ok=True)
    os.makedirs('media', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Exécuter le script de configuration
    print("⚙️ Configuration initiale...")
    if run_command(f"{sys.executable} scripts/setup.py", "Configuration initiale"):
        print("\n🎉 Système ITSM configuré avec succès!")
        print("\n📋 Informations de connexion:")
        print("- Admin: @admin.demo.demo / admin123")
        print("- Technicien: @technicien.demo.demo / tech123")
        print("- Utilisateur: @utilisateur.demo.demo / user123")
        
        print("\n🌐 Démarrage du serveur...")
        print("Accédez à: http://127.0.0.1:8000")
        print("Admin Django: http://127.0.0.1:8000/admin")
        print("\nPour arrêter le serveur, appuyez sur Ctrl+C")
        
        # Démarrer le serveur
        try:
            subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
        except KeyboardInterrupt:
            print("\n👋 Serveur arrêté")
    else:
        print("❌ Erreur lors de la configuration")

if __name__ == '__main__':
    main()