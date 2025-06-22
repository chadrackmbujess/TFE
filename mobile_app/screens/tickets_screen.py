"""
Écran de gestion des tickets pour l'application mobile ITSM Compagnon
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.chip import MDChip
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock


class TicketsScreen(Screen):
    """Écran de gestion des tickets"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tickets_data = []
        self.current_filters = {}
        self.build_ui()
    
    def build_ui(self):
        """Construire l'interface utilisateur"""
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical'
        )
        
        # Barre d'outils
        self.toolbar = MDTopAppBar(
            title="Mes Tickets",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["filter", lambda x: self.show_filters()],
                ["plus", lambda x: self.show_create_ticket()]
            ]
        )
        
        # Zone de filtres (cachée par défaut)
        self.filters_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            padding=dp(15),
            adaptive_height=True,
            size_hint_y=None,
            height=0,
            opacity=0
        )
        
        # Zone de contenu avec refresh
        self.refresh_layout = MDScrollViewRefreshLayout(
            refresh_callback=self.refresh_tickets,
            root_layout=main_layout
        )
        
        # Scroll view pour la liste
        scroll = MDScrollView()
        
        # Liste des tickets
        self.tickets_list = MDList()
        
        # Placeholder initial
        self.add_placeholder("Chargement des tickets...")
        
        scroll.add_widget(self.tickets_list)
        self.refresh_layout.add_widget(scroll)
        
        # Assembler le layout principal
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.filters_layout)
        main_layout.add_widget(self.refresh_layout)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Charger les tickets
        Clock.schedule_once(self.load_tickets, 1)
    
    def load_tickets(self, dt=None):
        """Charger la liste des tickets"""
        try:
            import threading
            thread = threading.Thread(target=self.fetch_tickets, daemon=True)
            thread.start()
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur chargement tickets: {e}")
            self.show_error("Erreur lors du chargement des tickets")
    
    def fetch_tickets(self):
        """Récupérer les tickets depuis l'API"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            success, tickets = app.api_client.get_tickets(self.current_filters)
            
            if success:
                self.tickets_data = tickets
                Clock.schedule_once(lambda dt: self.update_tickets_list(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error("Erreur lors du chargement"), 0)
                
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur fetch tickets: {e}")
            error_message = f"Erreur: {str(e)}"
            Clock.schedule_once(lambda dt: self.show_error(error_message), 0)
    
    def update_tickets_list(self):
        """Mettre à jour la liste des tickets"""
        try:
            self.tickets_list.clear_widgets()
            
            if not self.tickets_data:
                self.add_placeholder("Aucun ticket trouvé")
                return
            
            for ticket in self.tickets_data:
                # Déterminer l'icône selon la priorité
                priority = ticket.get('priorite', 'normale')
                if priority == 'urgente':
                    icon = "🔴"
                elif priority == 'haute':
                    icon = "🟠"
                else:
                    icon = "🟢"
                
                # Déterminer la couleur selon le statut
                status = ticket.get('statut', 'nouveau')
                if status == 'resolu':
                    status_icon = "✅"
                elif status == 'en_cours':
                    status_icon = "⏳"
                else:
                    status_icon = "📋"
                
                # Créer l'item de liste
                item = ThreeLineListItem(
                    text=f"{icon} #{ticket.get('numero', 'N/A')} - {ticket.get('titre', 'Sans titre')[:30]}",
                    secondary_text=f"{status_icon} {status.replace('_', ' ').title()}",
                    tertiary_text=f"Créé le: {ticket.get('date_creation', 'Inconnue')[:10]}",
                    on_release=lambda x, t=ticket: self.show_ticket_detail(t)
                )
                
                self.tickets_list.add_widget(item)
                
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur mise à jour liste: {e}")
    
    def add_placeholder(self, text):
        """Ajouter un placeholder à la liste"""
        placeholder = OneLineListItem(text=text)
        self.tickets_list.add_widget(placeholder)
    
    def refresh_tickets(self, *args):
        """Actualiser la liste des tickets"""
        self.load_tickets()
    
    def show_filters(self):
        """Afficher/masquer les filtres"""
        try:
            if self.filters_layout.height == 0:
                # Afficher les filtres
                self.create_filters()
                self.filters_layout.height = dp(60)
                self.filters_layout.opacity = 1
            else:
                # Masquer les filtres
                self.filters_layout.height = 0
                self.filters_layout.opacity = 0
                
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur filtres: {e}")
    
    def create_filters(self):
        """Créer les filtres"""
        try:
            self.filters_layout.clear_widgets()
            
            # Filtre par statut
            status_chip = MDChip(
                text="Tous",
                icon="filter",
                on_release=lambda x: self.show_status_filter()
            )
            
            # Filtre par priorité
            priority_chip = MDChip(
                text="Toutes priorités",
                icon="alert",
                on_release=lambda x: self.show_priority_filter()
            )
            
            # Bouton reset
            reset_button = MDFlatButton(
                text="Reset",
                on_release=lambda x: self.reset_filters()
            )
            
            self.filters_layout.add_widget(status_chip)
            self.filters_layout.add_widget(priority_chip)
            self.filters_layout.add_widget(reset_button)
            
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur création filtres: {e}")
    
    def show_status_filter(self):
        """Afficher le filtre de statut"""
        # Placeholder pour le filtre de statut
        self.show_info("Filtre de statut à implémenter")
    
    def show_priority_filter(self):
        """Afficher le filtre de priorité"""
        # Placeholder pour le filtre de priorité
        self.show_info("Filtre de priorité à implémenter")
    
    def reset_filters(self):
        """Réinitialiser les filtres"""
        self.current_filters = {}
        self.load_tickets()
        self.show_info("Filtres réinitialisés")
    
    def show_create_ticket(self):
        """Afficher le formulaire de création de ticket"""
        try:
            # Créer le formulaire
            content = MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                adaptive_height=True
            )
            
            # Champ titre
            title_field = MDTextField(
                hint_text="Titre du ticket",
                required=True
            )
            
            # Champ description
            desc_field = MDTextField(
                hint_text="Description du problème",
                multiline=True,
                max_text_length=500
            )
            
            content.add_widget(title_field)
            content.add_widget(desc_field)
            
            # Créer le dialogue
            def create_ticket(instance):
                if not title_field.text.strip():
                    self.show_error("Le titre est obligatoire")
                    return
                
                self.create_new_ticket(title_field.text, desc_field.text)
                dialog.dismiss()
            
            dialog = MDDialog(
                title="Nouveau Ticket",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="CRÉER",
                        on_release=create_ticket
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur création ticket: {e}")
            self.show_error("Erreur lors de l'ouverture du formulaire")
    
    def create_new_ticket(self, title, description):
        """Créer un nouveau ticket"""
        try:
            import threading
            
            def create_ticket_thread():
                try:
                    from kivymd.app import MDApp
                    app = MDApp.get_running_app()
                    
                    ticket_data = {
                        'titre': title,
                        'description': description,
                        'priorite': 'normale',
                        'statut': 'nouveau'
                    }
                    
                    success, result = app.api_client.create_ticket(ticket_data)
                    
                    if success:
                        Clock.schedule_once(lambda dt: self.on_ticket_created(), 0)
                    else:
                        Clock.schedule_once(lambda dt: self.show_error("Erreur lors de la création"), 0)
                        
                except Exception as e:
                    Logger.error(f"TicketsScreen: Erreur création: {e}")
                    error_message = f"Erreur: {str(e)}"
                    Clock.schedule_once(lambda dt: self.show_error(error_message), 0)
            
            thread = threading.Thread(target=create_ticket_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur nouveau ticket: {e}")
            self.show_error("Erreur lors de la création du ticket")
    
    def on_ticket_created(self):
        """Callback après création d'un ticket"""
        self.show_success("Ticket créé avec succès")
        self.load_tickets()
    
    def show_ticket_detail(self, ticket):
        """Afficher les détails d'un ticket"""
        try:
            # Créer le contenu des détails
            content = MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                adaptive_height=True
            )
            
            # Informations du ticket
            info_text = f"""
Numéro: #{ticket.get('numero', 'N/A')}
Titre: {ticket.get('titre', 'Sans titre')}
Statut: {ticket.get('statut', 'Inconnu')}
Priorité: {ticket.get('priorite', 'Normale')}
Créé le: {ticket.get('date_creation', 'Inconnue')}

Description:
{ticket.get('description', 'Aucune description')}
            """.strip()
            
            info_label = MDLabel(
                text=info_text,
                theme_text_color="Primary",
                size_hint_y=None
            )
            info_label.bind(texture_size=info_label.setter('size'))
            
            content.add_widget(info_label)
            
            # Créer le dialogue
            dialog = MDDialog(
                title=f"Ticket #{ticket.get('numero', 'N/A')}",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="FERMER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur détails ticket: {e}")
            self.show_error("Erreur lors de l'affichage des détails")
    
    def apply_filters(self, filters):
        """Appliquer des filtres externes"""
        self.current_filters.update(filters)
        self.load_tickets()
    
    def go_back(self):
        """Retourner au dashboard"""
        try:
            self.manager.current = 'dashboard'
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur retour: {e}")
    
    def show_info(self, message):
        """Afficher un message d'information"""
        try:
            Snackbar(text=message).open()
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur affichage info: {e}")
    
    def show_success(self, message):
        """Afficher un message de succès"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.2, 0.8, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur affichage succès: {e}")
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.8, 0.2, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur affichage erreur: {e}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            # Actualiser les tickets quand on arrive sur l'écran
            Clock.schedule_once(lambda dt: self.load_tickets(), 0.5)
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            # Masquer les filtres
            self.filters_layout.height = 0
            self.filters_layout.opacity = 0
        except Exception as e:
            Logger.error(f"TicketsScreen: Erreur on_leave: {e}")