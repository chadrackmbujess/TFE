"""
Configuration de l'interface d'administration pour le monitoring
"""
from django.contrib import admin

# Les modèles de monitoring seront ajoutés ici quand ils seront développés
# Exemple de structure pour les futurs modèles :

# @admin.register(StatusMachine)
# class StatusMachineAdmin(admin.ModelAdmin):
#     list_display = ['machine', 'statut', 'derniere_verification', 'temps_reponse']
#     list_filter = ['statut', 'derniere_verification']
#     search_fields = ['machine__nom']

# @admin.register(AlerteSysteme)
# class AlerteSystemeAdmin(admin.ModelAdmin):
#     list_display = ['titre', 'niveau', 'machine', 'date_creation', 'resolu']
#     list_filter = ['niveau', 'resolu', 'date_creation']
#     search_fields = ['titre', 'description']