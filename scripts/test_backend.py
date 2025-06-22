#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test complet du backend ITSM
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

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

from apps.users.models import User, Structure, Groupe, Site
from apps.tickets.models import Ticket, CategorieTicket
from apps.machines.models import Machine, TypeMachine
from apps.inventory.models import Equipement, CategorieEquipement


class ITSMTester:
    """Classe pour tester toutes les fonctionnalités du backend ITSM"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.api_url = f"{self.base_url}/api/v1"
        self.token = None
        self.test_results = []
    
    def log_test(self, test_name, success, message=""):
        """Enregistrer le résultat d'un test"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
    
    def test_database_models(self):
        """Tester les modèles de base de données"""
        print("\n🗄️ Test des modèles de base de données")
        print("-" * 50)
        
        try:
            # Test Structure
            structures = Structure.objects.all()
            self.log_test("Modèle Structure", True, f"{structures.count()} structures trouvées")
            
            # Test User
            users = User.objects.all()
            self.log_test("Modèle User", True, f"{users.count()} utilisateurs trouvés")
            
            # Test CategorieTicket
            categories = CategorieTicket.objects.all()
            self.log_test("Modèle CategorieTicket", True, f"{categories.count()} catégories trouvées")
            
            # Test TypeMachine
            types_machines = TypeMachine.objects.all()
            self.log_test("Modèle TypeMachine", True, f"{types_machines.count()} types de machines trouvés")
            
            # Test relations
            if users.exists():
                user = users.first()
                self.log_test("Relations User-Structure", 
                            user.structure is not None, 
                            f"Utilisateur {user.username} lié à {user.structure}")
            
        except Exception as e:
            self.log_test("Modèles de base de données", False, str(e))
    
    def test_authentication(self):
        """Tester l'authentification API"""
        print("\n🔐 Test de l'authentification")
        print("-" * 50)
        
        try:
            # Test avec les comptes de démonstration
            test_accounts = [
                {"username": "@admin.demo.demo", "password": "admin123"},
                {"username": "@technicien.demo.demo", "password": "tech123"},
                {"username": "@utilisateur.demo.demo", "password": "user123"}
            ]
            
            for account in test_accounts:
                try:
                    response = requests.post(
                        f"{self.base_url}/api/auth/token/",
                        data=account,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        token_data = response.json()
                        if 'token' in token_data:
                            self.log_test(f"Auth {account['username']}", True, "Token obtenu")
                            if not self.token:  # Utiliser le premier token valide
                                self.token = token_data['token']
                        else:
                            self.log_test(f"Auth {account['username']}", False, "Pas de token dans la réponse")
                    else:
                        self.log_test(f"Auth {account['username']}", False, f"Status {response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    self.log_test(f"Auth {account['username']}", False, f"Erreur réseau: {e}")
                    
        except Exception as e:
            self.log_test("Authentification API", False, str(e))
    
    def test_api_endpoints(self):
        """Tester les endpoints de l'API"""
        print("\n🌐 Test des endpoints API")
        print("-" * 50)
        
        if not self.token:
            self.log_test("API Endpoints", False, "Pas de token d'authentification")
            return
        
        headers = {"Authorization": f"Token {self.token}"}
        
        endpoints = [
            "/users/users/",
            "/users/structures/",
            "/users/groupes/",
            "/users/sites/",
            "/machines/",
            "/tickets/",
            "/inventory/",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data.get('results', data)) if isinstance(data, dict) else len(data)
                    self.log_test(f"GET {endpoint}", True, f"{count} éléments")
                else:
                    self.log_test(f"GET {endpoint}", False, f"Status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"GET {endpoint}", False, f"Erreur réseau: {e}")
    
    def test_admin_interface(self):
        """Tester l'interface d'administration"""
        print("\n⚙️ Test de l'interface d'administration")
        print("-" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=5)
            if response.status_code == 200:
                self.log_test("Interface Admin", True, "Page d'admin accessible")
            else:
                self.log_test("Interface Admin", False, f"Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_test("Interface Admin", False, f"Erreur réseau: {e}")
    
    def test_web_interface(self):
        """Tester l'interface web"""
        print("\n🌐 Test de l'interface web")
        print("-" * 50)
        
        pages = [
            ("/", "Page d'accueil"),
            ("/accounts/login/", "Page de connexion"),
        ]
        
        for url, name in pages:
            try:
                response = requests.get(f"{self.base_url}{url}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Web {name}", True, "Page accessible")
                else:
                    self.log_test(f"Web {name}", False, f"Status {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_test(f"Web {name}", False, f"Erreur réseau: {e}")
    
    def test_data_creation(self):
        """Tester la création de données"""
        print("\n📝 Test de création de données")
        print("-" * 50)
        
        try:
            # Créer un ticket de test
            structure = Structure.objects.first()
            user = User.objects.filter(structure=structure).first()
            categorie = CategorieTicket.objects.first()
            
            if user and categorie:
                ticket = Ticket.objects.create(
                    titre="Test Ticket",
                    description="Ticket de test automatique",
                    demandeur=user,
                    categorie=categorie,
                    priorite='normale'
                )
                self.log_test("Création Ticket", True, f"Ticket {ticket.numero} créé")
                
                # Supprimer le ticket de test
                ticket.delete()
                self.log_test("Suppression Ticket", True, "Ticket de test supprimé")
            else:
                self.log_test("Création Ticket", False, "Données manquantes (user/catégorie)")
                
        except Exception as e:
            self.log_test("Création de données", False, str(e))
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 TESTS DU BACKEND ITSM")
        print("=" * 60)
        print(f"Début des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Exécuter tous les tests
        self.test_database_models()
        self.test_authentication()
        self.test_api_endpoints()
        self.test_admin_interface()
        self.test_web_interface()
        self.test_data_creation()
        
        # Résumé des résultats
        print("\n📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total des tests: {total_tests}")
        print(f"✅ Tests réussis: {passed_tests}")
        print(f"❌ Tests échoués: {failed_tests}")
        print(f"📈 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTS ÉCHOUÉS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print(f"\nFin des tests: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return failed_tests == 0


def main():
    """Fonction principale"""
    print("🚀 Démarrage des tests du backend ITSM")
    
    # Vérifier que Django est configuré
    try:
        from django.conf import settings
        if not settings.configured:
            print("❌ Django n'est pas configuré")
            return False
    except Exception as e:
        print(f"❌ Erreur de configuration Django: {e}")
        return False
    
    # Exécuter les tests
    tester = ITSMTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("Le backend ITSM est fonctionnel et prêt à utiliser.")
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("Vérifiez que le serveur Django est démarré (python manage.py runserver)")
    
    return success


if __name__ == '__main__':
    main()