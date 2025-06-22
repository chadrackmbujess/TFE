"""
Modèles pour le monitoring et la supervision
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class StatusMachine(models.Model):
    """Statut de monitoring des machines"""
    
    STATUT_CHOICES = [
        ('online', 'En ligne'),
        ('offline', 'Hors ligne'),
        ('warning', 'Avertissement'),
        ('critical', 'Critique'),
        ('unknown', 'Inconnu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.OneToOneField('machines.Machine', on_delete=models.CASCADE, related_name='status_monitoring')
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='unknown')
    derniere_verification = models.DateTimeField(auto_now=True)
    temps_reponse = models.FloatField(null=True, blank=True, help_text="Temps de réponse en ms")
    
    # Métriques système
    cpu_usage = models.FloatField(null=True, blank=True, help_text="Utilisation CPU en %")
    ram_usage = models.FloatField(null=True, blank=True, help_text="Utilisation RAM en %")
    disk_usage = models.FloatField(null=True, blank=True, help_text="Utilisation disque en %")
    
    # Réseau
    ping_success = models.BooleanField(default=False)
    last_ping_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Statut de machine"
        verbose_name_plural = "Statuts de machines"
        ordering = ['-derniere_verification']
    
    def __str__(self):
        return f"{self.machine.nom} - {self.get_statut_display()}"


class AlerteSysteme(models.Model):
    """Alertes système"""
    
    NIVEAU_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('critical', 'Critique'),
    ]
    
    TYPE_CHOICES = [
        ('system', 'Système'),
        ('network', 'Réseau'),
        ('security', 'Sécurité'),
        ('performance', 'Performance'),
        ('disk', 'Disque'),
        ('memory', 'Mémoire'),
        ('cpu', 'Processeur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    type_alerte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Relations
    machine = models.ForeignKey('machines.Machine', on_delete=models.CASCADE, related_name='alertes')
    
    # Statut
    resolu = models.BooleanField(default=False)
    resolu_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertes_resolues')
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Données techniques
    valeur_seuil = models.FloatField(null=True, blank=True)
    valeur_actuelle = models.FloatField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Alerte système"
        verbose_name_plural = "Alertes système"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.machine.nom} ({self.get_niveau_display()})"


class MetriquePerformance(models.Model):
    """Métriques de performance des machines"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey('machines.Machine', on_delete=models.CASCADE, related_name='metriques')
    
    # Métriques CPU
    cpu_percent = models.FloatField(help_text="Utilisation CPU en %")
    cpu_count = models.IntegerField(help_text="Nombre de cœurs CPU")
    
    # Métriques mémoire
    memory_total = models.BigIntegerField(help_text="Mémoire totale en bytes")
    memory_used = models.BigIntegerField(help_text="Mémoire utilisée en bytes")
    memory_percent = models.FloatField(help_text="Utilisation mémoire en %")
    
    # Métriques disque
    disk_total = models.BigIntegerField(help_text="Espace disque total en bytes")
    disk_used = models.BigIntegerField(help_text="Espace disque utilisé en bytes")
    disk_percent = models.FloatField(help_text="Utilisation disque en %")
    
    # Métriques réseau
    network_bytes_sent = models.BigIntegerField(default=0)
    network_bytes_recv = models.BigIntegerField(default=0)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Métrique de performance"
        verbose_name_plural = "Métriques de performance"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['machine', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.machine.nom} - {self.timestamp}"


class SeuillAlerte(models.Model):
    """Configuration des seuils d'alerte"""
    
    METRIQUE_CHOICES = [
        ('cpu', 'CPU'),
        ('memory', 'Mémoire'),
        ('disk', 'Disque'),
        ('network', 'Réseau'),
        ('ping', 'Ping'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    metrique = models.CharField(max_length=20, choices=METRIQUE_CHOICES)
    
    # Seuils
    seuil_warning = models.FloatField(help_text="Seuil d'avertissement")
    seuil_critical = models.FloatField(help_text="Seuil critique")
    
    # Configuration
    actif = models.BooleanField(default=True)
    structure = models.ForeignKey('users.Structure', on_delete=models.CASCADE, related_name='seuils_alerte')
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Seuil d'alerte"
        verbose_name_plural = "Seuils d'alerte"
        unique_together = ['metrique', 'structure']
        ordering = ['metrique']
    
    def __str__(self):
        return f"{self.nom} - {self.get_metrique_display()}"


class RapportMonitoring(models.Model):
    """Rapports de monitoring"""
    
    TYPE_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    nom = models.CharField(max_length=100)
    type_rapport = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Période couverte
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    
    # Statistiques
    machines_monitored = models.IntegerField(default=0)
    alertes_generees = models.IntegerField(default=0)
    temps_indisponibilite = models.DurationField(null=True, blank=True)
    
    # Fichier de rapport
    fichier_rapport = models.FileField(upload_to='monitoring/reports/%Y/%m/', null=True, blank=True)
    
    # Métadonnées
    genere_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rapport de monitoring"
        verbose_name_plural = "Rapports de monitoring"
        ordering = ['-date_generation']
    
    def __str__(self):
        return f"{self.nom} - {self.date_debut.strftime('%Y-%m-%d')}"