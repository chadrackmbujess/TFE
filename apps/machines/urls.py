"""
URLs pour l'application machines
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MachineViewSet, TypeMachineViewSet, HistoriqueMachineViewSet
from .views_admin import (
    blocage_avance_view, api_logiciels_par_categorie, api_stats_blocage
)

router = DefaultRouter()
router.register(r'', MachineViewSet, basename='machine')
router.register(r'types', TypeMachineViewSet, basename='type-machine')
router.register(r'historique', HistoriqueMachineViewSet, basename='historique')

urlpatterns = [
    path('', include(router.urls)),
    # URLs pour l'administration avancée
    path('blocage-avance/', blocage_avance_view, name='blocage_avance'),
    path('api/logiciels-par-categorie/', api_logiciels_par_categorie, name='api_logiciels_par_categorie'),
    path('api/stats-blocage/', api_stats_blocage, name='api_stats_blocage'),
]