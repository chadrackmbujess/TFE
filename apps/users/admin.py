"""
Configuration de l'interface d'administration pour les utilisateurs
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Structure, Groupe, Site, JournalConnexion


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'telephone', 'email', 'actif', 'date_creation']
    list_filter = ['actif', 'date_creation']
    search_fields = ['nom', 'code', 'email']
    readonly_fields = ['id', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'actif')
        }),
        ('Contact', {
            'fields': ('adresse', 'telephone', 'email', 'site_web')
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'structure', 'actif', 'date_creation']
    list_filter = ['actif', 'structure', 'date_creation']
    search_fields = ['nom', 'structure__nom']
    readonly_fields = ['id', 'date_creation']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'structure', 'actif', 'date_creation']
    list_filter = ['actif', 'structure', 'date_creation']
    search_fields = ['nom', 'structure__nom', 'adresse']
    readonly_fields = ['id', 'date_creation']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'nom_complet', 'email', 'role', 'structure', 'actif', 'date_creation']
    list_filter = ['role', 'actif', 'structure', 'groupe', 'date_creation']
    search_fields = ['username', 'prenom', 'nom', 'email']
    readonly_fields = ['id', 'date_creation', 'date_modification', 'derniere_connexion_app']
    
    fieldsets = (
        ('Authentification', {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'poste')
        }),
        ('Organisation', {
            'fields': ('structure', 'groupe', 'site', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Préférences', {
            'fields': ('notifications_email', 'langue'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_creation', 'date_modification', 'derniere_connexion_app'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Informations requises', {
            'classes': ('wide',),
            'fields': ('prenom', 'nom', 'structure', 'email', 'password1', 'password2', 'role'),
        }),
    )

    def nom_complet(self, obj):
        return obj.nom_complet
    nom_complet.short_description = 'Nom complet'


@admin.register(JournalConnexion)
class JournalConnexionAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'adresse_ip', 'type_connexion', 'date_connexion', 'duree_session', 'succes_display']
    list_filter = ['type_connexion', 'succes', 'date_connexion']
    search_fields = ['utilisateur__prenom', 'utilisateur__nom', 'adresse_ip']
    readonly_fields = ['id', 'date_connexion', 'duree_session']
    date_hierarchy = 'date_connexion'
    
    def succes_display(self, obj):
        if obj.succes:
            return format_html('<span style="color: green;">✓ Succès</span>')
        else:
            return format_html('<span style="color: red;">✗ Échec</span>')
    succes_display.short_description = 'Statut'
    
    def has_add_permission(self, request):
        return False  # Empêche l'ajout manuel
    
    def has_change_permission(self, request, obj=None):
        return False  # Empêche la modification