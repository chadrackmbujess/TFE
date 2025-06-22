"""
Configuration de l'interface d'administration pour les rapports
"""
from django.contrib import admin

# Les modèles de rapports seront ajoutés ici quand ils seront développés
# Exemple de structure pour les futurs modèles :

# @admin.register(RapportPersonnalise)
# class RapportPersonnaliseAdmin(admin.ModelAdmin):
#     list_display = ['nom', 'type_rapport', 'cree_par', 'date_creation', 'derniere_execution']
#     list_filter = ['type_rapport', 'date_creation']
#     search_fields = ['nom', 'description']
#     readonly_fields = ['date_creation', 'derniere_execution']

# @admin.register(ExportRapport)
# class ExportRapportAdmin(admin.ModelAdmin):
#     list_display = ['rapport', 'format_export', 'cree_par', 'date_export', 'taille_fichier']
#     list_filter = ['format_export', 'date_export']
#     search_fields = ['rapport__nom']
#     readonly_fields = ['date_export', 'taille_fichier']

# @admin.register(TableauBord)
# class TableauBordAdmin(admin.ModelAdmin):
#     list_display = ['nom', 'proprietaire', 'public', 'date_creation', 'derniere_modification']
#     list_filter = ['public', 'date_creation']
#     search_fields = ['nom', 'description']