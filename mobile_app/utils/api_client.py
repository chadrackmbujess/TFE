"""
Client API pour l'application mobile ITSM Compagnon
Gère toutes les communications avec le backend Django
"""

import requests
import json
from typing import Dict, List, Tuple, Optional
from kivy.logger import Logger
try:
    from .storage_manager import StorageManager
except ImportError:
    from storage_manager import StorageManager


class APIClient:
    """Client pour communiquer avec l'API ITSM"""
    
    def __init__(self, base_url: str = None):
        if base_url is None:
            # Essayer de détecter l'adresse IP du réseau local
            base_url = self._detect_server_url()
        
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.token = None
        self.storage = StorageManager()
        
        # Charger le token sauvegardé
        self._load_token()
    
    def _load_token(self):
        """Charger le token d'authentification sauvegardé"""
        try:
            self.token = self.storage.get_auth_token()
            if self.token:
                self.session.headers.update({
                    'Authorization': f'Token {self.token}'
                })
                Logger.info("APIClient: Token d'authentification chargé")
        except Exception as e:
            Logger.error(f"APIClient: Erreur lors du chargement du token: {e}")
    
    def _save_token(self, token: str):
        """Sauvegarder le token d'authentification"""
        try:
            self.token = token
            self.storage.save_auth_token(token)
            self.session.headers.update({
                'Authorization': f'Token {token}'
            })
            Logger.info("APIClient: Token d'authentification sauvegardé")
        except Exception as e:
            Logger.error(f"APIClient: Erreur lors de la sauvegarde du token: {e}")
    
    def _make_request(self, method: str, endpoint: str, data: dict = None, 
                     params: dict = None) -> Tuple[bool, dict]:
        """Effectuer une requête HTTP"""
        try:
            url = f"{self.api_url}/{endpoint.lstrip('/')}"
            
            # Préparer les headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Effectuer la requête
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=10)
            else:
                return False, {'error': f'Méthode HTTP non supportée: {method}'}
            
            # Traiter la réponse
            if response.status_code in [200, 201]:
                try:
                    return True, response.json()
                except json.JSONDecodeError:
                    return True, {'message': 'Succès'}
            elif response.status_code == 401:
                Logger.warning("APIClient: Token expiré, déconnexion nécessaire")
                self.logout()
                return False, {'error': 'Session expirée, veuillez vous reconnecter'}
            else:
                try:
                    error_data = response.json()
                except json.JSONDecodeError:
                    error_data = {'error': f'Erreur HTTP {response.status_code}'}
                
                Logger.error(f"APIClient: Erreur {response.status_code}: {error_data}")
                return False, error_data
                
        except requests.exceptions.ConnectionError:
            Logger.error("APIClient: Erreur de connexion au serveur")
            return False, {'error': 'Impossible de se connecter au serveur'}
        except requests.exceptions.Timeout:
            Logger.error("APIClient: Timeout de la requête")
            return False, {'error': 'Délai d\'attente dépassé'}
        except Exception as e:
            Logger.error(f"APIClient: Erreur inattendue: {e}")
            return False, {'error': f'Erreur inattendue: {str(e)}'}
    
    def login(self, username: str, password: str) -> Tuple[bool, dict]:
        """Connexion utilisateur"""
        try:
            # Obtenir le token d'authentification (endpoint spécial hors API v1)
            url = f"{self.base_url}/api/auth/token/"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = self.session.post(url, json={
                'username': username,
                'password': password,
                'type_connexion': 'mobile'
            }, headers=headers, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                success = True
            else:
                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {'error': f'Erreur HTTP {response.status_code}'}
                success = False
            
            if success and 'token' in response_data:
                self._save_token(response_data['token'])
                
                # Récupérer les informations utilisateur
                user_success, user_data = self.get_user_profile()
                if user_success:
                    Logger.info(f"APIClient: Connexion réussie pour {username}")
                    return True, user_data
                else:
                    Logger.error("APIClient: Impossible de récupérer le profil utilisateur")
                    return False, {'error': 'Erreur lors de la récupération du profil'}
            else:
                Logger.warning(f"APIClient: Échec de connexion pour {username}")
                return False, response_data
                
        except Exception as e:
            Logger.error(f"APIClient: Erreur lors de la connexion: {e}")
            return False, {'error': str(e)}
    
    def logout(self):
        """Déconnexion utilisateur"""
        try:
            self.token = None
            self.storage.clear_auth_token()
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            Logger.info("APIClient: Déconnexion effectuée")
        except Exception as e:
            Logger.error(f"APIClient: Erreur lors de la déconnexion: {e}")
    
    def get_user_profile(self) -> Tuple[bool, dict]:
        """Récupérer le profil utilisateur"""
        return self._make_request('GET', 'users/profile/')
    
    # === GESTION DES TICKETS ===
    
    def get_tickets(self, filters: dict = None) -> Tuple[bool, List[dict]]:
        """Récupérer la liste des tickets"""
        success, response = self._make_request('GET', 'tickets/', params=filters)
        if success:
            return True, response.get('results', response)
        return False, response
    
    def get_ticket_detail(self, ticket_id: str) -> Tuple[bool, dict]:
        """Récupérer les détails d'un ticket"""
        return self._make_request('GET', f'tickets/{ticket_id}/')
    
    def create_ticket(self, ticket_data: dict) -> Tuple[bool, dict]:
        """Créer un nouveau ticket"""
        return self._make_request('POST', 'tickets/', ticket_data)
    
    def update_ticket(self, ticket_id: str, ticket_data: dict) -> Tuple[bool, dict]:
        """Mettre à jour un ticket"""
        return self._make_request('PUT', f'tickets/{ticket_id}/', ticket_data)
    
    def add_ticket_comment(self, ticket_id: str, comment_data: dict) -> Tuple[bool, dict]:
        """Ajouter un commentaire à un ticket"""
        comment_data['ticket'] = ticket_id
        return self._make_request('POST', 'tickets/commentaires/', comment_data)
    
    def get_ticket_comments(self, ticket_id: str) -> Tuple[bool, List[dict]]:
        """Récupérer les commentaires d'un ticket"""
        success, response = self._make_request('GET', 'tickets/commentaires/', 
                                             params={'ticket': ticket_id})
        if success:
            return True, response.get('results', response)
        return False, response
    
    # === GESTION DES MACHINES ===
    
    def get_machines(self, filters: dict = None) -> Tuple[bool, List[dict]]:
        """Récupérer la liste des machines"""
        success, response = self._make_request('GET', 'machines/', params=filters)
        if success:
            return True, response.get('results', response)
        return False, response
    
    def get_machine_detail(self, machine_id: str) -> Tuple[bool, dict]:
        """Récupérer les détails d'une machine"""
        return self._make_request('GET', f'machines/{machine_id}/')
    
    def search_machine_by_qr(self, qr_code: str) -> Tuple[bool, dict]:
        """Rechercher une machine par code QR"""
        # Le code QR peut contenir l'ID, le numéro de série ou le numéro d'inventaire
        filters = {
            'search': qr_code
        }
        success, machines = self.get_machines(filters)
        
        if success and machines:
            # Retourner la première machine trouvée
            return True, machines[0]
        elif success:
            return False, {'error': 'Aucune machine trouvée avec ce code QR'}
        else:
            return False, machines
    
    # === GESTION DES NOTIFICATIONS ===
    
    def get_notifications(self, unread_only: bool = False) -> Tuple[bool, List[dict]]:
        """Récupérer les notifications"""
        params = {}
        if unread_only:
            params['lu'] = 'false'
        
        # Utiliser l'endpoint correct pour les notifications
        success, response = self._make_request('GET', 'notifications/', params=params)
        if success:
            return True, response.get('results', response)
        return False, response
    
    def mark_notification_read(self, notification_id: str) -> Tuple[bool, dict]:
        """Marquer une notification comme lue"""
        return self._make_request('PUT', f'tickets/notifications/{notification_id}/', 
                                {'lu': True})
    
    def get_unread_count(self) -> int:
        """Récupérer le nombre de notifications non lues"""
        try:
            success, notifications = self.get_notifications(unread_only=True)
            if success:
                return len(notifications)
        except Exception as e:
            Logger.error(f"APIClient: Erreur lors du comptage des notifications: {e}")
        return 0
    
    # === GESTION DES CATÉGORIES ===
    
    def get_ticket_categories(self) -> Tuple[bool, List[dict]]:
        """Récupérer les catégories de tickets"""
        success, response = self._make_request('GET', 'tickets/categories/')
        if success:
            return True, response.get('results', response)
        return False, response
    
    # === UTILITAIRES ===
    
    def test_connection(self) -> bool:
        """Tester la connexion au serveur"""
        try:
            response = requests.get(f"{self.base_url}/admin/", timeout=5)
            return response.status_code in [200, 302, 403]  # 403 = pas connecté mais serveur accessible
        except:
            return False
    
    def get_server_info(self) -> Tuple[bool, dict]:
        """Récupérer les informations du serveur"""
        return self._make_request('GET', '')
    
    def _detect_server_url(self) -> str:
        """Détecter automatiquement l'URL du serveur"""
        try:
            # Essayer d'abord l'URL sauvegardée
            saved_url = self.storage.get_setting('server_url')
            if saved_url and self._test_server_url(saved_url):
                Logger.info(f"APIClient: URL sauvegardée utilisée: {saved_url}")
                return saved_url
            
            # Liste des URLs à tester (réseau local puis localhost)
            test_urls = [
                "http://0.0.0.0:8000",  # Serveur lancé en 0.0.0.0
                "http://192.168.1.100:8000",  # IP réseau commune
                "http://192.168.0.100:8000",  # IP réseau commune
                "http://127.0.0.1:8000",  # Localhost par défaut
            ]
            
            # Essayer de détecter l'IP du réseau local
            try:
                import socket
                # Obtenir l'IP locale
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                # Ajouter l'IP locale en premier dans la liste
                local_url = f"http://{local_ip}:8000"
                test_urls.insert(0, local_url)
                Logger.info(f"APIClient: IP locale détectée: {local_ip}")
                
            except Exception as e:
                Logger.warning(f"APIClient: Impossible de détecter l'IP locale: {e}")
            
            # Tester chaque URL
            for url in test_urls:
                if self._test_server_url(url):
                    Logger.info(f"APIClient: Serveur trouvé à: {url}")
                    # Sauvegarder l'URL qui fonctionne
                    self.storage.save_setting('server_url', url)
                    return url
            
            # Fallback vers localhost
            fallback_url = "http://127.0.0.1:8000"
            Logger.warning(f"APIClient: Aucun serveur trouvé, utilisation de: {fallback_url}")
            return fallback_url
            
        except Exception as e:
            Logger.error(f"APIClient: Erreur détection serveur: {e}")
            return "http://127.0.0.1:8000"
    
    def _test_server_url(self, url: str) -> bool:
        """Tester si une URL de serveur est accessible"""
        try:
            test_url = f"{url.rstrip('/')}/admin/"
            response = requests.get(test_url, timeout=3)
            return response.status_code in [200, 302, 403]  # 403 = pas connecté mais serveur accessible
        except:
            return False