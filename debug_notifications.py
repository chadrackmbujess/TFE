#!/usr/bin/env python
"""
Script de débogage pour les notifications
"""
import os
import sys
import django
import requests

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_backend.settings')
django.setup()

from apps.users.models import User
from apps.tickets.models import NotificationTicket
from rest_framework.authtoken.models import Token

def debug_notifications():
    """Déboguer les notifications"""
    try:
        # Récupérer l'utilisateur @aa.jess.cd
        user = User.objects.get(username='@aa.jess.cd')
        print(f"✅ Utilisateur trouvé: {user.username} - {user.nom_complet}")
        
        # Récupérer ou créer le token
        token, created = Token.objects.get_or_create(user=user)
        print(f"🔑 Token: {token.key}")
        
        # Vérifier les notifications dans la base de données
        notifications_db = NotificationTicket.objects.filter(destinataire=user)
        print(f"📊 Notifications dans la DB: {notifications_db.count()}")
        
        for notif in notifications_db:
            print(f"  - Ticket {notif.ticket.numero}: {notif.commentaire.contenu[:50]}... (Lu: {notif.lu})")
        
        # Tester l'API
        headers = {
            'Authorization': f'Token {token.key}',
            'Content-Type': 'application/json'
        }
        
        print("\n🔄 Test de l'API...")
        
        # Tester d'abord l'endpoint des tickets pour vérifier que l'API fonctionne
        print("🔍 Test de l'endpoint tickets...")
        response_tickets = requests.get(
            'http://127.0.0.1:8000/api/v1/tickets/',
            headers=headers,
            timeout=10
        )
        print(f"📡 Réponse tickets: {response_tickets.status_code}")
        
        # Tester l'endpoint des notifications
        print("🔍 Test de l'endpoint notifications...")
        
        # Tester différentes URLs possibles
        urls_to_test = [
            'http://127.0.0.1:8000/api/v1/tickets/notifications/',
            'http://127.0.0.1:8000/api/v1/notifications/',
            'http://127.0.0.1:8000/api/v1/notifications/notifications/',
            'http://127.0.0.1:8000/api/v1/tickets/notifications',
        ]
        
        for url in urls_to_test:
            print(f"🔍 Test URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📡 Réponse: {response.status_code}")
            if response.status_code == 200:
                break
        
        print(f"📡 Réponse API: {response.status_code}")
        
        if response.status_code == 200:
            notifications_api = response.json()
            print(f"✅ {len(notifications_api)} notifications récupérées via API")
            
            for i, notif in enumerate(notifications_api):
                print(f"  📝 Notification {i+1}: Ticket {notif.get('ticket_id')} - {notif.get('commentaire', '')[:50]}...")
        else:
            print(f"❌ Erreur API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Détails erreur: {error_data}")
            except:
                print(f"❌ Réponse brute: {response.text}")
        
    except User.DoesNotExist:
        print("❌ Utilisateur @aa.jess.cd non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    debug_notifications()