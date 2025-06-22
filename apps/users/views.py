"""
Vues pour l'authentification et la gestion des utilisateurs
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User, Structure, JournalConnexion
from .serializers import UserCreateSerializer, LoginSerializer, UserProfileSerializer, StructureSerializer


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Endpoint de connexion
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Vérifier l'accès pour l'application mobile Compagnon
        type_connexion = request.data.get('type_connexion', 'desktop')
        if type_connexion == 'mobile' and user.role != 'technicien':
            # Enregistrer la tentative de connexion refusée
            JournalConnexion.objects.create(
                utilisateur=user,
                adresse_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                type_connexion=type_connexion,
                succes=False
            )
            
            return Response({
                'status': 403,
                'message': 'Accès refusé : cette application est réservée aux techniciens.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Créer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)
        
        # Enregistrer la connexion
        JournalConnexion.objects.create(
            utilisateur=user,
            adresse_ip=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            type_connexion=type_connexion,
            succes=True
        )
        
        # Mettre à jour la dernière connexion
        user.derniere_connexion_app = timezone.now()
        user.save(update_fields=['derniere_connexion_app'])
        
        return Response({
            'token': token.key,
            'user': UserProfileSerializer(user).data,
            'message': 'Connexion réussie'
        }, status=status.HTTP_200_OK)
    
    # Enregistrer la tentative de connexion échouée
    username = request.data.get('username')
    if username:
        try:
            user = User.objects.get(username=username)
            JournalConnexion.objects.create(
                utilisateur=user,
                adresse_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                type_connexion=request.data.get('type_connexion', 'desktop'),
                succes=False
            )
        except User.DoesNotExist:
            pass
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    Endpoint d'enregistrement
    """
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Récupérer ou créer la structure par défaut
        structure_id = request.data.get('structure')
        if structure_id:
            try:
                structure = Structure.objects.get(id=structure_id)
            except Structure.DoesNotExist:
                structure = Structure.objects.get(code='demo')  # Structure par défaut
        else:
            structure = Structure.objects.get(code='demo')  # Structure par défaut
        
        # Créer l'utilisateur
        user_data = serializer.validated_data.copy()
        user_data['structure'] = structure
        
        user = serializer.create(user_data)
        
        # Créer le token pour l'utilisateur
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Inscription réussie'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Endpoint de déconnexion
    """
    try:
        # Supprimer le token
        request.user.auth_token.delete()
        return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Erreur lors de la déconnexion'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """
    Endpoint pour récupérer le profil de l'utilisateur connecté
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def structures_view(request):
    """
    Endpoint pour récupérer la liste des structures
    """
    structures = Structure.objects.filter(actif=True)
    serializer = StructureSerializer(structures, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip