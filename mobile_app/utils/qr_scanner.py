"""
Scanner QR Code pour l'application mobile ITSM Compagnon
Utilise la caméra pour scanner les codes QR des équipements
"""

import threading
import time
from typing import Optional, Callable, Dict, Any
from kivy.logger import Logger

try:
    from kivy.uix.camera import Camera
    from kivy.graphics.texture import Texture
    KIVY_CAMERA_AVAILABLE = True
except ImportError:
    Logger.warning("QRScanner: Caméra Kivy non disponible")
    KIVY_CAMERA_AVAILABLE = False

try:
    import cv2
    import numpy as np
    from pyzbar import pyzbar
    CV2_AVAILABLE = True
except ImportError:
    Logger.warning("QRScanner: OpenCV/pyzbar non disponibles")
    CV2_AVAILABLE = False

try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False


class QRScanner:
    """Scanner de codes QR pour identifier les équipements"""
    
    def __init__(self, camera_index=0):
        self.is_scanning = False
        self.camera = None
        self.scan_callback = None
        self.scan_thread = None
        self.last_scan_time = 0
        self.scan_cooldown = 2  # Cooldown de 2 secondes entre les scans
        self.camera_index = camera_index  # Index de la caméra à utiliser
        
        Logger.info(f"QRScanner: Initialisé avec caméra {camera_index}")
        
        # Demander les permissions caméra sur Android
        if ANDROID_AVAILABLE:
            self._request_camera_permission()
    
    def _request_camera_permission(self):
        """Demander la permission caméra sur Android"""
        try:
            request_permissions([Permission.CAMERA])
            Logger.info("QRScanner: Permission caméra demandée")
        except Exception as e:
            Logger.error(f"QRScanner: Erreur permission caméra: {e}")
    
    def start_scanning(self, callback: Callable[[str], None]) -> bool:
        """Démarrer le scan de codes QR"""
        if self.is_scanning:
            Logger.warning("QRScanner: Scan déjà en cours")
            return False
        
        if not CV2_AVAILABLE:
            Logger.warning("QRScanner: OpenCV non disponible - mode simulation activé")
            # Mode simulation pour les tests
            self.scan_callback = callback
            self.is_scanning = True
            Logger.info("QRScanner: Mode simulation démarré")
            return True
        
        try:
            self.scan_callback = callback
            self.is_scanning = True
            
            # Démarrer le thread de scan
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()
            
            Logger.info("QRScanner: Scan démarré")
            return True
            
        except Exception as e:
            Logger.error(f"QRScanner: Erreur démarrage scan: {e}")
            self.is_scanning = False
            return False
    
    def stop_scanning(self):
        """Arrêter le scan de codes QR"""
        try:
            self.is_scanning = False
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            if self.scan_thread and self.scan_thread.is_alive():
                self.scan_thread.join(timeout=2)
            
            Logger.info("QRScanner: Scan arrêté")
            
        except Exception as e:
            Logger.error(f"QRScanner: Erreur arrêt scan: {e}")
    
    def _scan_loop(self):
        """Boucle principale de scan"""
        try:
            # Initialiser la caméra avec l'index spécifié
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                Logger.error(f"QRScanner: Impossible d'ouvrir la caméra {self.camera_index}")
                self.is_scanning = False
                return
            
            Logger.info(f"QRScanner: Caméra {self.camera_index} initialisée")
            
            while self.is_scanning:
                try:
                    # Capturer une frame
                    ret, frame = self.camera.read()
                    
                    if not ret:
                        Logger.warning("QRScanner: Impossible de lire la frame")
                        time.sleep(0.1)
                        continue
                    
                    # Décoder les codes QR dans la frame
                    qr_codes = pyzbar.decode(frame)
                    
                    for qr_code in qr_codes:
                        # Vérifier le cooldown
                        current_time = time.time()
                        if current_time - self.last_scan_time < self.scan_cooldown:
                            continue
                        
                        # Extraire les données du QR code
                        qr_data = qr_code.data.decode('utf-8')
                        
                        Logger.info(f"QRScanner: Code QR détecté: {qr_data}")
                        
                        # Appeler le callback
                        if self.scan_callback:
                            try:
                                self.scan_callback(qr_data)
                                self.last_scan_time = current_time
                            except Exception as e:
                                Logger.error(f"QRScanner: Erreur callback: {e}")
                    
                    # Petite pause pour éviter de surcharger le CPU
                    time.sleep(0.1)
                    
                except Exception as e:
                    Logger.error(f"QRScanner: Erreur dans la boucle de scan: {e}")
                    time.sleep(0.5)
            
        except Exception as e:
            Logger.error(f"QRScanner: Erreur fatale dans le scan: {e}")
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None
            self.is_scanning = False
    
    def scan_image(self, image_path: str) -> Optional[str]:
        """Scanner un code QR depuis une image"""
        if not CV2_AVAILABLE:
            Logger.error("QRScanner: OpenCV non disponible")
            return None
        
        try:
            # Charger l'image
            image = cv2.imread(image_path)
            
            if image is None:
                Logger.error(f"QRScanner: Impossible de charger l'image: {image_path}")
                return None
            
            # Décoder les codes QR
            qr_codes = pyzbar.decode(image)
            
            if qr_codes:
                qr_data = qr_codes[0].data.decode('utf-8')
                Logger.info(f"QRScanner: Code QR trouvé dans l'image: {qr_data}")
                return qr_data
            else:
                Logger.info("QRScanner: Aucun code QR trouvé dans l'image")
                return None
                
        except Exception as e:
            Logger.error(f"QRScanner: Erreur scan image: {e}")
            return None
    
    def generate_qr_code(self, data: str, output_path: str) -> bool:
        """Générer un code QR (utilitaire)"""
        try:
            import qrcode
            from PIL import Image
            
            # Créer le code QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            
            Logger.info(f"QRScanner: Code QR généré: {output_path}")
            return True
            
        except ImportError:
            Logger.error("QRScanner: qrcode/PIL non disponibles pour la génération")
            return False
        except Exception as e:
            Logger.error(f"QRScanner: Erreur génération QR: {e}")
            return False
    
    def validate_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """Valider et analyser les données d'un code QR"""
        try:
            result = {
                'valid': False,
                'type': 'unknown',
                'data': qr_data,
                'parsed': {}
            }
            
            # Vérifier si c'est un UUID (ID de machine)
            import re
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if re.match(uuid_pattern, qr_data, re.IGNORECASE):
                result['valid'] = True
                result['type'] = 'machine_id'
                result['parsed']['machine_id'] = qr_data
                return result
            
            # Vérifier si c'est un numéro de série
            if len(qr_data) > 5 and qr_data.isalnum():
                result['valid'] = True
                result['type'] = 'serial_number'
                result['parsed']['serial_number'] = qr_data
                return result
            
            # Vérifier si c'est un numéro d'inventaire (format INV-XXXXXXXX)
            if qr_data.startswith('INV-') and len(qr_data) > 4:
                result['valid'] = True
                result['type'] = 'inventory_number'
                result['parsed']['inventory_number'] = qr_data
                return result
            
            # Vérifier si c'est du JSON
            try:
                import json
                parsed_json = json.loads(qr_data)
                if isinstance(parsed_json, dict):
                    result['valid'] = True
                    result['type'] = 'json'
                    result['parsed'] = parsed_json
                    return result
            except json.JSONDecodeError:
                pass
            
            # Vérifier si c'est une URL
            if qr_data.startswith(('http://', 'https://')):
                result['valid'] = True
                result['type'] = 'url'
                result['parsed']['url'] = qr_data
                return result
            
            # Si rien ne correspond, considérer comme texte libre
            if len(qr_data.strip()) > 0:
                result['valid'] = True
                result['type'] = 'text'
                result['parsed']['text'] = qr_data
            
            return result
            
        except Exception as e:
            Logger.error(f"QRScanner: Erreur validation QR: {e}")
            return {
                'valid': False,
                'type': 'error',
                'data': qr_data,
                'error': str(e)
            }
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Récupérer les informations sur les caméras disponibles"""
        info = {
            'available': False,
            'cameras': [],
            'cv2_available': CV2_AVAILABLE,
            'kivy_camera_available': KIVY_CAMERA_AVAILABLE
        }
        
        if not CV2_AVAILABLE:
            return info
        
        try:
            # Tester les caméras disponibles
            for i in range(5):  # Tester les 5 premiers indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        height, width = frame.shape[:2]
                        info['cameras'].append({
                            'index': i,
                            'width': width,
                            'height': height
                        })
                        info['available'] = True
                cap.release()
            
            Logger.info(f"QRScanner: {len(info['cameras'])} caméra(s) détectée(s)")
            
        except Exception as e:
            Logger.error(f"QRScanner: Erreur détection caméras: {e}")
        
        return info
    
    def is_available(self) -> bool:
        """Vérifier si le scanner est disponible"""
        # Pour l'instant, retourner True même sans OpenCV pour permettre l'utilisation de base
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Récupérer le statut du scanner"""
        return {
            'scanning': self.is_scanning,
            'available': self.is_available(),
            'cv2_available': CV2_AVAILABLE,
            'camera_info': self.get_camera_info(),
            'last_scan_time': self.last_scan_time,
            'scan_cooldown': self.scan_cooldown
        }