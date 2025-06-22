#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de configuration initiale du système ITSM
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configuration de l'encodage pour Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_backend.settings')
django.setup()

from apps.users.models import Structure, User, Groupe, Site
from apps.tickets.models import CategorieTicket, SLA
from apps.machines.models import TypeMachine
from apps.inventory.models import CategorieEquipement


def create_initial_data():
    """Créer les données initiales"""
    print("🚀 Création des données initiales...")
    
    # Créer une structure par défaut
    structure, created = Structure.objects.get_or_create(
        code='demo',
        defaults={
            'nom': 'Entreprise Démo',
            'adresse': '123 Rue de la Démo',
            'telephone': '+33 1 23 45 67 89',
            'email': 'contact@demo.com'
        }
    )
    if created:
        print(f"✅ Structure créée: {structure.nom}")
    
    # Créer un groupe par défaut
    groupe, created = Groupe.objects.get_or_create(
        nom='IT Support',
        structure=structure,
        defaults={'description': 'Équipe de support informatique'}
    )
    if created:
        print(f"✅ Groupe créé: {groupe.nom}")
    
    # Créer un site par défaut
    site, created = Site.objects.get_or_create(
        nom='Siège Social',
        structure=structure,
        defaults={'adresse': '123 Rue de la Démo, 75001 Paris'}
    )
    if created:
        print(f"✅ Site créé: {site.nom}")
    
    # Créer des catégories de tickets
    categories_tickets = [
        {'nom': 'Matériel', 'description': 'Problèmes matériels', 'couleur': '#dc3545'},
        {'nom': 'Logiciel', 'description': 'Problèmes logiciels', 'couleur': '#007bff'},
        {'nom': 'Réseau', 'description': 'Problèmes réseau', 'couleur': '#28a745'},
        {'nom': 'Accès', 'description': 'Problèmes d\'accès', 'couleur': '#ffc107'},
        {'nom': 'Autre', 'description': 'Autres demandes', 'couleur': '#6c757d'},
    ]
    
    for cat_data in categories_tickets:
        cat, created = CategorieTicket.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Catégorie de ticket créée: {cat.nom}")
    
    # Créer un SLA par défaut
    sla, created = SLA.objects.get_or_create(
        nom='SLA Standard',
        defaults={
            'description': 'Accord de niveau de service standard',
            'temps_reponse_critique': 1,
            'temps_reponse_haute': 4,
            'temps_reponse_normale': 24,
            'temps_reponse_basse': 72,
            'temps_resolution_critique': 4,
            'temps_resolution_haute': 8,
            'temps_resolution_normale': 48,
            'temps_resolution_basse': 168,
        }
    )
    if created:
        print(f"✅ SLA créé: {sla.nom}")
    
    # Créer des types de machines
    types_machines = [
        {'nom': 'Desktop', 'description': 'Ordinateur de bureau'},
        {'nom': 'Laptop', 'description': 'Ordinateur portable'},
        {'nom': 'Serveur', 'description': 'Serveur'},
        {'nom': 'Imprimante', 'description': 'Imprimante'},
        {'nom': 'Switch', 'description': 'Commutateur réseau'},
        {'nom': 'Routeur', 'description': 'Routeur réseau'},
    ]
    
    for type_data in types_machines:
        type_machine, created = TypeMachine.objects.get_or_create(
            nom=type_data['nom'],
            defaults=type_data
        )
        if created:
            print(f"✅ Type de machine créé: {type_machine.nom}")
    
    # Créer des catégories d'équipements
    categories_equipements = [
        {'nom': 'Informatique', 'description': 'Équipements informatiques'},
        {'nom': 'Réseau', 'description': 'Équipements réseau'},
        {'nom': 'Téléphonie', 'description': 'Équipements de téléphonie'},
        {'nom': 'Mobilier', 'description': 'Mobilier de bureau'},
        {'nom': 'Autre', 'description': 'Autres équipements'},
    ]
    
    for cat_data in categories_equipements:
        cat, created = CategorieEquipement.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Catégorie d'équipement créée: {cat.nom}")
    
    print("✨ Configuration initiale terminée!")


def create_demo_users():
    """Créer des utilisateurs de démonstration"""
    print("👥 Création des utilisateurs de démonstration...")
    
    structure = Structure.objects.get(code='demo')
    groupe = Groupe.objects.get(nom='IT Support', structure=structure)
    site = Site.objects.get(nom='Siège Social', structure=structure)
    
    # Administrateur
    admin_user, created = User.objects.get_or_create(
        username='@admin.demo.demo',
        defaults={
            'prenom': 'Admin',
            'nom': 'Demo',
            'email': 'admin@demo.com',
            'structure': structure,
            'groupe': groupe,
            'site': site,
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Administrateur créé: {admin_user.username}")
    
    # Technicien
    tech_user, created = User.objects.get_or_create(
        username='@technicien.demo.demo',
        defaults={
            'prenom': 'Technicien',
            'nom': 'Demo',
            'email': 'technicien@demo.com',
            'structure': structure,
            'groupe': groupe,
            'site': site,
            'role': 'technicien',
        }
    )
    if created:
        tech_user.set_password('tech123')
        tech_user.save()
        print(f"✅ Technicien créé: {tech_user.username}")
    
    # Utilisateur
    user, created = User.objects.get_or_create(
        username='@utilisateur.demo.demo',
        defaults={
            'prenom': 'Utilisateur',
            'nom': 'Demo',
            'email': 'utilisateur@demo.com',
            'structure': structure,
            'site': site,
            'role': 'utilisateur',
        }
    )
    if created:
        user.set_password('user123')
        user.save()
        print(f"✅ Utilisateur créé: {user.username}")
    
    print("👥 Utilisateurs de démonstration créés!")


def setup_database():
    """Configuration de la base de données avec gestion des erreurs"""
    print("📦 Configuration de la base de données...")
    
    try:
        # Supprimer l'ancienne base de données si elle existe
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️ Ancienne base de données supprimée")
        
        # Supprimer les anciens fichiers de migration
        apps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps')
        for app_name in ['users', 'machines', 'tickets', 'inventory', 'monitoring', 'maintenance', 'remote_control', 'knowledge_base', 'reports']:
            migrations_dir = os.path.join(apps_dir, app_name, 'migrations')
            if os.path.exists(migrations_dir):
                for file in os.listdir(migrations_dir):
                    if file.endswith('.py') and file != '__init__.py':
                        os.remove(os.path.join(migrations_dir, file))
                        print(f"🗑️ Migration supprimée: {app_name}/{file}")
        
        # Créer les migrations pour chaque app dans l'ordre correct
        print("📝 Création des migrations...")
        
        # D'abord users (car les autres apps en dépendent)
        execute_from_command_line(['manage.py', 'makemigrations', 'users'])
        print("✅ Migrations users créées")
        
        # Ensuite les autres apps
        for app in ['machines', 'tickets', 'inventory']:
            try:
                execute_from_command_line(['manage.py', 'makemigrations', app])
                print(f"✅ Migrations {app} créées")
            except Exception as e:
                print(f"⚠️ Erreur lors de la création des migrations pour {app}: {e}")
        
        # Appliquer toutes les migrations
        print("🔄 Application des migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration de la base de données: {e}")
        return False


if __name__ == '__main__':
    print("🔧 Configuration du système ITSM")
    print("=" * 50)
    
    # Configuration de la base de données
    if not setup_database():
        print("❌ Échec de la configuration de la base de données")
        sys.exit(1)
    
    # Données initiales
    try:
        create_initial_data()
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des données initiales: {e}")
    
    # Utilisateurs de démo
    try:
        create_demo_users()
    except Exception as e:
        print(f"⚠️ Erreur lors de la création des utilisateurs de démo: {e}")
    
    print("\n🎉 Configuration terminée!")
    print("\nComptes de démonstration:")
    print("- Admin: @admin.demo.demo / admin123")
    print("- Technicien: @technicien.demo.demo / tech123")
    print("- Utilisateur: @utilisateur.demo.demo / user123")
    print("\nLancez le serveur avec: python manage.py runserver")