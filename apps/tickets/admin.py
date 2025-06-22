"""
Configuration de l'interface d'administration pour les tickets
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    CategorieTicket, Ticket, CommentaireTicket, PieceJointeTicket, 
    EscaladeTicket, ModeleTicket, SLA
)


@admin.register(CategorieTicket)
class CategorieTicketAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur_display', 'sla_heures', 'assignation_auto', 'actif']
    list_filter = ['actif', 'assignation_auto']
    search_fields = ['nom', 'description']
    
    def couleur_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.couleur, obj.nom
        )
    couleur_display.short_description = 'Couleur'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['numero', 'titre', 'type_ticket', 'priorite', 'statut', 'demandeur', 'assigne_a', 'date_creation', 'est_en_retard_display']
    list_filter = ['type_ticket', 'priorite', 'statut', 'categorie', 'date_creation', 'demandeur__structure']
    search_fields = ['numero', 'titre', 'description', 'demandeur__prenom', 'demandeur__nom']
    readonly_fields = ['id', 'numero', 'date_creation', 'date_modification', 'temps_resolution', 'temps_ouvert']
    date_hierarchy = 'date_creation'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero', 'titre', 'description', 'type_ticket', 'categorie')
        }),
        ('Priorité et statut', {
            'fields': ('priorite', 'statut')
        }),
        ('Attribution', {
            'fields': ('demandeur', 'assigne_a', 'machine')
        }),
        ('Dates importantes', {
            'fields': ('date_creation', 'date_assignation', 'date_premiere_reponse', 'date_resolution', 'date_fermeture', 'date_echeance')
        }),
        ('Satisfaction', {
            'fields': ('note_satisfaction', 'commentaire_satisfaction'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('id', 'date_modification', 'temps_resolution', 'temps_ouvert'),
            'classes': ('collapse',)
        }),
    )
    
    def est_en_retard_display(self, obj):
        if obj.est_en_retard:
            return format_html('<span style="color: red;">⚠️ En retard</span>')
        else:
            return format_html('<span style="color: green;">✅ À jour</span>')
    est_en_retard_display.short_description = 'Statut SLA'


class CommentaireTicketInline(admin.TabularInline):
    model = CommentaireTicket
    extra = 0
    readonly_fields = ['date_creation', 'date_modification']


class PieceJointeTicketInline(admin.TabularInline):
    model = PieceJointeTicket
    extra = 0
    readonly_fields = ['date_upload', 'taille']


# Ajouter les inlines au TicketAdmin
TicketAdmin.inlines = [CommentaireTicketInline, PieceJointeTicketInline]


@admin.register(CommentaireTicket)
class CommentaireTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'auteur', 'type_commentaire', 'prive', 'date_creation']
    list_filter = ['type_commentaire', 'prive', 'date_creation']
    search_fields = ['ticket__numero', 'auteur__prenom', 'auteur__nom', 'contenu']
    readonly_fields = ['date_creation', 'date_modification']


@admin.register(PieceJointeTicket)
class PieceJointeTicketAdmin(admin.ModelAdmin):
    list_display = ['nom_fichier', 'ticket', 'uploade_par', 'taille_display', 'date_upload']
    list_filter = ['type_mime', 'date_upload']
    search_fields = ['nom_fichier', 'ticket__numero']
    readonly_fields = ['id', 'taille', 'date_upload']
    
    def taille_display(self, obj):
        if obj.taille:
            if obj.taille < 1024:
                return f"{obj.taille} B"
            elif obj.taille < 1024 * 1024:
                return f"{obj.taille / 1024:.1f} KB"
            else:
                return f"{obj.taille / (1024 * 1024):.1f} MB"
        return "N/A"
    taille_display.short_description = 'Taille'


@admin.register(EscaladeTicket)
class EscaladeTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'de_utilisateur', 'vers_utilisateur', 'date_escalade']
    list_filter = ['date_escalade']
    search_fields = ['ticket__numero', 'de_utilisateur__prenom', 'vers_utilisateur__prenom']
    readonly_fields = ['id', 'date_escalade']


@admin.register(ModeleTicket)
class ModeleTicketAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie_defaut', 'priorite_defaut', 'actif', 'date_creation']
    list_filter = ['actif', 'categorie_defaut', 'priorite_defaut']
    search_fields = ['nom', 'description']
    readonly_fields = ['date_creation']


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ['nom', 'temps_reponse_critique', 'temps_reponse_normale', 'temps_resolution_critique', 'temps_resolution_normale', 'actif']
    list_filter = ['actif']
    search_fields = ['nom', 'description']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'actif')
        }),
        ('Temps de réponse (heures)', {
            'fields': ('temps_reponse_critique', 'temps_reponse_haute', 'temps_reponse_normale', 'temps_reponse_basse')
        }),
        ('Temps de résolution (heures)', {
            'fields': ('temps_resolution_critique', 'temps_resolution_haute', 'temps_resolution_normale', 'temps_resolution_basse')
        }),
    )