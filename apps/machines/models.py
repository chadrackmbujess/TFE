"""
Modèles pour la gestion des machines et informations système
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()


class TypeMachine(models.Model):
    """Types de machines (Desktop, Laptop, Serveur, etc.)"""
    nom = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône pour l'interface")
    
    class Meta:
        verbose_name = "Type de machine"
        verbose_name_plural = "Types de machines"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Machine(models.Model):
    """Modèle principal pour les machines"""
    
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('maintenance', 'En maintenance'),
        ('hors_service', 'Hors service'),
        ('retire', 'Retiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    nom = models.CharField(max_length=100, help_text="Nom de la machine")
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    numero_inventaire = models.CharField(max_length=50, unique=True, blank=True, null=True)
    type_machine = models.ForeignKey(TypeMachine, on_delete=models.SET_NULL, null=True)
    
    # Relations
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='machines')
    structure = models.ForeignKey('users.Structure', on_delete=models.CASCADE, 
                                related_name='machines')
    site = models.ForeignKey('users.Site', on_delete=models.SET_NULL, null=True, blank=True,
                           related_name='machines')
    
    # Statut et dates
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    date_achat = models.DateField(null=True, blank=True)
    date_mise_service = models.DateField(null=True, blank=True)
    date_fin_garantie = models.DateField(null=True, blank=True)
    
    # Informations techniques de base
    marque = models.CharField(max_length=50, blank=True)
    modele = models.CharField(max_length=100, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    derniere_synchronisation = models.DateTimeField(null=True, blank=True)
    
    # Commentaires
    commentaires = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_statut_display()})"
    
    @property
    def est_en_ligne(self):
        """Vérifie si la machine est en ligne (basé sur la dernière synchronisation)"""
        if not self.derniere_synchronisation:
            return False
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() - self.derniere_synchronisation < timedelta(minutes=10)


class InformationSysteme(models.Model):
    """Informations système détaillées de la machine"""
    machine = models.OneToOneField(Machine, on_delete=models.CASCADE, related_name='info_systeme')
    
    # Système d'exploitation
    os_nom = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=100, blank=True)
    os_architecture = models.CharField(max_length=20, blank=True)
    os_build = models.CharField(max_length=50, blank=True)
    
    # Processeur
    cpu_nom = models.CharField(max_length=200, blank=True)
    cpu_architecture = models.CharField(max_length=20, blank=True)
    cpu_coeurs = models.IntegerField(null=True, blank=True)
    cpu_threads = models.IntegerField(null=True, blank=True)
    cpu_frequence = models.FloatField(null=True, blank=True, help_text="Fréquence en GHz")
    
    # Mémoire
    ram_totale = models.BigIntegerField(null=True, blank=True, help_text="RAM totale en bytes")
    ram_disponible = models.BigIntegerField(null=True, blank=True, help_text="RAM disponible en bytes")
    
    # Stockage
    stockage_total = models.BigIntegerField(null=True, blank=True, help_text="Stockage total en bytes")
    stockage_libre = models.BigIntegerField(null=True, blank=True, help_text="Stockage libre en bytes")
    
    # Réseau
    nom_machine = models.CharField(max_length=100, blank=True)
    domaine = models.CharField(max_length=100, blank=True)
    
    # Métadonnées
    date_collecte = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Information système"
        verbose_name_plural = "Informations système"
    
    def __str__(self):
        return f"Infos système - {self.machine.nom}"
    
    @property
    def ram_totale_gb(self):
        """RAM totale en GB"""
        if self.ram_totale:
            return round(self.ram_totale / (1024**3), 2)
        return None
    
    @property
    def stockage_total_gb(self):
        """Stockage total en GB"""
        if self.stockage_total:
            return round(self.stockage_total / (1024**3), 2)
        return None


class InterfaceReseau(models.Model):
    """Interfaces réseau de la machine"""
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='interfaces_reseau')
    
    nom = models.CharField(max_length=100)
    type_interface = models.CharField(max_length=50, choices=[
        ('ethernet', 'Ethernet'),
        ('wifi', 'Wi-Fi'),
        ('bluetooth', 'Bluetooth'),
        ('vpn', 'VPN'),
        ('autre', 'Autre'),
    ])
    adresse_mac = models.CharField(max_length=17, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    masque_reseau = models.GenericIPAddressField(null=True, blank=True)
    passerelle = models.GenericIPAddressField(null=True, blank=True)
    dns_primaire = models.GenericIPAddressField(null=True, blank=True)
    dns_secondaire = models.GenericIPAddressField(null=True, blank=True)
    
    actif = models.BooleanField(default=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Interface réseau"
        verbose_name_plural = "Interfaces réseau"
        unique_together = ['machine', 'nom']
    
    def __str__(self):
        return f"{self.machine.nom} - {self.nom} ({self.adresse_ip})"

class CategorieLogiciel(models.Model):
    """Catégories de logiciels pour l'organisation"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=7, default='#007bff', help_text="Couleur hexadécimale pour l'affichage")
    icone = models.CharField(max_length=50, blank=True)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Catégorie de logiciel"
        verbose_name_plural = "Catégories de logiciels"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class LogicielReference(models.Model):
    """Base de données des logiciels de référence pour l'autorisation"""
    
    NIVEAU_SECURITE_CHOICES = [
        ('libre', 'Libre - Aucune restriction'),
        ('controle', 'Contrôlé - Autorisation requise'),
        ('restreint', 'Restreint - Utilisateurs spécifiques'),
        ('interdit', 'Interdit - Bloqué par défaut'),
    ]
    
    nom = models.CharField(max_length=200, unique=True)
    editeur = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(CategorieLogiciel, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Niveau de sécurité et autorisation
    niveau_securite = models.CharField(max_length=20, choices=NIVEAU_SECURITE_CHOICES, default='libre')
    
    # Informations techniques
    versions_autorisees = models.TextField(blank=True, help_text="Versions autorisées (une par ligne)")
    versions_interdites = models.TextField(blank=True, help_text="Versions interdites (une par ligne)")
    
    # Gestion des licences
    licence_requise = models.BooleanField(default=False)
    type_licence = models.CharField(max_length=100, blank=True)
    cout_licence = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Métadonnées
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logiciel de référence"
        verbose_name_plural = "Logiciels de référence"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_niveau_securite_display()})"
    
    @classmethod
    def synchroniser_depuis_logiciels_installes(cls):
        """
        Synchronise les logiciels de référence avec tous les logiciels installés détectés
        Crée automatiquement les logiciels de référence manquants
        """
        # Utiliser django.apps pour éviter les problèmes d'importation circulaire
        from django.apps import apps
        LogicielInstalle = apps.get_model('machines', 'LogicielInstalle')
        
        logiciels_crees = 0
        logiciels_mis_a_jour = 0
        
        # Récupérer tous les logiciels installés uniques (nom + éditeur)
        logiciels_installes = LogicielInstalle.objects.values(
            'nom', 'editeur'
        ).distinct().order_by('nom')
        
        for logiciel_data in logiciels_installes:
            nom = logiciel_data['nom']
            editeur = logiciel_data['editeur'] or ''
            
            if not nom:  # Ignorer les logiciels sans nom
                continue
            
            # Vérifier si le logiciel de référence existe déjà
            logiciel_ref, created = cls.objects.get_or_create(
                nom=nom,
                defaults={
                    'editeur': editeur,
                    'niveau_securite': 'libre',  # Par défaut, autoriser sans restriction
                    'description': f'Logiciel détecté automatiquement depuis les machines',
                    'actif': True
                }
            )
            
            if created:
                logiciels_crees += 1
            else:
                # Mettre à jour l'éditeur si il était vide
                if not logiciel_ref.editeur and editeur:
                    logiciel_ref.editeur = editeur
                    logiciel_ref.save()
                    logiciels_mis_a_jour += 1
        
        return {
            'crees': logiciels_crees,
            'mis_a_jour': logiciels_mis_a_jour,
            'total_traites': len(logiciels_installes)
        }
    
    @classmethod
    def synchroniser_logiciel_specifique(cls, nom_logiciel, editeur=None):
        """
        Synchronise un logiciel spécifique depuis les logiciels installés
        """
        if not nom_logiciel:
            return None
        
        # Chercher des informations complémentaires depuis les logiciels installés
        from django.apps import apps
        LogicielInstalle = apps.get_model('machines', 'LogicielInstalle')
        logiciel_installe = LogicielInstalle.objects.filter(nom=nom_logiciel).first()
        
        if not logiciel_installe:
            return None
        
        logiciel_ref, created = cls.objects.get_or_create(
            nom=nom_logiciel,
            defaults={
                'editeur': editeur or logiciel_installe.editeur or '',
                'niveau_securite': 'libre',
                'description': f'Logiciel synchronisé depuis {logiciel_installe.machine.nom}',
                'actif': True
            }
        )
        
        return logiciel_ref


class AutorisationLogiciel(models.Model):
    """Autorisations spécifiques pour les logiciels par utilisateur/groupe/structure"""
    
    TYPE_AUTORISATION_CHOICES = [
        ('utilisateur', 'Utilisateur spécifique'),
        ('groupe', 'Groupe d\'utilisateurs'),
        ('structure', 'Structure complète'),
        ('site', 'Site spécifique'),
    ]
    
    STATUT_CHOICES = [
        ('autorise', 'Autorisé'),
        ('refuse', 'Refusé'),
        ('en_attente', 'En attente'),
        ('expire', 'Expiré'),
    ]
    
    logiciel = models.ForeignKey(LogicielReference, on_delete=models.CASCADE, related_name='autorisations')
    
    # Type d'autorisation
    type_autorisation = models.CharField(max_length=20, choices=TYPE_AUTORISATION_CHOICES)
    
    # Relations (une seule sera remplie selon le type)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='autorisations_logiciels')
    groupe = models.ForeignKey('users.Groupe', on_delete=models.CASCADE, null=True, blank=True, related_name='autorisations_logiciels')
    structure = models.ForeignKey('users.Structure', on_delete=models.CASCADE, null=True, blank=True, related_name='autorisations_logiciels')
    site = models.ForeignKey('users.Site', on_delete=models.CASCADE, null=True, blank=True, related_name='autorisations_logiciels')
    
    # Statut et validité
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='autorise')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True, help_text="Laisser vide pour une autorisation permanente")
    
    # Versions spécifiques autorisées
    versions_autorisees = models.TextField(blank=True, help_text="Versions spécifiquement autorisées (une par ligne)")
    
    # Gestion administrative
    autorise_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='autorisations_accordees')
    motif = models.TextField(blank=True, help_text="Motif de l'autorisation ou du refus")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Autorisation logiciel"
        verbose_name_plural = "Autorisations logiciels"
        ordering = ['-date_creation']
        # Éviter les doublons
        unique_together = [
            ['logiciel', 'utilisateur'],
            ['logiciel', 'groupe'],
            ['logiciel', 'structure'],
            ['logiciel', 'site'],
        ]
    
    def __str__(self):
        target = self.utilisateur or self.groupe or self.structure or self.site
        return f"{self.logiciel.nom} - {target} ({self.get_statut_display()})"
    
    def is_valide(self):
        """Vérifie si l'autorisation est encore valide"""
        if self.statut != 'autorise':
            return False
        if self.date_fin:
            from django.utils import timezone
            return timezone.now() <= self.date_fin
        return True


class DemandeAutorisation(models.Model):
    """Demandes d'autorisation de logiciels par les utilisateurs"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    ]
    
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    # Informations de base
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demandes_logiciels')
    logiciel_nom = models.CharField(max_length=200, help_text="Nom du logiciel demandé")
    logiciel_version = models.CharField(max_length=100, blank=True)
    logiciel_editeur = models.CharField(max_length=100, blank=True)
    
    # Lien vers le logiciel de référence s'il existe
    logiciel_reference = models.ForeignKey(LogicielReference, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Machine cible
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='demandes_logiciels')
    
    # Justification
    justification = models.TextField(help_text="Justification métier pour cette demande")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='normale')
    
    # Statut et traitement
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    traite_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='demandes_traitees')
    date_traitement = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Demande d'autorisation"
        verbose_name_plural = "Demandes d'autorisations"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.logiciel_nom} - {self.utilisateur.nom_complet} ({self.get_statut_display()})"


class LogicielInstalle(models.Model):
    """Logiciels installés sur la machine"""
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='logiciels')
    
    nom = models.CharField(max_length=200)
    version = models.CharField(max_length=100, blank=True)
    editeur = models.CharField(max_length=100, blank=True)
    date_installation = models.DateTimeField(null=True, blank=True)
    taille = models.BigIntegerField(null=True, blank=True, help_text="Taille en bytes")
    
    # Lien vers le logiciel de référence
    logiciel_reference = models.ForeignKey(LogicielReference, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Gestion des licences
    licence_requise = models.BooleanField(default=False)
    licence_valide = models.BooleanField(default=True)
    
    # Statut d'autorisation (calculé automatiquement)
    autorise = models.BooleanField(default=True)
    bloque = models.BooleanField(default=False)
    motif_blocage = models.TextField(blank=True)
    
    date_detection = models.DateTimeField(auto_now_add=True)
    date_derniere_maj = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Logiciel installé"
        verbose_name_plural = "Logiciels installés"
        unique_together = ['machine', 'nom', 'version']
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} {self.version} - {self.machine.nom}"
    
    def verifier_autorisation(self):
        """Vérifie et met à jour le statut d'autorisation du logiciel"""
        # Par défaut, tous les logiciels sont autorisés
        ancien_autorise = self.autorise
        ancien_bloque = self.bloque
        ancien_motif = self.motif_blocage

        self.autorise = True
        self.bloque = False
        self.motif_blocage = ""
        
        if not self.logiciel_reference:
            # Logiciel non référencé, chercher par nom
            try:
                self.logiciel_reference = LogicielReference.objects.get(nom__iexact=self.nom)
            except LogicielReference.DoesNotExist:
                # Logiciel non référencé, autoriser par défaut
                # Sauvegarder seulement si il y a eu des changements
                if (ancien_autorise != self.autorise or
                    ancien_bloque != self.bloque or
                    ancien_motif != self.motif_blocage):
                    self.save(update_fields=['autorise', 'bloque', 'motif_blocage'])
                return
        
        logiciel_ref = self.logiciel_reference
        utilisateur = self.machine.utilisateur
        
        # Seuls les logiciels explicitement interdits sont bloqués
        if logiciel_ref.niveau_securite == 'interdit':
            self.autorise = False
            self.bloque = True
            self.motif_blocage = "Logiciel interdit par la politique de sécurité"
        else:
            # Vérifier s'il y a des autorisations explicitement refusées QUI CONCERNENT CET UTILISATEUR
            autorisations_refusees = AutorisationLogiciel.objects.filter(
                logiciel=logiciel_ref,
                statut='refuse'
            )
            
            # Vérifier chaque autorisation refusée pour voir si elle concerne cet utilisateur
            autorisation_applicable = None
            for autorisation in autorisations_refusees:
                if autorisation.utilisateur == utilisateur:
                    # Blocage spécifique à cet utilisateur
                    autorisation_applicable = autorisation
                    break
                elif autorisation.groupe and utilisateur.groupe == autorisation.groupe:
                    # Blocage pour le groupe de cet utilisateur
                    autorisation_applicable = autorisation
                    break
                elif autorisation.structure and utilisateur.structure == autorisation.structure:
                    # Blocage pour la structure de cet utilisateur
                    autorisation_applicable = autorisation
                    break
                elif autorisation.site and utilisateur.site == autorisation.site:
                    # Blocage pour le site de cet utilisateur
                    autorisation_applicable = autorisation
                    break
            
            # Si une autorisation refusée concerne cet utilisateur, bloquer
            if autorisation_applicable:
                self.autorise = False
                self.bloque = True
                self.motif_blocage = autorisation_applicable.motif or f"Autorisation refusée par l'administrateur"
            # Sinon, l'utilisateur n'est pas concerné par les blocages, rester autorisé
        
        # Sauvegarder seulement si il y a eu des changements pour éviter les boucles infinies
        if (ancien_autorise != self.autorise or
            ancien_bloque != self.bloque or
            ancien_motif != self.motif_blocage):
            self.save(update_fields=['autorise', 'bloque', 'motif_blocage'])

    def get_logiciels_bloques_pour_machine(self):
        """Retourne la liste des logiciels bloqués pour cette machine"""
        return self.logiciels.filter(bloque=True).values_list('nom', 'version')


class HistoriqueMachine(models.Model):
    """Historique des modifications de la machine"""
    
    TYPE_MODIFICATION_CHOICES = [
        ('creation', 'Création'),
        ('modification', 'Modification'),
        ('changement_utilisateur', 'Changement d\'utilisateur'),
        ('changement_statut', 'Changement de statut'),
        ('maintenance', 'Maintenance'),
        ('synchronisation', 'Synchronisation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='historique')
    
    type_modification = models.CharField(max_length=30, choices=TYPE_MODIFICATION_CHOICES)
    description = models.TextField()
    
    # Utilisateur qui a effectué la modification
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Données avant/après (JSON)
    donnees_avant = models.JSONField(null=True, blank=True)
    donnees_apres = models.JSONField(null=True, blank=True)
    
    date_modification = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historique machine"
        verbose_name_plural = "Historiques machines"
        ordering = ['-date_modification']
    
    def __str__(self):
        return f"{self.machine.nom} - {self.get_type_modification_display()} - {self.date_modification}"