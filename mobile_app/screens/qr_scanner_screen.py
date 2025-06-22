"""
Écran de scan QR Code pour l'application mobile ITSM Compagnon
Permet de scanner les codes QR des équipements pour accès rapide
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.snackbar import MDSnackbar
from kivy.uix.camera import Camera
from kivy.metrics import dp
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.uix.image import Image


class QRScannerScreen(Screen):
    """Écran de scan de codes QR"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qr_scanner = None
        self.is_scanning = False
        self.camera_widget = None
        self.current_camera_index = 0  # Index de la caméra actuelle
        self.available_cameras = []    # Liste des caméras disponibles
        self.build_ui()
    
    def build_ui(self):
        """Construire l'interface utilisateur"""
        # Layout principal
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(10)
        )
        
        # Barre d'outils
        toolbar = MDTopAppBar(
            title="Scanner QR Code",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["camera-switch", lambda x: self.switch_camera()],
                ["flashlight", lambda x: self.toggle_flashlight()],
                ["image", lambda x: self.scan_from_gallery()]
            ]
        )
        
        # Zone de scan
        self.scan_area = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20)
        )
        
        # Titre
        title = MDLabel(
            text="Positionnez le code QR dans le cadre",
            theme_text_color="Primary",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )
        
        # Zone caméra/placeholder
        self.camera_container = MDCard(
            size_hint=(1, 0.6),
            elevation=3,
            padding=dp(10)
        )
        
        # Placeholder pour la caméra
        self.camera_placeholder = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20)
        )
        
        placeholder_icon = MDLabel(
            text="📷",
            font_size="72sp",
            halign="center",
            size_hint_y=None,
            height=dp(100)
        )
        
        placeholder_text = MDLabel(
            text="Scanner QR disponible\nOpenCV non installé - Mode simulation activé\nUtilisez 'Scanner depuis galerie' ou saisissez manuellement",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(80)
        )
        
        self.camera_placeholder.add_widget(placeholder_icon)
        self.camera_placeholder.add_widget(placeholder_text)
        self.camera_container.add_widget(self.camera_placeholder)
        
        # Boutons de contrôle
        button_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            adaptive_height=True,
            size_hint_y=None,
            height=dp(60)
        )
        
        self.scan_button = MDRaisedButton(
            text="Démarrer le scan",
            size_hint_x=0.25,
            on_release=self.toggle_scanning
        )
        
        gallery_button = MDRaisedButton(
            text="Galerie",
            size_hint_x=0.25,
            on_release=self.scan_from_gallery
        )
        
        manual_button = MDRaisedButton(
            text="Saisie manuelle",
            size_hint_x=0.25,
            on_release=self.manual_qr_input
        )
        
        iriun_button = MDRaisedButton(
            text="Iriun",
            size_hint_x=0.25,
            on_release=self.force_iriun_camera
        )
        
        button_layout.add_widget(self.scan_button)
        button_layout.add_widget(gallery_button)
        button_layout.add_widget(manual_button)
        button_layout.add_widget(iriun_button)
        
        # Instructions
        instructions_card = MDCard(
            size_hint_y=None,
            height=dp(120),
            padding=dp(15),
            elevation=2
        )
        
        instructions = MDLabel(
            text="Instructions:\n• Pointez la caméra vers le code QR\n• Maintenez l'appareil stable\n• Assurez-vous d'avoir un bon éclairage",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(90)
        )
        
        instructions_card.add_widget(instructions)
        
        # Assembler la zone de scan
        self.scan_area.add_widget(title)
        self.scan_area.add_widget(self.camera_container)
        self.scan_area.add_widget(button_layout)
        self.scan_area.add_widget(instructions_card)
        
        # Assembler le layout principal
        main_layout.add_widget(toolbar)
        main_layout.add_widget(self.scan_area)
        
        # Ajouter au screen
        self.add_widget(main_layout)
        
        # Initialiser le scanner
        Clock.schedule_once(self.initialize_scanner, 0.5)
    
    def initialize_scanner(self, dt):
        """Initialiser le scanner QR"""
        try:
            try:
                from ..utils.qr_scanner import QRScanner
            except ImportError:
                from utils.qr_scanner import QRScanner
            self.qr_scanner = QRScanner(camera_index=self.current_camera_index)
            
            # Vérifier si le scanner est disponible
            if self.qr_scanner.is_available():
                # Toujours essayer de configurer la caméra
                self.setup_camera()
            else:
                Logger.warning("QRScannerScreen: Scanner non disponible")
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur initialisation scanner: {e}")
    
    def setup_camera(self):
        """Configurer la caméra"""
        try:
            # Détecter les caméras disponibles
            self.detect_cameras()
            
            # Remplacer le placeholder par la caméra
            self.camera_container.clear_widgets()
            
            # Créer le widget caméra avec l'index actuel et démarrer automatiquement
            self.camera_widget = Camera(
                resolution=(640, 480),
                play=True,  # Démarrer automatiquement la caméra
                index=self.current_camera_index
            )
            
            self.camera_container.add_widget(self.camera_widget)
            
            # Mettre à jour le bouton
            self.scan_button.text = "Démarrer le scan"
            self.scan_button.disabled = False
            
            # Afficher des informations sur la caméra
            camera_info = f"Caméra {self.current_camera_index} active"
            if len(self.available_cameras) > 1:
                camera_info += f" ({len(self.available_cameras)} disponibles)"
            
            self.show_info(camera_info)
            Logger.info(f"QRScannerScreen: Caméra {self.current_camera_index} configurée et démarrée")
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur configuration caméra: {e}")
            self.show_error(f"Erreur caméra: {str(e)}")
    
    def detect_cameras(self):
        """Détecter les caméras disponibles"""
        try:
            self.available_cameras = []
            
            # Tester les indices de caméra de 0 à 4 (couvre la plupart des cas)
            for i in range(5):
                try:
                    # Test rapide avec OpenCV si disponible
                    if hasattr(self.qr_scanner, 'get_camera_info'):
                        camera_info = self.qr_scanner.get_camera_info()
                        if camera_info['cameras']:
                            self.available_cameras = [cam['index'] for cam in camera_info['cameras']]
                            break
                    else:
                        # Fallback : ajouter les indices standards
                        self.available_cameras = [0, 1, 2]  # Indices les plus communs
                        break
                except:
                    continue
            
            if not self.available_cameras:
                self.available_cameras = [0]  # Au moins l'index 0 par défaut
            
            # Par défaut, utiliser la webcam de la machine (index 0)
            # Détecter spécifiquement Iriun (souvent sur l'index 1 ou 2) mais ne pas l'utiliser par défaut
            iriun_index = self.detect_iriun_camera()
            if iriun_index is not None and iriun_index not in self.available_cameras:
                self.available_cameras.append(iriun_index)
                Logger.info(f"QRScannerScreen: Iriun détecté sur index {iriun_index} (disponible via bouton Iriun)")
            
            Logger.info(f"QRScannerScreen: Caméras détectées: {self.available_cameras}")
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur détection caméras: {e}")
            self.available_cameras = [0]
    
    def detect_iriun_camera(self):
        """Détecter spécifiquement la caméra Iriun"""
        try:
            # Iriun est souvent sur les indices 1, 2 ou 3
            for index in [1, 2, 3]:
                try:
                    # Test simple avec Kivy Camera
                    from kivy.uix.camera import Camera
                    test_camera = Camera(index=index, resolution=(320, 240))
                    # Si ça marche, c'est probablement une caméra valide
                    test_camera = None  # Libérer
                    return index
                except:
                    continue
            return None
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur détection Iriun: {e}")
            return None
    
    def switch_camera(self):
        """Changer de caméra"""
        try:
            if len(self.available_cameras) <= 1:
                self.show_info("Une seule caméra disponible")
                return
            
            # Arrêter le scan en cours
            if self.is_scanning:
                self.stop_scanning()
            
            # Passer à la caméra suivante
            current_pos = self.available_cameras.index(self.current_camera_index) if self.current_camera_index in self.available_cameras else 0
            next_pos = (current_pos + 1) % len(self.available_cameras)
            self.current_camera_index = self.available_cameras[next_pos]
            
            # Réinitialiser le scanner QR avec le nouvel index
            try:
                from ..utils.qr_scanner import QRScanner
            except ImportError:
                from utils.qr_scanner import QRScanner
            self.qr_scanner = QRScanner(camera_index=self.current_camera_index)
            
            # Reconfigurer la caméra
            self.setup_camera()
            
            Logger.info(f"QRScannerScreen: Changement vers caméra {self.current_camera_index}")
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur changement caméra: {e}")
            self.show_error(f"Erreur changement caméra: {str(e)}")
    
    def toggle_scanning(self, button):
        """Démarrer/arrêter le scan"""
        try:
            if not self.is_scanning:
                self.start_scanning()
            else:
                self.stop_scanning()
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur toggle scan: {e}")
            self.show_error(f"Erreur: {str(e)}")
    
    def start_scanning(self):
        """Démarrer le scan"""
        try:
            if not self.qr_scanner:
                self.show_error("Scanner non disponible")
                return
            
            # Démarrer la caméra
            if self.camera_widget:
                self.camera_widget.play = True
            
            # Démarrer le scan
            success = self.qr_scanner.start_scanning(self.on_qr_detected)
            
            if success:
                self.is_scanning = True
                self.scan_button.text = "Arrêter le scan"
                self.show_info("Scan en cours...")
                Logger.info("QRScannerScreen: Scan démarré")
            else:
                self.show_error("Impossible de démarrer le scan")
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur démarrage scan: {e}")
            self.show_error(f"Erreur: {str(e)}")
    
    def stop_scanning(self):
        """Arrêter le scan"""
        try:
            if self.qr_scanner:
                self.qr_scanner.stop_scanning()
            
            # Arrêter la caméra
            if self.camera_widget:
                self.camera_widget.play = False
            
            self.is_scanning = False
            self.scan_button.text = "Démarrer le scan"
            
            Logger.info("QRScannerScreen: Scan arrêté")
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur arrêt scan: {e}")
    
    def on_qr_detected(self, qr_data):
        """Callback appelé quand un QR code est détecté"""
        try:
            Logger.info(f"QRScannerScreen: QR détecté: {qr_data}")
            
            # Arrêter le scan
            Clock.schedule_once(lambda dt: self.stop_scanning(), 0)
            
            # Valider les données QR
            if self.qr_scanner:
                validation = self.qr_scanner.validate_qr_data(qr_data)
                Clock.schedule_once(lambda dt: self.process_qr_data(qr_data, validation), 0)
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur traitement QR: {e}")
    
    def process_qr_data(self, qr_data, validation):
        """Traiter les données du QR code"""
        try:
            if not validation['valid']:
                self.show_error("Code QR non reconnu")
                return
            
            qr_type = validation['type']
            
            if qr_type in ['machine_id', 'serial_number', 'inventory_number']:
                # Rechercher la machine
                self.search_machine(qr_data)
            elif qr_type == 'json':
                # Traiter les données JSON
                self.process_json_qr(validation['parsed'])
            elif qr_type == 'url':
                # Ouvrir l'URL
                self.open_url(validation['parsed']['url'])
            else:
                # Afficher les données
                self.show_qr_result(qr_data, validation)
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur traitement données QR: {e}")
            self.show_error(f"Erreur traitement: {str(e)}")
    
    def search_machine(self, qr_data):
        """Rechercher une machine par code QR"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            # Afficher un indicateur de chargement
            self.show_info("Recherche de la machine...")
            
            # Effectuer la recherche dans un thread
            import threading
            search_thread = threading.Thread(
                target=self.perform_machine_search,
                args=(qr_data,),
                daemon=True
            )
            search_thread.start()
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur recherche machine: {e}")
            self.show_error(f"Erreur recherche: {str(e)}")
    
    def perform_machine_search(self, qr_data):
        """Effectuer la recherche de machine (dans un thread)"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            
            success, machine_data = app.api_client.search_machine_by_qr(qr_data)
            
            # Programmer la mise à jour de l'UI
            Clock.schedule_once(
                lambda dt: self.on_machine_search_result(success, machine_data, qr_data), 
                0
            )
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur recherche thread: {e}")
            Clock.schedule_once(
                lambda dt: self.on_machine_search_result(False, {'error': str(e)}, qr_data), 
                0
            )
    
    def on_machine_search_result(self, success, result, qr_data):
        """Gérer le résultat de la recherche de machine"""
        try:
            if success:
                # Machine trouvée, afficher les détails
                self.show_machine_details(result)
            else:
                error_msg = result.get('error', 'Machine non trouvée')
                self.show_error(error_msg)
                # Proposer de créer un ticket
                self.offer_create_ticket(qr_data)
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur résultat recherche: {e}")
    
    def show_machine_details(self, machine_data):
        """Afficher les détails de la machine trouvée"""
        try:
            machine_name = machine_data.get('nom', 'Machine inconnue')
            machine_status = machine_data.get('statut', 'Statut inconnu')
            machine_user = machine_data.get('utilisateur_info', {}).get('nom_complet', 'Non assigné')
            
            def go_to_machine():
                dialog.dismiss()
                # Aller à l'écran des machines avec cette machine sélectionnée
                self.go_to_machine_detail(machine_data)
            
            def create_ticket():
                dialog.dismiss()
                # Aller à la création de ticket pour cette machine
                self.create_ticket_for_machine(machine_data)
            
            dialog = MDDialog(
                title=f"Machine trouvée: {machine_name}",
                text=f"Statut: {machine_status}\nUtilisateur: {machine_user}",
                buttons=[
                    MDFlatButton(
                        text="VOIR DÉTAILS",
                        on_release=lambda x: go_to_machine()
                    ),
                    MDFlatButton(
                        text="CRÉER TICKET",
                        on_release=lambda x: create_ticket()
                    ),
                    MDFlatButton(
                        text="FERMER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur affichage détails machine: {e}")
    
    def scan_from_gallery(self, button=None):
        """Scanner un QR code depuis la galerie"""
        try:
            # Placeholder pour l'implémentation de la galerie
            self.show_info("Fonctionnalité galerie à implémenter")
            
            # TODO: Implémenter la sélection d'image depuis la galerie
            # et le scan du QR code dans l'image
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur scan galerie: {e}")
            self.show_error(f"Erreur: {str(e)}")
    
    def manual_qr_input(self, button=None):
        """Saisie manuelle d'un code QR"""
        try:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.textfield import MDTextField
            from kivymd.uix.button import MDFlatButton, MDRaisedButton
            
            # Champ de saisie
            qr_field = MDTextField(
                hint_text="Saisissez le code QR (ID machine, numéro série, etc.)",
                multiline=False,
                size_hint_y=None,
                height=dp(60)
            )
            
            def process_manual_qr(instance):
                qr_data = qr_field.text.strip()
                if qr_data:
                    dialog.dismiss()
                    # Traiter le code QR saisi manuellement
                    self.on_qr_detected(qr_data)
                else:
                    self.show_error("Veuillez saisir un code QR")
            
            dialog = MDDialog(
                title="Saisie manuelle du code QR",
                type="custom",
                content_cls=qr_field,
                buttons=[
                    MDFlatButton(
                        text="ANNULER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="VALIDER",
                        on_release=process_manual_qr
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur saisie manuelle: {e}")
            self.show_error(f"Erreur: {str(e)}")
    
    def force_iriun_camera(self, button=None):
        """Forcer l'utilisation de la caméra Iriun"""
        try:
            # Arrêter le scan en cours
            if self.is_scanning:
                self.stop_scanning()
            
            # Essayer l'index 1 (Iriun par défaut)
            self.current_camera_index = 1
            
            # Ajouter l'index 1 aux caméras disponibles s'il n'y est pas
            if 1 not in self.available_cameras:
                self.available_cameras.append(1)
            
            # Réinitialiser le scanner QR avec l'index Iriun
            try:
                from ..utils.qr_scanner import QRScanner
            except ImportError:
                from utils.qr_scanner import QRScanner
            self.qr_scanner = QRScanner(camera_index=self.current_camera_index)
            
            # Reconfigurer la caméra
            self.setup_camera()
            
            self.show_info("Caméra Iriun forcée (index 1)")
            Logger.info("QRScannerScreen: Caméra Iriun forcée sur index 1")
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur force Iriun: {e}")
            self.show_error(f"Erreur Iriun: {str(e)}")
    
    def toggle_flashlight(self):
        """Activer/désactiver la lampe torche"""
        try:
            # Placeholder pour l'implémentation de la lampe torche
            self.show_info("Lampe torche à implémenter")
            
            # TODO: Implémenter le contrôle de la lampe torche
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur lampe torche: {e}")
    
    def go_to_machine_detail(self, machine_data):
        """Aller aux détails de la machine"""
        try:
            # Changer vers l'écran des machines
            self.manager.current = 'machines'
            
            # Passer les données de la machine à l'écran
            machines_screen = self.manager.get_screen('machines')
            if hasattr(machines_screen, 'show_machine_detail'):
                machines_screen.show_machine_detail(machine_data)
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur navigation machine: {e}")
    
    def create_ticket_for_machine(self, machine_data):
        """Créer un ticket pour la machine"""
        try:
            # Changer vers l'écran des tickets
            self.manager.current = 'tickets'
            
            # Passer les données de la machine à l'écran
            tickets_screen = self.manager.get_screen('tickets')
            if hasattr(tickets_screen, 'create_ticket_for_machine'):
                tickets_screen.create_ticket_for_machine(machine_data)
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur création ticket: {e}")
    
    def offer_create_ticket(self, qr_data):
        """Proposer de créer un ticket pour un équipement non trouvé"""
        try:
            dialog = MDDialog(
                title="Équipement non trouvé",
                text=f"Aucune machine trouvée pour le code: {qr_data}\n\nVoulez-vous créer un ticket d'incident?",
                buttons=[
                    MDFlatButton(
                        text="CRÉER TICKET",
                        on_release=lambda x: self.create_generic_ticket(qr_data, dialog)
                    ),
                    MDFlatButton(
                        text="ANNULER",
                        on_release=lambda x: dialog.dismiss()
                    ),
                ],
            )
            dialog.open()
            
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur proposition ticket: {e}")
    
    def create_generic_ticket(self, qr_data, dialog):
        """Créer un ticket générique"""
        try:
            dialog.dismiss()
            
            # Aller à l'écran des tickets avec des données pré-remplies
            self.manager.current = 'tickets'
            
            tickets_screen = self.manager.get_screen('tickets')
            if hasattr(tickets_screen, 'create_ticket_with_qr'):
                tickets_screen.create_ticket_with_qr(qr_data)
                
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur création ticket générique: {e}")
    
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
            Logger.error(f"QRScannerScreen: Erreur affichage info: {e}")
    
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
            Logger.error(f"QRScannerScreen: Erreur affichage erreur: {e}")
    
    def go_back(self):
        """Retourner à l'écran précédent"""
        try:
            self.stop_scanning()
            self.manager.current = 'dashboard'
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur retour: {e}")
    
    def on_enter(self):
        """Appelé quand l'écran devient actif"""
        try:
            Logger.info("QRScannerScreen: Écran activé")
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur on_enter: {e}")
    
    def on_leave(self):
        """Appelé quand l'écran devient inactif"""
        try:
            # Arrêter le scan quand on quitte l'écran
            self.stop_scanning()
            Logger.info("QRScannerScreen: Écran désactivé")
        except Exception as e:
            Logger.error(f"QRScannerScreen: Erreur on_leave: {e}")