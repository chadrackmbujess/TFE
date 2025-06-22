#!/usr/bin/env python
"""
Script pour tester l'API des notifications
"""
import requests
import json

def test_notifications_api():
    """Tester l'API des notifications"""
    base_url = 'http://127.0.0.1:8000'
    
    # 1. Se connecter avec l'utilisateur @aa.jess.cd
    print("🔐 Connexion de l'utilisateur @aa.jess.cd...")
    login_data = {
        'username': '@aa.jess.cd',
        'password': 'password123',  # Mot de passe correct
        'type_connexion': 'desktop'
    }
    
    try:
        response = requests.post(f'{base_url}/api/v1/users/login/', data=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('token')
            print(f"✅ Connexion réussie, token: {token[:20]}...")
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # 2. Récupérer les notifications
    print("\n📬 Récupération des notifications...")
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{base_url}/api/v1/tickets/notifications/', headers=headers, timeout=10)
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ {len(notifications)} notifications récupérées")
            
            for i, notif in enumerate(notifications, 1):
                print(f"\n📝 Notification {i}:")
                print(f"  - Ticket: #{notif.get('ticket_id')}")
                print(f"  - Titre: {notif.get('titre')}")
                print(f"  - Commentaire: {notif.get('commentaire')[:50]}...")
                print(f"  - Auteur: {notif.get('auteur')}")
                print(f"  - Lu: {notif.get('lu')}")
                print(f"  - Date: {notif.get('date')}")
        else:
            print(f"❌ Erreur lors de la récupération: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Erreur lors de la récupération: {e}")

if __name__ == '__main__':
    test_notifications_api()