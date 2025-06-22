"""
Configuration de l'interface d'administration pour la maintenance
"""
from django.contrib import admin

# Les modèles de maintenance seront ajoutés ici quand ils seront développés
# Exemple de structure pour les futurs modèles :

# @admin.register(PlanMaintenance)
# class PlanMaintenanceAdmin(admin.ModelAdmin):
#     list_display = ['nom', 'type_maintenance', 'frequence', 'prochaine_execution', 'actif']
#     list_filter = ['type_maintenance', 'actif', 'prochaine_execution']
#     search_fields = ['nom', 'description']

# @admin.register(InterventionMaintenance)
# class InterventionMaintenanceAdmin(admin.ModelAdmin):
#     list_display = ['machine', 'technicien', 'type_intervention', 'date_intervention', 'statut']
#     list_filter = ['type_intervention', 'statut', 'date_intervention']
#     search_fields = ['machine__nom', 'technicien__prenom', 'technicien__nom']