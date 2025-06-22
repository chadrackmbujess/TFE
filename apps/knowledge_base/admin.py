"""
Configuration de l'interface d'administration pour la base de connaissances
"""
from django.contrib import admin

# Les modèles de base de connaissances seront ajoutés ici quand ils seront développés
# Exemple de structure pour les futurs modèles :

# @admin.register(Article)
# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ['titre', 'categorie', 'auteur', 'date_creation', 'date_modification', 'publie']
#     list_filter = ['categorie', 'publie', 'date_creation']
#     search_fields = ['titre', 'contenu', 'mots_cles']
#     readonly_fields = ['date_creation', 'date_modification', 'nombre_vues']

# @admin.register(CategorieArticle)
# class CategorieArticleAdmin(admin.ModelAdmin):
#     list_display = ['nom', 'description', 'parent', 'ordre']
#     list_filter = ['parent']
#     search_fields = ['nom', 'description']

# @admin.register(FAQ)
# class FAQAdmin(admin.ModelAdmin):
#     list_display = ['question', 'categorie', 'ordre', 'actif']
#     list_filter = ['categorie', 'actif']
#     search_fields = ['question', 'reponse']