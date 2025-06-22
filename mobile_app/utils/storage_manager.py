"""
Gestionnaire de stockage local pour l'application mobile ITSM Compagnon
Gère la sauvegarde des données utilisateur, tokens et préférences
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from kivy.logger import Logger
from kivy.storage.jsonstore import JsonStore


class StorageManager:
    """Gestionnaire de stockage local sécurisé"""
    
    def __init__(self):
        # Créer le répertoire de données si nécessaire
        self.data_dir = Path.home() / '.itsm_companion'
        self.data_dir.mkdir(exist_ok=True)
        
        # Fichiers de stockage
        self.credentials_file = self.data_dir / 'credentials.json'
        self.settings_file = self.data_dir / 'settings.json'
        self.cache_file = self.data_dir / 'cache.json'
        
        # Stores Kivy
        self.credentials_store = JsonStore(str(self.credentials_file))
        self.settings_store = JsonStore(str(self.settings_file))
        self.cache_store = JsonStore(str(self.cache_file))
        
        Logger.info(f"StorageManager: Initialisé avec répertoire {self.data_dir}")
    
    # === GESTION DES IDENTIFIANTS ===
    
    def save_credentials(self, username: str, password: str):
        """Sauvegarder les identifiants utilisateur (chiffrés)"""
        try:
            # Simple encodage base64 pour l'exemple (à améliorer avec un vrai chiffrement)
            import base64
            encoded_password = base64.b64encode(password.encode()).decode()
            
            self.credentials_store.put('user_credentials', 
                                     username=username, 
                                     password=encoded_password)
            Logger.info("StorageManager: Identifiants sauvegardés")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur sauvegarde identifiants: {e}")
    
    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Récupérer les identifiants sauvegardés"""
        try:
            if self.credentials_store.exists('user_credentials'):
                creds = self.credentials_store.get('user_credentials')
                
                # Décoder le mot de passe
                import base64
                decoded_password = base64.b64decode(creds['password'].encode()).decode()
                
                return {
                    'username': creds['username'],
                    'password': decoded_password
                }
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération identifiants: {e}")
        return None
    
    def clear_credentials(self):
        """Supprimer les identifiants sauvegardés"""
        try:
            if self.credentials_store.exists('user_credentials'):
                self.credentials_store.delete('user_credentials')
            Logger.info("StorageManager: Identifiants supprimés")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur suppression identifiants: {e}")
    
    # === GESTION DU TOKEN D'AUTHENTIFICATION ===
    
    def save_auth_token(self, token: str):
        """Sauvegarder le token d'authentification"""
        try:
            self.credentials_store.put('auth_token', token=token)
            Logger.info("StorageManager: Token d'authentification sauvegardé")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur sauvegarde token: {e}")
    
    def get_auth_token(self) -> Optional[str]:
        """Récupérer le token d'authentification"""
        try:
            if self.credentials_store.exists('auth_token'):
                return self.credentials_store.get('auth_token')['token']
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération token: {e}")
        return None
    
    def clear_auth_token(self):
        """Supprimer le token d'authentification"""
        try:
            if self.credentials_store.exists('auth_token'):
                self.credentials_store.delete('auth_token')
            Logger.info("StorageManager: Token d'authentification supprimé")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur suppression token: {e}")
    
    # === GESTION DES PARAMÈTRES ===
    
    def save_setting(self, key: str, value: Any):
        """Sauvegarder un paramètre"""
        try:
            self.settings_store.put(key, value=value)
            Logger.debug(f"StorageManager: Paramètre {key} sauvegardé")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur sauvegarde paramètre {key}: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Récupérer un paramètre"""
        try:
            if self.settings_store.exists(key):
                return self.settings_store.get(key)['value']
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération paramètre {key}: {e}")
        return default
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Récupérer tous les paramètres"""
        try:
            settings = {}
            for key in self.settings_store.keys():
                settings[key] = self.settings_store.get(key)['value']
            return settings
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération paramètres: {e}")
            return {}
    
    def clear_settings(self):
        """Supprimer tous les paramètres"""
        try:
            self.settings_store.clear()
            Logger.info("StorageManager: Paramètres supprimés")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur suppression paramètres: {e}")
    
    # === GESTION DU CACHE ===
    
    def cache_data(self, key: str, data: Any, ttl: int = 3600):
        """Mettre en cache des données avec TTL (Time To Live)"""
        try:
            import time
            cache_entry = {
                'data': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            self.cache_store.put(key, **cache_entry)
            Logger.debug(f"StorageManager: Données mises en cache: {key}")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur mise en cache {key}: {e}")
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """Récupérer des données du cache si elles sont encore valides"""
        try:
            if self.cache_store.exists(key):
                cache_entry = self.cache_store.get(key)
                import time
                
                # Vérifier si le cache n'a pas expiré
                if time.time() - cache_entry['timestamp'] < cache_entry['ttl']:
                    Logger.debug(f"StorageManager: Cache hit pour {key}")
                    return cache_entry['data']
                else:
                    # Cache expiré, le supprimer
                    self.cache_store.delete(key)
                    Logger.debug(f"StorageManager: Cache expiré pour {key}")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération cache {key}: {e}")
        return None
    
    def clear_cache(self):
        """Vider tout le cache"""
        try:
            self.cache_store.clear()
            Logger.info("StorageManager: Cache vidé")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur vidage cache: {e}")
    
    def clear_expired_cache(self):
        """Supprimer les entrées de cache expirées"""
        try:
            import time
            current_time = time.time()
            expired_keys = []
            
            for key in self.cache_store.keys():
                try:
                    cache_entry = self.cache_store.get(key)
                    if current_time - cache_entry['timestamp'] >= cache_entry['ttl']:
                        expired_keys.append(key)
                except:
                    # Entrée corrompue, la marquer pour suppression
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.cache_store.delete(key)
            
            if expired_keys:
                Logger.info(f"StorageManager: {len(expired_keys)} entrées de cache expirées supprimées")
                
        except Exception as e:
            Logger.error(f"StorageManager: Erreur nettoyage cache: {e}")
    
    # === GESTION DES DONNÉES UTILISATEUR ===
    
    def save_user_data(self, user_data: Dict[str, Any]):
        """Sauvegarder les données utilisateur"""
        try:
            self.cache_data('user_profile', user_data, ttl=86400)  # 24h
            Logger.info("StorageManager: Données utilisateur sauvegardées")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur sauvegarde données utilisateur: {e}")
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Récupérer les données utilisateur"""
        return self.get_cached_data('user_profile')
    
    def clear_user_data(self):
        """Supprimer les données utilisateur"""
        try:
            if self.cache_store.exists('user_profile'):
                self.cache_store.delete('user_profile')
            Logger.info("StorageManager: Données utilisateur supprimées")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur suppression données utilisateur: {e}")
    
    # === GESTION DES PRÉFÉRENCES DE NOTIFICATION ===
    
    def save_notification_preferences(self, preferences: Dict[str, Any]):
        """Sauvegarder les préférences de notification"""
        try:
            for key, value in preferences.items():
                self.save_setting(f'notification_{key}', value)
            Logger.info("StorageManager: Préférences de notification sauvegardées")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur sauvegarde préférences notification: {e}")
    
    def get_notification_preferences(self) -> Dict[str, Any]:
        """Récupérer les préférences de notification"""
        try:
            preferences = {}
            all_settings = self.get_all_settings()
            
            for key, value in all_settings.items():
                if key.startswith('notification_'):
                    pref_key = key.replace('notification_', '')
                    preferences[pref_key] = value
            
            # Valeurs par défaut
            default_preferences = {
                'enabled': True,
                'sound': True,
                'vibration': True,
                'tickets': True,
                'comments': True,
                'assignments': True
            }
            
            # Fusionner avec les valeurs par défaut
            for key, default_value in default_preferences.items():
                if key not in preferences:
                    preferences[key] = default_value
            
            return preferences
            
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération préférences notification: {e}")
            return {
                'enabled': True,
                'sound': True,
                'vibration': True,
                'tickets': True,
                'comments': True,
                'assignments': True
            }
    
    # === NETTOYAGE GÉNÉRAL ===
    
    def clear_all_data(self):
        """Supprimer toutes les données stockées"""
        try:
            self.clear_credentials()
            self.clear_auth_token()
            self.clear_settings()
            self.clear_cache()
            self.clear_user_data()
            Logger.info("StorageManager: Toutes les données supprimées")
        except Exception as e:
            Logger.error(f"StorageManager: Erreur suppression générale: {e}")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Récupérer des informations sur le stockage"""
        try:
            info = {
                'data_directory': str(self.data_dir),
                'credentials_exists': self.credentials_store.exists('user_credentials'),
                'token_exists': self.credentials_store.exists('auth_token'),
                'settings_count': len(self.settings_store.keys()),
                'cache_count': len(self.cache_store.keys())
            }
            
            # Taille des fichiers
            for file_path in [self.credentials_file, self.settings_file, self.cache_file]:
                if file_path.exists():
                    info[f'{file_path.stem}_size'] = file_path.stat().st_size
                else:
                    info[f'{file_path.stem}_size'] = 0
            
            return info
            
        except Exception as e:
            Logger.error(f"StorageManager: Erreur récupération infos stockage: {e}")
            return {}