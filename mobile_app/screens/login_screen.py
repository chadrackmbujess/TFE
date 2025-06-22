"""
Écran de connexion pour l'application mobile ITSM Compagnon
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDTextButton
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.logger import Logger
from kivymd.uix.snackbar import MDSnackbar
from kivy.clock import Clock


class LoginScreen(Screen):
    """Écran de connexion utilisateur"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        """Construire l'interface utilisateur"""
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            adaptive_height=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.9, None)
        )
        
        # Logo/Titre
        logo_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            adaptive_height=True,
            size_hint_y=None,
            height=dp(120)
        )
        
        # Logo (placeholder)
        logo = Image(
            source='assets/images/logo.png',  # À remplacer par le vrai logo
            size_hint=(None, None),
            size=(dp(80), dp(80)),
            pos_hint={'center_x': 0.5}
        )
        
        # Titre
        title = MDLabel(
            text="ITSM Compagnon",
            theme_text_color="Primary",
            font_style="H4",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )
        
        logo_layout.add_widget(logo)
        logo_layout.add_widget(title)
        
        # Carte de connexion
        login_card = MDCard(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None,
            height=dp(400),
            elevation=3
        )
        
        # Titre de la carte
        card_title = MDLabel(
            text="Connexion",
            theme_text_color="Primary",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        
        # Champ nom d'utilisateur
        self.username_field = MDTextField(
            hint_text="Nom d'utilisateur",
            icon_left="account",
            size_hint_y=None,
            height=dp(60)
        )
        
        # Champ mot de passe
        self.password_field = MDTextField(
            hint_text="Mot de passe",
            icon_left="lock",
            password=True,
            size_hint_y=None,
            height=dp(60)
        )
        
        # Layout pour "Se souvenir de moi"
        remember_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            adaptive_height=True,
            size_hint_y=None,
            height=dp(40)
        )
        
        self.remember_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'center_y': 0.5}
        )
        
        remember_label = MDLabel(
            text="Se souvenir de moi",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30),
            pos_hint={'center_y': 0.5}
        )
        
        remember_layout.add_widget(self.remember_checkbox)
        remember_layout.add_widget(remember_label)
        
        # Bouton de connexion
        self.login_button = MDRaisedButton(
            text="Se connecter",
            size_hint_y=None,
            height=dp(50),
            on_release=self.on_login_pressed
        )
        
        # Barre de progression (cachée par défaut)
        self.progress_bar = MDProgressBar(
            size_hint_y=None,
            height=dp(4),
            opacity=0
        )
        
        # Bouton paramètres serveur
        server_button = MDTextButton(
            text="Paramètres serveur",
            size_hint_y=None,
            height=dp(40),
            on_release=self.show_server_settings
        )
        
        # Assembler la carte
        login_card.add_widget(card_title)
        login_card.add_widget(self.username_field)
        login_card.add_widget(self.password_field)
        login_card.add_widget(remember_layout)
        login_card.add_widget(self.login_button)
        login_card.add_widget(self.progress_bar)
        login_card.add_widget(server_button)
        
        # Assembler le layout principal
        main_layout.add_widget(logo_layout)
        main_layout.add_widget(login_card)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Charger les identifiants sauvegardés
        Clock.schedule_once(self.load_saved_credentials, 0.5)
    
    def load_saved_credentials(self, dt):
        """Charger les identifiants sauvegardés"""
        try:
            from ..utils.storage_manager import StorageManager
            storage = StorageManager()
            credentials = storage.get_credentials()
            
            if credentials:
                self.username_field.text = credentials['username']
                self.password_field.text = credentials['password']
                self.remember_checkbox.active = True
                Logger.info("LoginScreen: Identifiants chargés")
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur chargement identifiants: {e}")
    
    def on_login_pressed(self, button):
        """Gérer le clic sur le bouton de connexion"""
        username = self.username_field.text.strip()
        password = self.password_field.text.strip()
        remember_me = self.remember_checkbox.active
        
        # Validation des champs
        if not username:
            self.show_error("Veuillez saisir votre nom d'utilisateur")
            return
        
        if not password:
            self.show_error("Veuillez saisir votre mot de passe")
            return
        
        # Démarrer la connexion
        self.start_login(username, password, remember_me)
    
    def start_login(self, username, password, remember_me):
        """Démarrer le processus de connexion"""
        try:
            # Afficher la barre de progression
            self.show_progress(True)
            self.login_button.disabled = True
            
            # Effectuer la connexion dans un thread séparé
            import threading
            login_thread = threading.Thread(
                target=self.perform_login,
                args=(username, password, remember_me),
                daemon=True
            )
            login_thread.start()
            
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur démarrage connexion: {e}")
            self.show_progress(False)
            self.login_button.disabled = False
            self.show_error(f"Erreur: {str(e)}")
    
    def perform_login(self, username, password, remember_me):
        """Effectuer la connexion (dans un thread séparé)"""
        try:
            # Obtenir l'application principale
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            # Effectuer la connexion
            success, message = app.login(username, password, remember_me)
            
            # Programmer la mise à jour de l'UI dans le thread principal
            Clock.schedule_once(lambda dt: self.on_login_result(success, message), 0)
            
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur connexion: {e}")
            error_message = str(e)
            Clock.schedule_once(lambda dt: self.on_login_result(False, error_message), 0)
    
    def on_login_result(self, success, message):
        """Gérer le résultat de la connexion"""
        try:
            # Masquer la barre de progression
            self.show_progress(False)
            self.login_button.disabled = False
            
            if success:
                Logger.info("LoginScreen: Connexion réussie")
                self.show_success("Connexion réussie")
                # L'application se charge de changer d'écran
            else:
                Logger.warning(f"LoginScreen: Échec connexion: {message}")
                self.show_error(message)
                
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur traitement résultat: {e}")
    
    def show_progress(self, show):
        """Afficher/masquer la barre de progression"""
        try:
            if show:
                self.progress_bar.opacity = 1
            else:
                self.progress_bar.opacity = 0
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur affichage progression: {e}")
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        try:
            MDSnackbar(
                MDLabel(
                    text=message,
                    theme_text_color="Custom",
                    text_color="white"
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
                md_bg_color="red"
            ).open()
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur affichage erreur: {e}")
    
    def show_success(self, message):
        """Afficher un message de succès"""
        try:
            MDSnackbar(
                MDLabel(
                    text=message,
                    theme_text_color="Custom",
                    text_color="white"
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
                md_bg_color="green"
            ).open()
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur affichage succès: {e}")
    
    def show_server_settings(self, button):
        """Afficher les paramètres du serveur"""
        try:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.textfield import MDTextField
            from kivymd.uix.button import MDFlatButton
            
            # Champ URL du serveur
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            current_url = app.api_client.base_url if app.api_client else "http://127.0.0.1:8000"
            
            server_field = MDTextField(
                hint_text="URL du serveur (ex: http://192.168.1.100:8000)",
                text=current_url  # URL actuellement utilisée
            )
            
            def save_server_url(instance):
                try:
                    from ..utils.storage_manager import StorageManager
                    storage = StorageManager()
                    storage.save_setting('server_url', server_field.text.strip())
                    self.show_success("URL du serveur sauvegardée")
                    dialog.dismiss()
                except Exception as e:
                    self.show_error(f"Erreur sauvegarde: {str(e)}")
            
            dialog = MDDialog(
                title="Paramètres du serveur",
                type="custom",
                content_cls=server_field,
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="SAUVEGARDER",
                        on_release=save_server_url
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur paramètres serveur: {e}")
            self.show_error("Erreur lors de l'ouverture des paramètres")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            # Focus sur le champ nom d'utilisateur si vide
            if not self.username_field.text:
                self.username_field.focus = True
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            # Réinitialiser l'état
            self.show_progress(False)
            self.login_button.disabled = False
        except Exception as e:
            Logger.error(f"LoginScreen: Erreur on_leave: {e}")