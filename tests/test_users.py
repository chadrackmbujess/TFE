"""
Tests unitaires pour l'application users
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import Structure, Groupe, Site, JournalConnexion

User = get_user_model()


class StructureModelTest(TestCase):
    """Tests pour le modèle Structure"""
    
    def setUp(self):
        self.structure = Structure.objects.create(
            nom='Test Entreprise',
            code='test',
            email='test@example.com'
        )
    
    def test_structure_creation(self):
        """Test de création d'une structure"""
        self.assertEqual(self.structure.nom, 'Test Entreprise')
        self.assertEqual(self.structure.code, 'test')
        self.assertTrue(self.structure.actif)
    
    def test_structure_str(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.structure), 'Test Entreprise')


class UserModelTest(TestCase):
    """Tests pour le modèle User personnalisé"""
    
    def setUp(self):
        self.structure = Structure.objects.create(
            nom='Test Entreprise',
            code='test'
        )
        
        self.user = User.objects.create_user(
            prenom='John',
            nom='Doe',
            email='john.doe@test.com',
            structure=self.structure,
            password='testpass123'
        )
    
    def test_user_creation(self):
        """Test de création d'un utilisateur"""
        self.assertEqual(self.user.prenom, 'John')
        self.assertEqual(self.user.nom, 'Doe')
        self.assertEqual(self.user.structure, self.structure)
    
    def test_username_generation(self):
        """Test de génération automatique du username"""
        # Le username devrait être généré automatiquement
        expected_username = '@john.doe.test'
        self.assertEqual(self.user.username, expected_username)
    
    def test_nom_complet_property(self):
        """Test de la propriété nom_complet"""
        self.assertEqual(self.user.nom_complet, 'John Doe')
    
    def test_is_admin_method(self):
        """Test de la méthode is_admin"""
        self.assertFalse(self.user.is_admin())
        
        self.user.role = 'admin'
        self.assertTrue(self.user.is_admin())
    
    def test_is_technicien_method(self):
        """Test de la méthode is_technicien"""
        self.assertFalse(self.user.is_technicien())
        
        self.user.role = 'technicien'
        self.assertTrue(self.user.is_technicien())
        
        self.user.role = 'admin'
        self.assertTrue(self.user.is_technicien())


class GroupeModelTest(TestCase):
    """Tests pour le modèle Groupe"""
    
    def setUp(self):
        self.structure = Structure.objects.create(
            nom='Test Entreprise',
            code='test'
        )
        
        self.groupe = Groupe.objects.create(
            nom='IT Support',
            structure=self.structure,
            description='Équipe de support'
        )
    
    def test_groupe_creation(self):
        """Test de création d'un groupe"""
        self.assertEqual(self.groupe.nom, 'IT Support')
        self.assertEqual(self.groupe.structure, self.structure)
        self.assertTrue(self.groupe.actif)
    
    def test_groupe_str(self):
        """Test de la représentation string"""
        expected = 'IT Support (Test Entreprise)'
        self.assertEqual(str(self.groupe), expected)


class SiteModelTest(TestCase):
    """Tests pour le modèle Site"""
    
    def setUp(self):
        self.structure = Structure.objects.create(
            nom='Test Entreprise',
            code='test'
        )
        
        self.site = Site.objects.create(
            nom='Siège Social',
            adresse='123 Rue Test',
            structure=self.structure
        )
    
    def test_site_creation(self):
        """Test de création d'un site"""
        self.assertEqual(self.site.nom, 'Siège Social')
        self.assertEqual(self.site.structure, self.structure)
        self.assertTrue(self.site.actif)
    
    def test_site_str(self):
        """Test de la représentation string"""
        expected = 'Siège Social (Test Entreprise)'
        self.assertEqual(str(self.site), expected)


class JournalConnexionModelTest(TestCase):
    """Tests pour le modèle JournalConnexion"""
    
    def setUp(self):
        self.structure = Structure.objects.create(
            nom='Test Entreprise',
            code='test'
        )
        
        self.user = User.objects.create_user(
            prenom='John',
            nom='Doe',
            email='john.doe@test.com',
            structure=self.structure,
            password='testpass123'
        )
        
        self.journal = JournalConnexion.objects.create(
            utilisateur=self.user,
            adresse_ip='127.0.0.1',
            type_connexion='desktop'
        )
    
    def test_journal_creation(self):
        """Test de création d'un journal de connexion"""
        self.assertEqual(self.journal.utilisateur, self.user)
        self.assertEqual(self.journal.adresse_ip, '127.0.0.1')
        self.assertEqual(self.journal.type_connexion, 'desktop')
        self.assertTrue(self.journal.succes)
    
    def test_journal_str(self):
        """Test de la représentation string"""
        expected = f"{self.user.nom_complet} - {self.journal.date_connexion}"
        self.assertEqual(str(self.journal), expected)