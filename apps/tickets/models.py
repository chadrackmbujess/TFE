"""
Modèles pour la gestion des tickets (incidents et demandes)
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid

User = get_user_model()


class CategorieTicket(models.Model):
    """Catégories de tickets"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#007bff', help_text="Couleur hexadécimale")
    icone = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)
    
    # Paramètres de traitement
    sla_heures = models.IntegerField(default=24, help_text="SLA en heures")
    assignation_auto = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Catégorie de ticket"
        verbose_name_plural = "Catégories de tickets"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Ticket(models.Model):
    """Modèle principal pour les tickets"""
    
    TYPE_CHOICES = [
        ('incident', 'Incident'),
        ('demande', 'Demande'),
        ('probleme', 'Problème'),
        ('changement', 'Changement'),
    ]
    
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('critique', 'Critique'),
        ('urgente', 'Urgente'),
    ]
    
    STATUT_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('assigne', 'Assigné'),
        ('en_cours', 'En cours'),
        ('en_attente', 'En attente'),
        ('resolu', 'Résolu'),
        ('ferme', 'Fermé'),
        ('rejete', 'Rejeté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=20, unique=True, editable=False)
    
    # Informations de base
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_ticket = models.CharField(max_length=20, choices=TYPE_CHOICES, default='incident')
    categorie = models.ForeignKey(CategorieTicket, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Priorité et statut
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    
    # Relations utilisateurs
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_demandes')
    assigne_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='tickets_assignes')
    
    # Relations avec les machines
    machine = models.ForeignKey('machines.Machine', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='tickets')
    
    # Dates importantes
    date_creation = models.DateTimeField(auto_now_add=True)
    date_assignation = models.DateTimeField(null=True, blank=True)
    date_premiere_reponse = models.DateTimeField(null=True, blank=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    date_echeance = models.DateTimeField(null=True, blank=True)
    
    # Temps de traitement
    temps_resolution = models.DurationField(null=True, blank=True)
    
    # Satisfaction
    note_satisfaction = models.IntegerField(null=True, blank=True, 
                                          help_text="Note de 1 à 5")
    commentaire_satisfaction = models.TextField(blank=True)
    
    # Métadonnées
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-date_creation']
    
    def save(self, *args, **kwargs):
        if not self.numero:
            # Générer un numéro de ticket unique
            from django.utils import timezone
            year = timezone.now().year
            count = Ticket.objects.filter(date_creation__year=year).count() + 1
            self.numero = f"T{year}{count:06d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero} - {self.titre}"
    
    @property
    def est_en_retard(self):
        """Vérifie si le ticket est en retard"""
        if self.date_echeance and self.statut not in ['ferme', 'resolu']:
            from django.utils import timezone
            return timezone.now() > self.date_echeance
        return False
    
    @property
    def temps_ouvert(self):
        """Temps depuis l'ouverture du ticket"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Si le ticket n'a pas encore de date de création, retourner 0
        if not self.date_creation:
            return timedelta(0)
            
        if self.statut in ['ferme', 'resolu'] and self.date_fermeture:
            return self.date_fermeture - self.date_creation
        return timezone.now() - self.date_creation


class CommentaireTicket(models.Model):
    """Commentaires et suivi des tickets"""
    
    TYPE_COMMENTAIRE_CHOICES = [
        ('commentaire', 'Commentaire'),
        ('solution', 'Solution'),
        ('escalade', 'Escalade'),
        ('fermeture', 'Fermeture'),
        ('reouverture', 'Réouverture'),
        ('assignation', 'Assignation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='commentaires')
    
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    type_commentaire = models.CharField(max_length=20, choices=TYPE_COMMENTAIRE_CHOICES, 
                                       default='commentaire')
    
    contenu = models.TextField()
    prive = models.BooleanField(default=False, help_text="Visible uniquement par les techniciens")
    
    # Temps passé (pour les techniciens)
    temps_passe = models.DurationField(null=True, blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Commentaire de ticket"
        verbose_name_plural = "Commentaires de tickets"
        ordering = ['date_creation']
    
    def __str__(self):
        return f"{self.ticket.numero} - {self.auteur.nom_complet} - {self.date_creation}"


class PieceJointeTicket(models.Model):
    """Pièces jointes des tickets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='pieces_jointes')
    commentaire = models.ForeignKey(CommentaireTicket, on_delete=models.CASCADE, 
                                   null=True, blank=True, related_name='pieces_jointes')
    
    nom_fichier = models.CharField(max_length=255)
    fichier = models.FileField(
        upload_to='tickets/attachments/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar'
        ])]
    )
    taille = models.BigIntegerField(help_text="Taille en bytes")
    type_mime = models.CharField(max_length=100)
    
    uploade_par = models.ForeignKey(User, on_delete=models.CASCADE)
    date_upload = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        ordering = ['date_upload']
    
    def __str__(self):
        return f"{self.nom_fichier} - {self.ticket.numero}"


class EscaladeTicket(models.Model):
    """Escalades de tickets"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='escalades')
    
    de_utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalades_envoyees')
    vers_utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='escalades_recues')
    
    motif = models.TextField()
    date_escalade = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Escalade de ticket"
        verbose_name_plural = "Escalades de tickets"
        ordering = ['-date_escalade']
    
    def __str__(self):
        return f"{self.ticket.numero} - Escalade vers {self.vers_utilisateur.nom_complet}"


class ModeleTicket(models.Model):
    """Modèles de tickets pour les demandes récurrentes"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    titre_defaut = models.CharField(max_length=200)
    contenu_defaut = models.TextField()
    categorie_defaut = models.ForeignKey(CategorieTicket, on_delete=models.SET_NULL, null=True)
    priorite_defaut = models.CharField(max_length=20, choices=Ticket.PRIORITE_CHOICES, 
                                      default='normale')
    
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Modèle de ticket"
        verbose_name_plural = "Modèles de tickets"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class SLA(models.Model):
    """Service Level Agreement - Accords de niveau de service"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    
    # Temps de réponse par priorité (en heures)
    temps_reponse_critique = models.IntegerField(default=1)
    temps_reponse_haute = models.IntegerField(default=4)
    temps_reponse_normale = models.IntegerField(default=24)
    temps_reponse_basse = models.IntegerField(default=72)
    
    # Temps de résolution par priorité (en heures)
    temps_resolution_critique = models.IntegerField(default=4)
    temps_resolution_haute = models.IntegerField(default=8)
    temps_resolution_normale = models.IntegerField(default=48)
    temps_resolution_basse = models.IntegerField(default=168)
    
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "SLA"
        verbose_name_plural = "SLAs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    def get_temps_reponse(self, priorite):
        """Retourne le temps de réponse selon la priorité"""
        mapping = {
            'critique': self.temps_reponse_critique,
            'urgente': self.temps_reponse_critique,
            'haute': self.temps_reponse_haute,
            'normale': self.temps_reponse_normale,
            'basse': self.temps_reponse_basse,
        }
        return mapping.get(priorite, self.temps_reponse_normale)
    
    def get_temps_resolution(self, priorite):
        """Retourne le temps de résolution selon la priorité"""
        mapping = {
            'critique': self.temps_resolution_critique,
            'urgente': self.temps_resolution_critique,
            'haute': self.temps_resolution_haute,
            'normale': self.temps_resolution_normale,
            'basse': self.temps_resolution_basse,
        }
        return mapping.get(priorite, self.temps_resolution_normale)


class NotificationTicket(models.Model):
    """Notifications pour les commentaires de tickets"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    commentaire = models.ForeignKey(CommentaireTicket, on_delete=models.CASCADE, related_name='notifications')
    
    # Utilisateur qui doit recevoir la notification
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_recues')
    
    # Statut de lecture
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification de ticket"
        verbose_name_plural = "Notifications de tickets"
        ordering = ['-date_creation']
        unique_together = ['commentaire', 'destinataire']  # Éviter les doublons
    
    def __str__(self):
        return f"Notification pour {self.destinataire.username} - Ticket {self.ticket.numero}"
    
    def marquer_comme_lu(self):
        """Marquer la notification comme lue"""
        if not self.lu:
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()


@receiver(post_save, sender=CommentaireTicket)
def creer_notification_commentaire(sender, instance, created, **kwargs):
    """Créer une notification quand un commentaire est ajouté - seulement pour les techniciens assignés"""
    if created and not instance.prive:
        # Créer une notification SEULEMENT pour le technicien assigné au ticket
        # (et seulement si ce n'est pas lui qui a commenté)
        if (instance.ticket.assigne_a and 
            instance.auteur != instance.ticket.assigne_a and
            instance.ticket.assigne_a.role == 'technicien'):
            NotificationTicket.objects.get_or_create(
                ticket=instance.ticket,
                commentaire=instance,
                destinataire=instance.ticket.assigne_a,
                defaults={'lu': False}
            )