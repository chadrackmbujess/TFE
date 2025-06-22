#!/usr/bin/env python
"""
Script pour tester le ViewSet des notifications
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_backend.settings')
django.setup()

from apps.users.models import User
from apps.tickets.models import NotificationTicket
from apps.tickets.views import NotificationTicketViewSet
from rest_framework.test import APIRequestFactory
from rest_framework.authtoken.models import Token

def test_viewset():
    """Tester le ViewSet directement"""
    try:
        # Récupérer l'utilisateur @aa.jess.cd
        user = User.objects.get(username='@aa.jess.cd')
        print(f"✅ Utilisateur trouvé: {user.username}")
        
        # Créer une factory de requête
        factory = APIRequestFactory()
        
        # Créer une requête GET
        request = factory.get('/api/v1/tickets/notifications/')
        request.user = user
        
        # Tester le ViewSet
        viewset = NotificationTicketViewSet()
        viewset.request = request
        viewset.format_kwarg = None
        
        # Tester get_queryset
        queryset = viewset.get_queryset()
        print(f"📊 Queryset: {queryset.count()} notifications")
        
        for notif in queryset:
            print(f"  - {notif.ticket.numero}: {notif.commentaire.contenu[:50]}...")
        
        # Tester la méthode list
        response = viewset.list(request)
        print(f"✅ Réponse ViewSet: {response.status_code}")
        print(f"📝 Données: {len(response.data)} notifications")
        
        # Vérifier les URLs du routeur
        from apps.tickets.urls import router
        print(f"\n🔗 URLs du routeur:")
        for pattern in router.urls:
            print(f"  - {pattern.pattern}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_viewset()