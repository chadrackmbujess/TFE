"""
Configuration de l'interface d'administration pour l'application machines
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import (
    Machine, TypeMachine, InformationSysteme,
    InterfaceReseau, LogicielInstalle, HistoriqueMachine,
    CategorieLogiciel, LogicielReference, AutorisationLogiciel, DemandeAutorisation
)


@admin.register(TypeMachine)
class TypeMachineAdmin(admin.ModelAdmin):
    """Administration des types de machines"""
    list_display = ['nom', 'description', 'icone']
    search_fields = ['nom', 'description']
    ordering = ['nom']


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    """Administration des machines"""
    list_display = ['nom', 'numero_serie', 'type_machine', 'utilisateur', 'structure', 'statut', 'est_en_ligne']
    list_filter = ['statut', 'type_machine', 'structure', 'site']
    search_fields = ['nom', 'numero_serie', 'numero_inventaire', 'marque', 'modele']
    readonly_fields = ['id', 'date_creation', 'date_modification', 'derniere_synchronisation', 'est_en_ligne']
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'numero_serie', 'numero_inventaire', 'type_machine')
        }),
        ('Relations', {
            'fields': ('utilisateur', 'structure', 'site')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_achat', 'date_mise_service', 'date_fin_garantie')
        }),
        ('Informations techniques', {
            'fields': ('marque', 'modele')
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_creation', 'date_modification', 'derniere_synchronisation', 'est_en_ligne'),
            'classes': ('collapse',)
        }),
        ('Commentaires', {
            'fields': ('commentaires',)
        })
    )


@admin.register(InformationSysteme)
class InformationSystemeAdmin(admin.ModelAdmin):
    """Administration des informations système"""
    list_display = ['machine', 'os_nom', 'os_version', 'cpu_nom', 'ram_totale_gb', 'stockage_total_gb']
    list_filter = ['os_nom', 'os_architecture', 'cpu_architecture']
    search_fields = ['machine__nom', 'os_nom', 'cpu_nom']
    readonly_fields = ['ram_totale_gb', 'stockage_total_gb', 'date_collecte']
    fieldsets = (
        ('Machine', {
            'fields': ('machine',)
        }),
        ('Système d\'exploitation', {
            'fields': ('os_nom', 'os_version', 'os_architecture', 'os_build')
        }),
        ('Processeur', {
            'fields': ('cpu_nom', 'cpu_architecture', 'cpu_coeurs', 'cpu_threads', 'cpu_frequence')
        }),
        ('Mémoire', {
            'fields': ('ram_totale', 'ram_disponible', 'ram_totale_gb')
        }),
        ('Stockage', {
            'fields': ('stockage_total', 'stockage_libre', 'stockage_total_gb')
        }),
        ('Réseau', {
            'fields': ('nom_machine', 'domaine')
        }),
        ('Métadonnées', {
            'fields': ('date_collecte',),
            'classes': ('collapse',)
        })
    )


@admin.register(InterfaceReseau)
class InterfaceReseauAdmin(admin.ModelAdmin):
    """Administration des interfaces réseau"""
    list_display = ['machine', 'nom', 'type_interface', 'adresse_ip', 'adresse_mac', 'actif']
    list_filter = ['type_interface', 'actif']
    search_fields = ['machine__nom', 'nom', 'adresse_ip', 'adresse_mac']
    readonly_fields = ['date_derniere_maj']
    fieldsets = (
        ('Machine', {
            'fields': ('machine',)
        }),
        ('Interface', {
            'fields': ('nom', 'type_interface', 'adresse_mac', 'actif')
        }),
        ('Configuration réseau', {
            'fields': ('adresse_ip', 'masque_reseau', 'passerelle')
        }),
        ('DNS', {
            'fields': ('dns_primaire', 'dns_secondaire')
        }),
        ('Métadonnées', {
            'fields': ('date_derniere_maj',),
            'classes': ('collapse',)
        })
    )


@admin.register(CategorieLogiciel)
class CategorieLogicielAdmin(admin.ModelAdmin):
    """Administration des catégories de logiciels"""
    list_display = ['nom', 'description', 'couleur_display', 'icone', 'actif']
    list_filter = ['actif']
    search_fields = ['nom', 'description']
    ordering = ['nom']
    
    def couleur_display(self, obj):
        """Affiche la couleur avec un aperçu visuel"""
        return format_html(
            '<span style="background-color: {}; padding: 2px 8px; border-radius: 3px; color: white;">{}</span>',
            obj.couleur,
            obj.couleur
        )
    couleur_display.short_description = 'Couleur'


@admin.register(LogicielReference)
class LogicielReferenceAdmin(admin.ModelAdmin):
    """Administration des logiciels de référence"""
    list_display = ['nom', 'editeur', 'categorie', 'niveau_securite', 'licence_requise', 'actif']
    list_filter = ['niveau_securite', 'licence_requise', 'actif', 'categorie']
    search_fields = ['nom', 'editeur', 'description']
    readonly_fields = ['date_creation', 'date_modification']
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'editeur', 'description', 'categorie')
        }),
        ('Sécurité et autorisation', {
            'fields': ('niveau_securite', 'versions_autorisees', 'versions_interdites')
        }),
        ('Gestion des licences', {
            'fields': ('licence_requise', 'type_licence', 'cout_licence')
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('categorie')
    
    actions = ['synchroniser_depuis_desktop', 'bloquer_pour_tous_utilisateurs', 'bloquer_pour_toutes_structures', 'bloquer_pour_tous_sites', 'interdire_logiciels']
    
    def synchroniser_depuis_desktop(self, request, queryset):
        """Action pour synchroniser les logiciels de référence depuis les logiciels installés sur les machines"""
        from .models import LogicielReference
        
        resultats = LogicielReference.synchroniser_depuis_logiciels_installes()
        
        message = (
            f"Synchronisation terminée : "
            f"{resultats['crees']} logiciel(s) créé(s), "
            f"{resultats['mis_a_jour']} logiciel(s) mis à jour, "
            f"{resultats['total_traites']} logiciel(s) traité(s) au total."
        )
        
        self.message_user(request, message)
    synchroniser_depuis_desktop.short_description = "Synchroniser depuis les logiciels installés (Desktop)"
    
    def bloquer_pour_tous_utilisateurs(self, request, queryset):
        """Action pour bloquer les logiciels sélectionnés pour tous les utilisateurs"""
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        utilisateurs = User.objects.filter(is_active=True)
        
        created_count = 0
        for logiciel in queryset:
            for utilisateur in utilisateurs:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    utilisateur=utilisateur
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='utilisateur',
                        utilisateur=utilisateur,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) pour {queryset.count()} logiciel(s) et tous les utilisateurs.')
    bloquer_pour_tous_utilisateurs.short_description = "🚫 Bloquer pour TOUS les utilisateurs"
    
    def bloquer_pour_toutes_structures(self, request, queryset):
        """Action pour bloquer les logiciels sélectionnés pour toutes les structures"""
        from apps.users.models import Structure
        
        structures = Structure.objects.filter(active=True)
        
        created_count = 0
        for logiciel in queryset:
            for structure in structures:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    structure=structure
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='structure',
                        structure=structure,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) pour {queryset.count()} logiciel(s) et toutes les structures.')
    bloquer_pour_toutes_structures.short_description = "🏢 Bloquer pour TOUTES les structures"
    
    def bloquer_pour_tous_sites(self, request, queryset):
        """Action pour bloquer les logiciels sélectionnés pour tous les sites"""
        from apps.users.models import Site
        
        sites = Site.objects.filter(active=True)
        
        created_count = 0
        for logiciel in queryset:
            for site in sites:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    site=site
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='site',
                        site=site,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Logiciel {logiciel.nom} bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) pour {queryset.count()} logiciel(s) et tous les sites.')
    bloquer_pour_tous_sites.short_description = "🌍 Bloquer pour TOUS les sites"
    
    def interdire_logiciels(self, request, queryset):
        """Action pour marquer les logiciels comme interdits (niveau de sécurité)"""
        updated = queryset.update(niveau_securite='interdit')
        
        # Forcer la vérification des autorisations pour tous les logiciels installés correspondants
        from .models import LogicielInstalle
        logiciels_installes = LogicielInstalle.objects.filter(logiciel_reference__in=queryset)
        for logiciel_installe in logiciels_installes:
            logiciel_installe.verifier_autorisation()
        
        self.message_user(request, f'{updated} logiciel(s) marqué(s) comme INTERDIT. {logiciels_installes.count()} logiciel(s) installé(s) mis à jour.')
    interdire_logiciels.short_description = "⛔ Marquer comme INTERDIT (politique de sécurité)"


@admin.register(AutorisationLogiciel)
class AutorisationLogicielAdmin(admin.ModelAdmin):
    """Administration des autorisations de logiciels"""
    list_display = ['logiciel', 'type_autorisation', 'get_target', 'statut', 'get_logiciels_installes_count', 'autorise_par', 'date_creation']
    list_filter = ['type_autorisation', 'statut', 'date_creation', 'logiciel__niveau_securite', 'logiciel__categorie']
    search_fields = ['logiciel__nom', 'utilisateur__username', 'groupe__nom', 'structure__nom', 'site__nom']
    readonly_fields = ['date_debut', 'date_creation', 'date_modification', 'get_logiciels_installes_count']
    
    def changelist_view(self, request, extra_context=None):
        """Personnaliser la vue de liste pour ajouter un lien vers le blocage avancé"""
        extra_context = extra_context or {}
        extra_context['blocage_avance_url'] = '/api/v1/machines/blocage-avance/'
        return super().changelist_view(request, extra_context)
    fieldsets = (
        ('Logiciel', {
            'fields': ('logiciel',)
        }),
        ('Type d\'autorisation', {
            'fields': ('type_autorisation',)
        }),
        ('Cible de l\'autorisation', {
            'fields': ('utilisateur', 'groupe', 'structure', 'site'),
            'description': 'Sélectionner une seule cible selon le type d\'autorisation choisi'
        }),
        ('Autorisation', {
            'fields': ('statut', 'date_debut', 'date_fin', 'versions_autorisees')
        }),
        ('Gestion administrative', {
            'fields': ('autorise_par', 'motif', 'get_logiciels_installes_count')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_target(self, obj):
        """Retourne la cible de l'autorisation"""
        return obj.utilisateur or obj.groupe or obj.structure or obj.site
    get_target.short_description = 'Cible'
    
    def get_logiciels_installes_count(self, obj):
        """Affiche le nombre de logiciels installés correspondant à cette autorisation"""
        from .models import LogicielInstalle
        from django.db.models import Q
        
        if obj.statut != 'autorise' or not obj.is_valide():
            return format_html('<span style="color: gray;">-</span>')
        
        # Construire le filtre pour les utilisateurs concernés par cette autorisation
        user_filter = Q()
        if obj.utilisateur:
            user_filter = Q(machine__utilisateur=obj.utilisateur)
        elif obj.groupe:
            user_filter = Q(machine__utilisateur__groupe=obj.groupe)
        elif obj.structure:
            user_filter = Q(machine__utilisateur__structure=obj.structure)
        elif obj.site:
            user_filter = Q(machine__utilisateur__site=obj.site)
        
        count = LogicielInstalle.objects.filter(
            logiciel_reference=obj.logiciel,
            autorise=True,
            bloque=False
        ).filter(user_filter).count()
        
        if count > 0:
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        else:
            return format_html('<span style="color: orange;">0</span>')
    get_logiciels_installes_count.short_description = 'Logiciels installés'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related(
            'logiciel', 'utilisateur', 'groupe', 'structure', 'site', 'autorise_par'
        )
    
    actions = ['bloquer_pour_utilisateurs', 'bloquer_pour_structures', 'bloquer_pour_sites', 'autoriser_pour_cibles']
    
    def bloquer_pour_utilisateurs(self, request, queryset):
        """Action pour créer des blocages en masse pour des utilisateurs spécifiques"""
        from django.contrib.auth import get_user_model
        from .models import LogicielReference
        
        User = get_user_model()
        
        # Récupérer tous les logiciels sélectionnés
        logiciels = set()
        for autorisation in queryset:
            logiciels.add(autorisation.logiciel)
        
        # Récupérer tous les utilisateurs actifs
        utilisateurs = User.objects.filter(is_active=True)
        
        created_count = 0
        for logiciel in logiciels:
            for utilisateur in utilisateurs:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    utilisateur=utilisateur
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='utilisateur',
                        utilisateur=utilisateur,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) ou mis à jour pour tous les utilisateurs.')
    bloquer_pour_utilisateurs.short_description = "Bloquer ces logiciels pour TOUS les utilisateurs"
    
    def bloquer_pour_structures(self, request, queryset):
        """Action pour créer des blocages en masse pour des structures spécifiques"""
        from apps.users.models import Structure
        
        # Récupérer tous les logiciels sélectionnés
        logiciels = set()
        for autorisation in queryset:
            logiciels.add(autorisation.logiciel)
        
        # Récupérer toutes les structures actives
        structures = Structure.objects.filter(active=True)
        
        created_count = 0
        for logiciel in logiciels:
            for structure in structures:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    structure=structure
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='structure',
                        structure=structure,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) ou mis à jour pour toutes les structures.')
    bloquer_pour_structures.short_description = "Bloquer ces logiciels pour TOUTES les structures"
    
    def bloquer_pour_sites(self, request, queryset):
        """Action pour créer des blocages en masse pour des sites spécifiques"""
        from apps.users.models import Site
        
        # Récupérer tous les logiciels sélectionnés
        logiciels = set()
        for autorisation in queryset:
            logiciels.add(autorisation.logiciel)
        
        # Récupérer tous les sites actifs
        sites = Site.objects.filter(active=True)
        
        created_count = 0
        for logiciel in logiciels:
            for site in sites:
                # Vérifier si une autorisation existe déjà
                existing = AutorisationLogiciel.objects.filter(
                    logiciel=logiciel,
                    site=site
                ).first()
                
                if not existing:
                    # Créer une nouvelle autorisation refusée
                    AutorisationLogiciel.objects.create(
                        logiciel=logiciel,
                        type_autorisation='site',
                        site=site,
                        statut='refuse',
                        autorise_par=request.user,
                        motif=f'Bloqué en masse par {request.user.username}'
                    )
                    created_count += 1
                elif existing.statut != 'refuse':
                    # Mettre à jour l'autorisation existante
                    existing.statut = 'refuse'
                    existing.autorise_par = request.user
                    existing.motif = f'Bloqué en masse par {request.user.username}'
                    existing.save()
                    created_count += 1
        
        self.message_user(request, f'{created_count} blocage(s) créé(s) ou mis à jour pour tous les sites.')
    bloquer_pour_sites.short_description = "Bloquer ces logiciels pour TOUS les sites"
    
    def autoriser_pour_cibles(self, request, queryset):
        """Action pour autoriser en masse les logiciels sélectionnés"""
        updated = queryset.update(
            statut='autorise',
            autorise_par=request.user,
            motif=f'Autorisé en masse par {request.user.username}'
        )
        self.message_user(request, f'{updated} autorisation(s) accordée(s).')
    autoriser_pour_cibles.short_description = "Autoriser ces logiciels pour les cibles sélectionnées"


@admin.register(DemandeAutorisation)
class DemandeAutorisationAdmin(admin.ModelAdmin):
    """Administration des demandes d'autorisation"""
    list_display = ['logiciel_nom', 'utilisateur', 'machine', 'priorite', 'statut', 'date_creation']
    list_filter = ['statut', 'priorite', 'date_creation', 'machine__structure']
    search_fields = ['logiciel_nom', 'utilisateur__username', 'machine__nom', 'justification']
    readonly_fields = ['date_creation', 'date_modification']
    fieldsets = (
        ('Demande', {
            'fields': ('utilisateur', 'machine', 'priorite')
        }),
        ('Logiciel demandé', {
            'fields': ('logiciel_nom', 'logiciel_version', 'logiciel_editeur', 'logiciel_reference')
        }),
        ('Justification', {
            'fields': ('justification',)
        }),
        ('Traitement', {
            'fields': ('statut', 'traite_par', 'date_traitement', 'commentaire_admin')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related(
            'utilisateur', 'machine', 'logiciel_reference', 'traite_par'
        )
    
    actions = ['approuver_demandes', 'refuser_demandes']
    
    def approuver_demandes(self, request, queryset):
        """Action pour approuver plusieurs demandes"""
        updated = queryset.filter(statut='en_attente').update(
            statut='approuve',
            traite_par=request.user,
            date_traitement=timezone.now()
        )
        self.message_user(request, f'{updated} demande(s) approuvée(s).')
    approuver_demandes.short_description = "Approuver les demandes sélectionnées"
    
    def refuser_demandes(self, request, queryset):
        """Action pour refuser plusieurs demandes"""
        updated = queryset.filter(statut='en_attente').update(
            statut='refuse',
            traite_par=request.user,
            date_traitement=timezone.now()
        )
        self.message_user(request, f'{updated} demande(s) refusée(s).')
    refuser_demandes.short_description = "Refuser les demandes sélectionnées"


@admin.register(LogicielInstalle)
class LogicielInstalleAdmin(admin.ModelAdmin):
    """Administration des logiciels installés"""
    list_display = ['nom', 'version', 'editeur', 'machine', 'get_autorisations_count', 'autorise', 'bloque', 'licence_requise', 'logiciel_reference']
    list_filter = ['autorise', 'bloque', 'licence_requise', 'licence_valide', 'machine__structure', 'logiciel_reference__niveau_securite']
    search_fields = ['nom', 'version', 'editeur', 'machine__nom']
    readonly_fields = ['date_detection', 'date_derniere_maj', 'get_autorisations_count']
    fieldsets = (
        ('Logiciel', {
            'fields': ('machine', 'nom', 'version', 'editeur', 'logiciel_reference')
        }),
        ('Installation', {
            'fields': ('date_installation', 'taille')
        }),
        ('Licences', {
            'fields': ('licence_requise', 'licence_valide')
        }),
        ('Autorisation', {
            'fields': ('autorise', 'bloque', 'motif_blocage', 'get_autorisations_count')
        }),
        ('Métadonnées', {
            'fields': ('date_detection', 'date_derniere_maj'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verifier_autorisations', 'autoriser_logiciels', 'bloquer_logiciels']
    
    def verifier_autorisations(self, request, queryset):
        """Action pour vérifier les autorisations des logiciels sélectionnés"""
        for logiciel in queryset:
            logiciel.verifier_autorisation()
        self.message_user(request, f'Autorisations vérifiées pour {queryset.count()} logiciel(s).')
    verifier_autorisations.short_description = "Vérifier les autorisations"
    
    def autoriser_logiciels(self, request, queryset):
        """Action pour autoriser manuellement des logiciels"""
        updated = queryset.update(autorise=True, bloque=False, motif_blocage='')
        self.message_user(request, f'{updated} logiciel(s) autorisé(s).')
    autoriser_logiciels.short_description = "Autoriser les logiciels sélectionnés"
    
    def bloquer_logiciels(self, request, queryset):
        """Action pour bloquer manuellement des logiciels"""
        updated = queryset.update(autorise=False, bloque=True, motif_blocage='Bloqué manuellement par un administrateur')
        self.message_user(request, f'{updated} logiciel(s) bloqué(s).')
    bloquer_logiciels.short_description = "Bloquer les logiciels sélectionnés"
    
    def get_autorisations_count(self, obj):
        """Affiche le nombre d'autorisations liées à ce logiciel installé"""
        if obj.logiciel_reference and obj.machine.utilisateur:
            from .models import AutorisationLogiciel
            from django.db.models import Q
            
            count = AutorisationLogiciel.objects.filter(
                logiciel=obj.logiciel_reference,
                statut='autorise'
            ).filter(
                Q(utilisateur=obj.machine.utilisateur) |
                Q(groupe=obj.machine.utilisateur.groupe) |
                Q(structure=obj.machine.utilisateur.structure) |
                Q(site=obj.machine.utilisateur.site)
            ).count()
            
            if count > 0:
                return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
            else:
                return format_html('<span style="color: red;">0</span>')
        return '-'
    get_autorisations_count.short_description = 'Autorisations'
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('machine', 'machine__structure', 'logiciel_reference')


@admin.register(HistoriqueMachine)
class HistoriqueMachineAdmin(admin.ModelAdmin):
    """Administration de l'historique des machines"""
    list_display = ['machine', 'type_modification', 'utilisateur', 'date_modification']
    list_filter = ['type_modification', 'date_modification', 'machine__structure']
    search_fields = ['machine__nom', 'description', 'utilisateur__username']
    readonly_fields = ['id', 'date_modification']
    fieldsets = (
        ('Modification', {
            'fields': ('machine', 'type_modification', 'description', 'utilisateur')
        }),
        ('Données', {
            'fields': ('donnees_avant', 'donnees_apres'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Optimiser les requêtes avec select_related"""
        return super().get_queryset(request).select_related('machine', 'utilisateur', 'machine__structure')


# Personnalisation de l'interface d'administration
class MachinesAdminSite(admin.AdminSite):
    """Site d'administration personnalisé pour les machines"""
    site_header = "Administration ITSM - Machines"
    site_title = "ITSM Machines"
    index_title = "Gestion des Machines et Logiciels"
    
    def get_urls(self):
        """Ajouter des URLs personnalisées"""
        urls = super().get_urls()
        custom_urls = [
            path('blocage-avance/', self.admin_view(self.blocage_avance_view), name='blocage_avance'),
        ]
        return custom_urls + urls
    
    def blocage_avance_view(self, request):
        """Rediriger vers la vue de blocage avancé"""
        from django.shortcuts import redirect
        return redirect('/api/v1/machines/blocage-avance/')
    
    def index(self, request, extra_context=None):
        """Personnaliser la page d'accueil de l'admin"""
        extra_context = extra_context or {}
        extra_context['blocage_avance_url'] = '/api/v1/machines/blocage-avance/'
        return super().index(request, extra_context)


# Créer une instance du site d'administration personnalisé
# machines_admin_site = MachinesAdminSite(name='machines_admin')

# Ajouter un lien dans l'interface d'administration standard
def get_admin_urls():
    """Obtenir les URLs d'administration personnalisées"""
    from django.urls import path
    return [
        path('machines/blocage-avance/', 
             lambda request: HttpResponseRedirect('/machines/admin/blocage-avance/'),
             name='machines_blocage_avance'),
    ]