"""
Permissions personnalisées pour l'application users
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre la lecture à tous les utilisateurs authentifiés
    mais l'écriture seulement aux administrateurs.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Permissions de lecture pour tous les utilisateurs authentifiés
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissions d'écriture seulement pour les admins
        return request.user.is_superuser or request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux utilisateurs de modifier leur propre profil
    ou aux administrateurs de modifier n'importe quel profil.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Permissions de lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # L'utilisateur peut modifier son propre profil
        if obj == request.user:
            return True
        
        # Les admins peuvent modifier tous les profils
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        
        # Les techniciens peuvent modifier les profils de leur structure
        if (request.user.role == 'technicien' and 
            obj.structure == request.user.structure):
            return True
        
        return False


class IsTechnicienOrAdmin(permissions.BasePermission):
    """
    Permission pour les techniciens et administrateurs uniquement.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (request.user.is_superuser or 
                request.user.role in ['admin', 'technicien'])


class IsAdminOnly(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.is_superuser or request.user.role == 'admin'


class IsSameStructure(permissions.BasePermission):
    """
    Permission pour les utilisateurs de la même structure.
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Les admins ont accès à tout
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        
        # Vérifier si l'objet a un attribut structure
        if hasattr(obj, 'structure'):
            return obj.structure == request.user.structure
        
        # Vérifier si l'objet a un attribut utilisateur avec une structure
        if hasattr(obj, 'utilisateur'):
            return obj.utilisateur.structure == request.user.structure
        
        return False