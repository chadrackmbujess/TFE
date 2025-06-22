"""
Écran tableau de bord pour l'application mobile ITSM Compagnon
Vue d'ensemble des tickets, notifications et accès rapides
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerMenu
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem, MDList
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock


class DashboardScreen(Screen):
    """Écran principal du tableau de bord"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data = None
        self.stats_data = {}
        self.recent_tickets = []
        self.notifications_count = 0
        self.build_ui()
    
    def build_ui(self):
        """Construire l'interface utilisateur"""
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical'
        )
        
        # Barre d'outils
        self.toolbar = MDTopAppBar(
            title="ITSM Compagnon",
            left_action_items=[["menu", lambda x: self.open_navigation_drawer()]],
            right_action_items=[
                ["bell", lambda x: self.go_to_notifications()],
                ["logout", lambda x: self.logout()]
            ]
        )
        
        # Zone de contenu avec refresh
        self.refresh_layout = MDScrollViewRefreshLayout(
            refresh_callback=self.refresh_data,
            root_layout=main_layout
        )
        
        # Scroll view pour le contenu
        scroll = MDScrollView()
        
        # Contenu principal
        self.content_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            adaptive_height=True
        )
        
        # Carte de bienvenue
        self.welcome_card = self.create_welcome_card()
        
        # Cartes de statistiques
        self.stats_layout = MDGridLayout(
            cols=2,
            spacing=dp(10),
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Créer les cartes de stats
        self.tickets_card = self.create_stat_card("Mes Tickets", "0", "ticket", "tickets")
        self.notifications_card = self.create_stat_card("Notifications", "0", "bell", "notifications")
        self.machines_card = self.create_stat_card("Machines", "0", "desktop-classic", "machines")
        self.urgent_card = self.create_stat_card("Urgents", "0", "alert", "tickets", {"priorite": "urgente"})
        
        self.stats_layout.add_widget(self.tickets_card)
        self.stats_layout.add_widget(self.notifications_card)
        self.stats_layout.add_widget(self.machines_card)
        self.stats_layout.add_widget(self.urgent_card)
        
        # Boutons d'accès rapide
        self.quick_actions_card = self.create_quick_actions_card()
        
        # Tickets récents
        self.recent_tickets_card = self.create_recent_tickets_card()
        
        # Assembler le contenu
        self.content_layout.add_widget(self.welcome_card)
        self.content_layout.add_widget(self.stats_layout)
        self.content_layout.add_widget(self.quick_actions_card)
        self.content_layout.add_widget(self.recent_tickets_card)
        
        scroll.add_widget(self.content_layout)
        self.refresh_layout.add_widget(scroll)
        
        # Assembler le layout principal
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.refresh_layout)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Charger les données initiales
        Clock.schedule_once(self.load_initial_data, 1)
    
    def create_welcome_card(self):
        """Créer la carte de bienvenue"""
        card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=dp(15),
            elevation=2
        )
        
        layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15)
        )
        
        # Icône utilisateur
        icon_layout = MDBoxLayout(
            size_hint_x=None,
            width=dp(60),
            orientation='vertical'
        )
        
        user_icon = MDLabel(
            text="👤",
            font_size="36sp",
            halign="center",
            size_hint_y=None,
            height=dp(50)
        )
        
        icon_layout.add_widget(user_icon)
        
        # Informations utilisateur
        info_layout = MDBoxLayout(
            orientation='vertical'
        )
        
        self.welcome_label = MDLabel(
            text="Bienvenue !",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        
        self.user_info_label = MDLabel(
            text="Chargement...",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(25)
        )
        
        self.last_sync_label = MDLabel(
            text="",
            theme_text_color="Hint",
            font_size="12sp",
            size_hint_y=None,
            height=dp(20)
        )
        
        info_layout.add_widget(self.welcome_label)
        info_layout.add_widget(self.user_info_label)
        info_layout.add_widget(self.last_sync_label)
        
        layout.add_widget(icon_layout)
        layout.add_widget(info_layout)
        
        card.add_widget(layout)
        return card
    
    def create_stat_card(self, title, value, icon, screen, filters=None):
        """Créer une carte de statistique"""
        card = MDCard(
            size_hint_y=None,
            height=dp(120),
            padding=dp(15),
            elevation=2,
            on_release=lambda x: self.navigate_to_screen(screen, filters)
        )
        
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(5)
        )
        
        # Icône et valeur
        top_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10)
        )
        
        icon_label = MDLabel(
            text=f"[font=Icons]{icon}[/font]" if icon else "📊",
            markup=True,
            font_size="24sp",
            size_hint_x=None,
            width=dp(40),
            halign="center"
        )
        
        value_label = MDLabel(
            text=value,
            theme_text_color="Primary",
            font_style="H4",
            halign="right"
        )
        
        top_layout.add_widget(icon_label)
        top_layout.add_widget(value_label)
        
        # Titre
        title_label = MDLabel(
            text=title,
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )
        
        layout.add_widget(top_layout)
        layout.add_widget(title_label)
        
        card.add_widget(layout)
        
        # Stocker les références pour mise à jour
        card.value_label = value_label
        card.title = title
        
        return card
    
    def create_quick_actions_card(self):
        """Créer la carte d'actions rapides"""
        card = MDCard(
            size_hint_y=None,
            height=dp(180),
            padding=dp(15),
            elevation=2
        )
        
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15)
        )
        
        # Titre
        title = MDLabel(
            text="Actions rapides",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        
        # Boutons d'action
        actions_layout = MDGridLayout(
            cols=2,
            spacing=dp(10),
            adaptive_height=True,
            size_hint_y=None
        )
        
        # Scanner QR
        qr_button = MDRaisedButton(
            text="Scanner QR",
            icon="qrcode-scan",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: self.navigate_to_screen('qr_scanner')
        )
        
        # Nouveau ticket
        ticket_button = MDRaisedButton(
            text="Nouveau Ticket",
            icon="plus",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: self.create_new_ticket()
        )
        
        # Mes machines
        machines_button = MDRaisedButton(
            text="Mes Machines",
            icon="desktop-classic",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: self.navigate_to_screen('machines')
        )
        
        # Notifications
        notif_button = MDRaisedButton(
            text="Notifications",
            icon="bell",
            size_hint_y=None,
            height=dp(50),
            on_release=lambda x: self.navigate_to_screen('notifications')
        )
        
        actions_layout.add_widget(qr_button)
        actions_layout.add_widget(ticket_button)
        actions_layout.add_widget(machines_button)
        actions_layout.add_widget(notif_button)
        
        layout.add_widget(title)
        layout.add_widget(actions_layout)
        
        card.add_widget(layout)
        return card
    
    def create_recent_tickets_card(self):
        """Créer la carte des tickets récents"""
        card = MDCard(
            size_hint_y=None,
            height=dp(300),
            padding=dp(15),
            elevation=2
        )
        
        layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        
        # En-tête
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        title = MDLabel(
            text="Tickets récents",
            theme_text_color="Primary",
            font_style="H6"
        )
        
        see_all_button = MDFlatButton(
            text="Voir tout",
            size_hint_x=None,
            width=dp(80),
            on_release=lambda x: self.navigate_to_screen('tickets')
        )
        
        header_layout.add_widget(title)
        header_layout.add_widget(see_all_button)
        
        # Liste des tickets
        self.tickets_list = MDList()
        
        # Placeholder
        placeholder = OneLineListItem(
            text="Chargement des tickets..."
        )
        self.tickets_list.add_widget(placeholder)
        
        layout.add_widget(header_layout)
        layout.add_widget(self.tickets_list)
        
        card.add_widget(layout)
        return card
    
    def load_initial_data(self, dt):
        """Charger les données initiales"""
        try:
            self.refresh_data()
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur chargement initial: {e}")
    
    def refresh_data(self, *args):
        """Actualiser toutes les données"""
        try:
            Logger.info("DashboardScreen: Actualisation des données")
            
            # Lancer les requêtes en parallèle
            import threading
            
            threads = [
                threading.Thread(target=self.load_stats, daemon=True),
                threading.Thread(target=self.load_recent_tickets, daemon=True),
                threading.Thread(target=self.load_notifications_count, daemon=True)
            ]
            
            for thread in threads:
                thread.start()
            
            # Mettre à jour l'heure de dernière synchronisation
            self.update_last_sync()
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur actualisation: {e}")
            self.show_error("Erreur lors de l'actualisation")
    
    def load_stats(self):
        """Charger les statistiques"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            # Charger les tickets
            success, tickets = app.api_client.get_tickets()
            if success:
                my_tickets = len(tickets)
                urgent_tickets = len([t for t in tickets if t.get('priorite') == 'urgente'])
                
                Clock.schedule_once(
                    lambda dt: self.update_stat_card(self.tickets_card, str(my_tickets)), 0
                )
                Clock.schedule_once(
                    lambda dt: self.update_stat_card(self.urgent_card, str(urgent_tickets)), 0
                )
            
            # Charger les machines
            success, machines = app.api_client.get_machines()
            if success:
                my_machines = len(machines)
                Clock.schedule_once(
                    lambda dt: self.update_stat_card(self.machines_card, str(my_machines)), 0
                )
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur chargement stats: {e}")
    
    def load_recent_tickets(self):
        """Charger les tickets récents"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            success, tickets = app.api_client.get_tickets({'limit': 5})
            if success:
                Clock.schedule_once(
                    lambda dt: self.update_recent_tickets(tickets), 0
                )
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur chargement tickets récents: {e}")
    
    def load_notifications_count(self):
        """Charger le nombre de notifications"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            count = app.api_client.get_unread_count()
            Clock.schedule_once(
                lambda dt: self.update_stat_card(self.notifications_card, str(count)), 0
            )
            
            # Mettre à jour l'icône de la toolbar
            if count > 0:
                Clock.schedule_once(
                    lambda dt: self.update_notification_badge(count), 0
                )
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur chargement notifications: {e}")
    
    def update_stat_card(self, card, value):
        """Mettre à jour une carte de statistique"""
        try:
            if hasattr(card, 'value_label'):
                card.value_label.text = value
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur mise à jour stat: {e}")
    
    def update_recent_tickets(self, tickets):
        """Mettre à jour la liste des tickets récents"""
        try:
            self.tickets_list.clear_widgets()
            
            if not tickets:
                placeholder = OneLineListItem(text="Aucun ticket récent")
                self.tickets_list.add_widget(placeholder)
                return
            
            for ticket in tickets[:5]:  # Limiter à 5 tickets
                # Déterminer l'icône selon la priorité
                priority = ticket.get('priorite', 'normale')
                if priority == 'urgente':
                    icon = "🔴"
                elif priority == 'haute':
                    icon = "🟠"
                else:
                    icon = "🟢"
                
                # Créer l'item de liste
                item = ThreeLineListItem(
                    text=f"{icon} {ticket.get('numero', 'N/A')}",
                    secondary_text=ticket.get('titre', 'Sans titre')[:50],
                    tertiary_text=f"Statut: {ticket.get('statut', 'Inconnu')}",
                    on_release=lambda x, t=ticket: self.open_ticket_detail(t)
                )
                
                self.tickets_list.add_widget(item)
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur mise à jour tickets récents: {e}")
    
    def update_notification_badge(self, count):
        """Mettre à jour le badge de notifications"""
        try:
            # Modifier l'icône de notification dans la toolbar
            if count > 0:
                self.toolbar.right_action_items = [
                    ["bell-badge", lambda x: self.go_to_notifications()],
                    ["logout", lambda x: self.logout()]
                ]
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur badge notification: {e}")
    
    def update_last_sync(self):
        """Mettre à jour l'heure de dernière synchronisation"""
        try:
            from datetime import datetime
            now = datetime.now()
            sync_text = f"Dernière sync: {now.strftime('%H:%M')}"
            self.last_sync_label.text = sync_text
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur mise à jour sync: {e}")
    
    def update_user_info(self, user_data):
        """Mettre à jour les informations utilisateur"""
        try:
            self.user_data = user_data
            
            if user_data:
                name = user_data.get('nom_complet', user_data.get('username', 'Utilisateur'))
                role = user_data.get('role', 'Technicien')
                structure = user_data.get('structure', {}).get('nom', 'Structure inconnue')
                
                self.welcome_label.text = f"Bienvenue, {name} !"
                self.user_info_label.text = f"{role} - {structure}"
            
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur mise à jour utilisateur: {e}")
    
    def navigate_to_screen(self, screen_name, filters=None):
        """Naviguer vers un écran"""
        try:
            self.manager.current = screen_name
            
            # Passer les filtres si nécessaire
            if filters and hasattr(self.manager.get_screen(screen_name), 'apply_filters'):
                screen = self.manager.get_screen(screen_name)
                screen.apply_filters(filters)
                
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur navigation: {e}")
    
    def create_new_ticket(self):
        """Créer un nouveau ticket"""
        try:
            self.manager.current = 'tickets'
            tickets_screen = self.manager.get_screen('tickets')
            if hasattr(tickets_screen, 'show_create_ticket'):
                tickets_screen.show_create_ticket()
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur création ticket: {e}")
    
    def open_ticket_detail(self, ticket):
        """Ouvrir les détails d'un ticket"""
        try:
            self.manager.current = 'tickets'
            tickets_screen = self.manager.get_screen('tickets')
            if hasattr(tickets_screen, 'show_ticket_detail'):
                tickets_screen.show_ticket_detail(ticket)
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur ouverture ticket: {e}")
    
    def go_to_notifications(self):
        """Aller aux notifications"""
        try:
            self.manager.current = 'notifications'
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur navigation notifications: {e}")
    
    def open_navigation_drawer(self):
        """Ouvrir le tiroir de navigation"""
        try:
            # Placeholder pour le tiroir de navigation
            self.show_info("Menu de navigation à implémenter")
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur tiroir navigation: {e}")
    
    def logout(self):
        """Déconnecter l'utilisateur"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            app.logout()
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur déconnexion: {e}")
    
    def show_info(self, message):
        """Afficher un message d'information"""
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
            ).open()
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur affichage info: {e}")
    
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
            Logger.error(f"DashboardScreen: Erreur affichage erreur: {e}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            # Actualiser les données quand on revient sur le dashboard
            Clock.schedule_once(lambda dt: self.refresh_data(), 0.5)
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            Logger.info("DashboardScreen: Écran quitté")
        except Exception as e:
            Logger.error(f"DashboardScreen: Erreur on_leave: {e}")