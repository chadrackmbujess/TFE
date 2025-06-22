#!/usr/bin/env python
"""
Test final des notifications pour l'utilisateur @aa.jess.cd
"""
import requests

def test_notifications():
    """Tester les notifications avec le bon token"""
    
    # Token récupéré du script de débogage
    token = "fea7c490e882151f61c5f4c06841031d5cb21c49"
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    print("🔄 Test de l'API des notifications...")
    print(f"🔑 Token utilisé: {token[:20]}...")
    
    try:
        # Tester l'endpoint spécifique des notifications
        response = requests.get(
            'http://127.0.0.1:8000/api/v1/tickets/notifications/',
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Réponse API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📋 Format des données: {type(data)}")
            print(f"📋 Contenu complet: {data}")
            
            # Extraire les notifications selon le format
            if isinstance(data, dict):
                if 'results' in data:
                    notifications = data['results']
                elif 'data' in data:
                    notifications = data['data']
                else:
                    notifications = list(data.values()) if data else []
            else:
                notifications = data
            
            print(f"✅ {len(notifications)} notifications récupérées")
            
            if isinstance(notifications, list):
                unread_count = sum(1 for notif in notifications if isinstance(notif, dict) and not notif.get('lu', False))
                total_count = len(notifications)
                
                print(f"📊 Compteurs: {total_count} total, {unread_count} non lus")
                
                for i, notif in enumerate(notifications):
                    if isinstance(notif, dict):
                        print(f"  📝 Notification {i+1}:")
                        print(f"    - Ticket: #{notif.get('ticket_id')}")
                        print(f"    - Titre: {notif.get('titre')}")
                        print(f"    - Commentaire: {notif.get('commentaire', '')[:50]}...")
                        print(f"    - Auteur: {notif.get('auteur')}")
                        print(f"    - Lu: {notif.get('lu')}")
                        print(f"    - Date: {notif.get('date')}")
                        print()
                    else:
                        print(f"  ⚠️ Notification {i+1} format inattendu: {type(notif)} - {notif}")
            else:
                print(f"⚠️ Format de réponse inattendu: {type(notifications)}")
            
            print("🎉 L'API des notifications fonctionne correctement !")
            print(f"L'application desktop devrait afficher: {total_count} 💬 et badge rouge avec {unread_count}")
            
        else:
            print(f"❌ Erreur API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Détails erreur: {error_data}")
            except:
                print(f"❌ Réponse brute: {response.text}")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    test_notifications()