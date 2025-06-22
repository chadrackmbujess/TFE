#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application Desktop ITSM - Interface utilisateur Kivy
"""
import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFloatingActionButton

from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationDrawerMenu
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.widget import MDWidget
from kivymd.theming import ThemableBehavior
from kivy.animation import Animation
from kivy.metrics import dp
import requests
import json
from datetime import datetime

# Configuration du chemin pour importer les modules Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LoginScreen(MDScreen):
    """Écran de connexion"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        self.build_ui()

    def build_ui(self):
        """Construire l'interface de connexion ultra moderne et responsive"""
        from kivy.core.window import Window

        # Layout principal responsive
        main_layout = MDRelativeLayout()

        # Fond avec dégradé moderne et animation
        background = MDWidget()
        background.md_bg_color = [0.02, 0.02, 0.08, 1]  # Bleu très foncé professionnel
        main_layout.add_widget(background)

        # Container central responsive avec marges équilibrées
        window_width = Window.width
        container_width = min(0.9, max(0.3, 400 / window_width)) if window_width > 0 else 0.4

        center_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(25),
            adaptive_height=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            size_hint=(container_width, None),
            padding=[dp(20), dp(20), dp(20), dp(20)]  # Marges gauche, haut, droite, bas
        )

        # En-tête avec marges équilibrées
        title_card = MDCard(
            orientation='vertical',
            padding=dp(25),  # Marge augmentée
            size_hint=(1, None),
            height=dp(130),
            elevation=8,
            md_bg_color=[0.1, 0.1, 0.2, 0.95]
        )

        title = MDLabel(
            text='🚀 ITSM Pro',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(55),
            halign='center',
            font_style='H3',
            bold=True
        )

        subtitle = MDLabel(
            text='Système de Gestion IT Nouvelle Génération',
            theme_text_color='Custom',
            text_color=[0.7, 0.7, 0.8, 1],
            size_hint_y=None,
            height=dp(35),
            halign='center',
            font_style='Caption'
        )

        title_card.add_widget(title)
        title_card.add_widget(subtitle)

        # Carte de connexion ultra moderne
        login_card = MDCard(
            orientation='vertical',
            spacing=dp(25),
            padding=dp(30),
            size_hint=(1, None),
            height=dp(400),
            elevation=12,
            md_bg_color=[0.08, 0.08, 0.18, 0.98]
        )

        # Champs de saisie avec style moderne
        self.username_field = MDTextField(
            hint_text='Nom d\'utilisateur (@prenom.nom.entreprise)',
            helper_text='Format: @prenom.nom.entreprise',
            helper_text_mode='on_focus',
            size_hint_y=None,
            height=dp(60),
            mode="line",  # Changé de "outlined" à "line"
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1],
            # icon_left="account-circle",  # Propriété supprimée car non supportée
            # radius=[15, 15, 15, 15]  # Propriété supprimée car non supportée
        )

        self.password_field = MDTextField(
            hint_text='Mot de passe',
            password=True,
            size_hint_y=None,
            height=dp(60),
            mode="line",  # Changé de "outlined" à "line"
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1],
            # icon_left="lock",  # Propriété supprimée car non supportée
            # radius=[15, 15, 15, 15]  # Propriété supprimée car non supportée
        )

        # Boutons modernes avec dégradé
        buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )

        login_button = MDRaisedButton(
            text='Se connecter',
            size_hint_x=0.6,
            md_bg_color=[0.2, 0.6, 1, 1],  # Bleu moderne
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=6,
            on_release=self.login
        )

        register_button = MDRaisedButton(
            text='S\'inscrire',
            size_hint_x=0.4,
            md_bg_color=[0.1, 0.8, 0.4, 1],  # Vert moderne
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=6,
            on_release=self.go_to_register
        )

        buttons_layout.add_widget(login_button)
        buttons_layout.add_widget(register_button)

        # Message d'état
        self.status_label = MDLabel(
            text='',
            theme_text_color='Error',
            size_hint_y=None,
            height='30dp',
            halign='center'
        )

        # Pied de page avec marges équilibrées
        demo_card = MDCard(
            orientation='vertical',
            padding=dp(25),  # Même marge que l'en-tête
            size_hint=(1, None),
            height=dp(130),
            elevation=4,
            md_bg_color=[0.08, 0.08, 0.16, 0.9]
        )

        demo_info = MDLabel(
            text='Comptes de démonstration:\n'
                 'Admin: @admin.demo.demo / admin123\n'
                 'Technicien: @technicien.demo.demo / tech123\n'
                 'Utilisateur: @utilisateur.demo.demo / user123',
            theme_text_color='Custom',
            text_color=[0.6, 0.6, 0.7, 1],
            size_hint_y=None,
            height=dp(80),
            halign='center',
            font_size='12sp'
        )

        demo_card.add_widget(demo_info)

        # Assemblage
        login_card.add_widget(self.username_field)
        login_card.add_widget(self.password_field)
        login_card.add_widget(buttons_layout)
        login_card.add_widget(self.status_label)

        center_layout.add_widget(title_card)
        center_layout.add_widget(login_card)
        center_layout.add_widget(demo_card)

        main_layout.add_widget(center_layout)
        self.add_widget(main_layout)

    def login(self, instance):
        """Gérer la connexion"""
        username = self.username_field.text
        password = self.password_field.text

        if not username or not password:
            self.status_label.text = 'Veuillez remplir tous les champs'
            return

        try:
            # Tentative de connexion à l'API
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/users/login/',
                data={'username': username, 'password': password, 'type_connexion': 'desktop'},
                timeout=5
            )

            if response.status_code == 200:
                token_data = response.json()
                if 'token' in token_data:
                    # Stocker le token et les informations utilisateur
                    app = MDApp.get_running_app()
                    app.user_token = token_data['token']
                    app.current_user = username

                    # Synchroniser automatiquement la machine locale
                    self.status_label.text = 'Synchronisation de la machine...'
                    self.synchroniser_machine_locale()

                    # Démarrer la surveillance des logiciels
                    app.start_software_monitoring()

                    # Passer à l'écran principal
                    self.manager.current = 'dashboard'
                    self.status_label.text = ''
                else:
                    self.status_label.text = 'Erreur de connexion'
            else:
                self.status_label.text = 'Identifiants incorrects'

        except requests.exceptions.RequestException:
            self.status_label.text = 'Erreur de connexion au serveur'
        except Exception as e:
            self.status_label.text = f'Erreur: {str(e)}'

    def synchroniser_machine_locale(self):
        """Synchroniser les informations de la machine locale avec le serveur"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                print("❌ Aucun token d'authentification disponible")
                return

            # Headers avec token d'authentification
            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            print(f"🔄 Synchronisation de la machine pour l'utilisateur: {app.current_user}")

            # Appeler l'endpoint de synchronisation
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/machines/synchroniser_machine_locale/',
                headers=headers,
                timeout=60  # Augmenté à 60 secondes pour les machines lentes
            )

            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    machine_info = response_data.get('machine', {})
                    machine_nom = machine_info.get('nom', 'Machine inconnue')

                    print(f"✅ Machine synchronisée avec succès: {machine_nom}")
                    self.status_label.text = f'Machine {machine_nom} synchronisée!'
                    self.status_label.theme_text_color = 'Primary'
                except:
                    print("✅ Machine synchronisée avec succès")
                    self.status_label.text = 'Machine synchronisée!'
                    self.status_label.theme_text_color = 'Primary'
            else:
                try:
                    error_data = response.json()
                    print(f"⚠️ Erreur de synchronisation ({response.status_code}): {error_data}")
                    self.status_label.text = f'Erreur de synchronisation: {error_data.get("error", "Erreur inconnue")}'
                except:
                    print(f"⚠️ Erreur de synchronisation: {response.status_code}")
                    self.status_label.text = f'Erreur de synchronisation (Code: {response.status_code})'
                self.status_label.theme_text_color = 'Error'

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion lors de la synchronisation: {e}")
            self.status_label.text = 'Erreur de connexion au serveur'
            self.status_label.theme_text_color = 'Error'
        except Exception as e:
            print(f"❌ Erreur lors de la synchronisation: {e}")
            self.status_label.text = f'Erreur: {str(e)}'
            self.status_label.theme_text_color = 'Error'

    def go_to_register(self, instance):
        """Aller à l'écran d'inscription"""
        self.manager.current = 'register'


class DashboardScreen(MDScreen):
    """Écran principal du tableau de bord"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        self.build_ui()

    def build_ui(self):
        """Construire l'interface du tableau de bord en trois parties"""
        # Layout principal avec fond moderne
        main_layout = MDRelativeLayout()

        # Fond avec dégradé
        background = MDWidget()
        background.md_bg_color = [0.03, 0.03, 0.12, 1]  # Bleu très foncé
        main_layout.add_widget(background)

        # Container principal
        content_container = MDBoxLayout(orientation='vertical')

        # Barre d'outils moderne
        toolbar = MDTopAppBar(
            title='🚀 ITSM Pro Dashboard',
            md_bg_color=[0.1, 0.1, 0.2, 0.95],
            specific_text_color=[0.3, 0.7, 1, 1],
            left_action_items=[['menu', lambda x: self.open_drawer()]],
            right_action_items=[
                ['refresh', lambda x: self.refresh_all_data()],
                ['account-circle', lambda x: None],
                ['logout', lambda x: self.logout()]
            ],
            elevation=8
        )

        # Layout principal horizontal pour les trois parties
        main_content_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            padding=dp(15)
        )

        # PARTIE GAUCHE - Tickets envoyés
        self.tickets_card = self.create_tickets_section()

        # PARTIE CENTRALE - Informations machine
        self.machine_card = self.create_machine_section()

        # PARTIE DROITE - Commentaires permanents
        self.comments_card = self.create_comments_section()

        # Ajouter les trois parties au layout principal
        main_content_layout.add_widget(self.tickets_card)
        main_content_layout.add_widget(self.machine_card)
        main_content_layout.add_widget(self.comments_card)

        # Assemblage final
        content_container.add_widget(toolbar)
        content_container.add_widget(main_content_layout)

        main_layout.add_widget(content_container)
        self.add_widget(main_layout)

        # Initialiser les données
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.initialize_all_data(), 1)

    def create_tickets_section(self):
        """Créer la section des tickets envoyés (partie gauche)"""
        tickets_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_x=0.33,  # 1/3 de la largeur
            elevation=6,
            md_bg_color=[0.08, 0.08, 0.18, 0.95],
            radius=[dp(10)]
        )

        # En-tête de la section avec nombre total
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        tickets_icon = MDIconButton(
            icon='ticket-confirmation',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='24sp',
            disabled=True
        )

        tickets_title = MDLabel(
            text='Mes Tickets Envoyés',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            font_size='16sp',
            bold=True,
            halign='left'
        )

        # Badge avec nombre total de tickets
        self.total_tickets_badge = MDCard(
            size_hint=(None, None),
            size=(dp(30), dp(25)),
            md_bg_color=[0.3, 0.7, 1, 1],
            radius=[dp(12)],
            elevation=2,
            padding=dp(2)
        )

        self.total_tickets_badge_label = MDLabel(
            text='0',
            theme_text_color='Custom',
            text_color=[1, 1, 1, 1],
            font_size='12sp',
            bold=True,
            halign='center',
            valign='center'
        )

        self.total_tickets_badge.add_widget(self.total_tickets_badge_label)

        header_layout.add_widget(tickets_icon)
        header_layout.add_widget(tickets_title)
        header_layout.add_widget(self.total_tickets_badge)

        # Statistiques des tickets (statuts)
        stats_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8)
        )

        # Compteur ouverts
        open_card = MDCard(
            orientation='vertical',
            padding=dp(8),
            size_hint_x=0.33,
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.open_tickets_label = MDLabel(
            text='0',
            theme_text_color='Custom',
            text_color=[1, 0.6, 0.2, 1],
            font_size='20sp',
            bold=True,
            halign='center'
        )

        open_text = MDLabel(
            text='Ouverts',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='10sp',
            halign='center'
        )

        open_card.add_widget(self.open_tickets_label)
        open_card.add_widget(open_text)

        # Compteur en cours
        progress_card = MDCard(
            orientation='vertical',
            padding=dp(8),
            size_hint_x=0.33,
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.progress_tickets_label = MDLabel(
            text='0',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            font_size='20sp',
            bold=True,
            halign='center'
        )

        progress_text = MDLabel(
            text='En cours',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='10sp',
            halign='center'
        )

        progress_card.add_widget(self.progress_tickets_label)
        progress_card.add_widget(progress_text)

        # Compteur fermés
        closed_card = MDCard(
            orientation='vertical',
            padding=dp(8),
            size_hint_x=0.33,
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.closed_tickets_label = MDLabel(
            text='0',
            theme_text_color='Custom',
            text_color=[0.1, 0.8, 0.4, 1],
            font_size='20sp',
            bold=True,
            halign='center'
        )

        closed_text = MDLabel(
            text='Fermés',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='10sp',
            halign='center'
        )

        closed_card.add_widget(self.closed_tickets_label)
        closed_card.add_widget(closed_text)

        stats_layout.add_widget(open_card)
        stats_layout.add_widget(progress_card)
        stats_layout.add_widget(closed_card)

        # Espacement avant la carte des catégories
        categories_spacer_top = MDWidget(
            size_hint_y=None,
            height=dp(15)  # Marge supérieure pour séparer des cartes de statut
        )

        # Carte des catégories de tickets
        categories_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(130),  # Augmenté pour accommoder l'icône et les marges
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        # En-tête avec icône pour la section catégories
        categories_header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5)
        )

        categories_icon = MDIconButton(
            icon='chart-pie',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='16sp',
            disabled=True,
            size_hint_x=None,
            width=dp(25),
            size_hint_y=None,
            height=dp(25),
            pos_hint={'center_y': 0.5}
        )

        categories_header = MDLabel(
            text='Répartition par Catégorie',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(25),
            font_size='12sp',
            bold=True,
            halign='left',
            valign='center'
        )

        categories_header_layout.add_widget(categories_icon)
        categories_header_layout.add_widget(categories_header)

        # Espacement sous le titre avec deux sauts de ligne
        categories_spacer = MDWidget(
            size_hint_y=None,
            height=dp(15)  # Augmenté pour créer plus d'espace (équivalent à 2 sauts de ligne)
        )

        # Layout pour les catégories (2 colonnes)
        categories_grid = MDGridLayout(
            cols=2,
            spacing=dp(5),
            adaptive_height=True,
            size_hint_y=None,
            height=dp(90)  # Augmenté pour accommoder 6 catégories (3 lignes)
        )

        # Initialiser les labels des catégories
        self.categories_labels = {}
        categories_info = [
            ('Matériel', 'desktop-classic', [1, 0.6, 0.2, 1]),
            ('Logiciel', 'application', [0.3, 0.7, 1, 1]),
            ('Réseau', 'network', [0.1, 0.8, 0.4, 1]),
            ('Accès', 'key', [0.8, 0.4, 1, 1]),
            ('Sécurité', 'shield-check', [1, 0.2, 0.2, 1]),
            ('Autre', 'help-circle', [0.6, 0.6, 0.6, 1])
        ]

        for category_name, icon_name, color in categories_info:
            category_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_y=None,
                height=dp(15)
            )

            icon_widget = MDIconButton(
                icon=icon_name,
                theme_icon_color='Custom',
                icon_color=color,
                icon_size='12sp',
                disabled=True,
                size_hint_x=None,
                width=dp(20),
                size_hint_y=None,
                height=dp(15),
                pos_hint={'center_y': 0.5}
            )

            category_label = MDLabel(
                text=f'{category_name}: 0',
                theme_text_color='Custom',
                text_color=color,
                font_size='10sp',
                halign='left'
            )

            category_layout.add_widget(icon_widget)
            category_layout.add_widget(category_label)
            categories_grid.add_widget(category_layout)

            # Stocker la référence pour mise à jour
            self.categories_labels[category_name.lower()] = category_label

        categories_card.add_widget(categories_header_layout)
        categories_card.add_widget(categories_spacer)
        categories_card.add_widget(categories_grid)

        # Liste des tickets récents
        from kivymd.uix.scrollview import MDScrollView

        tickets_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.tickets_list = MDBoxLayout(
            orientation='vertical',
            spacing=dp(5),
            adaptive_height=True,
            padding=dp(5)
        )

        tickets_scroll.add_widget(self.tickets_list)

        # Bouton créer ticket
        create_ticket_btn = MDRaisedButton(
            text='+ Créer un Ticket',
            size_hint_y=None,
            height=dp(40),
            md_bg_color=[0.1, 0.8, 0.4, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=self.create_ticket
        )

        # Assemblage
        tickets_card.add_widget(header_layout)
        tickets_card.add_widget(stats_layout)
        tickets_card.add_widget(categories_spacer_top)
        tickets_card.add_widget(categories_card)
        tickets_card.add_widget(tickets_scroll)
        tickets_card.add_widget(create_ticket_btn)

        return tickets_card

    def create_machine_section(self):
        """Créer la section des informations machine (partie centrale)"""
        machine_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_x=0.34,  # 1/3 de la largeur
            elevation=6,
            md_bg_color=[0.08, 0.08, 0.18, 0.95],
            radius=[dp(10)]
        )

        # En-tête de la section
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        machine_icon = MDIconButton(
            icon='desktop-classic',
            theme_icon_color='Custom',
            icon_color=[0.1, 0.8, 0.4, 1],
            icon_size='24sp',
            disabled=True
        )

        machine_title = MDLabel(
            text='Informations Machine',
            theme_text_color='Custom',
            text_color=[0.1, 0.8, 0.4, 1],
            font_size='16sp',
            bold=True,
            halign='left'
        )

        header_layout.add_widget(machine_icon)
        header_layout.add_widget(machine_title)

        # Informations système
        from kivymd.uix.scrollview import MDScrollView

        machine_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        machine_info_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10),
            adaptive_height=True,
            padding=dp(5)
        )

        # Carte nom de la machine
        name_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(60),
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.machine_name_label = MDLabel(
            text='Chargement...',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            font_size='16sp',
            bold=True,
            halign='center'
        )

        name_subtitle = MDLabel(
            text='Nom de la machine',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='12sp',
            halign='center'
        )

        name_card.add_widget(self.machine_name_label)
        name_card.add_widget(name_subtitle)

        # Carte système d'exploitation
        os_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(60),
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.machine_os_label = MDLabel(
            text='Chargement...',
            theme_text_color='Custom',
            text_color=[0.1, 0.8, 0.4, 1],
            font_size='14sp',
            halign='center'
        )

        os_subtitle = MDLabel(
            text='Système d\'exploitation',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='12sp',
            halign='center'
        )

        os_card.add_widget(self.machine_os_label)
        os_card.add_widget(os_subtitle)

        # Carte processeur
        cpu_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(80),  # Augmenté pour accommoder le texte sur plusieurs lignes
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.machine_cpu_label = MDLabel(
            text='Chargement...',
            theme_text_color='Custom',
            text_color=[1, 0.6, 0.2, 1],
            font_size='12sp',  # Réduit légèrement pour s'adapter
            text_size=(dp(280), dp(60)),  # Permettre le retour à la ligne
            halign='center',
            valign='center'
        )

        cpu_subtitle = MDLabel(
            text='Processeur',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='12sp',
            halign='center'
        )

        cpu_card.add_widget(self.machine_cpu_label)
        cpu_card.add_widget(cpu_subtitle)

        # Carte mémoire
        memory_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(60),
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.machine_memory_label = MDLabel(
            text='Chargement...',
            theme_text_color='Custom',
            text_color=[1, 0.3, 0.5, 1],
            font_size='14sp',
            halign='center'
        )

        memory_subtitle = MDLabel(
            text='Mémoire RAM',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='12sp',
            halign='center'
        )

        memory_card.add_widget(self.machine_memory_label)
        memory_card.add_widget(memory_subtitle)

        # Carte disques durs
        hdd_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            size_hint_y=None,
            height=dp(80),  # Plus haut pour accommoder plusieurs disques
            elevation=2,
            md_bg_color=[0.1, 0.1, 0.2, 0.8],
            radius=[dp(8)]
        )

        self.machine_hdd_label = MDLabel(
            text='Chargement...',
            theme_text_color='Custom',
            text_color=[0.3, 0.8, 0.6, 1],  # Couleur verte pour les disques
            font_size='12sp',
            text_size=(dp(280), dp(50)),  # Permettre le retour à la ligne
            halign='center',
            valign='center'
        )

        hdd_subtitle = MDLabel(
            text='Disques durs',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='12sp',
            halign='center'
        )

        hdd_card.add_widget(self.machine_hdd_label)
        hdd_card.add_widget(hdd_subtitle)

        # Assemblage des cartes d'informations
        machine_info_layout.add_widget(name_card)
        machine_info_layout.add_widget(os_card)
        machine_info_layout.add_widget(cpu_card)
        machine_info_layout.add_widget(memory_card)
        machine_info_layout.add_widget(hdd_card)

        machine_scroll.add_widget(machine_info_layout)

        # Bouton synchroniser
        sync_btn = MDRaisedButton(
            text='🔄 Synchroniser',
            size_hint_y=None,
            height=dp(40),
            md_bg_color=[0.3, 0.7, 1, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=self.sync_machine_data
        )

        # Assemblage
        machine_card.add_widget(header_layout)
        machine_card.add_widget(machine_scroll)
        machine_card.add_widget(sync_btn)

        return machine_card

    def create_comments_section(self):
        """Créer la section des commentaires permanents (partie droite)"""
        comments_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_x=0.33,  # 1/3 de la largeur
            elevation=6,
            md_bg_color=[0.08, 0.08, 0.18, 0.95],
            radius=[dp(10)]
        )

        # En-tête de la section
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        comments_icon = MDIconButton(
            icon='comment-multiple',
            theme_icon_color='Custom',
            icon_color=[1, 0.3, 0.5, 1],
            icon_size='24sp',
            disabled=True
        )

        comments_title = MDLabel(
            text='Commentaires',
            theme_text_color='Custom',
            text_color=[1, 0.3, 0.5, 1],
            font_size='16sp',
            bold=True,
            halign='left'
        )

        # Badge de notification intégré
        self.comments_badge = MDCard(
            size_hint=(None, None),
            size=(dp(25), dp(25)),
            md_bg_color=[1, 0.2, 0.2, 1],
            radius=[dp(12)],
            elevation=2,
            padding=dp(2)
        )

        self.comments_badge_label = MDLabel(
            text='0',
            theme_text_color='Custom',
            text_color=[1, 1, 1, 1],
            font_size='12sp',
            bold=True,
            halign='center',
            valign='center'
        )

        self.comments_badge.add_widget(self.comments_badge_label)

        header_layout.add_widget(comments_icon)
        header_layout.add_widget(comments_title)
        header_layout.add_widget(self.comments_badge)

        # Statut des commentaires
        self.comments_status = MDLabel(
            text='Chargement des commentaires...',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(30),
            font_size='12sp',
            halign='center'
        )

        # Liste des commentaires avec scroll
        from kivymd.uix.scrollview import MDScrollView

        comments_scroll = MDScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.comments_list = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            adaptive_height=True,
            padding=dp(5)
        )

        comments_scroll.add_widget(self.comments_list)

        # Boutons d'action
        actions_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        refresh_btn = MDRaisedButton(
            text='🔄',
            size_hint_x=0.3,
            md_bg_color=[0.3, 0.7, 1, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=lambda x: self.refresh_comments()
        )

        mark_all_read_btn = MDRaisedButton(
            text='✅ Tout lu',
            size_hint_x=0.7,
            md_bg_color=[0.1, 0.8, 0.4, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=lambda x: self.mark_all_notifications_as_read()
        )

        actions_layout.add_widget(refresh_btn)
        actions_layout.add_widget(mark_all_read_btn)

        # Assemblage
        comments_card.add_widget(header_layout)
        comments_card.add_widget(self.comments_status)
        comments_card.add_widget(comments_scroll)
        comments_card.add_widget(actions_layout)

        # Initialiser les compteurs
        self.unread_notifications_count = 0
        self.total_comments_count = 0

        return comments_card

    def initialize_all_data(self):
        """Initialiser toutes les données des trois sections"""
        print("🔄 Initialisation des données du dashboard...")
        self.fetch_tickets_data()
        self.fetch_machine_data()
        self.fetch_notifications()

    def refresh_all_data(self):
        """Actualiser toutes les données"""
        print("🔄 Actualisation de toutes les données...")
        self.initialize_all_data()

    def fetch_tickets_data(self):
        """Récupérer les données des tickets"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                'http://127.0.0.1:8000/api/v1/tickets/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                tickets_data = response.json()
                tickets = tickets_data.get('results', tickets_data) if isinstance(tickets_data, dict) else tickets_data

                # Calculer les statistiques par statut
                total_tickets = len(tickets)
                open_tickets = sum(1 for ticket in tickets if ticket.get('statut') == 'ouvert')
                progress_tickets = sum(1 for ticket in tickets if ticket.get('statut') == 'en_cours')
                closed_tickets = sum(1 for ticket in tickets if ticket.get('statut') == 'ferme')

                # Mettre à jour les compteurs de statut
                self.total_tickets_badge_label.text = str(total_tickets)
                self.open_tickets_label.text = str(open_tickets)
                self.progress_tickets_label.text = str(progress_tickets)
                self.closed_tickets_label.text = str(closed_tickets)

                # Calculer les statistiques par catégorie
                categories_count = {}

                # Récupérer les vraies catégories depuis l'API
                category_mapping = self.get_categories_mapping()

                # Initialiser les compteurs pour les catégories affichées
                for cat_name in ['matériel', 'logiciel', 'réseau', 'accès', 'sécurité', 'autre']:
                    categories_count[cat_name] = 0

                print(f"🔍 Mapping des catégories récupéré: {category_mapping}")
                print(f"🎫 Nombre de tickets à analyser: {len(tickets)}")

                # Compter les tickets par catégorie
                for ticket in tickets:
                    category_id = ticket.get('categorie')
                    print(f"🎫 Ticket {ticket.get('numero', 'N/A')}: catégorie ID = {category_id}")
                    if category_id and category_id in category_mapping:
                        category_name = category_mapping[category_id].lower()
                        print(f"   → Catégorie trouvée: {category_name}")
                        if category_name in categories_count:
                            categories_count[category_name] += 1
                            print(f"   → Compteur {category_name} incrémenté: {categories_count[category_name]}")
                        else:
                            print(f"   → Catégorie {category_name} non prise en compte dans l'affichage")
                    else:
                        print(f"   → Catégorie ID {category_id} non trouvée dans le mapping")

                # Mettre à jour les labels des catégories
                print(f"📊 Mise à jour des labels avec les compteurs: {categories_count}")
                for category_name, count in categories_count.items():
                    if category_name in self.categories_labels:
                        old_text = self.categories_labels[category_name].text
                        new_text = f'{category_name.capitalize()}: {count}'
                        self.categories_labels[category_name].text = new_text
                        print(f"  🏷️ {category_name}: '{old_text}' → '{new_text}'")
                    else:
                        print(f"  ❌ Label pour '{category_name}' non trouvé dans self.categories_labels")

                print(f"📋 Labels disponibles: {list(self.categories_labels.keys())}")

                # Mettre à jour la liste des tickets récents
                self.update_tickets_list(tickets[:5])  # Afficher les 5 derniers

                print(f"📊 RÉCUPÉRATION TICKETS - Utilisateur: {app.current_user}")
                print(f"📈 Nombre exact de tickets récupérés depuis la base de données: {total_tickets}")
                print(
                    f"✅ Répartition par statut: {open_tickets} ouverts, {progress_tickets} en cours, {closed_tickets} fermés")
                print(f"📊 Répartition par catégories: {categories_count}")

                # Afficher aussi dans l'interface utilisateur
                if hasattr(self, 'comments_status'):
                    # Utiliser temporairement le label de statut des commentaires pour afficher l'info
                    original_text = self.comments_status.text
                    self.comments_status.text = f"📊 {total_tickets} tickets récupérés pour {app.current_user}"
                    self.comments_status.text_color = [0.3, 0.7, 1, 1]

                    # Remettre le texte original après 3 secondes
                    from kivy.clock import Clock
                    Clock.schedule_once(lambda dt: setattr(self.comments_status, 'text', original_text), 3)
            else:
                print(f"❌ Erreur lors du chargement des tickets: {response.status_code}")

        except Exception as e:
            print(f"❌ Erreur lors du chargement des tickets: {e}")

    def get_categories_mapping(self):
        """Récupérer le mapping des catégories depuis l'API"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                print("❌ Aucun token pour récupérer les catégories")
                return {}

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            print(f"🔄 Tentative de récupération des catégories...")
            print(f"🔑 Token utilisé: {app.user_token[:20]}...")
            print(f"📡 URL appelée: http://127.0.0.1:8000/api/v1/tickets/categories/")

            response = requests.get(
                'http://127.0.0.1:8000/api/v1/tickets/categories/',
                headers=headers,
                timeout=10
            )

            print(f"📡 Réponse API catégories: Status {response.status_code}")
            print(f"📄 Contenu brut de la réponse: {response.text}")

            if response.status_code == 200:
                categories_data = response.json()
                print(f"📋 Type des données reçues: {type(categories_data)}")
                print(f"📋 Données complètes: {categories_data}")

                categories = categories_data.get('results', categories_data) if isinstance(categories_data,
                                                                                           dict) else categories_data
                print(f"📋 Catégories extraites: {categories}")

                # Créer le mapping ID -> nom
                mapping = {}
                for i, category in enumerate(categories):
                    print(f"  📝 Catégorie {i + 1}: {category}")
                    category_id = category.get('id')
                    category_name = category.get('nom', '').lower()
                    print(f"    - ID: {category_id}")
                    print(f"    - Nom: '{category.get('nom', '')}' -> '{category_name}'")
                    if category_id and category_name:
                        mapping[category_id] = category_name
                        print(f"    ✅ Ajouté au mapping: {category_id} -> {category_name}")
                    else:
                        print(f"    ❌ Ignoré (ID ou nom manquant)")

                print(f"✅ Mapping final des catégories: {mapping}")
                return mapping
            else:
                print(f"❌ Erreur lors de la récupération des catégories: {response.status_code}")
                print(f"📄 Réponse d'erreur: {response.text}")
                print("🔄 Utilisation du mapping de fallback...")
                return self.get_fallback_categories_mapping()

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des catégories: {e}")
            import traceback
            print(f"❌ Traceback complet: {traceback.format_exc()}")
            print("🔄 Utilisation du mapping de fallback...")
            return self.get_fallback_categories_mapping()

    def get_fallback_categories_mapping(self):
        """Mapping de fallback basé sur les données connues de la base"""
        fallback_mapping = {
            1: 'matériel',
            2: 'logiciel',
            3: 'réseau',
            4: 'accès',
            5: 'autre',
            6: 'sécurité'
        }
        print(f"📋 Mapping de fallback utilisé: {fallback_mapping}")
        return fallback_mapping

    def fetch_machine_data(self):
        """Récupérer les données de la machine locale automatiquement"""
        try:
            print("🔄 Récupération des informations système locales...")

            # Récupérer les informations système locales
            machine_info = self.get_local_machine_info()

            # Mettre à jour les informations de la machine
            self.machine_name_label.text = machine_info.get('nom', 'Machine inconnue')
            self.machine_os_label.text = machine_info.get('systeme_exploitation', 'OS inconnu')
            self.machine_cpu_label.text = machine_info.get('processeur', 'CPU inconnu')

            # Formatage de la mémoire
            memory_gb = machine_info.get('memoire_ram', 0)
            if memory_gb > 1024:
                memory_text = f"{memory_gb / 1024:.1f} TB"
            elif memory_gb > 0:
                memory_text = f"{memory_gb:.1f} GB"
            else:
                memory_text = "Inconnue"

            self.machine_memory_label.text = memory_text

            # Mettre à jour les informations des disques durs
            if hasattr(self, 'machine_hdd_label'):
                hdd_info = machine_info.get('disques_durs', 'Inconnu')
                self.machine_hdd_label.text = hdd_info

            print(f"✅ Informations machine locales chargées: {machine_info.get('nom', 'Inconnue')}")

        except Exception as e:
            print(f"❌ Erreur lors du chargement des informations machine: {e}")
            # Valeurs par défaut en cas d'erreur
            self.machine_name_label.text = "Erreur de récupération"
            self.machine_os_label.text = "Erreur de récupération"
            self.machine_cpu_label.text = "Erreur de récupération"
            self.machine_memory_label.text = "Erreur de récupération"
            if hasattr(self, 'machine_hdd_label'):
                self.machine_hdd_label.text = "Erreur de récupération"

    def get_local_machine_info(self):
        """Récupérer les informations système locales"""
        import platform
        import socket
        import psutil

        machine_info = {}

        try:
            # Nom de la machine
            machine_info['nom'] = socket.gethostname()

            # Système d'exploitation avec architecture
            os_name = platform.system()
            os_release = platform.release()
            architecture = platform.machine()

            # Convertir l'architecture en format lisible
            if architecture in ['AMD64', 'x86_64']:
                arch_display = 'x64'
            elif architecture in ['x86', 'i386', 'i686']:
                arch_display = 'x86'
            else:
                arch_display = architecture

            if os_name == "Windows":
                os_info = f"{os_name} {os_release} / {arch_display}"
            else:
                os_info = f"{os_name} {os_release} / {arch_display}"

            machine_info['systeme_exploitation'] = os_info

            # Processeur avec détails avancés
            cpu_info = self.get_detailed_cpu_info()
            machine_info['processeur'] = cpu_info

            # Mémoire RAM (en GB)
            memory_bytes = psutil.virtual_memory().total
            memory_gb = round(memory_bytes / (1024 ** 3), 1)
            machine_info['memoire_ram'] = memory_gb

            # Disques durs
            disques_info = self.get_disk_info()
            machine_info['disques_durs'] = disques_info

            print(f"📊 Informations système récupérées:")
            print(f"  - Nom: {machine_info['nom']}")
            print(f"  - OS: {machine_info['systeme_exploitation']}")
            print(f"  - CPU: {machine_info['processeur'][:80]}...")
            print(f"  - RAM: {machine_info['memoire_ram']} GB")
            print(f"  - Disques: {machine_info['disques_durs']}")

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des informations système: {e}")
            # Valeurs par défaut
            machine_info = {
                'nom': 'Machine inconnue',
                'systeme_exploitation': 'OS inconnu',
                'processeur': 'CPU inconnu',
                'memoire_ram': 0,
                'disques_durs': 'Inconnu'
            }

        return machine_info

    def get_detailed_cpu_info(self):
        """Récupérer les informations détaillées du processeur au format système exact"""
        import psutil

        try:
            # Récupération du nom complet CPU via WMI
            try:
                import wmi
                c = wmi.WMI()
                cpu_name = "CPU inconnu"
                for cpu in c.Win32_Processor():
                    cpu_name = cpu.Name.strip()
                    break
            except ImportError:
                print("⚠️ Module WMI non disponible, utilisation de platform.processor()")
                import platform
                cpu_name = platform.processor() or "CPU inconnu"
            except Exception as e:
                print(f"⚠️ Erreur WMI: {e}, utilisation de platform.processor()")
                import platform
                cpu_name = platform.processor() or "CPU inconnu"

            # Récupération des fréquences via psutil
            try:
                freq = psutil.cpu_freq()
                if freq:
                    min_freq = freq.min / 1000 if freq.min else 0
                    max_freq = freq.max / 1000 if freq.max else 0

                    # Afficher les deux fréquences avec formatage correct
                    freq_parts = []

                    if min_freq > 0:
                        min_freq_str = f"{min_freq:.2f}GHz"
                        freq_parts.append(min_freq_str)

                    if max_freq > 0 and max_freq != min_freq:
                        max_freq_str = f"{max_freq:.2f} GHz"
                        freq_parts.append(max_freq_str)

                    if freq_parts:
                        freq_str = "  ".join(freq_parts)
                    else:
                        freq_str = "Fréquence inconnue"
                else:
                    freq_str = "Fréquence inconnue"
            except Exception as e:
                print(f"⚠️ Erreur récupération fréquences: {e}")
                freq_str = "Fréquence inconnue"

            # Combiner le nom du CPU et les fréquences avec saut de ligne
            if cpu_name != "CPU inconnu" and freq_str != "Fréquence inconnue":
                cpu_info = f"{cpu_name}\n{freq_str}"
            elif cpu_name != "CPU inconnu":
                cpu_info = cpu_name
            else:
                cpu_info = "Informations processeur indisponibles"

            print(f"🔧 CPU complet récupéré: {cpu_info}")
            return cpu_info

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des détails CPU: {e}")
            return "Erreur de récupération CPU"

    def get_disk_info(self):
        """Récupérer les informations sur les disques durs"""
        try:
            disques = []
            total_size = 0

            # Récupérer tous les points de montage
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    # Ignorer les lecteurs système et réseau
                    if partition.fstype and partition.mountpoint:
                        usage = psutil.disk_usage(partition.mountpoint)
                        size_gb = round(usage.total / (1024 ** 3))

                        if size_gb > 0:  # Ignorer les disques de 0 GB
                            disque_nom = partition.mountpoint.replace('\\', '').replace(':', '')
                            if not disque_nom:
                                disque_nom = partition.device.replace('\\', '').replace(':', '')

                            disques.append(f"Disque {disque_nom} = {size_gb} Go")
                            total_size += size_gb

                except (PermissionError, OSError):
                    # Ignorer les disques inaccessibles
                    continue

            if disques:
                disques_text = " • ".join(disques)
                if len(disques) > 1:
                    disques_text += f" • Total = {total_size} Go"
                return disques_text
            else:
                return "Aucun disque détecté"

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des disques: {e}")
            return "Erreur de récupération des disques"

    def update_tickets_list(self, tickets):
        """Mettre à jour la liste des tickets récents"""
        # Vider la liste actuelle
        self.tickets_list.clear_widgets()

        if not tickets:
            no_tickets = MDLabel(
                text='Aucun ticket',
                theme_text_color='Custom',
                text_color=[0.6, 0.6, 0.7, 1],
                size_hint_y=None,
                height=dp(30),
                font_size='12sp',
                halign='center'
            )
            self.tickets_list.add_widget(no_tickets)
            return

        for ticket in tickets:
            ticket_card = MDCard(
                orientation='vertical',
                padding=dp(8),
                size_hint_y=None,
                height=dp(70),
                elevation=1,
                md_bg_color=[0.1, 0.1, 0.2, 0.8],
                radius=[dp(6)]
            )

            # Titre du ticket
            title_label = MDLabel(
                text=ticket.get('titre', 'Sans titre')[:25] + "..." if len(
                    ticket.get('titre', '')) > 25 else ticket.get('titre', 'Sans titre'),
                theme_text_color='Custom',
                text_color=[0.3, 0.7, 1, 1],
                size_hint_y=None,
                height=dp(20),
                font_size='12sp',
                bold=True,
                halign='left'
            )

            # Statut et priorité
            status_layout = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(20),
                spacing=dp(5)
            )

            status_colors = {
                'ouvert': [1, 0.6, 0.2, 1],
                'en_cours': [0.3, 0.7, 1, 1],
                'ferme': [0.1, 0.8, 0.4, 1]
            }

            priority_colors = {
                'basse': [0.1, 0.8, 0.4, 1],
                'normale': [0.3, 0.7, 1, 1],
                'haute': [1, 0.6, 0.2, 1],
                'critique': [1, 0.2, 0.2, 1]
            }

            status_label = MDLabel(
                text=ticket.get('statut', 'inconnu').replace('_', ' ').title(),
                theme_text_color='Custom',
                text_color=status_colors.get(ticket.get('statut', 'ouvert'), [0.8, 0.8, 0.9, 1]),
                size_hint_x=0.6,
                font_size='10sp',
                halign='left'
            )

            priority_label = MDLabel(
                text=ticket.get('priorite', 'normale').title(),
                theme_text_color='Custom',
                text_color=priority_colors.get(ticket.get('priorite', 'normale'), [0.8, 0.8, 0.9, 1]),
                size_hint_x=0.4,
                font_size='10sp',
                halign='right'
            )

            status_layout.add_widget(status_label)
            status_layout.add_widget(priority_label)

            # Date
            date_label = MDLabel(
                text=f"#{ticket.get('id', 'N/A')} • {ticket.get('date_creation', 'Date inconnue')[:10]}",
                theme_text_color='Custom',
                text_color=[0.6, 0.6, 0.7, 1],
                size_hint_y=None,
                height=dp(15),
                font_size='9sp',
                halign='left'
            )

            ticket_card.add_widget(title_label)
            ticket_card.add_widget(status_layout)
            ticket_card.add_widget(date_label)

            self.tickets_list.add_widget(ticket_card)

    def refresh_comments(self):
        """Actualiser les commentaires"""
        self.fetch_notifications()

    def sync_machine_data(self, instance):
        """Synchroniser les données de la machine"""
        self.machine_name_label.text = "Synchronisation..."
        self.machine_os_label.text = "En cours..."
        self.machine_cpu_label.text = "Patientez..."
        self.machine_memory_label.text = "..."

        # Appeler la synchronisation
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                'http://127.0.0.1:8000/api/v1/machines/synchroniser_machine_locale/',
                headers=headers,
                timeout=30
            )

            if response.status_code in [200, 201]:
                print("✅ Machine synchronisée avec succès")
                # Recharger les données
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.fetch_machine_data(), 1)
            else:
                print(f"❌ Erreur de synchronisation: {response.status_code}")

        except Exception as e:
            print(f"❌ Erreur lors de la synchronisation: {e}")

    def create_modern_stat_card(self, title, value, emoji, color):
        """Créer une carte de statistique moderne"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_x=1,
            elevation=8,
            md_bg_color=[0.08, 0.08, 0.18, 0.95]
        )

        # Header avec emoji et couleur
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        emoji_label = MDLabel(
            text=emoji,
            size_hint_x=None,
            width=dp(40),
            font_size='24sp',
            halign='center'
        )

        title_label = MDLabel(
            text=title,
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='14sp',
            bold=True
        )

        header_layout.add_widget(emoji_label)
        header_layout.add_widget(title_label)

        # Valeur avec couleur personnalisée
        value_label = MDLabel(
            text=value,
            theme_text_color='Custom',
            text_color=color,
            size_hint_y=None,
            height=dp(50),
            font_style='H3',
            halign='center',
            bold=True
        )

        # Indicateur de tendance
        trend_label = MDLabel(
            text='📈 +0%',
            theme_text_color='Custom',
            text_color=[0.6, 0.6, 0.7, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            halign='center'
        )

        card.add_widget(header_layout)
        card.add_widget(value_label)
        card.add_widget(trend_label)

        return card

    def open_drawer(self):
        """Ouvrir le menu de navigation"""
        # TODO: Implémenter le drawer de navigation
        pass

    def logout(self):
        """Déconnexion"""
        app = MDApp.get_running_app()
        app.user_token = None
        app.current_user = None
        self.manager.current = 'login'

    def create_ticket(self, instance):
        """Créer un nouveau ticket"""
        self.manager.current = 'create_ticket'

    def sync_data(self, instance):
        """Synchroniser les données avec le serveur"""
        # TODO: Implémenter la synchronisation
        pass

    def show_software_blocked(self, software_name):
        """Afficher une notification de logiciel bloqué"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="🚫 Logiciel Bloqué",
            text=f"Le logiciel '{software_name}' a été bloqué par votre administrateur IT.\n\n"
                 f"Ce logiciel n'est pas autorisé sur votre machine selon la politique de sécurité.",
            buttons=[
                MDFlatButton(
                    text="Compris",
                    theme_text_color="Custom",
                    text_color=[0.3, 0.7, 1, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

    def show_software_unblocked(self, software_name):
        """Afficher une notification de logiciel débloqué/autorisé"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        dialog = MDDialog(
            title="✅ Logiciel Autorisé",
            text=f"Le logiciel '{software_name}' a été autorisé par votre administrateur IT.\n\n"
                 f"Vous pouvez maintenant utiliser ce logiciel normalement.",
            buttons=[
                MDFlatButton(
                    text="Parfait !",
                    theme_text_color="Custom",
                    text_color=[0.1, 0.8, 0.4, 1],
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

    def create_notification_widget(self):
        """Créer un widget de notification visible dans l'interface"""
        # Widget de notification intégré dans l'interface
        notification_card = MDCard(
            orientation='horizontal',
            padding=dp(15),
            size_hint=(1, None),
            height=dp(60),
            elevation=4,
            md_bg_color=[0.1, 0.1, 0.2, 0.95],
            radius=[dp(8)],
            spacing=dp(10)
        )

        # Icône de notification
        notification_icon = MDIconButton(
            icon='bell',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='24sp',
            disabled=True
        )

        # Texte des notifications
        self.notification_text = MDLabel(
            text='Chargement des notifications...',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            font_size='14sp',
            halign='left',
            valign='center'
        )

        # Bouton pour voir les détails
        view_button = MDRaisedButton(
            text='Voir',
            size_hint_x=None,
            width=dp(80),
            md_bg_color=[0.3, 0.7, 1, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=2,
            on_release=lambda x: self.show_notifications()
        )

        notification_card.add_widget(notification_icon)
        notification_card.add_widget(self.notification_text)
        notification_card.add_widget(view_button)

        # Initialiser les compteurs
        self.unread_notifications_count = 0
        self.total_comments_count = 0

        return notification_card

    def update_notification_badge(self):
        """Mettre à jour l'affichage du badge de notification dans la section commentaires"""
        # Cette méthode met à jour directement la section des commentaires
        # car il n'y a pas de widget de notification séparé
        print(f"🔄 Mise à jour du badge: {self.unread_notifications_count} non lus, {self.total_comments_count} total")

        # Mettre à jour la section des commentaires directement
        self.update_comments_section()

    def show_notifications(self):
        """Afficher la liste des notifications style Facebook avec les commentaires détaillés"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDIconButton
        from kivymd.uix.list import MDList
        from kivymd.uix.scrollview import MDScrollView
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.relativelayout import MDRelativeLayout

        # Éviter l'ouverture multiple du dialog
        if hasattr(self, 'notifications_dialog') and self.notifications_dialog:
            print("⚠️ Dialog des notifications déjà ouvert, fermeture...")
            self.notifications_dialog.dismiss()
            return

        print("🔔 Ouverture du dialog des notifications...")

        # Récupérer les notifications depuis l'API
        self.fetch_notifications()

        # Container principal pour les notifications style Facebook
        notifications_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),  # Augmenté pour plus d'espacement
            adaptive_height=True,
            padding=dp(15)  # Augmenté pour plus de marges
        )

        print(f"📋 Vérification des notifications: {hasattr(self, 'notifications')}")
        if hasattr(self, 'notifications'):
            print(f"📊 Nombre de notifications: {len(self.notifications) if self.notifications else 0}")
            if self.notifications:
                for i, notification in enumerate(self.notifications):
                    print(f"  📝 Notification {i + 1}: {notification.get('titre', 'Sans titre')[:30]}...")

        if hasattr(self, 'notifications') and self.notifications:
            print(f"✅ Création de {len(self.notifications)} cartes de notification...")
            for notification in self.notifications:
                # Créer une carte pour chaque notification (style Facebook)
                notification_card = self.create_facebook_style_notification(notification)
                notifications_container.add_widget(notification_card)
                print(f"  ➕ Carte ajoutée pour: {notification.get('titre', 'Sans titre')[:30]}...")
        else:
            print("⚠️ Aucune notification trouvée, affichage du message vide...")
            # Message si aucune notification
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(20),
                size_hint_y=None,
                height=dp(120),
                elevation=2,
                md_bg_color=[0.08, 0.08, 0.18, 0.95],
                radius=[dp(10)]
            )

            empty_icon = MDIconButton(
                icon='bell-outline',
                theme_icon_color='Custom',
                icon_color=[0.7, 0.7, 0.7, 1],
                icon_size='48sp',
                disabled=True,
                size_hint_y=None,
                height=dp(60)
            )

            empty_text = MDLabel(
                text='Aucune notification\nLes commentaires des admins apparaîtront ici\n\nVérifiez que le serveur est démarré\net que vous êtes connecté.',
                theme_text_color='Custom',
                text_color=[0.7, 0.7, 0.7, 1],
                size_hint_y=None,
                height=dp(80),
                halign='center',
                font_size='14sp'
            )

            empty_card.add_widget(empty_icon)
            empty_card.add_widget(empty_text)
            notifications_container.add_widget(empty_card)

        # Créer le scroll view pour les notifications
        scroll_view = MDScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        scroll_view.add_widget(notifications_container)

        # Titre avec compteur style Facebook
        title_text = f"💬 Commentaires"
        if hasattr(self, 'unread_notifications_count') and self.unread_notifications_count > 0:
            title_text += f" • {self.unread_notifications_count} nouveaux"
        if hasattr(self, 'total_comments_count') and self.total_comments_count > 0:
            title_text += f" ({self.total_comments_count} total)"

        print(f"🏷️ Titre du dialog: {title_text}")

        # Créer et afficher le dialog style Facebook
        self.notifications_dialog = MDDialog(
            title=title_text,
            type="custom",
            content_cls=scroll_view,
            size_hint=(0.95, 0.85),  # Plus grand pour une meilleure visibilité
            buttons=[
                MDFlatButton(
                    text="✅ Tout marquer comme lu",
                    theme_text_color="Custom",
                    text_color=[0.3, 0.7, 1, 1],
                    on_release=lambda x: self.mark_all_notifications_as_read()
                ),
                MDFlatButton(
                    text="🔄 Actualiser",
                    theme_text_color="Custom",
                    text_color=[0.1, 0.8, 0.4, 1],
                    on_release=lambda x: self.refresh_notifications_dialog()
                ),
                MDFlatButton(
                    text="Fermer",
                    theme_text_color="Custom",
                    text_color=[0.6, 0.6, 0.6, 1],
                    on_release=lambda x: self.close_notifications_dialog()
                ),
            ],
        )

        print("🚀 Ouverture du dialog...")
        self.notifications_dialog.open()

    def create_facebook_style_notification(self, notification):
        """Créer une notification style Facebook avec nom du ticket, commentaire et commentateur"""
        from kivymd.uix.card import MDCard
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.relativelayout import MDRelativeLayout

        # Couleur de fond selon le statut de lecture
        is_unread = not notification.get('lu', False)
        bg_color = [0.12, 0.12, 0.22, 1] if is_unread else [0.08, 0.08, 0.18, 0.95]

        # Carte principale - hauteur augmentée pour plus d'informations
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(200),  # Augmenté pour accommoder toutes les informations
            elevation=3 if is_unread else 1,
            md_bg_color=bg_color,
            radius=[dp(12)],
            on_release=lambda x: self.show_facebook_style_detail(notification)
        )

        # Header avec statut nouveau/lu
        header_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=dp(10)
        )

        # Indicateur nouveau commentaire
        status_text = "🔴 NOUVEAU COMMENTAIRE" if is_unread else "✅ Commentaire lu"
        status_label = MDLabel(
            text=status_text,
            theme_text_color='Custom',
            text_color=[1, 0.3, 0.3, 1] if is_unread else [0.3, 0.8, 0.3, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            bold=is_unread,
            halign='left'
        )

        header_layout.add_widget(status_label)

        # Nom du ticket (plus visible)
        ticket_name_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5)
        )

        ticket_icon = MDIconButton(
            icon='ticket',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1] if is_unread else [0.6, 0.8, 1, 1],
            icon_size='18sp',
            disabled=True,
            size_hint_x=None,
            width=dp(25)
        )

        ticket_name = MDLabel(
            text=f"Ticket #{notification.get('ticket_id', 'N/A')}: {notification.get('titre', 'Sans titre')}",
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1] if is_unread else [0.6, 0.8, 1, 1],
            size_hint_y=None,
            height=dp(25),
            text_size=(dp(320), dp(25)),
            font_size='14sp',
            bold=True,
            halign='left',
            valign='center'
        )

        ticket_name_layout.add_widget(ticket_icon)
        ticket_name_layout.add_widget(ticket_name)

        # Commentaire (section principale)
        comment_layout = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5)
        )

        comment_header = MDLabel(
            text='💬 Commentaire:',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            bold=True,
            halign='left'
        )

        comment_text = notification.get('commentaire', 'Pas de commentaire disponible')
        print(f"🔍 Commentaire brut pour affichage: '{comment_text}'")

        # Vérifier si le commentaire existe et n'est pas vide
        if not comment_text or comment_text.strip() == '':
            comment_text = 'Aucun commentaire disponible'
            print("⚠️ Commentaire vide détecté, utilisation du texte par défaut")

        # Limiter la longueur du commentaire affiché
        if len(comment_text) > 120:
            comment_text = comment_text[:120] + "..."
            print(f"✂️ Commentaire tronqué à 120 caractères")

        comment_content = MDLabel(
            text=f'"{comment_text}"',
            theme_text_color='Custom',
            text_color=[1, 1, 1, 1] if is_unread else [0.9, 0.9, 0.9, 1],
            size_hint_y=None,
            height=dp(55),
            text_size=(dp(350), dp(55)),
            font_size='13sp',
            italic=True,
            halign='left',
            valign='top'
        )

        print(f"📝 Texte final affiché: '{comment_content.text}'")

        comment_layout.add_widget(comment_header)
        comment_layout.add_widget(comment_content)

        # Nom du commentateur (section importante)
        commentator_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=dp(5)
        )

        commentator_icon = MDIconButton(
            icon='account',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1] if is_unread else [0.7, 0.7, 0.8, 1],
            icon_size='16sp',
            disabled=True,
            size_hint_x=None,
            width=dp(25)
        )

        commentator_name = MDLabel(
            text=f"Commenté par: {notification.get('auteur', 'Admin')}",
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1] if is_unread else [0.7, 0.7, 0.8, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='13sp',
            bold=True,
            halign='left'
        )

        commentator_layout.add_widget(commentator_icon)
        commentator_layout.add_widget(commentator_name)

        # Footer avec date et actions
        footer_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25),
            spacing=dp(10)
        )

        date_label = MDLabel(
            text=f"📅 {notification.get('date', 'Récemment')}",
            theme_text_color='Custom',
            text_color=[0.5, 0.5, 0.6, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='11sp'
        )

        # Boutons d'action rapide
        actions_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            width=dp(100),
            spacing=dp(5)
        )

        like_btn = MDIconButton(
            icon='thumb-up-outline',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='18sp',
            on_release=lambda x: self.react_to_notification(notification, 'like')
        )

        reply_btn = MDIconButton(
            icon='reply',
            theme_icon_color='Custom',
            icon_color=[0.1, 0.8, 0.4, 1],
            icon_size='18sp',
            on_release=lambda x: self.reply_to_notification(notification)
        )

        actions_layout.add_widget(like_btn)
        actions_layout.add_widget(reply_btn)

        footer_layout.add_widget(date_label)
        footer_layout.add_widget(actions_layout)

        # Assemblage de la carte dans l'ordre demandé
        card.add_widget(header_layout)  # Statut nouveau/lu
        card.add_widget(ticket_name_layout)  # Nom du ticket
        card.add_widget(comment_layout)  # Commentaire
        card.add_widget(commentator_layout)  # Nom du commentateur
        card.add_widget(footer_layout)  # Date et actions

        return card

    def show_facebook_style_detail(self, notification):
        """Afficher le détail complet d'une notification style Facebook"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDIconButton
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel
        from kivymd.uix.card import MDCard
        from kivymd.uix.textfield import MDTextField

        print(f"🔍 Ouverture du détail pour la notification: {notification.get('titre', 'Sans titre')}")

        # Marquer automatiquement comme lu quand on ouvre le détail
        if not notification.get('lu', False):
            self.mark_notification_as_read(notification)

        # Container principal pour le contenu
        content_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            adaptive_height=True,
            padding=dp(10)
        )

        # Header style Facebook
        header_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(100),
            elevation=2,
            md_bg_color=[0.12, 0.12, 0.22, 1],
            radius=[dp(10)]
        )

        # Informations de l'auteur
        author_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        avatar = MDIconButton(
            icon='account-circle',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='32sp',
            disabled=True,
            size_hint_x=None,
            width=dp(40)
        )

        author_info = MDBoxLayout(orientation='vertical')

        author_name = MDLabel(
            text=f"{notification.get('auteur', 'Admin')}",
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='16sp',
            bold=True
        )

        ticket_info = MDLabel(
            text=f"Ticket #{notification.get('ticket_id', 'N/A')}: {notification.get('titre', 'Sans titre')}",
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='14sp'
        )

        author_info.add_widget(author_name)
        author_info.add_widget(ticket_info)

        # Date et statut
        date_status = MDLabel(
            text=f"📅 {notification.get('date', 'Récemment')} • ✅ Lu",
            theme_text_color='Custom',
            text_color=[0.6, 0.6, 0.7, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='12sp'
        )

        author_layout.add_widget(avatar)
        author_layout.add_widget(author_info)

        header_card.add_widget(author_layout)
        header_card.add_widget(date_status)

        # Contenu du commentaire
        comment_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(200),  # Augmenté pour permettre l'affichage complet
            elevation=1,
            md_bg_color=[0.08, 0.08, 0.18, 0.95],
            radius=[dp(8)]
        )

        comment_label = MDLabel(
            text=f'💬 "{notification.get("commentaire", "Pas de commentaire disponible")}"',
            theme_text_color='Custom',
            text_color=[1, 1, 1, 1],
            text_size=(dp(400), None),  # Largeur fixe pour permettre le retour à la ligne
            font_size='14sp',
            italic=True,
            halign='left',
            valign='top'
        )

        comment_card.add_widget(comment_label)

        # Section réactions style Facebook
        reactions_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            size_hint_y=None,
            height=dp(80),
            elevation=1,
            md_bg_color=[0.08, 0.08, 0.18, 0.95],
            radius=[dp(8)]
        )

        reactions_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )

        # Boutons de réaction
        like_btn = MDIconButton(
            icon='thumb-up',
            theme_icon_color='Custom',
            icon_color=[0.3, 0.7, 1, 1],
            icon_size='24sp',
            on_release=lambda x: self.react_to_notification(notification, 'like')
        )

        love_btn = MDIconButton(
            icon='heart',
            theme_icon_color='Custom',
            icon_color=[1, 0.3, 0.5, 1],
            icon_size='24sp',
            on_release=lambda x: self.react_to_notification(notification, 'love')
        )

        reply_btn = MDIconButton(
            icon='reply',
            theme_icon_color='Custom',
            icon_color=[0.1, 0.8, 0.4, 1],
            icon_size='24sp',
            on_release=lambda x: self.reply_to_notification(notification)
        )

        reactions_layout.add_widget(like_btn)
        reactions_layout.add_widget(love_btn)
        reactions_layout.add_widget(reply_btn)

        reactions_label = MDLabel(
            text='👍 J\'aime • ❤️ J\'adore • 💬 Répondre',
            theme_text_color='Custom',
            text_color=[0.6, 0.6, 0.7, 1],
            size_hint_y=None,
            height=dp(20),
            font_size='12sp'
        )

        reactions_card.add_widget(reactions_layout)
        reactions_card.add_widget(reactions_label)

        # Assemblage du contenu
        content_container.add_widget(header_card)
        content_container.add_widget(comment_card)
        content_container.add_widget(reactions_card)

        # Créer et afficher le dialog
        detail_dialog = MDDialog(
            title="💬 Détail du commentaire",
            type="custom",
            content_cls=content_container,
            size_hint=(0.95, 0.85),  # Augmenté pour une meilleure visibilité
            buttons=[
                MDFlatButton(
                    text="Fermer",
                    theme_text_color="Custom",
                    text_color=[0.6, 0.6, 0.6, 1],
                    on_release=lambda x: detail_dialog.dismiss()
                ),
            ],
        )
        detail_dialog.open()

    def react_to_notification(self, notification, reaction_type):
        """Réagir à une notification (like, love, etc.)"""
        from kivymd.uix.snackbar import Snackbar

        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            # Données de la réaction
            data = {
                'type_reaction': reaction_type,
                'notification_id': notification['id']
            }

            # Envoyer la réaction au serveur
            response = requests.post(
                f'http://127.0.0.1:8000/api/v1/notifications/{notification["id"]}/react/',
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                # Afficher une confirmation style Facebook
                reaction_emoji = '👍' if reaction_type == 'like' else '❤️' if reaction_type == 'love' else '👏'
                reaction_text = 'J\'aime' if reaction_type == 'like' else 'J\'adore' if reaction_type == 'love' else 'Bravo'

                snackbar = Snackbar(
                    text=f"{reaction_emoji} Vous avez réagi : {reaction_text}",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=0.5
                )
                snackbar.open()

                print(f"✅ Réaction {reaction_type} envoyée pour la notification {notification['id']}")
            else:
                print(f"❌ Erreur lors de l'envoi de la réaction: {response.status_code}")

        except Exception as e:
            print(f"❌ Erreur lors de la réaction: {e}")

    def reply_to_notification(self, notification):
        """Répondre rapidement à une notification style Facebook"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        from kivymd.uix.textfield import MDTextField
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel

        # Container pour la réponse
        reply_container = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            adaptive_height=True,
            padding=dp(10)
        )

        # Contexte du commentaire original
        context_label = MDLabel(
            text=f'Répondre à {notification.get("auteur", "Admin")} sur le ticket #{notification.get("ticket_id", "N/A")}:',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(30),
            font_size='14sp',
            bold=True
        )

        # Aperçu du commentaire original
        original_comment = MDLabel(
            text=f'💬 "{notification.get("commentaire", "")[:100]}..."',
            theme_text_color='Custom',
            text_color=[0.6, 0.6, 0.7, 1],
            size_hint_y=None,
            height=dp(40),
            font_size='12sp',
            italic=True
        )

        # Champ de réponse
        reply_field = MDTextField(
            hint_text='Écrivez votre réponse...',
            helper_text='Réponse rapide style Facebook',
            helper_text_mode='on_focus',
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            mode="outlined",
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1]
        )

        reply_container.add_widget(context_label)
        reply_container.add_widget(original_comment)
        reply_container.add_widget(reply_field)

        # Fonction pour envoyer la réponse
        def send_reply(instance):
            reply_text = reply_field.text.strip()
            if reply_text:
                self.send_reply_to_notification(notification, reply_text)
                reply_dialog.dismiss()
            else:
                reply_field.error = True
                reply_field.helper_text = 'Veuillez saisir une réponse'

        # Créer et afficher le dialog de réponse
        reply_dialog = MDDialog(
            title="💬 Réponse rapide",
            type="custom",
            content_cls=reply_container,
            size_hint=(0.8, 0.6),
            buttons=[
                MDFlatButton(
                    text="📤 Envoyer",
                    theme_text_color="Custom",
                    text_color=[0.1, 0.8, 0.4, 1],
                    on_release=send_reply
                ),
                MDFlatButton(
                    text="Annuler",
                    theme_text_color="Custom",
                    text_color=[0.6, 0.6, 0.6, 1],
                    on_release=lambda x: reply_dialog.dismiss()
                ),
            ],
        )
        reply_dialog.open()

    def send_reply_to_notification(self, notification, reply_text):
        """Envoyer une réponse à une notification"""
        from kivymd.uix.snackbar import Snackbar

        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            # Données de la réponse
            data = {
                'contenu': reply_text,
                'notification_id': notification['id'],
                'ticket_id': notification.get('ticket_id')
            }

            # Envoyer la réponse au serveur
            response = requests.post(
                f'http://127.0.0.1:8000/api/v1/notifications/{notification["id"]}/reply/',
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 201:
                # Afficher une confirmation
                snackbar = Snackbar(
                    text="💬 Réponse envoyée avec succès !",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=0.5
                )
                snackbar.open()

                print(f"✅ Réponse envoyée pour la notification {notification['id']}")

                # Rafraîchir les notifications
                self.fetch_notifications()
            else:
                print(f"❌ Erreur lors de l'envoi de la réponse: {response.status_code}")

                # Afficher une erreur
                snackbar = Snackbar(
                    text="❌ Erreur lors de l'envoi de la réponse",
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=0.5
                )
                snackbar.open()

        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de la réponse: {e}")

            # Afficher une erreur
            snackbar = Snackbar(
                text="❌ Erreur de connexion",
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=0.5
            )
            snackbar.open()

    def show_notification_detail(self, notification):
        """Afficher le détail complet d'une notification"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        # Contenu complet du commentaire
        commentaire_complet = notification.get('commentaire', 'Pas de commentaire disponible')

        # Boutons selon le statut de lecture
        buttons = []

        if not notification.get('lu', False):
            # Si non lu, proposer de marquer comme lu
            buttons.append(
                MDFlatButton(
                    text="✅ Marquer comme lu",
                    theme_text_color="Custom",
                    text_color=[0.1, 0.8, 0.4, 1],
                    on_release=lambda x: self.mark_notification_as_read_and_close(notification, detail_dialog)
                )
            )
        else:
            # Si déjà lu, proposer de marquer comme non lu
            buttons.append(
                MDFlatButton(
                    text="🔴 Marquer comme non lu",
                    theme_text_color="Custom",
                    text_color=[1, 0.4, 0.2, 1],
                    on_release=lambda x: self.mark_notification_as_unread_and_close(notification, detail_dialog)
                )
            )

        buttons.append(
            MDFlatButton(
                text="Fermer",
                theme_text_color="Custom",
                text_color=[0.6, 0.6, 0.6, 1],
                on_release=lambda x: detail_dialog.dismiss()
            )
        )

        # Statut de lecture dans le titre
        statut_lecture = "🔴 Non lu" if not notification.get('lu', False) else "✅ Lu"

        detail_dialog = MDDialog(
            title=f"💬 Commentaire - Ticket #{notification.get('ticket_id', 'N/A')} ({statut_lecture})",
            text=f"Titre: {notification.get('titre', 'Sans titre')}\n\n"
                 f"Commentaire de {notification.get('auteur', 'Admin')}:\n"
                 f"{commentaire_complet}\n\n"
                 f"Date: {notification.get('date', 'Date inconnue')}",
            buttons=buttons,
        )
        detail_dialog.open()

    def fetch_notifications(self):
        """Récupérer les notifications depuis l'API"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                print("❌ Aucun token d'authentification disponible")
                self.notifications = []
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            print(f"🔄 Récupération des notifications pour l'utilisateur: {app.current_user}")
            print(f"🔑 Token: {app.user_token[:20]}...")

            response = requests.get(
                'http://127.0.0.1:8000/api/v1/notifications/',
                headers=headers,
                timeout=10
            )

            print(f"📡 Réponse API: {response.status_code}")
            print(f"📄 Contenu brut de la réponse: {response.text[:500]}...")

            if response.status_code == 200:
                data = response.json()
                print(f"📋 Format des données: {type(data)}")
                print(f"📋 Données complètes: {data}")

                # Extraire les notifications selon le format
                if isinstance(data, dict):
                    if 'results' in data:
                        # Format paginé DRF
                        self.notifications = data['results']
                        print(f"📋 Utilisation du format paginé DRF: {len(self.notifications)} notifications")
                    elif 'data' in data:
                        self.notifications = data['data']
                        print(f"📋 Utilisation du format data: {len(self.notifications)} notifications")
                    else:
                        # Convertir en liste si c'est un dict simple
                        self.notifications = list(data.values()) if data else []
                        print(f"📋 Conversion dict vers liste: {len(self.notifications)} notifications")
                else:
                    self.notifications = data
                    print(f"📋 Utilisation directe des données: {len(self.notifications)} notifications")

                print(f"✅ {len(self.notifications)} notifications récupérées")

                # Traiter les vraies notifications de commentaires
                if self.notifications:
                    # Compter les notifications non lues et le total
                    self.unread_notifications_count = sum(
                        1 for notif in self.notifications if not notif.get('lu', False))
                    self.total_comments_count = len(self.notifications)
                    print(
                        f"📊 Notifications réelles: {self.total_comments_count} commentaires, {self.unread_notifications_count} non lus")

                    # Afficher les détails complets des notifications pour débogage
                    for i, notif in enumerate(self.notifications):
                        print(f"  📝 Notification {i + 1}:")
                        print(f"    - ID: {notif.get('id', 'N/A')}")
                        print(f"    - Ticket ID: {notif.get('ticket_id', 'N/A')}")
                        print(f"    - Titre: {notif.get('titre', 'Sans titre')}")
                        print(f"    - Commentaire: {notif.get('commentaire', 'Pas de commentaire')}")
                        print(f"    - Auteur: {notif.get('auteur', 'Inconnu')}")
                        print(f"    - Lu: {notif.get('lu', False)}")
                        print(f"    - Date: {notif.get('date', 'Inconnue')}")
                        print(f"    - Toutes les clés: {list(notif.keys())}")
                else:
                    self.total_comments_count = 0
                    self.unread_notifications_count = 0
                    print(f"📊 Aucune notification")

                self.update_notification_badge()
                self.update_comments_section()
            else:
                print(f"❌ Erreur API: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"❌ Détails erreur: {error_data}")
                except:
                    print(f"❌ Réponse brute: {response.text}")

                self.notifications = []
                self.unread_notifications_count = 0
                self.total_comments_count = 0
                self.update_notification_badge()
                self.update_comments_section()

        except Exception as e:
            print(f"❌ Erreur lors de la récupération des notifications: {e}")
            import traceback
            print(f"❌ Traceback complet: {traceback.format_exc()}")
            self.notifications = []
            self.unread_notifications_count = 0
            self.total_comments_count = 0
            self.update_notification_badge()
            self.update_comments_section()

    def update_comments_section(self):
        """Mettre à jour la section des commentaires permanents"""
        # Mettre à jour le badge
        if hasattr(self, 'comments_badge_label'):
            self.comments_badge_label.text = str(self.unread_notifications_count)
            if self.unread_notifications_count > 0:
                self.comments_badge.md_bg_color = [1, 0.2, 0.2, 1]  # Rouge
                self.comments_badge.opacity = 1
            else:
                self.comments_badge.md_bg_color = [0.3, 0.8, 0.3, 1]  # Vert
                self.comments_badge.opacity = 0.7

        # Mettre à jour le statut
        if hasattr(self, 'comments_status'):
            if self.total_comments_count > 0:
                if self.unread_notifications_count > 0:
                    self.comments_status.text = f"{self.total_comments_count} commentaires • {self.unread_notifications_count} nouveaux"
                    self.comments_status.text_color = [1, 0.3, 0.3, 1]
                else:
                    self.comments_status.text = f"{self.total_comments_count} commentaires • Tous lus"
                    self.comments_status.text_color = [0.3, 0.8, 0.3, 1]
            else:
                self.comments_status.text = "Aucun commentaire"
                self.comments_status.text_color = [0.8, 0.8, 0.9, 1]

        # Mettre à jour la liste des commentaires
        if hasattr(self, 'comments_list'):
            self.update_comments_list()

    def update_comments_list(self):
        """Mettre à jour la liste des commentaires dans la section droite"""
        print("🔄 DEBUG: update_comments_list() appelée")

        # Vider la liste actuelle
        self.comments_list.clear_widgets()

        # Debug: vérifier l'existence des notifications
        has_notifications = hasattr(self, 'notifications')
        notifications_exist = has_notifications and self.notifications
        notifications_count = len(self.notifications) if has_notifications and self.notifications else 0

        print(f"🔍 DEBUG: hasattr(self, 'notifications') = {has_notifications}")
        print(f"🔍 DEBUG: self.notifications existe = {notifications_exist}")
        print(f"🔍 DEBUG: Nombre de notifications = {notifications_count}")

        if not has_notifications or not self.notifications:
            print("⚠️ DEBUG: Aucune notification trouvée, affichage du message par défaut")
            no_comments = MDLabel(
                text='Aucun commentaire\nLes commentaires des admins\napparaîtront ici',
                theme_text_color='Custom',
                text_color=[0.6, 0.6, 0.7, 1],
                size_hint_y=None,
                height=dp(60),
                font_size='12sp',
                halign='center'
            )
            self.comments_list.add_widget(no_comments)
            return

        # Afficher les commentaires récents (limité à 10 pour éviter la surcharge)
        recent_notifications = self.notifications[:10]

        for notification in recent_notifications:
            comment_card = MDCard(
                orientation='vertical',
                padding=dp(8),
                size_hint_y=None,
                height=dp(100),
                elevation=2 if not notification.get('lu', False) else 1,
                md_bg_color=[0.12, 0.12, 0.22, 1] if not notification.get('lu', False) else [0.1, 0.1, 0.2, 0.8],
                radius=[dp(6)],
                on_release=lambda x, notif=notification: self.show_facebook_style_detail(notif)
            )

            # 1. Ticket numero_X (en haut de la carte)
            ticket_numero_label = MDLabel(
                text=f"Ticket numero_{notification.get('ticket_id', 'N/A')}",
                theme_text_color='Custom',
                text_color=[0.3, 0.7, 1, 1] if not notification.get('lu', False) else [0.6, 0.8, 1, 1],
                size_hint_y=None,
                height=dp(18),
                font_size='11sp',
                bold=not notification.get('lu', False),
                halign='left'
            )

            # 2. Titre du ticket
            title_label = MDLabel(
                text=notification.get('titre', 'Sans titre'),
                theme_text_color='Custom',
                text_color=[0.3, 0.7, 1, 1] if not notification.get('lu', False) else [0.8, 0.8, 0.9, 1],
                size_hint_y=None,
                height=dp(18),
                font_size='11sp',
                bold=not notification.get('lu', False),
                halign='left'
            )

            # 3. Contenu du commentaire (tronqué à 10 mots maximum)
            comment_text = notification.get('commentaire', 'Pas de commentaire')
            # Tronquer à 10 mots maximum
            comment_words = comment_text.split()
            if len(comment_words) > 10:
                comment_text = ' '.join(comment_words[:10]) + '…'
            else:
                comment_text = ' '.join(comment_words)

            comment_label = MDLabel(
                text=comment_text,
                theme_text_color='Custom',
                text_color=[1, 1, 1, 1] if not notification.get('lu', False) else [0.9, 0.9, 0.9, 1],
                size_hint_y=None,
                height=dp(30),
                text_size=(dp(250), None),  # Permettre le retour à la ligne automatique
                font_size='10sp',
                halign='left',
                valign='top'
            )

            # 4. Par : nom_du_commentateur (en bas)
            author_label = MDLabel(
                text=f"Par : {notification.get('auteur', 'Admin')}",
                theme_text_color='Custom',
                text_color=[0.7, 0.7, 0.8, 1],
                size_hint_y=None,
                height=dp(15),
                font_size='9sp',
                halign='left'
            )

            # Assemblage de la carte dans l'ordre demandé
            comment_card.add_widget(ticket_numero_label)
            comment_card.add_widget(title_label)
            comment_card.add_widget(comment_label)
            comment_card.add_widget(author_label)

            self.comments_list.add_widget(comment_card)

    def mark_notification_as_read(self, notification):
        """Marquer une notification comme lue"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.patch(
                f'http://127.0.0.1:8000/api/v1/notifications/{notification["id"]}/mark_read/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                # Mettre à jour localement
                notification['lu'] = True
                self.unread_notifications_count = max(0, self.unread_notifications_count - 1)
                self.update_notification_badge()

                # Fermer et rouvrir le dialog pour rafraîchir
                if hasattr(self, 'notifications_dialog'):
                    self.notifications_dialog.dismiss()
                    self.show_notifications()

        except Exception as e:
            print(f"❌ Erreur lors du marquage de la notification: {e}")

    def mark_notification_as_read_and_close(self, notification, dialog):
        """Marquer une notification comme lue et fermer le dialogue"""
        self.mark_notification_as_read(notification)
        dialog.dismiss()

    def mark_notification_as_unread_and_close(self, notification, dialog):
        """Marquer une notification comme non lue et fermer le dialogue"""
        self.mark_notification_as_unread(notification)
        dialog.dismiss()

    def mark_notification_as_unread(self, notification):
        """Marquer une notification comme non lue"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.patch(
                f'http://127.0.0.1:8000/api/v1/notifications/{notification["id"]}/mark_unread/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                # Mettre à jour localement
                notification['lu'] = False
                self.unread_notifications_count += 1
                self.update_notification_badge()

                # Fermer et rouvrir le dialog pour rafraîchir
                if hasattr(self, 'notifications_dialog'):
                    self.notifications_dialog.dismiss()
                    self.show_notifications()

        except Exception as e:
            print(f"❌ Erreur lors du marquage de la notification comme non lue: {e}")

    def close_notifications_dialog(self):
        """Fermer proprement le dialog des notifications"""
        if hasattr(self, 'notifications_dialog') and self.notifications_dialog:
            self.notifications_dialog.dismiss()
            self.notifications_dialog = None
            print("🔒 Dialog des notifications fermé")

    def refresh_notifications_dialog(self):
        """Actualiser le dialog des notifications"""
        if hasattr(self, 'notifications_dialog'):
            self.notifications_dialog.dismiss()
            self.notifications_dialog = None
        self.show_notifications()

    def mark_all_notifications_as_read(self):
        """Marquer toutes les notifications comme lues"""
        try:
            app = MDApp.get_running_app()
            if not app.user_token:
                return

            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.post(
                'http://127.0.0.1:8000/api/v1/notifications/mark_all_read/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                # Mettre à jour localement
                for notification in self.notifications:
                    notification['lu'] = True
                self.unread_notifications_count = 0
                self.update_notification_badge()

                # Fermer et rouvrir le dialog pour rafraîchir
                if hasattr(self, 'notifications_dialog'):
                    self.notifications_dialog.dismiss()
                    self.show_notifications()

        except Exception as e:
            print(f"❌ Erreur lors du marquage de toutes les notifications: {e}")


import psutil
import subprocess
import threading
import time
from kivy.clock import Clock


class SoftwareMonitor:
    """Service de surveillance et de blocage des logiciels"""

    def __init__(self, app):
        self.app = app
        self.blocked_software = []
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Démarrer la surveillance des logiciels"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("🔍 Surveillance des logiciels démarrée")

    def stop_monitoring(self):
        """Arrêter la surveillance"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ Surveillance des logiciels arrêtée")

    def _monitor_loop(self):
        """Boucle de surveillance en arrière-plan"""
        while self.monitoring:
            try:
                self.check_running_processes()
                time.sleep(1)  # Vérifier toutes les secondes pour une réaction plus rapide
            except Exception as e:
                print(f"❌ Erreur de surveillance: {e}")
                time.sleep(2)  # Réduire le délai d'erreur aussi

    def check_running_processes(self):
        """Vérifier les processus en cours d'exécution"""
        try:
            for process in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    process_name = process.info['name']
                    if self.is_software_blocked(process_name):
                        self.block_process(process.info['pid'], process_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"❌ Erreur lors de la vérification des processus: {e}")

    def is_software_blocked(self, software_name):
        """Vérifier si un logiciel est bloqué"""
        # Ignorer les services système Windows critiques
        services_systeme_critiques = [
            'svchost.exe',
            'winlogon.exe',
            'csrss.exe',
            'lsass.exe',
            'dwm.exe',
            'explorer.exe',
            'system',
            'registry'
        ]

        # Ne pas ignorer les services d'applications utilisateur
        if software_name.lower() in services_systeme_critiques:
            print(f"⚠️ Service système critique ignoré: {software_name}")
            return False

        # Vérifier si le logiciel est dans la liste des bloqués
        for blocked in self.blocked_software:
            blocked_name = blocked['nom'].lower()
            software_lower = software_name.lower()

            # Correspondance exacte ou partielle
            if (blocked_name in software_lower or
                    software_lower in blocked_name or
                    blocked_name.replace(' ', '') in software_lower.replace(' ', '') or
                    any(word in software_lower for word in blocked_name.split() if len(word) > 3)):
                print(f"🚫 Logiciel détecté comme bloqué: {software_name} (correspond à {blocked['nom']})")
                return True

        return False

    def block_process(self, pid, process_name):
        """Bloquer un processus de manière plus agressive"""
        try:
            process = psutil.Process(pid)

            # Essayer d'abord terminate()
            process.terminate()

            # Attendre un peu et vérifier si le processus est toujours actif
            time.sleep(0.5)
            if process.is_running():
                # Si toujours actif, forcer avec kill()
                process.kill()
                print(f"🚫 Processus forcé à s'arrêter: {process_name} (PID: {pid})")
            else:
                print(f"🚫 Processus bloqué: {process_name} (PID: {pid})")

            # Notifier l'utilisateur
            Clock.schedule_once(
                lambda dt: self.show_block_notification(process_name), 0
            )

        except psutil.NoSuchProcess:
            # Le processus s'est déjà arrêté
            print(f"✅ Processus déjà arrêté: {process_name}")
        except Exception as e:
            print(f"❌ Impossible de bloquer le processus {process_name}: {e}")

    def show_block_notification(self, software_name):
        """Afficher une notification de blocage"""
        # Trouver l'écran actuel et afficher une notification
        try:
            current_screen = self.app.root.current_screen
            if hasattr(current_screen, 'show_software_blocked'):
                current_screen.show_software_blocked(software_name)
            else:
                # Fallback : afficher une notification générique
                print(f"🚫 Logiciel bloqué: {software_name}")
        except Exception as e:
            print(f"❌ Erreur lors de l'affichage de la notification: {e}")
            print(f"🚫 Logiciel bloqué: {software_name}")

    def update_blocked_software_list(self):
        """Mettre à jour la liste des logiciels bloqués depuis le serveur"""
        try:
            if not self.app.user_token:
                return

            headers = {
                'Authorization': f'Token {self.app.user_token}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                'http://127.0.0.1:8000/api/v1/machines/logiciels_bloques/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                nouvelle_liste = response.json()

                # Toujours comparer les listes pour détecter les changements, même si la taille est identique
                anciens_noms = {logiciel['nom'] for logiciel in self.blocked_software}
                nouveaux_noms = {logiciel['nom'] for logiciel in nouvelle_liste}

                # Détecter les nouveaux logiciels bloqués
                nouveaux_bloques = nouveaux_noms - anciens_noms
                if nouveaux_bloques:
                    print(f"🚫 Nouveaux logiciels bloqués: {', '.join(nouveaux_bloques)}")
                    # Vérifier immédiatement si ces logiciels sont en cours d'exécution
                    Clock.schedule_once(lambda dt: self.check_running_processes(), 0.1)

                # Détecter les logiciels débloqués (maintenant autorisés)
                debloques = anciens_noms - nouveaux_noms
                if debloques:
                    print(f"✅ Logiciels maintenant autorisés: {', '.join(debloques)}")
                    # Notifier l'utilisateur des logiciels maintenant autorisés
                    for logiciel_nom in debloques:
                        Clock.schedule_once(
                            lambda dt, nom=logiciel_nom: self.show_software_unblocked(nom), 0.1
                        )

                # Détecter si des changements ont eu lieu
                if nouveaux_bloques or debloques:
                    print(
                        f"🔄 Mise à jour détectée: {len(nouvelle_liste)} logiciels bloqués (était {len(self.blocked_software)})")

                self.blocked_software = nouvelle_liste
                print(f"📋 Liste des logiciels bloqués mise à jour: {len(self.blocked_software)} logiciels")
            else:
                print(f"⚠️ Erreur lors de la récupération des logiciels bloqués: {response.status_code}")

        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour des logiciels bloqués: {e}")

    def show_software_unblocked(self, software_name):
        """Afficher une notification de logiciel débloqué/autorisé"""
        try:
            current_screen = self.app.root.current_screen
            if hasattr(current_screen, 'show_software_unblocked'):
                current_screen.show_software_unblocked(software_name)
            else:
                # Fallback : afficher une notification générique
                print(f"✅ Logiciel maintenant autorisé: {software_name}")
        except Exception as e:
            print(f"❌ Erreur lors de l'affichage de la notification: {e}")
            print(f"✅ Logiciel maintenant autorisé: {software_name}")


class RegisterScreen(MDScreen):
    """Écran d'inscription"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'register'
        self.build_ui()

    def build_ui(self):
        """Construire l'interface d'inscription ultra moderne et responsive"""
        from kivy.core.window import Window

        # Layout principal responsive
        main_layout = MDRelativeLayout()

        # Fond avec dégradé moderne
        background = MDWidget()
        background.md_bg_color = [0.02, 0.02, 0.08, 1]  # Bleu très foncé professionnel
        main_layout.add_widget(background)

        # Container central responsive avec marges équilibrées
        window_width = Window.width
        container_width = min(0.9, max(0.3, 450 / window_width)) if window_width > 0 else 0.5

        center_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            adaptive_height=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(container_width, None),
            padding=[dp(20), dp(20), dp(20), dp(20)]  # Marges équilibrées
        )

        # Titre en en-tête
        title_card = MDCard(
            orientation='vertical',
            padding=dp(25),
            size_hint=(1, None),
            height=dp(80),
            elevation=8,
            md_bg_color=[0.1, 0.1, 0.2, 0.95]
        )

        title = MDLabel(
            text='📝 Inscription ITSM Pro',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            font_style='H4',
            bold=True
        )
        title_card.add_widget(title)

        # Carte d'inscription responsive
        register_card = MDCard(
            orientation='vertical',
            spacing=dp(15),
            padding=[dp(20), dp(20) if Window.width < 1000 else dp(40)],  # Padding adaptatif
            size_hint=(None, None),
            size=(
                min(Window.width * 0.9, dp(1000)),  # Largeur maximale de 1000dp
                min(Window.height * 0.85, dp(900))  # Hauteur maximale de 900dp
            ),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=15,
            md_bg_color=[0.06, 0.06, 0.15, 0.98],
            radius=[dp(15)],
        )

        # Champ Prénom séparé
        self.prenom_field = MDTextField(
            hint_text='Prénom *',
            helper_text='Obligatoire',
            helper_text_mode='on_focus',
            size_hint_y=None,
            height=dp(60),
            mode="line",
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1]
        )

        # Champ Nom séparé
        self.nom_field = MDTextField(
            hint_text='Nom *',
            helper_text='Obligatoire',
            helper_text_mode='on_focus',
            size_hint_y=None,
            height=dp(60),
            mode="line",
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1]
        )

        # Champs verticaux - responsive
        fields = [
            {
                'name': 'email_field',
                'hint': 'Adresse Email *',
                'helper': 'Format: exemple@domaine.com'
            },
            {
                'name': 'username_field',
                'hint': 'Nom d\'utilisateur *',
                'helper': 'Format: @username.entreprise'
            },
            {
                'name': 'password_field',
                'hint': 'Mot de passe *',
                'helper': 'Minimum 8 caractères',
                'password': True
            },
            {
                'name': 'password_confirm_field',
                'hint': 'Confirmer le mot de passe *',
                'helper': 'Doit correspondre au mot de passe',
                'password': True
            }
        ]

        for field in fields:
            setattr(self, field['name'], MDTextField(
                hint_text=field['hint'],
                helper_text=field['helper'],
                helper_text_mode='on_focus',
                size_hint_y=None,
                height=dp(60),
                mode="fill",
                fill_color_normal=[0.1, 0.1, 0.2, 1],
                fill_color_focus=[0.15, 0.15, 0.25, 1],
                line_color_focus=[0.3, 0.7, 1, 1],
                text_color_focus=[1, 1, 1, 1],
                hint_text_color_focus=[0.3, 0.7, 1, 1],
                password=field.get('password', False)
            ))

        # Structure (combobox)
        structure_label = MDLabel(
            text='Structure/Entreprise *',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            bold=True
        )

        self.structure_button = MDRaisedButton(
            text='Sélectionner une structure',
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.15, 0.15, 0.25, 1],
            theme_text_color="Custom",
            text_color=[0.8, 0.8, 0.9, 1],
            elevation=4,
            on_release=self.open_structure_menu
        )

        self.selected_structure = None
        self.structures_list = []

        # Les widgets seront ajoutés dans la section assemblage plus bas

        # Les champs prénom et nom sont maintenant séparés individuellement

        # Boutons
        buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )

        register_button = MDRaisedButton(
            text='S\'inscrire',
            size_hint_x=0.6,
            md_bg_color=[0.1, 0.8, 0.4, 1],  # Vert moderne
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=6,
            on_release=self.register
        )

        back_button = MDRaisedButton(
            text='Retour',
            size_hint_x=0.4,
            md_bg_color=[0.6, 0.6, 0.6, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=self.go_back
        )

        buttons_layout.add_widget(register_button)
        buttons_layout.add_widget(back_button)

        # Message d'état
        self.status_label = MDLabel(
            text='',
            theme_text_color='Error',
            size_hint_y=None,
            height='30dp',
            halign='center'
        )

        # Assemblage - Ordre: prénom, nom, email, nom d'utilisateur, structure, mot de passe, confirmation
        register_card.add_widget(self.prenom_field)
        register_card.add_widget(self.nom_field)
        register_card.add_widget(self.email_field)
        register_card.add_widget(self.username_field)
        register_card.add_widget(structure_label)
        register_card.add_widget(self.structure_button)
        register_card.add_widget(self.password_field)
        register_card.add_widget(self.password_confirm_field)
        register_card.add_widget(buttons_layout)
        register_card.add_widget(self.status_label)

        # Charger les structures au démarrage
        self.load_structures()

        center_layout.add_widget(title_card)
        center_layout.add_widget(register_card)

        main_layout.add_widget(center_layout)
        self.add_widget(main_layout)

    def load_structures(self):
        """Charger les structures depuis l'API"""
        try:
            response = requests.get('http://127.0.0.1:8000/api/v1/users/structures/', timeout=5)
            if response.status_code == 200:
                self.structures_list = response.json()
                if self.structures_list:
                    # Sélectionner la première structure par défaut
                    self.selected_structure = self.structures_list[0]
                    self.structure_button.text = self.selected_structure['nom']
            else:
                # Structure par défaut si l'API n'est pas accessible
                self.structures_list = [{'id': 1, 'nom': 'Entreprise Démo', 'code': 'demo'}]
                self.selected_structure = self.structures_list[0]
                self.structure_button.text = self.selected_structure['nom']
        except:
            # Structure par défaut en cas d'erreur
            self.structures_list = [{'id': 1, 'nom': 'Entreprise Démo', 'code': 'demo'}]
            self.selected_structure = self.structures_list[0]
            self.structure_button.text = self.selected_structure['nom']

    def open_structure_menu(self, instance):
        """Ouvrir le menu de sélection des structures"""
        menu_items = []
        for structure in self.structures_list:
            menu_items.append({
                "text": structure['nom'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=structure: self.select_structure(x),
            })

        self.structure_menu = MDDropdownMenu(
            caller=self.structure_button,
            items=menu_items,
            width_mult=4,
        )
        self.structure_menu.open()

    def select_structure(self, structure):
        """Sélectionner une structure"""
        self.selected_structure = structure
        self.structure_button.text = structure['nom']
        self.structure_menu.dismiss()

    def register(self, instance):
        """Gérer l'inscription"""
        # Récupérer les données du formulaire
        prenom = self.prenom_field.text.strip()
        nom = self.nom_field.text.strip()
        email = self.email_field.text.strip()
        username = self.username_field.text.strip()
        password = self.password_field.text
        password_confirm = self.password_confirm_field.text

        # Validation des champs obligatoires
        if not all([prenom, nom, email, username, password, password_confirm]):
            self.status_label.text = 'Veuillez remplir tous les champs obligatoires'
            return

        # Validation de la structure
        if not self.selected_structure:
            self.status_label.text = 'Veuillez sélectionner une structure'
            return

        # Validation du mot de passe
        if password != password_confirm:
            self.status_label.text = 'Les mots de passe ne correspondent pas'
            return

        if len(password) < 8:
            self.status_label.text = 'Le mot de passe doit contenir au moins 8 caractères'
            return

        # Validation de l'email
        if '@' not in email or '.' not in email:
            self.status_label.text = 'Adresse email invalide'
            return

        try:
            # Préparer les données pour l'inscription
            data = {
                'prenom': prenom,
                'nom': nom,
                'email': email,
                'username': username,
                'password': password,
                'password_confirm': password_confirm,
                'structure': self.selected_structure['id'],
                'role': 'utilisateur'
            }

            # Tentative d'inscription via l'API
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/users/register/',
                data=data,
                timeout=10
            )

            if response.status_code == 201:
                self.status_label.text = 'Inscription réussie! Vous pouvez maintenant vous connecter.'
                self.status_label.theme_text_color = 'Primary'

                # Vider les champs
                self.clear_fields()

                # Retourner à l'écran de connexion après 2 secondes
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.go_back(None), 2)

            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    if 'prenom' in error_data:
                        self.status_label.text = 'Erreur dans le prénom'
                    elif 'nom' in error_data:
                        self.status_label.text = 'Erreur dans le nom'
                    elif 'email' in error_data:
                        self.status_label.text = 'Cette adresse email est déjà utilisée'
                    elif 'username' in error_data:
                        self.status_label.text = 'Un utilisateur avec ce nom existe déjà'
                    elif 'structure' in error_data:
                        self.status_label.text = 'Erreur dans la structure sélectionnée'
                    elif 'password' in error_data:
                        self.status_label.text = 'Erreur dans le mot de passe'
                    elif 'password_confirm' in error_data:
                        self.status_label.text = 'Erreur dans la confirmation du mot de passe'
                    else:
                        self.status_label.text = 'Erreur de validation des données'
                except:
                    self.status_label.text = 'Erreur de validation des données'
            else:
                self.status_label.text = f'Erreur d\'inscription (Code: {response.status_code})'

        except requests.exceptions.RequestException:
            self.status_label.text = 'Erreur de connexion au serveur'
        except Exception as e:
            self.status_label.text = f'Erreur: {str(e)}'

    def clear_fields(self):
        """Vider tous les champs du formulaire"""
        self.prenom_field.text = ''
        self.nom_field.text = ''
        self.email_field.text = ''
        self.username_field.text = ''
        self.password_field.text = ''
        self.password_confirm_field.text = ''

    def go_back(self, instance):
        """Retourner à l'écran de connexion"""
        self.manager.current = 'login'


class CreateTicketScreen(MDScreen):
    """Écran de création de tickets"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'create_ticket'
        self.build_ui()

    def build_ui(self):
        """Construire l'interface de création de tickets"""
        from kivy.core.window import Window

        # Layout principal responsive
        main_layout = MDRelativeLayout()

        # Fond avec dégradé moderne
        background = MDWidget()
        background.md_bg_color = [0.02, 0.02, 0.08, 1]
        main_layout.add_widget(background)

        # Container central responsive
        window_width = Window.width
        container_width = min(0.9, max(0.4, 500 / window_width)) if window_width > 0 else 0.6

        center_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            adaptive_height=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(container_width, None),
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )

        # Titre
        title_card = MDCard(
            orientation='vertical',
            padding=dp(25),
            size_hint=(1, None),
            height=dp(80),
            elevation=8,
            md_bg_color=[0.1, 0.1, 0.2, 0.95]
        )

        title = MDLabel(
            text='🎫 Créer un Nouveau Ticket',
            theme_text_color='Custom',
            text_color=[0.3, 0.7, 1, 1],
            size_hint_y=None,
            height=dp(40),
            halign='center',
            font_style='H4',
            bold=True
        )
        title_card.add_widget(title)

        # Carte de création de ticket
        ticket_card = MDCard(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(30),
            size_hint=(1, None),
            height=dp(600),
            elevation=15,
            md_bg_color=[0.06, 0.06, 0.15, 0.98]
        )

        # Champ Titre
        self.titre_field = MDTextField(
            hint_text='Titre du ticket *',
            helper_text='Décrivez brièvement le problème',
            helper_text_mode='on_focus',
            size_hint_y=None,
            height=dp(60),
            mode="line",
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1]
        )

        # Champ Description
        self.description_field = MDTextField(
            hint_text='Description détaillée *',
            helper_text='Décrivez le problème en détail',
            helper_text_mode='on_focus',
            multiline=True,
            size_hint_y=None,
            height=dp(120),
            mode="line",
            line_color_focus=[0.3, 0.7, 1, 1],
            text_color_focus=[1, 1, 1, 1],
            hint_text_color_focus=[0.3, 0.7, 1, 1]
        )

        # Champ Priorité
        priority_label = MDLabel(
            text='Priorité *',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            bold=True
        )

        self.priority_button = MDRaisedButton(
            text='Sélectionner la priorité',
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.15, 0.15, 0.25, 1],
            theme_text_color="Custom",
            text_color=[0.8, 0.8, 0.9, 1],
            elevation=4,
            on_release=self.open_priority_menu
        )

        self.selected_priority = None
        self.priorities_list = [
            {'id': 'basse', 'nom': 'Basse', 'color': [0.1, 0.8, 0.4, 1]},
            {'id': 'normale', 'nom': 'Normale', 'color': [0.3, 0.7, 1, 1]},
            {'id': 'haute', 'nom': 'Haute', 'color': [1, 0.6, 0.2, 1]},
            {'id': 'critique', 'nom': 'Critique', 'color': [1, 0.2, 0.2, 1]}
        ]

        # Champ Catégorie
        category_label = MDLabel(
            text='Catégorie *',
            theme_text_color='Custom',
            text_color=[0.8, 0.8, 0.9, 1],
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            bold=True
        )

        self.category_button = MDRaisedButton(
            text='Sélectionner la catégorie',
            size_hint_y=None,
            height=dp(50),
            md_bg_color=[0.15, 0.15, 0.25, 1],
            theme_text_color="Custom",
            text_color=[0.8, 0.8, 0.9, 1],
            elevation=4,
            on_release=self.open_category_menu
        )

        self.selected_category = None
        self.categories_list = [
            {'id': 1, 'nom': 'Matériel'},
            {'id': 2, 'nom': 'Logiciel'},
            {'id': 3, 'nom': 'Réseau'},
            {'id': 4, 'nom': 'Sécurité'},
            {'id': 5, 'nom': 'Autre'}
        ]

        # Boutons
        buttons_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(50)
        )

        create_button = MDRaisedButton(
            text='Créer le Ticket',
            size_hint_x=0.6,
            md_bg_color=[0.1, 0.8, 0.4, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=6,
            on_release=self.create_ticket
        )

        cancel_button = MDRaisedButton(
            text='Annuler',
            size_hint_x=0.4,
            md_bg_color=[0.6, 0.6, 0.6, 1],
            theme_text_color="Custom",
            text_color=[1, 1, 1, 1],
            elevation=4,
            on_release=self.go_back
        )

        buttons_layout.add_widget(create_button)
        buttons_layout.add_widget(cancel_button)

        # Message d'état
        self.status_label = MDLabel(
            text='',
            theme_text_color='Error',
            size_hint_y=None,
            height='30dp',
            halign='center'
        )

        # Assemblage
        ticket_card.add_widget(self.titre_field)
        ticket_card.add_widget(self.description_field)
        ticket_card.add_widget(priority_label)
        ticket_card.add_widget(self.priority_button)
        ticket_card.add_widget(category_label)
        ticket_card.add_widget(self.category_button)
        ticket_card.add_widget(buttons_layout)
        ticket_card.add_widget(self.status_label)

        center_layout.add_widget(title_card)
        center_layout.add_widget(ticket_card)

        main_layout.add_widget(center_layout)
        self.add_widget(main_layout)

    def open_priority_menu(self, instance):
        """Ouvrir le menu de sélection des priorités"""
        menu_items = []
        for priority in self.priorities_list:
            menu_items.append({
                "text": priority['nom'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=priority: self.select_priority(x),
            })

        self.priority_menu = MDDropdownMenu(
            caller=self.priority_button,
            items=menu_items,
            width_mult=4,
        )
        self.priority_menu.open()

    def select_priority(self, priority):
        """Sélectionner une priorité"""
        self.selected_priority = priority
        self.priority_button.text = priority['nom']
        self.priority_button.md_bg_color = priority['color']
        self.priority_menu.dismiss()

    def open_category_menu(self, instance):
        """Ouvrir le menu de sélection des catégories"""
        menu_items = []
        for category in self.categories_list:
            menu_items.append({
                "text": category['nom'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=category: self.select_category(x),
            })

        self.category_menu = MDDropdownMenu(
            caller=self.category_button,
            items=menu_items,
            width_mult=4,
        )
        self.category_menu.open()

    def select_category(self, category):
        """Sélectionner une catégorie"""
        self.selected_category = category
        self.category_button.text = category['nom']
        self.category_menu.dismiss()

    def create_ticket(self, instance):
        """Créer le ticket"""
        # Récupérer les données du formulaire
        titre = self.titre_field.text.strip()
        description = self.description_field.text.strip()

        # Validation des champs obligatoires
        if not titre:
            self.status_label.text = 'Le titre est obligatoire'
            return

        if not description:
            self.status_label.text = 'La description est obligatoire'
            return

        if not self.selected_priority:
            self.status_label.text = 'Veuillez sélectionner une priorité'
            return

        if not self.selected_category:
            self.status_label.text = 'Veuillez sélectionner une catégorie'
            return

        try:
            # Récupérer le token utilisateur
            app = MDApp.get_running_app()
            if not app.user_token:
                self.status_label.text = 'Erreur d\'authentification'
                return

            # Préparer les données pour la création du ticket
            data = {
                'titre': titre,
                'description': description,
                'priorite': self.selected_priority['id'],
                'categorie': self.selected_category['id'],
                'statut': 'ouvert'
            }

            # Headers avec token d'authentification
            headers = {
                'Authorization': f'Token {app.user_token}',
                'Content-Type': 'application/json'
            }

            # Tentative de création du ticket via l'API
            response = requests.post(
                'http://127.0.0.1:8000/api/v1/tickets/',
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 201:
                self.status_label.text = 'Ticket créé avec succès!'
                self.status_label.theme_text_color = 'Primary'

                # Vider les champs
                self.clear_fields()

                # Retourner au dashboard après 2 secondes
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.go_back(None), 2)

            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.status_label.text = f'Erreur de validation: {error_data}'
                except:
                    self.status_label.text = 'Erreur de validation des données'
            else:
                self.status_label.text = f'Erreur de création (Code: {response.status_code})'

        except requests.exceptions.RequestException:
            self.status_label.text = 'Erreur de connexion au serveur'
        except Exception as e:
            self.status_label.text = f'Erreur: {str(e)}'

    def clear_fields(self):
        """Vider tous les champs du formulaire"""
        self.titre_field.text = ''
        self.description_field.text = ''
        self.selected_priority = None
        self.selected_category = None
        self.priority_button.text = 'Sélectionner la priorité'
        self.priority_button.md_bg_color = [0.15, 0.15, 0.25, 1]
        self.category_button.text = 'Sélectionner la catégorie'

    def go_back(self, instance):
        """Retourner au dashboard"""
        self.manager.current = 'dashboard'


class ITSMApp(MDApp):
    """Application principale ITSM"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'ITSM Pro - Système de Gestion IT Nouvelle Génération'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.accent_palette = 'LightBlue'
        self.theme_cls.material_style = "M3"
        self.user_token = None
        self.current_user = None

        # Initialiser le moniteur de logiciels
        self.software_monitor = SoftwareMonitor(self)

        # Configuration responsive
        from kivy.core.window import Window
        Window.minimum_width = 800
        Window.minimum_height = 600

    def build(self):
        """Construire l'interface utilisateur principale"""
        # Créer le gestionnaire d'écrans
        screen_manager = ScreenManager()

        # Ajouter tous les écrans
        screen_manager.add_widget(LoginScreen())
        screen_manager.add_widget(RegisterScreen())
        screen_manager.add_widget(DashboardScreen())
        screen_manager.add_widget(CreateTicketScreen())

        # Commencer par l'écran de connexion
        screen_manager.current = 'login'

        return screen_manager

    def on_start(self):
        """Démarrage de l'application"""
        print("🚀 Application ITSM démarrée")

        # Vérifier la connexion au serveur
        try:
            response = requests.get('http://127.0.0.1:8000/', timeout=5)
            if response.status_code == 200:
                print("✅ Connexion au serveur ITSM réussie")
            else:
                print("⚠️ Serveur ITSM non accessible")
        except:
            print("❌ Impossible de se connecter au serveur ITSM")

    def start_software_monitoring(self):
        """Démarrer la surveillance des logiciels après connexion"""
        if self.user_token:
            self.software_monitor.update_blocked_software_list()
            self.software_monitor.start_monitoring()

            # Programmer une mise à jour périodique de la liste (temps réel rapide)
            Clock.schedule_interval(
                lambda dt: self.software_monitor.update_blocked_software_list(),
                2  # Toutes les 2 secondes pour un temps réel très rapide
            )

            # Démarrer la surveillance des notifications
            self.start_notification_monitoring()

    def start_notification_monitoring(self):
        """Démarrer la surveillance des notifications"""
        # Vérifier les notifications toutes les 30 secondes
        Clock.schedule_interval(
            lambda dt: self.check_notifications(),
            30
        )

    def check_notifications(self):
        """Vérifier les nouvelles notifications"""
        try:
            # Trouver l'écran dashboard actuel
            current_screen = self.root.current_screen
            if hasattr(current_screen, 'fetch_notifications') and current_screen.name == 'dashboard':
                current_screen.fetch_notifications()
        except Exception as e:
            print(f"❌ Erreur lors de la vérification des notifications: {e}")

    def stop_software_monitoring(self):
        """Arrêter la surveillance des logiciels"""
        self.software_monitor.stop_monitoring()

    def on_stop(self):
        """Arrêt de l'application"""
        self.stop_software_monitoring()
        print("👋 Application ITSM fermée")


def main():
    """Fonction principale"""
    print("🖥️ Démarrage de l'application desktop ITSM")

    # Vérifier les dépendances
    try:
        import kivy
        import kivymd
        print(f"✅ Kivy {kivy.__version__} détecté")
        print(f"✅ KivyMD détecté")
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Installez avec: pip install kivy kivymd")
        return

    # Lancer l'application
    app = ITSMApp()
    app.run()


if __name__ == '__main__':
    main()