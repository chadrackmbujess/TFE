#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_backend.settings')
django.setup()

from apps.users.models import User
from apps.tickets.models import Ticket, CategorieTicket

def check_user_tickets():
    try:
        # Récupérer l'utilisateur
        user = User.objects.get(username='@aa.jess.cd')
        print(f"✅ Utilisateur trouvé: {user.username}")
        
        # Récupérer ses tickets
        tickets = Ticket.objects.filter(demandeur=user)
        print(f"📊 Nombre de tickets pour {user.username}: {tickets.count()}")
        
        # Afficher les détails des tickets
        for ticket in tickets:
            cat_info = f"{ticket.categorie.nom} (ID: {ticket.categorie.id})" if ticket.categorie else "Aucune catégorie"
            print(f"🎫 Ticket {ticket.numero}: {ticket.titre}")
            print(f"   - Catégorie: {cat_info}")
            print(f"   - Statut: {ticket.statut}")
            print(f"   - Priorité: {ticket.priorite}")
            print()
        
        # Afficher toutes les catégories disponibles
        print("📋 Catégories disponibles dans la base:")
        categories = CategorieTicket.objects.all()
        for cat in categories:
            print(f"   ID {cat.id}: {cat.nom}")
        
        # Compter les tickets par catégorie pour cet utilisateur
        print(f"\n📊 Répartition des tickets de {user.username} par catégorie:")
        for cat in categories:
            count = tickets.filter(categorie=cat).count()
            print(f"   {cat.nom}: {count} ticket(s)")
            
    except User.DoesNotExist:
        print("❌ Utilisateur @aa.jess.cd non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_user_tickets()