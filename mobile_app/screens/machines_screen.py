"""
Écran de gestion des machines pour l'application mobile ITSM Compagnon
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


class MachinesScreen(Screen):
    """Écran de gestion des machines"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.machines_data = []
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
            title="Mes Machines",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["filter", lambda x: self.show_filters()],
                ["qrcode-scan", lambda x: self.scan_machine()]
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
            refresh_callback=self.refresh_machines,
            root_layout=main_layout
        )
        
        # Scroll view pour la liste
        scroll = MDScrollView()
        
        # Liste des machines
        self.machines_list = MDList()
        
        # Placeholder initial
        self.add_placeholder("Chargement des machines...")
        
        scroll.add_widget(self.machines_list)
        self.refresh_layout.add_widget(scroll)
        
        # Assembler le layout principal
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.filters_layout)
        main_layout.add_widget(self.refresh_layout)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Charger les machines
        Clock.schedule_once(self.load_machines, 1)
    
    def load_machines(self, dt=None):
        """Charger la liste des machines"""
        try:
            import threading
            thread = threading.Thread(target=self.fetch_machines, daemon=True)
            thread.start()
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur chargement machines: {e}")
            self.show_error("Erreur lors du chargement des machines")
    
    def fetch_machines(self):
        """Récupérer les machines depuis l'API"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            success, machines = app.api_client.get_machines(self.current_filters)
            
            if success:
                self.machines_data = machines
                Clock.schedule_once(lambda dt: self.update_machines_list(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error("Erreur lors du chargement"), 0)
                
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur fetch machines: {e}")
            error_message = f"Erreur: {str(e)}"
            Clock.schedule_once(lambda dt: self.show_error(error_message), 0)
    
    def update_machines_list(self):
        """Mettre à jour la liste des machines"""
        try:
            self.machines_list.clear_widgets()
            
            if not self.machines_data:
                self.add_placeholder("Aucune machine trouvée")
                return
            
            for machine in self.machines_data:
                # Déterminer l'icône selon le type
                machine_type = machine.get('type', 'ordinateur')
                if machine_type == 'serveur':
                    icon = "🖥️"
                elif machine_type == 'portable':
                    icon = "💻"
                elif machine_type == 'imprimante':
                    icon = "🖨️"
                else:
                    icon = "🖥️"
                
                # Déterminer la couleur selon le statut
                status = machine.get('statut', 'actif')
                if status == 'actif':
                    status_icon = "🟢"
                elif status == 'maintenance':
                    status_icon = "🟠"
                elif status == 'hors_service':
                    status_icon = "🔴"
                else:
                    status_icon = "⚪"
                
                # Créer l'item de liste
                item = ThreeLineListItem(
                    text=f"{icon} {machine.get('nom', 'Machine sans nom')}",
                    secondary_text=f"{status_icon} {status.replace('_', ' ').title()} - {machine.get('type', 'Type inconnu')}",
                    tertiary_text=f"IP: {machine.get('adresse_ip', 'Non définie')} | Utilisateur: {machine.get('utilisateur', 'Non assigné')}",
                    on_release=lambda x, m=machine: self.show_machine_detail(m)
                )
                
                self.machines_list.add_widget(item)
                
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur mise à jour liste: {e}")
    
    def add_placeholder(self, text):
        """Ajouter un placeholder à la liste"""
        placeholder = OneLineListItem(text=text)
        self.machines_list.add_widget(placeholder)
    
    def refresh_machines(self, *args):
        """Actualiser la liste des machines"""
        self.load_machines()
    
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
            Logger.error(f"MachinesScreen: Erreur filtres: {e}")
    
    def create_filters(self):
        """Créer les filtres"""
        try:
            self.filters_layout.clear_widgets()
            
            # Filtre par type
            type_chip = MDChip(
                text="Tous types",
                icon="desktop-classic",
                on_release=lambda x: self.show_type_filter()
            )
            
            # Filtre par statut
            status_chip = MDChip(
                text="Tous statuts",
                icon="circle",
                on_release=lambda x: self.show_status_filter()
            )
            
            # Bouton reset
            reset_button = MDFlatButton(
                text="Reset",
                on_release=lambda x: self.reset_filters()
            )
            
            self.filters_layout.add_widget(type_chip)
            self.filters_layout.add_widget(status_chip)
            self.filters_layout.add_widget(reset_button)
            
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur création filtres: {e}")
    
    def show_type_filter(self):
        """Afficher le filtre de type"""
        # Placeholder pour le filtre de type
        self.show_info("Filtre de type à implémenter")
    
    def show_status_filter(self):
        """Afficher le filtre de statut"""
        # Placeholder pour le filtre de statut
        self.show_info("Filtre de statut à implémenter")
    
    def reset_filters(self):
        """Réinitialiser les filtres"""
        self.current_filters = {}
        self.load_machines()
        self.show_info("Filtres réinitialisés")
    
    def scan_machine(self):
        """Scanner une machine via QR code"""
        try:
            self.manager.current = 'qr_scanner'
            # Le scanner redirigera vers les détails de la machine
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur scan: {e}")
            self.show_error("Erreur lors de l'ouverture du scanner")
    
    def show_machine_detail(self, machine):
        """Afficher les détails d'une machine"""
        try:
            # Créer le contenu des détails
            content = MDBoxLayout(
                orientation='vertical',
                spacing=dp(10),
                adaptive_height=True
            )
            
            # Informations de la machine
            info_text = f"""
Nom: {machine.get('nom', 'Non défini')}
Type: {machine.get('type', 'Inconnu')}
Statut: {machine.get('statut', 'Inconnu')}
Adresse IP: {machine.get('adresse_ip', 'Non définie')}
Utilisateur: {machine.get('utilisateur', 'Non assigné')}
Localisation: {machine.get('localisation', 'Non définie')}

Spécifications:
OS: {machine.get('systeme_exploitation', 'Inconnu')}
RAM: {machine.get('memoire_ram', 'Non définie')}
Stockage: {machine.get('stockage', 'Non défini')}

Dernière mise à jour: {machine.get('derniere_maj', 'Inconnue')}
            """.strip()
            
            info_label = MDLabel(
                text=info_text,
                theme_text_color="Primary",
                size_hint_y=None
            )
            info_label.bind(texture_size=info_label.setter('size'))
            
            content.add_widget(info_label)
            
            # Boutons d'action
            actions_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                adaptive_height=True,
                size_hint_y=None,
                height=dp(40)
            )
            
            ticket_button = MDFlatButton(
                text="Créer Ticket",
                on_release=lambda x: self.create_ticket_for_machine(machine, dialog)
            )
            
            actions_layout.add_widget(ticket_button)
            content.add_widget(actions_layout)
            
            # Créer le dialogue
            dialog = MDDialog(
                title=f"Machine: {machine.get('nom', 'Sans nom')}",
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
            Logger.error(f"MachinesScreen: Erreur détails machine: {e}")
            self.show_error("Erreur lors de l'affichage des détails")
    
    def create_ticket_for_machine(self, machine, dialog):
        """Créer un ticket pour une machine"""
        try:
            dialog.dismiss()
            
            # Aller à l'écran des tickets avec la machine pré-sélectionnée
            self.manager.current = 'tickets'
            tickets_screen = self.manager.get_screen('tickets')
            
            # Pré-remplir le formulaire avec les infos de la machine
            if hasattr(tickets_screen, 'show_create_ticket'):
                tickets_screen.show_create_ticket()
                
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur création ticket: {e}")
            self.show_error("Erreur lors de la création du ticket")
    
    def apply_filters(self, filters):
        """Appliquer des filtres externes"""
        self.current_filters.update(filters)
        self.load_machines()
    
    def go_back(self):
        """Retourner au dashboard"""
        try:
            self.manager.current = 'dashboard'
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur retour: {e}")
    
    def show_info(self, message):
        """Afficher un message d'information"""
        try:
            Snackbar(text=message).open()
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur affichage info: {e}")
    
    def show_success(self, message):
        """Afficher un message de succès"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.2, 0.8, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur affichage succès: {e}")
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.8, 0.2, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur affichage erreur: {e}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            # Actualiser les machines quand on arrive sur l'écran
            Clock.schedule_once(lambda dt: self.load_machines(), 0.5)
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            # Masquer les filtres
            self.filters_layout.height = 0
            self.filters_layout.opacity = 0
        except Exception as e:
            Logger.error(f"MachinesScreen: Erreur on_leave: {e}")