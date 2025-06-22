"""
Serializers pour l'application tickets
"""
from rest_framework import serializers
from .models import (
    Ticket, CategorieTicket, CommentaireTicket, 
    PieceJointeTicket, EscaladeTicket, ModeleTicket, SLA, NotificationTicket
)
from apps.users.serializers import UserSerializer


class CategorieTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories de tickets"""
    
    class Meta:
        model = CategorieTicket
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    """Serializer pour les tickets"""
    demandeur_info = UserSerializer(source='demandeur', read_only=True)
    assigne_a_info = UserSerializer(source='assigne_a', read_only=True)
    categorie_info = CategorieTicketSerializer(source='categorie', read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'numero', 'titre', 'description', 'type_ticket',
            'categorie', 'categorie_info', 'priorite', 'statut',
            'demandeur', 'demandeur_info', 'assigne_a', 'assigne_a_info',
            'machine', 'date_creation', 'date_assignation', 
            'date_premiere_reponse', 'date_resolution', 'date_fermeture',
            'date_echeance', 'temps_resolution', 'note_satisfaction',
            'commentaire_satisfaction', 'date_modification',
            'est_en_retard', 'temps_ouvert'
        ]
        read_only_fields = [
            'id', 'numero', 'demandeur', 'date_creation', 
            'date_modification', 'est_en_retard', 'temps_ouvert'
        ]
    
    def create(self, validated_data):
        """Créer un nouveau ticket"""
        # Le demandeur est automatiquement l'utilisateur connecté
        validated_data['demandeur'] = self.context['request'].user
        return super().create(validated_data)


class CommentaireTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires de tickets"""
    auteur_info = UserSerializer(source='auteur', read_only=True)
    
    class Meta:
        model = CommentaireTicket
        fields = [
            'id', 'ticket', 'auteur', 'auteur_info', 'type_commentaire',
            'contenu', 'prive', 'temps_passe', 'date_creation', 'date_modification'
        ]
        read_only_fields = ['id', 'auteur', 'date_creation', 'date_modification']
    
    def create(self, validated_data):
        """Créer un nouveau commentaire"""
        validated_data['auteur'] = self.context['request'].user
        return super().create(validated_data)


class PieceJointeTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les pièces jointes"""
    uploade_par_info = UserSerializer(source='uploade_par', read_only=True)
    
    class Meta:
        model = PieceJointeTicket
        fields = [
            'id', 'ticket', 'commentaire', 'nom_fichier', 'fichier',
            'taille', 'type_mime', 'uploade_par', 'uploade_par_info', 'date_upload'
        ]
        read_only_fields = ['id', 'uploade_par', 'taille', 'type_mime', 'date_upload']
    
    def create(self, validated_data):
        """Créer une nouvelle pièce jointe"""
        validated_data['uploade_par'] = self.context['request'].user
        
        # Récupérer les informations du fichier
        fichier = validated_data['fichier']
        validated_data['taille'] = fichier.size
        validated_data['type_mime'] = fichier.content_type
        validated_data['nom_fichier'] = fichier.name
        
        return super().create(validated_data)


class EscaladeTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les escalades"""
    de_utilisateur_info = UserSerializer(source='de_utilisateur', read_only=True)
    vers_utilisateur_info = UserSerializer(source='vers_utilisateur', read_only=True)
    
    class Meta:
        model = EscaladeTicket
        fields = [
            'id', 'ticket', 'de_utilisateur', 'de_utilisateur_info',
            'vers_utilisateur', 'vers_utilisateur_info', 'motif', 'date_escalade'
        ]
        read_only_fields = ['id', 'de_utilisateur', 'date_escalade']
    
    def create(self, validated_data):
        """Créer une nouvelle escalade"""
        validated_data['de_utilisateur'] = self.context['request'].user
        return super().create(validated_data)


class ModeleTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les modèles de tickets"""
    categorie_defaut_info = CategorieTicketSerializer(source='categorie_defaut', read_only=True)
    
    class Meta:
        model = ModeleTicket
        fields = [
            'id', 'nom', 'description', 'titre_defaut', 'contenu_defaut',
            'categorie_defaut', 'categorie_defaut_info', 'priorite_defaut',
            'actif', 'date_creation'
        ]
        read_only_fields = ['id', 'date_creation']


class SLASerializer(serializers.ModelSerializer):
    """Serializer pour les SLA"""
    
    class Meta:
        model = SLA
        fields = '__all__'


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la création de tickets depuis l'app desktop"""
    
    class Meta:
        model = Ticket
        fields = [
            'titre', 'description', 'priorite', 'categorie'
        ]
    
    def create(self, validated_data):
        """Créer un nouveau ticket avec les valeurs par défaut et la machine de l'utilisateur"""
        # Le demandeur est automatiquement l'utilisateur connecté
        user = self.context['request'].user
        validated_data['demandeur'] = user
        validated_data['type_ticket'] = 'incident'  # Par défaut
        validated_data['statut'] = 'nouveau'  # Par défaut
        
        # Récupérer automatiquement la machine de l'utilisateur
        try:
            from apps.machines.models import Machine
            machine_utilisateur = Machine.objects.filter(utilisateur=user).first()
            if machine_utilisateur:
                validated_data['machine'] = machine_utilisateur
                print(f"✅ Machine associée au ticket: {machine_utilisateur.nom}")
            else:
                print(f"⚠️ Aucune machine trouvée pour l'utilisateur {user.username}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la machine: {str(e)}")
        
        return super().create(validated_data)


class NotificationTicketSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications de tickets"""
    ticket_id = serializers.CharField(source='ticket.numero', read_only=True)
    titre = serializers.CharField(source='ticket.titre', read_only=True)
    commentaire = serializers.CharField(source='commentaire.contenu', read_only=True)
    auteur = serializers.CharField(source='commentaire.auteur.nom_complet', read_only=True)
    date = serializers.DateTimeField(source='date_creation', read_only=True)
    
    class Meta:
        model = NotificationTicket
        fields = [
            'id', 'ticket_id', 'titre', 'commentaire', 'auteur', 
            'lu', 'date', 'date_lecture'
        ]
        read_only_fields = ['id', 'date_creation']