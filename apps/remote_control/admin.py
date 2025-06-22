"""
Configuration de l'interface d'administration pour le contrôle distant
"""
from django.contrib import admin

# Les modèles de contrôle distant seront ajoutés ici quand ils seront développés
# Exemple de structure pour les futurs modèles :

# @admin.register(SessionControleDistant)
# class SessionControleDistantAdmin(admin.ModelAdmin):
#     list_display = ['machine', 'technicien', 'type_action', 'date_debut', 'date_fin', 'statut']
#     list_filter = ['type_action', 'statut', 'date_debut']
#     search_fields = ['machine__nom', 'technicien__prenom', 'technicien__nom']
#     readonly_fields = ['date_debut', 'date_fin']

# @admin.register(CommandeDistante)
# class CommandeDistanteAdmin(admin.ModelAdmin):
#     list_display = ['machine', 'commande', 'executee_par', 'date_execution', 'succes']
#     list_filter = ['succes', 'date_execution']
#     search_fields = ['machine__nom', 'commande']
#     readonly_fields = ['date_execution', 'resultat']