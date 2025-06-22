"""
Modèles pour la gestion des utilisateurs et des structures
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import uuid


class Structure(models.Model):
    """Modèle pour les structures/entreprises"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Code court pour l'entreprise (ex: jessmi)")
    adresse = models.TextField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    site_web = models.URLField(blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Structure"
        verbose_name_plural = "Structures"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Groupe(models.Model):
    """Modèle pour les groupes d'utilisateurs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='groupes')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Groupe"
        verbose_name_plural = "Groupes"
        unique_together = ['nom', 'structure']
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.structure.nom})"


class Site(models.Model):
    """Modèle pour les sites/localisations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='sites')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        unique_together = ['nom', 'structure']
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.structure.nom})"


class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('technicien', 'Technicien'),
        ('utilisateur', 'Utilisateur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations personnelles
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, blank=True)
    poste = models.CharField(max_length=100, blank=True)
    
    # Relations organisationnelles
    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='utilisateurs')
    groupe = models.ForeignKey(Groupe, on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='utilisateurs')
    
    # Rôle et permissions
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='utilisateur')
    
    # Statut et dates
    actif = models.BooleanField(default=True)
    derniere_connexion_app = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Préférences
    notifications_email = models.BooleanField(default=True)
    langue = models.CharField(max_length=5, default='fr', choices=[('fr', 'Français'), ('en', 'English')])

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['nom', 'prenom']

    def save(self, *args, **kwargs):
        """Génère automatiquement le username au format @prenom.nom.entreprise"""
        if not self.username and self.prenom and self.nom and self.structure:
            self.username = f"@{self.prenom.lower()}.{self.nom.lower()}.{self.structure.code.lower()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_role_display()})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def is_admin(self):
        return self.role == 'admin'

    def is_technicien(self):
        return self.role in ['admin', 'technicien']


class JournalConnexion(models.Model):
    """Journal des connexions utilisateurs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connexions')
    adresse_ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    date_connexion = models.DateTimeField(auto_now_add=True)
    date_deconnexion = models.DateTimeField(null=True, blank=True)
    duree_session = models.DurationField(null=True, blank=True)
    type_connexion = models.CharField(max_length=20, choices=[
        ('desktop', 'Application Desktop'),
        ('web', 'Interface Web'),
        ('mobile', 'Application Mobile'),
        ('api', 'API'),
    ], default='desktop')
    succes = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Journal de connexion"
        verbose_name_plural = "Journaux de connexions"
        ordering = ['-date_connexion']

    def __str__(self):
        return f"{self.utilisateur.nom_complet} - {self.date_connexion}"