"""
Configuration de l'interface d'administration pour l'inventaire
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CategorieEquipement, Equipement, AutorisationInventaire


@admin.register(CategorieEquipement)
class CategorieEquipementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'icone', 'actif']
    list_filter = ['actif']
    search_fields = ['nom', 'description']
    ordering = ['nom']


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'numero_inventaire', 'categorie', 'statut', 'utilisateur', 'site', 'get_logiciels_autorises_count', 'get_logiciels_installes_count', 'prix_achat']
    list_filter = ['statut', 'categorie', 'site', 'date_achat', 'date_fin_garantie']
    search_fields = ['nom', 'numero_inventaire', 'numero_serie', 'marque', 'modele', 'utilisateur__prenom', 'utilisateur__nom']
    readonly_fields = ['id', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'categorie')
        }),
        ('Identification', {
            'fields': ('numero_inventaire', 'numero_serie', 'code_barre')
        }),
        ('Informations techniques', {
            'fields': ('marque', 'modele')
        }),
        ('Attribution', {
            'fields': ('statut', 'utilisateur', 'site')
        }),
        ('Informations financières', {
            'fields': ('prix_achat', 'date_achat', 'fournisseur')
        }),
        ('Garantie', {
            'fields': ('date_fin_garantie',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('categorie', 'utilisateur', 'site')
    
    def get_logiciels_autorises_count(self, obj):
        """Affiche le nombre de logiciels autorisés pour cet équipement"""
        if obj.utilisateur:
            count = len(obj.get_logiciels_autorises())
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', count)
        return '-'
    get_logiciels_autorises_count.short_description = 'Logiciels autorisés'
    
    def get_logiciels_installes_count(self, obj):
        """Affiche le nombre de logiciels installés autorisés"""
        if obj.utilisateur:
            count = len(obj.get_logiciels_installes_autorises())
            return format_html('<span style="color: blue; font-weight: bold;">{}</span>', count)
        return '-'
    get_logiciels_installes_count.short_description = 'Logiciels installés'


@admin.register(AutorisationInventaire)
class AutorisationInventaireAdmin(admin.ModelAdmin):
    """Administration des autorisations de logiciels dans l'inventaire"""
    list_display = ['equipement', 'utilisateur', 'get_logiciel_nom', 'get_statut_autorisation', 'est_valide', 'date_attribution']
    list_filter = ['actif', 'date_attribution', 'equipement__categorie', 'autorisation_logiciel__statut']
    search_fields = [
        'equipement__nom', 
        'equipement__numero_inventaire',
        'utilisateur__prenom', 
        'utilisateur__nom',
        'autorisation_logiciel__logiciel__nom'
    ]
    readonly_fields = ['date_attribution', 'date_modification', 'est_valide']
    
    fieldsets = (
        ('Attribution', {
            'fields': ('equipement', 'utilisateur')
        }),
        ('Autorisation', {
            'fields': ('autorisation_logiciel', 'actif')
        }),
        ('Informations', {
            'fields': ('est_valide', 'date_attribution', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def get_logiciel_nom(self, obj):
        """Affiche le nom du logiciel autorisé"""
        return obj.autorisation_logiciel.logiciel.nom
    get_logiciel_nom.short_description = 'Logiciel'
    
    def get_statut_autorisation(self, obj):
        """Affiche le statut de l'autorisation avec couleur"""
        statut = obj.autorisation_logiciel.statut
        couleurs = {
            'autorise': 'green',
            'refuse': 'red',
            'en_attente': 'orange',
            'expire': 'gray'
        }
        couleur = couleurs.get(statut, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            couleur,
            obj.autorisation_logiciel.get_statut_display()
        )
    get_statut_autorisation.short_description = 'Statut'
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        return super().get_queryset(request).select_related(
            'equipement', 
            'utilisateur', 
            'autorisation_logiciel', 
            'autorisation_logiciel__logiciel'
        )
    
    actions = ['synchroniser_autorisations']
    
    def synchroniser_autorisations(self, request, queryset):
        """Action pour synchroniser les autorisations avec les logiciels installés"""
        from .models import AutorisationInventaire
        
        # Récupérer les utilisateurs uniques des équipements sélectionnés
        utilisateurs = set()
        for autorisation in queryset:
            if autorisation.utilisateur:
                utilisateurs.add(autorisation.utilisateur)
        
        total_creees = 0
        for utilisateur in utilisateurs:
            creees = AutorisationInventaire.synchroniser_avec_logiciels_installes(utilisateur=utilisateur)
            total_creees += creees
        
        self.message_user(
            request, 
            f'{total_creees} nouvelle(s) autorisation(s) créée(s) à partir des logiciels installés.'
        )
    synchroniser_autorisations.short_description = "Synchroniser avec les logiciels installés"