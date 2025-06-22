"""
Tests unitaires pour l'application tickets
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.users.models import Structure
from apps.tickets.models import CategorieTicket, Ticket, CommentaireTicket, SLA

User = get_user_model()


class CategorieTicketModelTest(TestCase):
    """Tests pour le modèle CategorieTicket"""
    
    def setUp(self):
        self.categorie = CategorieTicket.objects.create(
            nom='Matériel',
            description='Problèmes matériels',
            couleur='#dc3545'
        )
    
    def test_categorie_creation(self):
        """Test de création d'une catégorie"""
        self.assertEqual(self.categorie.nom, 'Matériel')
        self.assertEqual(self.categorie.couleur, '#dc3545')
        self.assertTrue(self.categorie.actif)
    
    def test_categorie_str(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.categorie), 'Matériel')


class TicketModelTest(TestCase):
    """Tests pour le modèle Ticket"""
    
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
        
        self.categorie = CategorieTicket.objects.create(
            nom='Matériel',
            description='Problèmes matériels'
        )
        
        self.ticket = Ticket.objects.create(
            titre='Problème d\'écran',
            description='L\'écran ne s\'allume plus',
            demandeur=self.user,
            categorie=self.categorie
        )
    
    def test_ticket_creation(self):
        """Test de création d'un ticket"""
        self.assertEqual(self.ticket.titre, 'Problème d\'écran')
        self.assertEqual(self.ticket.demandeur, self.user)
        self.assertEqual(self.ticket.statut, 'nouveau')
        self.assertEqual(self.ticket.priorite, 'normale')
    
    def test_numero_generation(self):
        """Test de génération automatique du numéro"""
        # Le numéro devrait être généré automatiquement
        self.assertTrue(self.ticket.numero.startswith('T'))
        self.assertTrue(len(self.ticket.numero) > 5)
    
    def test_ticket_str(self):
        """Test de la représentation string"""
        expected = f"{self.ticket.numero} - Problème d'écran"
        self.assertEqual(str(self.ticket), expected)
    
    def test_est_en_retard_property(self):
        """Test de la propriété est_en_retard"""
        # Ticket sans échéance
        self.assertFalse(self.ticket.est_en_retard)
        
        # Ticket avec échéance passée
        past_date = timezone.now() - timezone.timedelta(days=1)
        self.ticket.date_echeance = past_date
        self.assertTrue(self.ticket.est_en_retard)
        
        # Ticket fermé avec échéance passée
        self.ticket.statut = 'ferme'
        self.assertFalse(self.ticket.est_en_retard)
    
    def test_temps_ouvert_property(self):
        """Test de la propriété temps_ouvert"""
        temps_ouvert = self.ticket.temps_ouvert
        self.assertIsNotNone(temps_ouvert)
        self.assertTrue(temps_ouvert.total_seconds() >= 0)


class CommentaireTicketModelTest(TestCase):
    """Tests pour le modèle CommentaireTicket"""
    
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
        
        self.ticket = Ticket.objects.create(
            titre='Test Ticket',
            description='Description test',
            demandeur=self.user
        )
        
        self.commentaire = CommentaireTicket.objects.create(
            ticket=self.ticket,
            auteur=self.user,
            contenu='Commentaire de test',
            type_commentaire='commentaire'
        )
    
    def test_commentaire_creation(self):
        """Test de création d'un commentaire"""
        self.assertEqual(self.commentaire.ticket, self.ticket)
        self.assertEqual(self.commentaire.auteur, self.user)
        self.assertEqual(self.commentaire.contenu, 'Commentaire de test')
        self.assertFalse(self.commentaire.prive)
    
    def test_commentaire_str(self):
        """Test de la représentation string"""
        expected = f"{self.ticket.numero} - {self.user.nom_complet} - {self.commentaire.date_creation}"
        self.assertEqual(str(self.commentaire), expected)


class SLAModelTest(TestCase):
    """Tests pour le modèle SLA"""
    
    def setUp(self):
        self.sla = SLA.objects.create(
            nom='SLA Standard',
            description='Accord standard',
            temps_reponse_critique=1,
            temps_reponse_normale=24,
            temps_resolution_critique=4,
            temps_resolution_normale=48
        )
    
    def test_sla_creation(self):
        """Test de création d'un SLA"""
        self.assertEqual(self.sla.nom, 'SLA Standard')
        self.assertEqual(self.sla.temps_reponse_critique, 1)
        self.assertTrue(self.sla.actif)
    
    def test_get_temps_reponse(self):
        """Test de la méthode get_temps_reponse"""
        self.assertEqual(self.sla.get_temps_reponse('critique'), 1)
        self.assertEqual(self.sla.get_temps_reponse('normale'), 24)
        self.assertEqual(self.sla.get_temps_reponse('inexistant'), 24)  # Valeur par défaut
    
    def test_get_temps_resolution(self):
        """Test de la méthode get_temps_resolution"""
        self.assertEqual(self.sla.get_temps_resolution('critique'), 4)
        self.assertEqual(self.sla.get_temps_resolution('normale'), 48)
        self.assertEqual(self.sla.get_temps_resolution('inexistant'), 48)  # Valeur par défaut