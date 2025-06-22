"""
Écran de gestion des notifications pour l'application mobile ITSM Compagnon
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.refreshlayout import MDScrollViewRefreshLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.chip import MDChip
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock


class NotificationsScreen(Screen):
    """Écran de gestion des notifications"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notifications_data = []
        self.unread_count = 0
        self.build_ui()
    
    def build_ui(self):
        """Construire l'interface utilisateur"""
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical'
        )
        
        # Barre d'outils
        self.toolbar = MDTopAppBar(
            title="Notifications",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["check-all", lambda x: self.mark_all_read()],
                ["delete-sweep", lambda x: self.clear_all_notifications()]
            ]
        )
        
        # Zone de statistiques
        self.stats_card = self.create_stats_card()
        
        # Zone de contenu avec refresh
        self.refresh_layout = MDScrollViewRefreshLayout(
            refresh_callback=self.refresh_notifications,
            root_layout=main_layout
        )
        
        # Scroll view pour la liste
        scroll = MDScrollView()
        
        # Liste des notifications
        self.notifications_list = MDList()
        
        # Placeholder initial
        self.add_placeholder("Chargement des notifications...")
        
        scroll.add_widget(self.notifications_list)
        self.refresh_layout.add_widget(scroll)
        
        # Assembler le layout principal
        main_layout.add_widget(self.toolbar)
        main_layout.add_widget(self.stats_card)
        main_layout.add_widget(self.refresh_layout)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Charger les notifications
        Clock.schedule_once(self.load_notifications, 1)
    
    def create_stats_card(self):
        """Créer la carte de statistiques"""
        card = MDCard(
            size_hint_y=None,
            height=dp(80),
            padding=dp(15),
            elevation=2
        )
        
        layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20)
        )
        
        # Notifications non lues
        self.unread_label = MDLabel(
            text="Non lues: 0",
            theme_text_color="Primary",
            font_style="H6",
            halign="center"
        )
        
        # Total des notifications
        self.total_label = MDLabel(
            text="Total: 0",
            theme_text_color="Secondary",
            halign="center"
        )
        
        layout.add_widget(self.unread_label)
        layout.add_widget(self.total_label)
        
        card.add_widget(layout)
        return card
    
    def load_notifications(self, dt=None):
        """Charger la liste des notifications"""
        try:
            import threading
            thread = threading.Thread(target=self.fetch_notifications, daemon=True)
            thread.start()
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur chargement notifications: {e}")
            self.show_error("Erreur lors du chargement des notifications")
    
    def fetch_notifications(self):
        """Récupérer les notifications depuis l'API"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            success, notifications = app.api_client.get_notifications()
            
            if success:
                self.notifications_data = notifications
                self.unread_count = len([n for n in notifications if not n.get('lu', False)])
                Clock.schedule_once(lambda dt: self.update_notifications_list(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error("Erreur lors du chargement"), 0)
                
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur fetch notifications: {e}")
            Clock.schedule_once(lambda dt: self.show_error(f"Erreur: {str(e)}"), 0)
    
    def update_notifications_list(self):
        """Mettre à jour la liste des notifications"""
        try:
            self.notifications_list.clear_widgets()
            
            # Mettre à jour les statistiques
            self.update_stats()
            
            if not self.notifications_data:
                self.add_placeholder("Aucune notification")
                return
            
            # Trier par date (plus récentes en premier)
            sorted_notifications = sorted(
                self.notifications_data,
                key=lambda x: x.get('date_creation', ''),
                reverse=True
            )
            
            for notification in sorted_notifications:
                # Déterminer l'icône selon le type
                notif_type = notification.get('type', 'info')
                if notif_type == 'ticket':
                    icon = "📋"
                elif notif_type == 'machine':
                    icon = "🖥️"
                elif notif_type == 'urgent':
                    icon = "🚨"
                elif notif_type == 'maintenance':
                    icon = "🔧"
                else:
                    icon = "ℹ️"
                
                # Déterminer si lu ou non
                is_read = notification.get('lu', False)
                read_icon = "📖" if is_read else "📩"
                
                # Style selon le statut de lecture
                text_color = "Secondary" if is_read else "Primary"
                
                # Créer l'item de liste
                item = ThreeLineListItem(
                    text=f"{read_icon} {icon} {notification.get('titre', 'Notification sans titre')}",
                    secondary_text=notification.get('message', 'Aucun message')[:60] + "...",
                    tertiary_text=f"📅 {notification.get('date_creation', 'Date inconnue')[:16]}",
                    theme_text_color=text_color,
                    on_release=lambda x, n=notification: self.show_notification_detail(n)
                )
                
                self.notifications_list.add_widget(item)
                
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur mise à jour liste: {e}")
    
    def update_stats(self):
        """Mettre à jour les statistiques"""
        try:
            total = len(self.notifications_data)
            unread = self.unread_count
            
            self.unread_label.text = f"Non lues: {unread}"
            self.total_label.text = f"Total: {total}"
            
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur mise à jour stats: {e}")
    
    def add_placeholder(self, text):
        """Ajouter un placeholder à la liste"""
        placeholder = OneLineListItem(text=text)
        self.notifications_list.add_widget(placeholder)
    
    def refresh_notifications(self, *args):
        """Actualiser la liste des notifications"""
        self.load_notifications()
    
    def show_notification_detail(self, notification):
        """Afficher les détails d'une notification"""
        try:
            # Marquer comme lue si pas encore lu
            if not notification.get('lu', False):
                self.mark_notification_read(notification)
            
            # Créer le contenu des détails
            content = MDBoxLayout(
                orientation='vertical',
                spacing=dp(15),
                adaptive_height=True
            )
            
            # Informations de la notification
            info_text = f"""
Type: {notification.get('type', 'Inconnu').title()}
Date: {notification.get('date_creation', 'Inconnue')}

Message:
{notification.get('message', 'Aucun message')}
            """.strip()
            
            info_label = MDLabel(
                text=info_text,
                theme_text_color="Primary",
                size_hint_y=None
            )
            info_label.bind(texture_size=info_label.setter('size'))
            
            content.add_widget(info_label)
            
            # Boutons d'action selon le type
            actions_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(10),
                adaptive_height=True,
                size_hint_y=None,
                height=dp(40)
            )
            
            # Si c'est une notification de ticket, permettre d'ouvrir le ticket
            if notification.get('type') == 'ticket' and notification.get('ticket_id'):
                ticket_button = MDFlatButton(
                    text="Voir Ticket",
                    on_release=lambda x: self.open_related_ticket(notification, dialog)
                )
                actions_layout.add_widget(ticket_button)
            
            # Si c'est une notification de machine, permettre d'ouvrir la machine
            if notification.get('type') == 'machine' and notification.get('machine_id'):
                machine_button = MDFlatButton(
                    text="Voir Machine",
                    on_release=lambda x: self.open_related_machine(notification, dialog)
                )
                actions_layout.add_widget(machine_button)
            
            if actions_layout.children:
                content.add_widget(actions_layout)
            
            # Créer le dialogue
            dialog = MDDialog(
                title=notification.get('titre', 'Notification'),
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
            Logger.error(f"NotificationsScreen: Erreur détails notification: {e}")
            self.show_error("Erreur lors de l'affichage des détails")
    
    def mark_notification_read(self, notification):
        """Marquer une notification comme lue"""
        try:
            import threading
            
            def mark_read_thread():
                try:
                    from kivymd.app import MDApp
                    app = MDApp.get_running_app()
                    
                    success = app.api_client.mark_notification_read(notification.get('id'))
                    
                    if success:
                        notification['lu'] = True
                        self.unread_count = max(0, self.unread_count - 1)
                        Clock.schedule_once(lambda dt: self.update_stats(), 0)
                        
                except Exception as e:
                    Logger.error(f"NotificationsScreen: Erreur marquage lu: {e}")
            
            thread = threading.Thread(target=mark_read_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur mark read: {e}")
    
    def mark_all_read(self):
        """Marquer toutes les notifications comme lues"""
        try:
            import threading
            
            def mark_all_read_thread():
                try:
                    from kivymd.app import MDApp
                    app = MDApp.get_running_app()
                    
                    success = app.api_client.mark_all_notifications_read()
                    
                    if success:
                        for notification in self.notifications_data:
                            notification['lu'] = True
                        self.unread_count = 0
                        Clock.schedule_once(lambda dt: self.update_notifications_list(), 0)
                        Clock.schedule_once(lambda dt: self.show_success("Toutes les notifications marquées comme lues"), 0)
                    else:
                        Clock.schedule_once(lambda dt: self.show_error("Erreur lors du marquage"), 0)
                        
                except Exception as e:
                    Logger.error(f"NotificationsScreen: Erreur mark all read: {e}")
                    error_message = f"Erreur: {str(e)}"
                    Clock.schedule_once(lambda dt: self.show_error(error_message), 0)
            
            thread = threading.Thread(target=mark_all_read_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur mark all read: {e}")
    
    def clear_all_notifications(self):
        """Supprimer toutes les notifications"""
        try:
            # Demander confirmation
            def confirm_clear(instance):
                self.perform_clear_all()
                dialog.dismiss()
            
            dialog = MDDialog(
                title="Confirmer la suppression",
                text="Êtes-vous sûr de vouloir supprimer toutes les notifications ?",
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="SUPPRIMER",
                        on_release=confirm_clear
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur clear all: {e}")
    
    def perform_clear_all(self):
        """Effectuer la suppression de toutes les notifications"""
        try:
            import threading
            
            def clear_all_thread():
                try:
                    from kivymd.app import MDApp
                    app = MDApp.get_running_app()
                    
                    success = app.api_client.clear_all_notifications()
                    
                    if success:
                        self.notifications_data = []
                        self.unread_count = 0
                        Clock.schedule_once(lambda dt: self.update_notifications_list(), 0)
                        Clock.schedule_once(lambda dt: self.show_success("Toutes les notifications supprimées"), 0)
                    else:
                        Clock.schedule_once(lambda dt: self.show_error("Erreur lors de la suppression"), 0)
                        
                except Exception as e:
                    Logger.error(f"NotificationsScreen: Erreur clear all: {e}")
                    error_message = f"Erreur: {str(e)}"
                    Clock.schedule_once(lambda dt: self.show_error(error_message), 0)
            
            thread = threading.Thread(target=clear_all_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur perform clear: {e}")
    
    def open_related_ticket(self, notification, dialog):
        """Ouvrir le ticket lié à la notification"""
        try:
            dialog.dismiss()
            
            # Aller à l'écran des tickets
            self.manager.current = 'tickets'
            tickets_screen = self.manager.get_screen('tickets')
            
            # Filtrer par le ticket spécifique si possible
            if hasattr(tickets_screen, 'apply_filters'):
                filters = {'ticket_id': notification.get('ticket_id')}
                tickets_screen.apply_filters(filters)
                
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur ouverture ticket: {e}")
            self.show_error("Erreur lors de l'ouverture du ticket")
    
    def open_related_machine(self, notification, dialog):
        """Ouvrir la machine liée à la notification"""
        try:
            dialog.dismiss()
            
            # Aller à l'écran des machines
            self.manager.current = 'machines'
            machines_screen = self.manager.get_screen('machines')
            
            # Filtrer par la machine spécifique si possible
            if hasattr(machines_screen, 'apply_filters'):
                filters = {'machine_id': notification.get('machine_id')}
                machines_screen.apply_filters(filters)
                
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur ouverture machine: {e}")
            self.show_error("Erreur lors de l'ouverture de la machine")
    
    def go_back(self):
        """Retourner au dashboard"""
        try:
            self.manager.current = 'dashboard'
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur retour: {e}")
    
    def show_info(self, message):
        """Afficher un message d'information"""
        try:
            Snackbar(text=message).open()
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur affichage info: {e}")
    
    def show_success(self, message):
        """Afficher un message de succès"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.2, 0.8, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur affichage succès: {e}")
    
    def show_error(self, message):
        """Afficher un message d'erreur"""
        try:
            Snackbar(
                text=message,
                bg_color=(0.8, 0.2, 0.2, 1)
            ).open()
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur affichage erreur: {e}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            # Actualiser les notifications quand on arrive sur l'écran
            Clock.schedule_once(lambda dt: self.load_notifications(), 0.5)
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            Logger.info("NotificationsScreen: Écran quitté")
        except Exception as e:
            Logger.error(f"NotificationsScreen: Erreur on_leave: {e}")