"""
URLs pour l'application tickets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketViewSet, CategorieTicketViewSet, CommentaireTicketViewSet,
    PieceJointeTicketViewSet, EscaladeTicketViewSet, ModeleTicketViewSet, SLAViewSet, NotificationTicketViewSet
)

router = DefaultRouter()
router.register(r'', TicketViewSet, basename='ticket')
router.register(r'categories', CategorieTicketViewSet, basename='categorie')
router.register(r'commentaires', CommentaireTicketViewSet, basename='commentaire')
router.register(r'pieces-jointes', PieceJointeTicketViewSet, basename='piece-jointe')
router.register(r'escalades', EscaladeTicketViewSet, basename='escalade')
router.register(r'modeles', ModeleTicketViewSet, basename='modele')
router.register(r'sla', SLAViewSet, basename='sla')
router.register(r'notifications', NotificationTicketViewSet, basename='notification')

from .views import NotificationListView

urlpatterns = [
    path('', include(router.urls)),
    # Vue spécifique pour les notifications (contournement)
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
]