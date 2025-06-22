#!/usr/bin/env python
import requests
import json

def test_categories_api():
    """Tester l'API des catégories"""
    
    # D'abord se connecter pour obtenir un token
    login_data = {
        'username': '@aa.jess.cd',
        'password': 'user123',
        'type_connexion': 'desktop'
    }
    
    try:
        # Connexion
        print("🔐 Connexion à l'API...")
        login_response = requests.post(
            'http://127.0.0.1:8000/api/v1/users/login/',
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('token')
            print(f"✅ Connexion réussie, token: {token[:20]}...")
            
            # Headers avec token
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json'
            }
            
            # Test de l'API des catégories
            print("\n📋 Test de l'API des catégories...")
            categories_response = requests.get(
                'http://127.0.0.1:8000/api/v1/tickets/categories/',
                headers=headers,
                timeout=10
            )
            
            if categories_response.status_code == 200:
                categories_data = categories_response.json()
                print(f"✅ Catégories récupérées: {categories_response.status_code}")
                print(f"📄 Format des données: {type(categories_data)}")
                print(f"📄 Contenu: {json.dumps(categories_data, indent=2, ensure_ascii=False)}")
                
                # Créer le mapping comme dans l'application desktop
                categories = categories_data.get('results', categories_data) if isinstance(categories_data, dict) else categories_data
                mapping = {}
                for category in categories:
                    category_id = category.get('id')
                    category_name = category.get('nom', '').lower()
                    if category_id and category_name:
                        mapping[category_id] = category_name
                
                print(f"\n🗺️ Mapping créé: {mapping}")
                
            else:
                print(f"❌ Erreur API catégories: {categories_response.status_code}")
                print(f"📄 Réponse: {categories_response.text}")
            
            # Test de l'API des tickets
            print("\n🎫 Test de l'API des tickets...")
            tickets_response = requests.get(
                'http://127.0.0.1:8000/api/v1/tickets/',
                headers=headers,
                timeout=10
            )
            
            if tickets_response.status_code == 200:
                tickets_data = tickets_response.json()
                tickets = tickets_data.get('results', tickets_data) if isinstance(tickets_data, dict) else tickets_data
                print(f"✅ Tickets récupérés: {len(tickets)} tickets")
                
                # Analyser les catégories des tickets
                categories_count = {}
                for ticket in tickets[:5]:  # Analyser les 5 premiers
                    category_id = ticket.get('categorie')
                    print(f"🎫 Ticket {ticket.get('numero', 'N/A')}: catégorie ID = {category_id}")
                    if category_id in mapping:
                        category_name = mapping[category_id]
                        categories_count[category_name] = categories_count.get(category_name, 0) + 1
                        print(f"   → Catégorie: {category_name}")
                    else:
                        print(f"   → Catégorie ID {category_id} non trouvée dans le mapping")
                
                print(f"\n📊 Comptage des catégories (5 premiers tickets): {categories_count}")
                
            else:
                print(f"❌ Erreur API tickets: {tickets_response.status_code}")
                print(f"📄 Réponse: {tickets_response.text}")
                
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            print(f"📄 Réponse: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_categories_api()