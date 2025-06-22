"""
Sérialiseurs pour l'API des utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Structure, Groupe, Site, JournalConnexion


class StructureSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les structures"""
    
    class Meta:
        model = Structure
        fields = ['id', 'nom', 'code', 'adresse', 'telephone', 'email', 'site_web', 'actif', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class GroupeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les groupes"""
    structure_nom = serializers.CharField(source='structure.nom', read_only=True)
    
    class Meta:
        model = Groupe
        fields = ['id', 'nom', 'description', 'structure', 'structure_nom', 'actif', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class SiteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les sites"""
    structure_nom = serializers.CharField(source='structure.nom', read_only=True)
    
    class Meta:
        model = Site
        fields = ['id', 'nom', 'adresse', 'structure', 'structure_nom', 'actif', 'date_creation']
        read_only_fields = ['id', 'date_creation']


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    nom_complet = serializers.CharField(read_only=True)
    structure_nom = serializers.CharField(source='structure.nom', read_only=True)
    groupe_nom = serializers.CharField(source='groupe.nom', read_only=True)
    site_nom = serializers.CharField(source='site.nom', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'prenom', 'nom', 'nom_complet', 'email', 'telephone', 'poste',
            'structure', 'structure_nom', 'groupe', 'groupe_nom', 'site', 'site_nom',
            'role', 'actif', 'notifications_email', 'langue', 'derniere_connexion_app',
            'date_creation'
        ]
        read_only_fields = ['id', 'username', 'nom_complet', 'derniere_connexion_app', 'date_creation']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'utilisateurs"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'prenom', 'nom', 'email', 'telephone', 'poste',
            'structure', 'groupe', 'site', 'role',
            'password', 'password_confirm', 'notifications_email', 'langue'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Générer le username au format @prenom.nom.entreprise
        prenom = validated_data.get('prenom', '').lower()
        nom = validated_data.get('nom', '').lower()

        username = f"@{prenom}{nom}.jess.cd"

        # Ajouter le username aux données validées
        validated_data['username'] = username

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Sérialiseur pour l'authentification"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Identifiants invalides.')
            if not user.is_active:
                raise serializers.ValidationError('Compte désactivé.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username et mot de passe requis.')
        
        return attrs


class JournalConnexionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le journal des connexions"""
    utilisateur_nom = serializers.CharField(source='utilisateur.nom_complet', read_only=True)
    
    class Meta:
        model = JournalConnexion
        fields = [
            'id', 'utilisateur', 'utilisateur_nom', 'adresse_ip', 'user_agent',
            'date_connexion', 'date_deconnexion', 'duree_session',
            'type_connexion', 'succes'
        ]
        read_only_fields = ['id', 'date_connexion', 'duree_session']


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil utilisateur (lecture seule étendue)"""
    structure_info = StructureSerializer(source='structure', read_only=True)
    groupe_info = GroupeSerializer(source='groupe', read_only=True)
    site_info = SiteSerializer(source='site', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'prenom', 'nom', 'email', 'telephone', 'poste',
            'structure_info', 'groupe_info', 'site_info', 'role',
            'notifications_email', 'langue', 'derniere_connexion_app', 'date_creation'
        ]
        read_only_fields = ['id', 'username', 'role', 'derniere_connexion_app', 'date_creation']