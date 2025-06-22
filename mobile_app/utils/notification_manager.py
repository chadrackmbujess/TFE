"""
Gestionnaire de notifications push pour l'application mobile ITSM Compagnon
Gère les notifications locales et push natives
"""

import threading
import time
from typing import Dict, List, Optional, Callable
from kivy.logger import Logger
from kivy.clock import Clock

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    Logger.warning("NotificationManager: Plyer non disponible, notifications désactivées")
    PLYER_AVAILABLE = False

try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, cast
    ANDROID_AVAILABLE = True
    
    # Classes Android pour les notifications
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationCompat = autoclass('android.support.v4.app.NotificationCompat')
    
except ImportError:
    Logger.info("NotificationManager: Environnement non-Android détecté")
    ANDROID_AVAILABLE = False


class NotificationManager:
    """Gestionnaire de notifications push et locales"""
    
    def __init__(self):
        self.user_id = None
        self.is_running = False
        self.check_interval = 30  # Vérifier toutes les 30 secondes
        self.last_notification_count = 0
        self.notification_callbacks = []
        self.check_thread = None
        
        # Préférences de notification (chargées depuis le storage)
        self.preferences = {
            'enabled': True,
            'sound': True,
            'vibration': True,
            'tickets': True,
            'comments': True,
            'assignments': True
        }
        
        Logger.info("NotificationManager: Initialisé")
        
        # Demander les permissions Android si nécessaire
        if ANDROID_AVAILABLE:
            self._request_android_permissions()
    
    def _request_android_permissions(self):
        """Demander les permissions Android nécessaires"""
        try:
            permissions = [
                Permission.VIBRATE,
                Permission.WAKE_LOCK,
                Permission.RECEIVE_BOOT_COMPLETED
            ]
            request_permissions(permissions)
            Logger.info("NotificationManager: Permissions Android demandées")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur permissions Android: {e}")
    
    def initialize(self, user_id: str):
        """Initialiser le gestionnaire pour un utilisateur"""
        try:
            self.user_id = user_id
            self.start_monitoring()
            Logger.info(f"NotificationManager: Initialisé pour l'utilisateur {user_id}")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur initialisation: {e}")
    
    def start_monitoring(self):
        """Démarrer la surveillance des notifications"""
        if self.is_running:
            return
        
        try:
            self.is_running = True
            
            # Démarrer le thread de vérification
            self.check_thread = threading.Thread(target=self._notification_loop, daemon=True)
            self.check_thread.start()
            
            Logger.info("NotificationManager: Surveillance démarrée")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur démarrage surveillance: {e}")
            self.is_running = False
    
    def stop_monitoring(self):
        """Arrêter la surveillance des notifications"""
        try:
            self.is_running = False
            if self.check_thread and self.check_thread.is_alive():
                self.check_thread.join(timeout=2)
            Logger.info("NotificationManager: Surveillance arrêtée")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur arrêt surveillance: {e}")
    
    def stop(self):
        """Arrêter complètement le gestionnaire"""
        self.stop_monitoring()
        self.user_id = None
        self.notification_callbacks.clear()
    
    def _notification_loop(self):
        """Boucle principale de vérification des notifications"""
        while self.is_running:
            try:
                if self.preferences.get('enabled', True):
                    self.check_notifications()
                time.sleep(self.check_interval)
            except Exception as e:
                Logger.error(f"NotificationManager: Erreur dans la boucle: {e}")
                time.sleep(self.check_interval)
    
    def check_notifications(self):
        """Vérifier les nouvelles notifications"""
        if not self.user_id or not self.preferences.get('enabled', True):
            return
        
        try:
            # Importer ici pour éviter les imports circulaires
            from .api_client import APIClient
            
            api_client = APIClient()
            success, notifications = api_client.get_notifications(unread_only=True)
            
            if success:
                current_count = len(notifications)
                
                # Vérifier s'il y a de nouvelles notifications
                if current_count > self.last_notification_count:
                    new_notifications = notifications[:current_count - self.last_notification_count]
                    
                    for notification_data in new_notifications:
                        self._show_notification(notification_data)
                    
                    # Notifier les callbacks
                    Clock.schedule_once(lambda dt: self._notify_callbacks(notifications), 0)
                
                self.last_notification_count = current_count
                
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur vérification notifications: {e}")
    
    def _show_notification(self, notification_data: Dict):
        """Afficher une notification système"""
        if not self.preferences.get('enabled', True):
            return
        
        try:
            # Extraire les informations de la notification
            title = f"Ticket {notification_data.get('ticket_id', 'N/A')}"
            message = notification_data.get('commentaire', 'Nouveau commentaire')
            author = notification_data.get('auteur', 'Utilisateur')
            
            # Limiter la longueur du message
            if len(message) > 100:
                message = message[:97] + "..."
            
            full_message = f"{author}: {message}"
            
            # Afficher la notification selon la plateforme
            if ANDROID_AVAILABLE:
                self._show_android_notification(title, full_message)
            elif PLYER_AVAILABLE:
                self._show_plyer_notification(title, full_message)
            else:
                Logger.info(f"Notification: {title} - {full_message}")
            
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur affichage notification: {e}")
    
    def _show_android_notification(self, title: str, message: str):
        """Afficher une notification Android native"""
        try:
            # Obtenir le contexte Android
            context = PythonActivity.mActivity.getApplicationContext()
            
            # Créer la notification
            builder = NotificationCompat.Builder(context, "itsm_channel")
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(android.R.drawable.ic_dialog_info)
            builder.setAutoCancel(True)
            
            # Configurer le son et la vibration
            if self.preferences.get('sound', True):
                builder.setDefaults(NotificationCompat.DEFAULT_SOUND)
            
            if self.preferences.get('vibration', True):
                builder.setDefaults(NotificationCompat.DEFAULT_VIBRATE)
            
            # Afficher la notification
            notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
            notification_manager.notify(int(time.time()), builder.build())
            
            Logger.info(f"NotificationManager: Notification Android affichée: {title}")
            
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur notification Android: {e}")
            # Fallback vers Plyer
            self._show_plyer_notification(title, message)
    
    def _show_plyer_notification(self, title: str, message: str):
        """Afficher une notification via Plyer"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="ITSM Compagnon",
                timeout=10
            )
            Logger.info(f"NotificationManager: Notification Plyer affichée: {title}")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur notification Plyer: {e}")
    
    def show_local_notification(self, title: str, message: str):
        """Afficher une notification locale immédiate"""
        try:
            if self.preferences.get('enabled', True):
                if ANDROID_AVAILABLE:
                    self._show_android_notification(title, message)
                elif PLYER_AVAILABLE:
                    self._show_plyer_notification(title, message)
                else:
                    Logger.info(f"Notification locale: {title} - {message}")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur notification locale: {e}")
    
    def add_notification_callback(self, callback: Callable):
        """Ajouter un callback pour les nouvelles notifications"""
        if callback not in self.notification_callbacks:
            self.notification_callbacks.append(callback)
    
    def remove_notification_callback(self, callback: Callable):
        """Supprimer un callback de notification"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
    
    def _notify_callbacks(self, notifications: List[Dict]):
        """Notifier tous les callbacks enregistrés"""
        for callback in self.notification_callbacks:
            try:
                callback(notifications)
            except Exception as e:
                Logger.error(f"NotificationManager: Erreur callback: {e}")
    
    def update_preferences(self, preferences: Dict):
        """Mettre à jour les préférences de notification"""
        try:
            self.preferences.update(preferences)
            
            # Sauvegarder les préférences
            from .storage_manager import StorageManager
            storage = StorageManager()
            storage.save_notification_preferences(preferences)
            
            Logger.info("NotificationManager: Préférences mises à jour")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur mise à jour préférences: {e}")
    
    def load_preferences(self):
        """Charger les préférences depuis le stockage"""
        try:
            from .storage_manager import StorageManager
            storage = StorageManager()
            self.preferences = storage.get_notification_preferences()
            Logger.info("NotificationManager: Préférences chargées")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur chargement préférences: {e}")
    
    def get_preferences(self) -> Dict:
        """Récupérer les préférences actuelles"""
        return self.preferences.copy()
    
    def set_check_interval(self, interval: int):
        """Définir l'intervalle de vérification (en secondes)"""
        if interval >= 10:  # Minimum 10 secondes
            self.check_interval = interval
            Logger.info(f"NotificationManager: Intervalle défini à {interval}s")
        else:
            Logger.warning("NotificationManager: Intervalle minimum de 10 secondes")
    
    def force_check(self):
        """Forcer une vérification immédiate des notifications"""
        try:
            threading.Thread(target=self.check_notifications, daemon=True).start()
            Logger.info("NotificationManager: Vérification forcée démarrée")
        except Exception as e:
            Logger.error(f"NotificationManager: Erreur vérification forcée: {e}")
    
    def get_status(self) -> Dict:
        """Récupérer le statut du gestionnaire"""
        return {
            'running': self.is_running,
            'user_id': self.user_id,
            'check_interval': self.check_interval,
            'last_count': self.last_notification_count,
            'preferences': self.preferences,
            'android_available': ANDROID_AVAILABLE,
            'plyer_available': PLYER_AVAILABLE
        }