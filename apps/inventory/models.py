"""
Modèles pour la gestion de l'inventaire
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
import uuid

User = get_user_model()


class CategorieEquipement(models.Model):
    """Catégories d'équipements"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Catégorie d'équipement"
        verbose_name_plural = "Catégories d'équipements"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Equipement(models.Model):
    """Équipements de l'inventaire"""
    
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('utilise', 'Utilisé'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
        ('retire', 'Retiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(CategorieEquipement, on_delete=models.SET_NULL, null=True)
    
    # Identification
    numero_serie = models.CharField(max_length=100, unique=True, blank=True)
    numero_inventaire = models.CharField(max_length=50, unique=True)
    code_barre = models.CharField(max_length=100, blank=True)
    
    # Informations techniques
    marque = models.CharField(max_length=100, blank=True)
    modele = models.CharField(max_length=100, blank=True)
    
    # Statut et localisation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    site = models.ForeignKey('users.Site', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Informations financières
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_achat = models.DateField(null=True, blank=True)
    fournisseur = models.CharField(max_length=200, blank=True)
    
    # Garantie
    date_fin_garantie = models.DateField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.numero_inventaire})"
    
    def get_autorisations_logiciels_utilisateur(self):
        """Récupère toutes les autorisations de logiciels pour l'utilisateur de cet équipement"""
        if not self.utilisateur:
            return []
        
        from apps.machines.models import AutorisationLogiciel
        
        # Récupérer les autorisations directes de l'utilisateur
        autorisations = AutorisationLogiciel.objects.filter(
            Q(utilisateur=self.utilisateur) |
            Q(groupe=self.utilisateur.groupe) |
            Q(structure=self.utilisateur.structure) |
            Q(site=self.utilisateur.site),
            statut='autorise'
        ).select_related('logiciel', 'logiciel__categorie')
        
        # Filtrer les autorisations valides
        autorisations_valides = [auth for auth in autorisations if auth.is_valide()]
        
        return autorisations_valides
    
    def get_logiciels_autorises(self):
        """Récupère la liste des logiciels autorisés pour l'utilisateur de cet équipement"""
        autorisations = self.get_autorisations_logiciels_utilisateur()
        return [auth.logiciel for auth in autorisations]
    
    def get_logiciels_installes_autorises(self):
        """Récupère les logiciels installés et autorisés sur les machines de l'utilisateur"""
        if not self.utilisateur:
            return []
        
        from apps.machines.models import LogicielInstalle
        
        # Récupérer tous les logiciels installés sur les machines de l'utilisateur
        logiciels_installes = LogicielInstalle.objects.filter(
            machine__utilisateur=self.utilisateur,
            autorise=True,
            bloque=False
        ).select_related('machine', 'logiciel_reference', 'logiciel_reference__categorie')
        
        return logiciels_installes
    
    def get_resume_autorisations(self):
        """Récupère un résumé des autorisations de logiciels pour l'utilisateur"""
        if not self.utilisateur:
            return {
                'total_autorisations': 0,
                'logiciels_autorises': 0,
                'logiciels_installes': 0,
                'categories': {}
            }
        
        autorisations = self.get_autorisations_logiciels_utilisateur()
        logiciels_installes = self.get_logiciels_installes_autorises()
        
        # Compter par catégorie
        categories = {}
        for auth in autorisations:
            if auth.logiciel.categorie:
                cat_nom = auth.logiciel.categorie.nom
                if cat_nom not in categories:
                    categories[cat_nom] = {'autorises': 0, 'installes': 0}
                categories[cat_nom]['autorises'] += 1
        
        for logiciel in logiciels_installes:
            if logiciel.logiciel_reference and logiciel.logiciel_reference.categorie:
                cat_nom = logiciel.logiciel_reference.categorie.nom
                if cat_nom not in categories:
                    categories[cat_nom] = {'autorises': 0, 'installes': 0}
                categories[cat_nom]['installes'] += 1
        
        return {
            'total_autorisations': len(autorisations),
            'logiciels_autorises': len(set(auth.logiciel.id for auth in autorisations)),
            'logiciels_installes': len(logiciels_installes),
            'categories': categories
        }


class AutorisationInventaire(models.Model):
    """Modèle pour lier les autorisations de logiciels à l'inventaire"""
    
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE, related_name='autorisations_logiciels')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Référence vers l'autorisation de logiciel
    autorisation_logiciel = models.ForeignKey(
        'machines.AutorisationLogiciel', 
        on_delete=models.CASCADE,
        related_name='equipements_inventaire'
    )
    
    # Métadonnées
    date_attribution = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Autorisation inventaire"
        verbose_name_plural = "Autorisations inventaire"
        unique_together = ['equipement', 'autorisation_logiciel']
        ordering = ['-date_attribution']
    
    def __str__(self):
        return f"{self.equipement.nom} - {self.autorisation_logiciel.logiciel.nom}"
    
    @property
    def est_valide(self):
        """Vérifie si l'autorisation est encore valide"""
        return self.actif and self.autorisation_logiciel.is_valide()
    
    @classmethod
    def synchroniser_avec_logiciels_installes(cls, utilisateur=None, equipement=None):
        """
        Synchronise les autorisations d'inventaire avec les logiciels réellement installés
        """
        from apps.machines.models import LogicielInstalle, AutorisationLogiciel
        
        # Filtrer par utilisateur ou équipement si spécifié
        if utilisateur:
            equipements = Equipement.objects.filter(utilisateur=utilisateur)
        elif equipement:
            equipements = [equipement]
        else:
            equipements = Equipement.objects.filter(utilisateur__isnull=False)
        
        autorisations_creees = 0
        
        for equip in equipements:
            if not equip.utilisateur:
                continue
                
            # Récupérer tous les logiciels installés autorisés pour cet utilisateur
            logiciels_installes = LogicielInstalle.objects.filter(
                machine__utilisateur=equip.utilisateur,
                autorise=True,
                bloque=False,
                logiciel_reference__isnull=False
            ).select_related('logiciel_reference')
            
            for logiciel_installe in logiciels_installes:
                # Chercher une autorisation correspondante
                autorisations = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel_installe.logiciel_reference,
                    statut='autorise'
                ).filter(
                    Q(utilisateur=equip.utilisateur) |
                    Q(groupe=equip.utilisateur.groupe) |
                    Q(structure=equip.utilisateur.structure) |
                    Q(site=equip.utilisateur.site)
                )
                
                # Prendre la première autorisation valide
                autorisation_valide = None
                for auth in autorisations:
                    if auth.is_valide():
                        autorisation_valide = auth
                        break
                
                if autorisation_valide:
                    # Créer ou mettre à jour l'autorisation d'inventaire
                    autorisation_inventaire, created = cls.objects.get_or_create(
                        equipement=equip,
                        autorisation_logiciel=autorisation_valide,
                        defaults={
                            'utilisateur': equip.utilisateur,
                            'actif': True
                        }
                    )
                    
                    if created:
                        autorisations_creees += 1
                    elif not autorisation_inventaire.actif:
                        autorisation_inventaire.actif = True
                        autorisation_inventaire.save()
        
        return autorisations_creees


# Ajoutez d'autres modèles selon vos besoins