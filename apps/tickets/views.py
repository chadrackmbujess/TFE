"""
Vues pour l'application tickets
"""
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    Ticket, CategorieTicket, CommentaireTicket,
    PieceJointeTicket, EscaladeTicket, ModeleTicket, SLA, NotificationTicket
)
from .serializers import (
    TicketSerializer, TicketCreateSerializer, CategorieTicketSerializer,
    CommentaireTicketSerializer, PieceJointeTicketSerializer,
    EscaladeTicketSerializer, ModeleTicketSerializer, SLASerializer, NotificationTicketSerializer
)


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des tickets"""
    queryset = Ticket.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retourner le serializer approprié selon l'action"""
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer
    
    def get_queryset(self):
        """Filtrer les tickets selon l'utilisateur"""
        user = self.request.user
        queryset = Ticket.objects.select_related(
            'demandeur', 'assigne_a', 'categorie', 'machine'
        ).prefetch_related('commentaires', 'pieces_jointes')
        
        # Filtrer selon le rôle de l'utilisateur
        if user.role == 'admin':
            # Les admins voient tous les tickets
            return queryset
        elif user.role in ['technicien', 'manager']:
            # Les techniciens voient leurs tickets assignés + tous les non-assignés
            return queryset.filter(
                Q(assigne_a=user) | Q(assigne_a__isnull=True) | Q(demandeur=user)
            )
        else:
            # Les utilisateurs normaux voient seulement leurs tickets
            return queryset.filter(demandeur=user)
    
    def perform_create(self, serializer):
        """Créer un ticket avec l'utilisateur connecté comme demandeur et assignation aléatoire d'un technicien"""
        import random
        from apps.users.models import User
        
        # Récupérer tous les techniciens disponibles
        techniciens = User.objects.filter(role='technicien', is_active=True)
        
        # Assigner aléatoirement un technicien si disponible
        technicien_assigne = None
        if techniciens.exists():
            technicien_assigne = random.choice(techniciens)
        
        # Sauvegarder le ticket avec assignation
        ticket = serializer.save(
            demandeur=self.request.user,
            assigne_a=technicien_assigne,
            statut='assigne' if technicien_assigne else 'nouveau',
            date_assignation=timezone.now() if technicien_assigne else None
        )
        
        # Créer un commentaire d'assignation automatique si un technicien a été assigné
        if technicien_assigne:
            CommentaireTicket.objects.create(
                ticket=ticket,
                auteur=self.request.user,
                type_commentaire='assignation',
                contenu=f'Ticket assigné automatiquement à {technicien_assigne.nom_complet}'
            )
    
    @action(detail=False, methods=['get'])
    def mes_tickets(self, request):
        """Récupérer les tickets de l'utilisateur connecté"""
        tickets = self.get_queryset().filter(demandeur=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assignes(self, request):
        """Récupérer les tickets assignés à l'utilisateur connecté"""
        tickets = self.get_queryset().filter(assigne_a=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assigner(self, request, pk=None):
        """Assigner un ticket à un technicien"""
        ticket = self.get_object()
        technicien_id = request.data.get('technicien_id')
        
        if not technicien_id:
            return Response(
                {'error': 'ID du technicien requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.users.models import User
            technicien = User.objects.get(id=technicien_id, role__in=['technicien', 'admin'])
            
            ticket.assigne_a = technicien
            ticket.statut = 'assigne'
            ticket.date_assignation = timezone.now()
            ticket.save()
            
            # Créer un commentaire d'assignation
            CommentaireTicket.objects.create(
                ticket=ticket,
                auteur=request.user,
                type_commentaire='assignation',
                contenu=f'Ticket assigné à {technicien.nom_complet}'
            )
            
            serializer = self.get_serializer(ticket)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Technicien non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """Changer le statut d'un ticket"""
        ticket = self.get_object()
        nouveau_statut = request.data.get('statut')
        commentaire = request.data.get('commentaire', '')
        
        if nouveau_statut not in dict(Ticket.STATUT_CHOICES):
            return Response(
                {'error': 'Statut invalide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ancien_statut = ticket.statut
        ticket.statut = nouveau_statut
        
        # Mettre à jour les dates selon le statut
        if nouveau_statut == 'en_cours' and not ticket.date_premiere_reponse:
            ticket.date_premiere_reponse = timezone.now()
        elif nouveau_statut in ['resolu', 'ferme']:
            ticket.date_resolution = timezone.now()
            if nouveau_statut == 'ferme':
                ticket.date_fermeture = timezone.now()
        
        ticket.save()
        
        # Créer un commentaire de changement de statut
        CommentaireTicket.objects.create(
            ticket=ticket,
            auteur=request.user,
            type_commentaire='commentaire',
            contenu=f'Statut changé de "{ancien_statut}" à "{nouveau_statut}". {commentaire}'
        )
        
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """Récupérer les statistiques des tickets"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'par_statut': {},
            'par_priorite': {},
            'en_retard': queryset.filter(
                date_echeance__lt=timezone.now(),
                statut__in=['nouveau', 'assigne', 'en_cours']
            ).count(),
            'resolus_ce_mois': queryset.filter(
                date_resolution__gte=timezone.now().replace(day=1)
            ).count()
        }
        
        # Statistiques par statut
        for statut, label in Ticket.STATUT_CHOICES:
            stats['par_statut'][statut] = queryset.filter(statut=statut).count()
        
        # Statistiques par priorité
        for priorite, label in Ticket.PRIORITE_CHOICES:
            stats['par_priorite'][priorite] = queryset.filter(priorite=priorite).count()
        
        return Response(stats)


class CategorieTicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories de tickets"""
    queryset = CategorieTicket.objects.filter(actif=True)
    serializer_class = CategorieTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentaireTicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commentaires de tickets"""
    serializer_class = CommentaireTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les commentaires selon les permissions"""
        user = self.request.user
        queryset = CommentaireTicket.objects.select_related('auteur', 'ticket')
        
        # Les utilisateurs normaux ne voient que les commentaires publics de leurs tickets
        if user.role not in ['admin', 'technicien', 'manager']:
            queryset = queryset.filter(
                ticket__demandeur=user,
                prive=False
            )
        
        return queryset


class PieceJointeTicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour les pièces jointes"""
    serializer_class = PieceJointeTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les pièces jointes selon les permissions"""
        user = self.request.user
        queryset = PieceJointeTicket.objects.select_related('uploade_par', 'ticket')
        
        # Les utilisateurs normaux ne voient que les pièces jointes de leurs tickets
        if user.role not in ['admin', 'technicien', 'manager']:
            queryset = queryset.filter(ticket__demandeur=user)
        
        return queryset


class EscaladeTicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour les escalades"""
    serializer_class = EscaladeTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les escalades selon les permissions"""
        user = self.request.user
        return EscaladeTicket.objects.filter(
            Q(de_utilisateur=user) | Q(vers_utilisateur=user)
        ).select_related('de_utilisateur', 'vers_utilisateur', 'ticket')


class ModeleTicketViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les modèles de tickets (lecture seule)"""
    queryset = ModeleTicket.objects.filter(actif=True)
    serializer_class = ModeleTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


class SLAViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les SLA (lecture seule)"""
    queryset = SLA.objects.filter(actif=True)
    serializer_class = SLASerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationTicketViewSet(viewsets.ModelViewSet):
    """ViewSet pour les notifications de tickets"""
    serializer_class = NotificationTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Récupérer les notifications de l'utilisateur connecté - seulement pour les tickets assignés"""
        return NotificationTicket.objects.filter(
            destinataire=self.request.user,
            ticket__assigne_a=self.request.user  # Seulement les tickets assignés au technicien
        ).select_related('ticket', 'commentaire', 'commentaire__auteur')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Marquer toutes les notifications comme lues"""
        notifications = self.get_queryset().filter(lu=False)
        count = notifications.update(lu=True, date_lecture=timezone.now())
        
        return Response({
            'message': f'{count} notifications marquées comme lues',
            'count': count
        })
    
    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        """Marquer une notification comme lue"""
        notification = self.get_object()
        notification.marquer_comme_lu()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class NotificationListView(generics.ListAPIView):
    """Vue simple pour lister les notifications"""
    serializer_class = NotificationTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Récupérer les notifications de l'utilisateur connecté - seulement pour les tickets assignés"""
        return NotificationTicket.objects.filter(
            destinataire=self.request.user,
            ticket__assigne_a=self.request.user  # Seulement les tickets assignés au technicien
        ).select_related('ticket', 'commentaire', 'commentaire__auteur').order_by('-date_creation')