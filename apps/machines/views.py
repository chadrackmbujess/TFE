"""
Vues pour l'application machines
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
import platform
import psutil
import socket

from .models import (
    Machine, TypeMachine, InformationSysteme,
    InterfaceReseau, HistoriqueMachine
)
from .serializers import (
    MachineSerializer, MachineCreateUpdateSerializer, TypeMachineSerializer,
    InformationSystemeSerializer, InterfaceReseauSerializer,
    HistoriqueMachineSerializer
)


class MachineViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des machines"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retourner le serializer approprié selon l'action"""
        if self.action in ['create', 'update', 'partial_update']:
            return MachineCreateUpdateSerializer
        return MachineSerializer
    
    def get_queryset(self):
        """Filtrer les machines selon l'utilisateur"""
        user = self.request.user
        queryset = Machine.objects.select_related(
            'utilisateur', 'type_machine', 'structure', 'site'
        ).prefetch_related('interfaces_reseau', 'logiciels', 'info_systeme')
        
        # Filtrer selon le rôle de l'utilisateur
        if user.role == 'admin':
            # Les admins voient toutes les machines
            return queryset
        elif user.role in ['technicien', 'manager']:
            # Les techniciens voient les machines de leur structure
            return queryset.filter(structure=user.structure)
        else:
            # Les utilisateurs normaux voient seulement leurs machines
            return queryset.filter(utilisateur=user)
    
    def perform_create(self, serializer):
        """Créer une machine avec l'utilisateur connecté"""
        machine = serializer.save()
        
        # Créer un historique
        HistoriqueMachine.objects.create(
            machine=machine,
            type_modification='creation',
            description=f'Machine créée depuis l\'application desktop',
            utilisateur=self.request.user,
            donnees_apres=MachineSerializer(machine).data
        )
    
    @action(detail=False, methods=['get'])
    def mes_machines(self, request):
        """Récupérer les machines de l'utilisateur connecté"""
        machines = self.get_queryset().filter(utilisateur=request.user)
        serializer = self.get_serializer(machines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def synchroniser_machine_locale(self, request):
        """Synchroniser automatiquement la machine locale - Chaque utilisateur a sa propre machine"""
        try:
            # Collecter les informations de la machine locale
            machine_data = self.collecter_infos_machine_locale()
            
            print(f"🔍 Données collectées pour {request.user.username}: {machine_data}")  # Debug
            
            # Créer un nom unique pour la machine basé sur le nom de machine + utilisateur
            nom_machine_original = machine_data['nom']
            nom_machine_unique = f"{nom_machine_original}_{request.user.username}"
            machine_data['nom'] = nom_machine_unique
            
            # Vérifier si l'utilisateur a déjà une machine avec ce nom unique
            machine_existante = Machine.objects.filter(
                utilisateur=request.user,
                nom=nom_machine_unique
            ).first()
            
            if machine_existante:
                print(f"🔄 Mise à jour de la machine existante de {request.user.username}: {machine_existante.nom}")  # Debug
                
                # Mettre à jour la machine existante
                serializer = MachineCreateUpdateSerializer(
                    machine_existante, 
                    data=machine_data, 
                    context={'request': request}
                )
                if serializer.is_valid():
                    machine = serializer.save()
                    machine.derniere_synchronisation = timezone.now()
                    machine.save()
                    
                    # Créer un historique
                    HistoriqueMachine.objects.create(
                        machine=machine,
                        type_modification='synchronisation',
                        description=f'Synchronisation automatique depuis l\'application desktop - Machine: {nom_machine_original} (Utilisateur: {request.user.username})',
                        utilisateur=request.user
                    )
                    
                    print(f"✅ Machine mise à jour avec succès pour {request.user.username}: {machine.id}")  # Debug
                    
                    # Forcer la vérification des autorisations pour tous les logiciels de cette machine
                    self.verifier_autorisations_machine(machine)
                    
                    return Response({
                        'message': f'Machine {nom_machine_original} mise à jour avec succès pour {request.user.username}',
                        'machine': MachineSerializer(machine).data
                    })
                else:
                    print(f"❌ Erreurs de validation pour {request.user.username}: {serializer.errors}")  # Debug
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(f"🆕 Création d'une nouvelle machine pour {request.user.username}: {nom_machine_unique}")  # Debug
                
                # Créer une nouvelle machine pour cet utilisateur
                serializer = MachineCreateUpdateSerializer(
                    data=machine_data, 
                    context={'request': request}
                )
                if serializer.is_valid():
                    machine = serializer.save()
                    machine.derniere_synchronisation = timezone.now()
                    machine.save()
                    
                    # Créer un historique
                    HistoriqueMachine.objects.create(
                        machine=machine,
                        type_modification='creation',
                        description=f'Machine créée automatiquement depuis l\'application desktop - Machine: {nom_machine_original} (Utilisateur: {request.user.username})',
                        utilisateur=request.user
                    )
                    
                    print(f"✅ Machine créée avec succès pour {request.user.username}: {machine.id}")  # Debug
                    print(f"📊 Détails machine: ID={machine.id}, Nom={machine.nom}, Utilisateur={machine.utilisateur.username}, Structure={machine.structure.nom}")  # Debug détaillé
                    
                    # Vérifier que la machine est bien dans la base
                    machine_count = Machine.objects.filter(utilisateur=request.user).count()
                    print(f"📈 Nombre total de machines pour {request.user.username}: {machine_count}")  # Debug
                    
                    # Forcer la vérification des autorisations pour tous les logiciels de cette machine
                    self.verifier_autorisations_machine(machine)
                    
                    return Response({
                        'message': f'Machine {nom_machine_original} créée avec succès pour {request.user.username}',
                        'machine': MachineSerializer(machine).data
                    }, status=status.HTTP_201_CREATED)
                else:
                    print(f"❌ Erreurs de validation pour {request.user.username}: {serializer.errors}")  # Debug
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
        except Exception as e:
            print(f"❌ Erreur lors de la synchronisation pour {request.user.username}: {str(e)}")  # Debug
            import traceback
            traceback.print_exc()  # Debug complet
            return Response({
                'error': f'Erreur lors de la synchronisation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def collecter_infos_machine_locale(self):
        """Collecter les informations de la machine locale"""
        try:
            # Informations de base
            nom_machine = socket.gethostname()
            
            # Informations système
            os_info = platform.uname()
            
            # Informations CPU avec gestion d'erreurs
            try:
                cpu_coeurs = psutil.cpu_count(logical=False) or 1
                cpu_threads = psutil.cpu_count(logical=True) or 1
                # Fréquence CPU en GHz
                cpu_freq = psutil.cpu_freq()
                cpu_frequence_ghz = round(cpu_freq.current / 1000, 2) if cpu_freq and cpu_freq.current else 0.0
            except:
                cpu_coeurs = 1
                cpu_threads = 1
                cpu_frequence_ghz = 0.0
            
            cpu_info = {
                'nom': platform.processor() or 'Processeur inconnu',
                'architecture': platform.machine(),
                'coeurs': cpu_coeurs,
                'threads': cpu_threads,
                'frequence_ghz': cpu_frequence_ghz,
            }
            
            # Informations mémoire avec gestion d'erreurs - Conversion en GB
            try:
                memory = psutil.virtual_memory()
                # Convertir de bytes en GB (1 GB = 1024^3 bytes)
                ram_totale_gb = round(memory.total / (1024**3), 2)
                ram_disponible_gb = round(memory.available / (1024**3), 2)
                # Garder aussi les valeurs en bytes pour compatibilité
                ram_totale = memory.total
                ram_disponible = memory.available
            except:
                ram_totale_gb = 0.0
                ram_disponible_gb = 0.0
                ram_totale = 0
                ram_disponible = 0
            
            # Informations stockage - toutes les partitions + total
            partitions_info = []
            stockage_total_global = 0
            stockage_libre_global = 0
            
            try:
                # Récupérer toutes les partitions
                partitions = psutil.disk_partitions()
                
                for partition in partitions:
                    try:
                        # Obtenir les informations d'usage pour chaque partition
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        # Convertir en GB pour lisibilité
                        total_gb = round(usage.total / (1024**3), 2)
                        libre_gb = round(usage.free / (1024**3), 2)
                        utilise_gb = round((usage.total - usage.free) / (1024**3), 2)
                        pourcentage_utilise = round(((usage.total - usage.free) / usage.total) * 100, 1) if usage.total > 0 else 0
                        
                        partition_info = {
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype,
                            'total_bytes': usage.total,
                            'libre_bytes': usage.free,
                            'utilise_bytes': usage.total - usage.free,
                            'total_gb': total_gb,
                            'libre_gb': libre_gb,
                            'utilise_gb': utilise_gb,
                            'pourcentage_utilise': pourcentage_utilise
                        }
                        
                        partitions_info.append(partition_info)
                        
                        # Ajouter au total global
                        stockage_total_global += usage.total
                        stockage_libre_global += usage.free
                        
                    except (PermissionError, OSError):
                        # Ignorer les partitions inaccessibles
                        continue
                        
            except Exception as e:
                print(f"Erreur lors de la collecte des partitions: {e}")
                # Fallback sur la partition principale
                try:
                    if platform.system() == 'Windows':
                        disk = psutil.disk_usage('C:')
                    else:
                        disk = psutil.disk_usage('/')
                    stockage_total_global = disk.total
                    stockage_libre_global = disk.free
                except:
                    stockage_total_global = 0
                    stockage_libre_global = 0
            
            # Interfaces réseau avec gestion d'erreurs
            interfaces = []
            try:
                for interface_name, interface_addresses in psutil.net_if_addrs().items():
                    for address in interface_addresses:
                        if address.family == socket.AF_INET:  # IPv4
                            interfaces.append({
                                'nom': interface_name,
                                'type_interface': 'ethernet',
                                'adresse_ip': address.address,
                                'masque_reseau': getattr(address, 'netmask', ''),
                                'actif': True
                            })
            except:
                # Interface par défaut si erreur
                interfaces = [{
                    'nom': 'Interface par défaut',
                    'type_interface': 'ethernet',
                    'adresse_ip': '127.0.0.1',
                    'masque_reseau': '255.0.0.0',
                    'actif': True
                }]
            
            # Logiciels installés - Collecte automatique
            logiciels = self.collecter_logiciels_installes()
            print(f"🔍 Logiciels collectés pour transmission: {len(logiciels)}")
            if logiciels:
                print(f"🔍 Premier logiciel à transmettre: {logiciels[0]}")
            
            return {
                'nom': nom_machine,
                'numero_serie': '',  # Nécessiterait des commandes système spécifiques
                'marque': '',
                'modele': '',
                'info_systeme': {
                    'os_nom': os_info.system,
                    'os_version': os_info.release,
                    'os_architecture': os_info.machine,
                    'os_build': os_info.version,
                    'cpu_nom': cpu_info['nom'],
                    'cpu_architecture': cpu_info['architecture'],
                    'cpu_coeurs': cpu_info['coeurs'],
                    'cpu_threads': cpu_info['threads'],
                    'cpu_frequence': cpu_info['frequence_ghz'],  # Fréquence en GHz
                    'ram_totale': int(ram_totale),  # RAM en bytes (entier requis par le modèle)
                    'ram_disponible': int(ram_disponible),  # RAM en bytes (entier requis par le modèle)
                    'ram_totale_gb': ram_totale_gb,  # RAM en GB (pour affichage)
                    'ram_disponible_gb': ram_disponible_gb,  # RAM en GB (pour affichage)
                    'stockage_total': int(stockage_total_global),  # Stockage en bytes (entier requis par le modèle)
                    'stockage_libre': int(stockage_libre_global),  # Stockage en bytes (entier requis par le modèle)
                    'stockage_total_gb': round(stockage_total_global / (1024**3), 2),  # Stockage en GB (pour affichage)
                    'stockage_libre_gb': round(stockage_libre_global / (1024**3), 2),  # Stockage en GB (pour affichage)
                    'nom_machine': nom_machine,
                    'partitions': partitions_info,  # Détails de toutes les partitions
                },
                'interfaces_reseau': interfaces,
                'logiciels': logiciels
            }
        except Exception as e:
            # Retourner des données minimales en cas d'erreur
            return {
                'nom': socket.gethostname(),
                'numero_serie': '',
                'marque': '',
                'modele': '',
                'info_systeme': {
                    'os_nom': platform.system(),
                    'os_version': platform.release(),
                    'os_architecture': platform.machine(),
                    'os_build': platform.version(),
                    'cpu_nom': 'Processeur inconnu',
                    'cpu_architecture': platform.machine(),
                    'cpu_coeurs': 1,
                    'cpu_threads': 1,
                    'cpu_frequence': 0.0,  # Fréquence en GHz par défaut
                    'ram_totale': 0,  # RAM en bytes (entier requis par le modèle)
                    'ram_disponible': 0,  # RAM en bytes (entier requis par le modèle)
                    'ram_totale_gb': 0.0,  # RAM en GB (pour affichage)
                    'ram_disponible_gb': 0.0,  # RAM en GB (pour affichage)
                    'stockage_total': 0,  # Stockage en bytes (entier requis par le modèle)
                    'stockage_libre': 0,  # Stockage en bytes (entier requis par le modèle)
                    'stockage_total_gb': 0.0,  # Stockage en GB (pour affichage)
                    'stockage_libre_gb': 0.0,  # Stockage en GB (pour affichage)
                    'nom_machine': socket.gethostname(),
                    'partitions': [],  # Partitions vides par défaut
                },
                'interfaces_reseau': [],
                'logiciels': []
            }
    
    def collecter_logiciels_installes(self):
        """Collecter la liste des logiciels installés selon l'OS"""
        logiciels = []
        
        try:
            import platform
            os_name = platform.system()
            
            if os_name == 'Windows':
                logiciels = self.collecter_logiciels_windows()
            elif os_name == 'Linux':
                logiciels = self.collecter_logiciels_linux()
            elif os_name == 'Darwin':  # macOS
                logiciels = self.collecter_logiciels_macos()
            else:
                print(f"⚠️ OS non supporté pour la collecte de logiciels: {os_name}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des logiciels: {str(e)}")
            
        return logiciels
    
    def collecter_logiciels_windows(self):
        """Collecter les logiciels installés sur Windows via le registre"""
        logiciels = []
        
        try:
            import winreg
            import os
            from datetime import datetime
            
            # Clés de registre pour les programmes installés
            registry_keys = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            ]
            
            for hkey, subkey_path in registry_keys:
                try:
                    with winreg.OpenKey(hkey, subkey_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        # Récupérer les informations du logiciel
                                        nom = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        
                                        # Ignorer les mises à jour et composants système
                                        if any(skip in nom.lower() for skip in ['update', 'hotfix', 'security update', 'kb']):
                                            continue
                                        
                                        logiciel = {
                                            'nom': nom,
                                            'version': '',
                                            'editeur': '',
                                            'date_installation': None,
                                            'taille': None
                                        }
                                        
                                        # Version
                                        try:
                                            logiciel['version'] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                        except FileNotFoundError:
                                            pass
                                        
                                        # Éditeur
                                        try:
                                            logiciel['editeur'] = winreg.QueryValueEx(subkey, "Publisher")[0]
                                        except FileNotFoundError:
                                            pass
                                        
                                        # Date d'installation
                                        try:
                                            install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                                            if install_date and len(install_date) == 8:
                                                # Format YYYYMMDD
                                                year = int(install_date[:4])
                                                month = int(install_date[4:6])
                                                day = int(install_date[6:8])
                                                logiciel['date_installation'] = datetime(year, month, day).isoformat()
                                        except (FileNotFoundError, ValueError):
                                            pass
                                        
                                        # Taille
                                        try:
                                            size_kb = int(winreg.QueryValueEx(subkey, "EstimatedSize")[0])
                                            logiciel['taille'] = size_kb * 1024  # Convertir en bytes
                                        except (FileNotFoundError, ValueError):
                                            pass
                                        
                                        logiciels.append(logiciel)
                                        
                                    except FileNotFoundError:
                                        # Pas de DisplayName, ignorer cette entrée
                                        continue
                                        
                            except Exception as e:
                                continue
                                
                except Exception as e:
                    print(f"⚠️ Erreur d'accès au registre {subkey_path}: {str(e)}")
                    continue
                    
        except ImportError:
            print("⚠️ Module winreg non disponible (pas sur Windows)")
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des logiciels Windows: {str(e)}")
            
        print(f"✅ {len(logiciels)} logiciels collectés sur Windows")
        return logiciels
    
    def collecter_logiciels_linux(self):
        """Collecter les logiciels installés sur Linux"""
        logiciels = []
        
        try:
            import subprocess
            
            # Essayer différents gestionnaires de paquets
            gestionnaires = [
                ('dpkg', ['dpkg', '-l']),  # Debian/Ubuntu
                ('rpm', ['rpm', '-qa']),   # RedHat/CentOS/Fedora
                ('pacman', ['pacman', '-Q']),  # Arch Linux
                ('apk', ['apk', 'list', '--installed'])  # Alpine Linux
            ]
            
            for nom_gestionnaire, commande in gestionnaires:
                try:
                    result = subprocess.run(commande, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        if nom_gestionnaire == 'dpkg':
                            logiciels = self.parser_dpkg_output(result.stdout)
                        elif nom_gestionnaire == 'rpm':
                            logiciels = self.parser_rpm_output(result.stdout)
                        elif nom_gestionnaire == 'pacman':
                            logiciels = self.parser_pacman_output(result.stdout)
                        elif nom_gestionnaire == 'apk':
                            logiciels = self.parser_apk_output(result.stdout)
                        
                        print(f"✅ {len(logiciels)} logiciels collectés via {nom_gestionnaire}")
                        break
                        
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
                    
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des logiciels Linux: {str(e)}")
            
        return logiciels
    
    def collecter_logiciels_macos(self):
        """Collecter les logiciels installés sur macOS"""
        logiciels = []
        
        try:
            import subprocess
            import plistlib
            import os
            
            # Applications dans /Applications
            apps_dir = '/Applications'
            if os.path.exists(apps_dir):
                for app_name in os.listdir(apps_dir):
                    if app_name.endswith('.app'):
                        app_path = os.path.join(apps_dir, app_name)
                        info_plist = os.path.join(app_path, 'Contents', 'Info.plist')
                        
                        if os.path.exists(info_plist):
                            try:
                                with open(info_plist, 'rb') as f:
                                    plist_data = plistlib.load(f)
                                
                                logiciel = {
                                    'nom': plist_data.get('CFBundleDisplayName', app_name.replace('.app', '')),
                                    'version': plist_data.get('CFBundleShortVersionString', ''),
                                    'editeur': plist_data.get('CFBundleIdentifier', '').split('.')[1] if '.' in plist_data.get('CFBundleIdentifier', '') else '',
                                    'date_installation': None,
                                    'taille': None
                                }
                                
                                # Taille de l'application
                                try:
                                    result = subprocess.run(['du', '-s', app_path], capture_output=True, text=True)
                                    if result.returncode == 0:
                                        size_kb = int(result.stdout.split()[0])
                                        logiciel['taille'] = size_kb * 1024
                                except:
                                    pass
                                
                                logiciels.append(logiciel)
                                
                            except Exception as e:
                                continue
            
            print(f"✅ {len(logiciels)} logiciels collectés sur macOS")
            
        except Exception as e:
            print(f"❌ Erreur lors de la collecte des logiciels macOS: {str(e)}")
            
        return logiciels
    
    def parser_dpkg_output(self, output):
        """Parser la sortie de dpkg -l"""
        logiciels = []
        lines = output.strip().split('\n')[5:]  # Ignorer les en-têtes
        
        for line in lines:
            if line.startswith('ii'):  # Paquet installé
                parts = line.split()
                if len(parts) >= 4:
                    logiciels.append({
                        'nom': parts[1],
                        'version': parts[2],
                        'editeur': '',
                        'date_installation': None,
                        'taille': None
                    })
        
        return logiciels
    
    def parser_rpm_output(self, output):
        """Parser la sortie de rpm -qa"""
        logiciels = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if line.strip():
                # Format: nom-version-release.arch
                parts = line.rsplit('-', 2)
                if len(parts) >= 2:
                    logiciels.append({
                        'nom': parts[0],
                        'version': parts[1] if len(parts) > 1 else '',
                        'editeur': '',
                        'date_installation': None,
                        'taille': None
                    })
        
        return logiciels
    
    def parser_pacman_output(self, output):
        """Parser la sortie de pacman -Q"""
        logiciels = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if ' ' in line:
                nom, version = line.split(' ', 1)
                logiciels.append({
                    'nom': nom,
                    'version': version,
                    'editeur': '',
                    'date_installation': None,
                    'taille': None
                })
        
        return logiciels
    
    def parser_apk_output(self, output):
        """Parser la sortie de apk list --installed"""
        logiciels = []
        lines = output.strip().split('\n')
        
        for line in lines:
            if '{' in line:
                parts = line.split('{')
                if len(parts) >= 2:
                    nom_version = parts[0].strip()
                    if '-' in nom_version:
                        nom, version = nom_version.rsplit('-', 1)
                        logiciels.append({
                            'nom': nom,
                            'version': version,
                            'editeur': '',
                            'date_installation': None,
                            'taille': None
                        })
        
        return logiciels
    
    def verifier_autorisations_machine(self, machine):
        """Vérifier et mettre à jour les autorisations pour tous les logiciels d'une machine"""
        try:
            from .models import LogicielInstalle, LogicielReference
            
            print(f"🔍 Vérification des autorisations pour la machine {machine.nom}")
            
            # Récupérer tous les logiciels installés sur cette machine
            logiciels_installes = LogicielInstalle.objects.filter(machine=machine)
            
            logiciels_traites = 0
            logiciels_lies = 0
            logiciels_bloques = 0
            
            for logiciel in logiciels_installes:
                logiciels_traites += 1
                
                # 1. Essayer de lier le logiciel à une référence si pas déjà fait
                if not logiciel.logiciel_reference:
                    try:
                        # Chercher par nom exact
                        logiciel_ref = LogicielReference.objects.filter(nom__iexact=logiciel.nom).first()
                        if logiciel_ref:
                            logiciel.logiciel_reference = logiciel_ref
                            logiciel.save()
                            logiciels_lies += 1
                            print(f"🔗 Logiciel {logiciel.nom} lié à la référence {logiciel_ref.nom}")
                        else:
                            # Créer automatiquement une référence pour ce logiciel
                            logiciel_ref = LogicielReference.objects.create(
                                nom=logiciel.nom,
                                editeur=logiciel.editeur or '',
                                niveau_securite='libre',  # Par défaut, autoriser sans restriction
                                description=f'Logiciel détecté automatiquement depuis {machine.nom}',
                                actif=True
                            )
                            logiciel.logiciel_reference = logiciel_ref
                            logiciel.save()
                            logiciels_lies += 1
                            print(f"🆕 Référence créée et liée pour {logiciel.nom}")
                    except Exception as e:
                        print(f"❌ Erreur lors de la liaison du logiciel {logiciel.nom}: {e}")
                
                # 2. Vérifier l'autorisation du logiciel
                try:
                    ancien_statut = logiciel.autorise
                    logiciel.verifier_autorisation()
                    
                    if not logiciel.autorise and ancien_statut:
                        logiciels_bloques += 1
                        print(f"🚫 Logiciel {logiciel.nom} bloqué: {logiciel.motif_blocage}")
                    elif logiciel.autorise and not ancien_statut:
                        print(f"✅ Logiciel {logiciel.nom} autorisé")
                        
                except Exception as e:
                    print(f"❌ Erreur lors de la vérification de {logiciel.nom}: {e}")
            
            print(f"📊 Résumé vérification machine {machine.nom}:")
            print(f"   - Logiciels traités: {logiciels_traites}")
            print(f"   - Logiciels liés aux références: {logiciels_lies}")
            print(f"   - Logiciels bloqués: {logiciels_bloques}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification des autorisations de la machine {machine.nom}: {e}")
            import traceback
            traceback.print_exc()

    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        """Changer le statut d'une machine"""
        machine = self.get_object()
        nouveau_statut = request.data.get('statut')
        commentaire = request.data.get('commentaire', '')
        
        if nouveau_statut not in dict(Machine.STATUT_CHOICES):
            return Response(
                {'error': 'Statut invalide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ancien_statut = machine.statut
        machine.statut = nouveau_statut
        machine.save()
        
        # Créer un historique
        HistoriqueMachine.objects.create(
            machine=machine,
            type_modification='changement_statut',
            description=f'Statut changé de "{ancien_statut}" à "{nouveau_statut}". {commentaire}',
            utilisateur=request.user,
            donnees_avant={'statut': ancien_statut},
            donnees_apres={'statut': nouveau_statut}
        )
        
        serializer = self.get_serializer(machine)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def logiciels_bloques(self, request):
        """Récupérer la liste des logiciels bloqués pour l'utilisateur connecté"""
        try:
            from .models import LogicielInstalle, AutorisationLogiciel, LogicielReference
            
            # ÉTAPE 1: Forcer la vérification des autorisations pour tous les logiciels de l'utilisateur
            print(f"🔄 Vérification des autorisations pour {request.user.username}")
            
            logiciels_utilisateur = LogicielInstalle.objects.filter(
                machine__utilisateur=request.user
            ).select_related('machine', 'logiciel_reference')
            
            logiciels_reverifies = 0
            for logiciel in logiciels_utilisateur:
                ancien_statut = logiciel.bloque
                logiciel.verifier_autorisation()
                if ancien_statut != logiciel.bloque:
                    logiciels_reverifies += 1
                    print(f"🔄 Statut mis à jour pour {logiciel.nom}: bloqué={logiciel.bloque}")
            
            print(f"✅ {logiciels_reverifies} logiciels ont eu leur statut mis à jour")
            
            # ÉTAPE 2: Récupérer uniquement les logiciels effectivement bloqués
            logiciels_data = []
            
            # Récupérer les logiciels directement bloqués (bloque=True) après vérification
            logiciels_bloques_directs = LogicielInstalle.objects.filter(
                machine__utilisateur=request.user,
                bloque=True
            ).select_related('machine', 'logiciel_reference')
            
            for logiciel in logiciels_bloques_directs:
                logiciels_data.append({
                    'nom': logiciel.nom,
                    'version': logiciel.version or '',
                    'editeur': logiciel.editeur or '',
                    'motif_blocage': logiciel.motif_blocage or 'Logiciel bloqué',
                    'machine': logiciel.machine.nom,
                    'autorise': logiciel.autorise,
                    'niveau_securite': logiciel.logiciel_reference.niveau_securite if logiciel.logiciel_reference else 'libre'
                })
            
            # Supprimer les doublons basés sur nom + version + machine
            logiciels_uniques = {}
            for logiciel in logiciels_data:
                cle = f"{logiciel['nom']}_{logiciel['version']}_{logiciel['machine']}"
                if cle not in logiciels_uniques:
                    logiciels_uniques[cle] = logiciel
            
            logiciels_data_finaux = list(logiciels_uniques.values())
            
            # ÉTAPE 3: Statistiques détaillées pour le debug
            total_logiciels = LogicielInstalle.objects.filter(machine__utilisateur=request.user).count()
            logiciels_autorises = LogicielInstalle.objects.filter(machine__utilisateur=request.user, autorise=True).count()
            logiciels_bloques_count = LogicielInstalle.objects.filter(machine__utilisateur=request.user, bloque=True).count()
            
            autorisations_refusees_count = AutorisationLogiciel.objects.filter(
                statut='refuse'
            ).filter(
                Q(utilisateur=request.user) |
                Q(groupe=request.user.groupe) |
                Q(structure=request.user.structure) |
                Q(site=request.user.site)
            ).count()
            
            logiciels_interdits_count = LogicielReference.objects.filter(niveau_securite='interdit').count()
            
            print(f"📊 Statistiques pour {request.user.username}:")
            print(f"   - Total logiciels: {total_logiciels}")
            print(f"   - Logiciels autorisés: {logiciels_autorises}")
            print(f"   - Logiciels bloqués: {logiciels_bloques_count}")
            print(f"   - Autorisations refusées: {autorisations_refusees_count}")
            print(f"   - Logiciels interdits (politique): {logiciels_interdits_count}")
            print(f"   - Logiciels bloqués retournés: {len(logiciels_data_finaux)}")
            
            return Response(logiciels_data_finaux)
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des logiciels bloqués: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'Erreur lors de la récupération des logiciels bloqués: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def forcer_verification_autorisations(self, request):
        """Forcer la vérification des autorisations pour tous les logiciels de l'utilisateur"""
        try:
            from .models import LogicielInstalle
            
            print(f"🔄 Forçage de la vérification des autorisations pour {request.user.username}")
            
            logiciels_utilisateur = LogicielInstalle.objects.filter(
                machine__utilisateur=request.user
            ).select_related('machine', 'logiciel_reference')
            
            resultats = {
                'total_logiciels': 0,
                'logiciels_autorises': 0,
                'logiciels_bloques': 0,
                'changements': 0,
                'details': []
            }
            
            for logiciel in logiciels_utilisateur:
                resultats['total_logiciels'] += 1
                
                ancien_autorise = logiciel.autorise
                ancien_bloque = logiciel.bloque
                ancien_motif = logiciel.motif_blocage
                
                # Forcer la vérification
                logiciel.verifier_autorisation()
                
                # Compter les résultats
                if logiciel.autorise:
                    resultats['logiciels_autorises'] += 1
                if logiciel.bloque:
                    resultats['logiciels_bloques'] += 1
                
                # Détecter les changements
                if (ancien_autorise != logiciel.autorise or 
                    ancien_bloque != logiciel.bloque or 
                    ancien_motif != logiciel.motif_blocage):
                    resultats['changements'] += 1
                    resultats['details'].append({
                        'nom': logiciel.nom,
                        'version': logiciel.version,
                        'machine': logiciel.machine.nom,
                        'ancien_statut': {
                            'autorise': ancien_autorise,
                            'bloque': ancien_bloque,
                            'motif': ancien_motif
                        },
                        'nouveau_statut': {
                            'autorise': logiciel.autorise,
                            'bloque': logiciel.bloque,
                            'motif': logiciel.motif_blocage
                        }
                    })
            
            print(f"✅ Vérification terminée pour {request.user.username}:")
            print(f"   - Total: {resultats['total_logiciels']}")
            print(f"   - Autorisés: {resultats['logiciels_autorises']}")
            print(f"   - Bloqués: {resultats['logiciels_bloques']}")
            print(f"   - Changements: {resultats['changements']}")
            
            return Response(resultats)
            
        except Exception as e:
            print(f"❌ Erreur lors de la vérification forcée: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'Erreur lors de la vérification forcée: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TypeMachineViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les types de machines (lecture seule)"""
    queryset = TypeMachine.objects.all()
    serializer_class = TypeMachineSerializer
    permission_classes = [permissions.IsAuthenticated]


class HistoriqueMachineViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour l'historique des machines (lecture seule)"""
    serializer_class = HistoriqueMachineSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer l'historique selon les permissions"""
        user = self.request.user
        queryset = HistoriqueMachine.objects.select_related('machine', 'utilisateur')
        
        # Filtrer selon le rôle de l'utilisateur
        if user.role == 'admin':
            return queryset
        elif user.role in ['technicien', 'manager']:
            return queryset.filter(machine__structure=user.structure)
        else:
            return queryset.filter(machine__utilisateur=user)