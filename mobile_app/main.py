"""
Application Mobile Compagnon ITSM
Point d'entrée principal de l'application mobile
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.metrics import dp

# Imports des écrans
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.tickets_screen import TicketsScreen
from screens.machines_screen import MachinesScreen
from screens.qr_scanner_screen import QRScannerScreen
from screens.notifications_screen import NotificationsScreen

# Imports des utilitaires
from utils.api_client import APIClient
from utils.notification_manager import NotificationManager
from utils.storage_manager import StorageManager


class ITSMCompanionApp(MDApp):
    """Application principale ITSM Compagnon"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ITSM Compagnon"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Gestionnaires
        self.api_client = APIClient()
        self.notification_manager = NotificationManager()
        self.storage_manager = StorageManager()
        
        # État de l'application
        self.user_data = None
        self.is_authenticated = False
        
    def build(self):
        """Construire l'interface utilisateur"""
        Logger.info("ITSMApp: Construction de l'interface utilisateur")
        
        # Créer le gestionnaire d'écrans
        self.screen_manager = ScreenManager()
        
        # Ajouter les écrans
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(DashboardScreen(name='dashboard'))
        self.screen_manager.add_widget(TicketsScreen(name='tickets'))
        self.screen_manager.add_widget(MachinesScreen(name='machines'))
        self.screen_manager.add_widget(QRScannerScreen(name='qr_scanner'))
        self.screen_manager.add_widget(NotificationsScreen(name='notifications'))
        
        # Démarrer sur l'écran de connexion
        self.screen_manager.current = 'login'
        
        # Vérifier si l'utilisateur est déjà connecté
        Clock.schedule_once(self.check_saved_login, 0.5)
        
        return self.screen_manager
    
    def check_saved_login(self, dt):
        """Vérifier si l'utilisateur a des identifiants sauvegardés"""
        try:
            saved_credentials = self.storage_manager.get_credentials()
            if saved_credentials:
                Logger.info("ITSMApp: Tentative de connexion automatique")
                self.auto_login(saved_credentials)
        except Exception as e:
            Logger.error(f"ITSMApp: Erreur lors de la vérification des identifiants: {e}")
    
    def auto_login(self, credentials):
        """Connexion automatique avec les identifiants sauvegardés"""
        try:
            success, user_data = self.api_client.login(
                credentials['username'], 
                credentials['password']
            )
            
            if success:
                self.user_data = user_data
                self.is_authenticated = True
                self.go_to_dashboard()
                Logger.info("ITSMApp: Connexion automatique réussie")
            else:
                Logger.warning("ITSMApp: Échec de la connexion automatique")
                # Supprimer les identifiants invalides
                self.storage_manager.clear_credentials()
                
        except Exception as e:
            Logger.error(f"ITSMApp: Erreur lors de la connexion automatique: {e}")
    
    def login(self, username, password, remember_me=False):
        """Gérer la connexion utilisateur"""
        try:
            success, user_data = self.api_client.login(username, password)
            
            if success:
                self.user_data = user_data
                self.is_authenticated = True
                
                # Sauvegarder les identifiants si demandé
                if remember_me:
                    self.storage_manager.save_credentials(username, password)
                
                # Initialiser les notifications push
                self.notification_manager.initialize(user_data.get('id'))
                
                self.go_to_dashboard()
                return True, "Connexion réussie"
            else:
                return False, "Identifiants incorrects"
                
        except Exception as e:
            Logger.error(f"ITSMApp: Erreur lors de la connexion: {e}")
            return False, f"Erreur de connexion: {str(e)}"
    
    def logout(self):
        """Déconnecter l'utilisateur"""
        try:
            # Nettoyer les données utilisateur
            self.user_data = None
            self.is_authenticated = False
            
            # Arrêter les notifications
            self.notification_manager.stop()
            
            # Nettoyer le cache API
            self.api_client.logout()
            
            # Retourner à l'écran de connexion
            self.screen_manager.current = 'login'
            
            Logger.info("ITSMApp: Déconnexion réussie")
            
        except Exception as e:
            Logger.error(f"ITSMApp: Erreur lors de la déconnexion: {e}")
    
    def go_to_dashboard(self):
        """Aller au tableau de bord"""
        self.screen_manager.current = 'dashboard'
        
        # Mettre à jour le tableau de bord avec les données utilisateur
        dashboard_screen = self.screen_manager.get_screen('dashboard')
        dashboard_screen.update_user_info(self.user_data)
    
    def show_snackbar(self, message, duration=3):
        """Afficher un message snackbar"""
        MDSnackbar(
            MDLabel(
                text=message,
                theme_text_color="Custom",
                text_color="white"
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            duration=duration
        ).open()
    
    def show_error_dialog(self, title, message):
        """Afficher une boîte de dialogue d'erreur"""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def on_pause(self):
        """Gérer la mise en pause de l'application"""
        Logger.info("ITSMApp: Application mise en pause")
        return True
    
    def on_resume(self):
        """Gérer la reprise de l'application"""
        Logger.info("ITSMApp: Application reprise")
        
        # Vérifier les nouvelles notifications
        if self.is_authenticated:
            self.notification_manager.check_notifications()


if __name__ == '__main__':
    # Configurer les logs
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer l'application
    ITSMCompanionApp().run()