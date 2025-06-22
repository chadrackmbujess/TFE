#!/usr/bin/env python
"""
Script pour créer des notifications de test pour l'utilisateur @aa.jess.cd
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_backend.settings')
django.setup()

from apps.users.models import User
from apps.tickets.models import Ticket, CommentaireTicket, NotificationTicket
from django.utils import timezone

def create_test_notifications():
    """Créer des notifications de test"""
    try:
        # Récupérer l'utilisateur @aa.jess.cd
        user = User.objects.get(username='@aa.jess.cd')
        print(f"✅ Utilisateur trouvé: {user.username} - {user.nom_complet}")
        
        # Récupérer ou créer un ticket pour cet utilisateur
        ticket = Ticket.objects.filter(demandeur=user).first()
        if not ticket:
            # Créer un ticket de test
            from apps.tickets.models import CategorieTicket
            categorie = CategorieTicket.objects.first()
            
            ticket = Ticket.objects.create(
                titre="Problème de connexion réseau",
                description="Je n'arrive pas à me connecter au réseau de l'entreprise",
                demandeur=user,
                priorite='normale',
                categorie=categorie
            )
            print(f"✅ Ticket créé: {ticket.numero}")
        else:
            print(f"✅ Ticket existant trouvé: {ticket.numero}")
        
        # Récupérer un admin pour créer des commentaires
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            print("❌ Aucun admin trouvé")
            return
        
        print(f"✅ Admin trouvé: {admin_user.username}")
        
        # Créer des commentaires de test (qui vont automatiquement créer des notifications)
        commentaires_test = [
            "Bonjour, j'ai bien reçu votre demande. Je vais examiner le problème de connexion réseau.",
            "Après vérification, il semble que votre machine ne soit pas correctement configurée pour le réseau.",
            "Pouvez-vous redémarrer votre machine et réessayer la connexion ?",
            "Si le problème persiste, nous devrons peut-être reconfigurer vos paramètres réseau."
        ]
        
        for i, contenu in enumerate(commentaires_test):
            commentaire = CommentaireTicket.objects.create(
                ticket=ticket,
                auteur=admin_user,
                contenu=contenu,
                type_commentaire='commentaire'
            )
            print(f"✅ Commentaire {i+1} créé: {contenu[:50]}...")
        
        # Vérifier les notifications créées
        notifications = NotificationTicket.objects.filter(destinataire=user)
        print(f"✅ {notifications.count()} notifications créées pour {user.username}")
        
        for notif in notifications:
            print(f"  - Ticket {notif.ticket.numero}: {notif.commentaire.contenu[:50]}... (Lu: {notif.lu})")
        
        print("\n🎉 Notifications de test créées avec succès!")
        print(f"L'utilisateur {user.username} devrait maintenant voir {notifications.count()} commentaires dans l'application desktop.")
        
    except User.DoesNotExist:
        print("❌ Utilisateur @aa.jess.cd non trouvé")
        print("Utilisateurs disponibles:")
        for u in User.objects.all():
            print(f"  - {u.username}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    create_test_notifications()