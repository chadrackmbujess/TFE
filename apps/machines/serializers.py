"""
Serializers pour l'application machines
"""
from rest_framework import serializers
from .models import (
    Machine, TypeMachine, InformationSysteme, 
    InterfaceReseau, LogicielInstalle, HistoriqueMachine
)
from apps.users.serializers import UserSerializer


class TypeMachineSerializer(serializers.ModelSerializer):
    """Serializer pour les types de machines"""
    
    class Meta:
        model = TypeMachine
        fields = '__all__'


class InformationSystemeSerializer(serializers.ModelSerializer):
    """Serializer pour les informations système"""
    ram_totale_gb = serializers.ReadOnlyField()
    stockage_total_gb = serializers.ReadOnlyField()
    
    class Meta:
        model = InformationSysteme
        fields = [
            'os_nom', 'os_version', 'os_architecture', 'os_build',
            'cpu_nom', 'cpu_architecture', 'cpu_coeurs', 'cpu_threads', 'cpu_frequence',
            'ram_totale', 'ram_disponible', 'stockage_total', 'stockage_libre',
            'nom_machine', 'domaine', 'date_collecte', 'ram_totale_gb', 'stockage_total_gb'
        ]


class InterfaceReseauSerializer(serializers.ModelSerializer):
    """Serializer pour les interfaces réseau"""
    
    class Meta:
        model = InterfaceReseau
        fields = [
            'nom', 'type_interface', 'adresse_mac', 'adresse_ip', 'masque_reseau',
            'passerelle', 'dns_primaire', 'dns_secondaire', 'actif', 'date_derniere_maj'
        ]


class LogicielInstalleSerializer(serializers.ModelSerializer):
    """Serializer pour les logiciels installés"""
    
    class Meta:
        model = LogicielInstalle
        fields = [
            'nom', 'version', 'editeur', 'date_installation', 'taille',
            'licence_requise', 'licence_valide', 'autorise', 'bloque',
            'date_detection', 'date_derniere_maj'
        ]





class MachineSerializer(serializers.ModelSerializer):
    """Serializer pour les machines"""
    utilisateur_info = UserSerializer(source='utilisateur', read_only=True)
    type_machine_info = TypeMachineSerializer(source='type_machine', read_only=True)
    info_systeme = InformationSystemeSerializer(read_only=True)
    interfaces_reseau = InterfaceReseauSerializer(many=True, read_only=True)
    logiciels = LogicielInstalleSerializer(many=True, read_only=True)

    est_en_ligne = serializers.ReadOnlyField()
    
    class Meta:
        model = Machine
        fields = [
            'id', 'nom', 'numero_serie', 'numero_inventaire', 'type_machine',
            'type_machine_info', 'utilisateur', 'utilisateur_info', 'structure',
            'site', 'statut', 'date_achat', 'date_mise_service', 'date_fin_garantie',
            'marque', 'modele', 'date_creation', 'date_modification',
            'derniere_synchronisation', 'commentaires', 'est_en_ligne',
            'info_systeme', 'interfaces_reseau', 'logiciels'
        ]
        read_only_fields = [
            'id', 'date_creation', 'date_modification', 'derniere_synchronisation'
        ]


class MachineCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/mettre à jour les machines depuis l'app desktop"""
    info_systeme = InformationSystemeSerializer(required=False)
    interfaces_reseau = InterfaceReseauSerializer(many=True, required=False)
    logiciels = LogicielInstalleSerializer(many=True, required=False)

    
    class Meta:
        model = Machine
        fields = [
            'nom', 'numero_serie', 'type_machine', 'marque', 'modele',
            'info_systeme', 'interfaces_reseau', 'logiciels'
        ]
    
    def create(self, validated_data):
        """Créer une machine avec ses informations système"""
        print(f"🔍 Données reçues dans create: {list(validated_data.keys())}")
        info_systeme_data = validated_data.pop('info_systeme', None)
        interfaces_data = validated_data.pop('interfaces_reseau', [])
        logiciels_data = validated_data.pop('logiciels', [])
        print(f"🔍 Logiciels extraits: {len(logiciels_data)} logiciels")
        
        # Assigner automatiquement l'utilisateur connecté et sa structure
        user = self.context['request'].user
        validated_data['utilisateur'] = user
        
        # AJOUTER CETTE LOGIQUE DE GESTION DES CHAMPS UNIQUE
        # Gérer les champs UNIQUE - convertir les chaînes vides en None pour éviter les violations de contrainte
        if 'numero_serie' in validated_data and not validated_data['numero_serie']:
            validated_data['numero_serie'] = None
        if 'numero_inventaire' in validated_data and not validated_data['numero_inventaire']:
            validated_data['numero_inventaire'] = None
        
        # Générer un numéro d'inventaire unique si nécessaire
        if not validated_data.get('numero_inventaire'):
            import uuid
            validated_data['numero_inventaire'] = f"INV-{str(uuid.uuid4())[:8].upper()}"
        
        # Gérer le cas où l'utilisateur n'a pas de structure
        if hasattr(user, 'structure') and user.structure:
            validated_data['structure'] = user.structure
        else:
            # Créer ou récupérer une structure par défaut
            from apps.users.models import Structure
            structure_defaut, created = Structure.objects.get_or_create(
                nom='Structure par défaut',
                defaults={
                    'code': 'default',
                    'description': 'Structure créée automatiquement pour les utilisateurs sans structure'
                }
            )
            validated_data['structure'] = structure_defaut
            print(f"⚠️ Utilisateur {user.username} sans structure, assignation à la structure par défaut")
        
        try:
            # Créer la machine
            machine = Machine.objects.create(**validated_data)
            print(f"✅ Machine créée en base: {machine.id} - {machine.nom}")
            print(f"📋 Numéro d'inventaire: {machine.numero_inventaire}")
            
            # Préparer les données pour l'historique
            donnees_creation = {
                'machine_id': str(machine.id),
                'nom': machine.nom,
                'utilisateur': user.username,
                'structure': machine.structure.nom if machine.structure else None,
                'numero_inventaire': machine.numero_inventaire,
                'source': 'application_desktop'
            }
            
            # Créer les informations système
            interfaces_creees = []
            logiciels_crees = []
            
            if info_systeme_data:
                info_systeme = InformationSysteme.objects.create(machine=machine, **info_systeme_data)
                print(f"✅ Informations système créées: {info_systeme.id}")
                
                # Ajouter les infos système aux données de log
                donnees_creation['info_systeme'] = {
                    'os': f"{info_systeme_data.get('os_nom', '')} {info_systeme_data.get('os_version', '')}",
                    'cpu': info_systeme_data.get('cpu_nom', ''),
                    'ram_gb': round(info_systeme_data.get('ram_totale', 0) / (1024**3), 2) if info_systeme_data.get('ram_totale') else 0,
                    'stockage_gb': round(info_systeme_data.get('stockage_total', 0) / (1024**3), 2) if info_systeme_data.get('stockage_total') else 0
                }
            
            # Créer les interfaces réseau avec gestion des noms dupliqués
            interface_names_count = {}
            for interface_data in interfaces_data:
                nom_original = interface_data['nom']
                
                # Gérer les noms dupliqués en ajoutant un suffixe
                if nom_original in interface_names_count:
                    interface_names_count[nom_original] += 1
                    interface_data['nom'] = f"{nom_original} ({interface_names_count[nom_original]})"
                else:
                    interface_names_count[nom_original] = 0
                
                interface = InterfaceReseau.objects.create(machine=machine, **interface_data)
                print(f"✅ Interface réseau créée: {interface.nom}")
                
                interfaces_creees.append({
                    'nom': interface.nom,
                    'type': interface.type_interface,
                    'ip': interface.adresse_ip
                })
            
            # Créer les logiciels
            print(f"🔍 Nombre de logiciels à créer: {len(logiciels_data)}")
            if logiciels_data:
                print(f"🔍 Premier logiciel: {logiciels_data[0] if logiciels_data else 'Aucun'}")
            
            for i, logiciel_data in enumerate(logiciels_data):
                try:
                    print(f"🔍 Création logiciel {i+1}/{len(logiciels_data)}: {logiciel_data.get('nom', 'Nom manquant')}")
                    logiciel = LogicielInstalle.objects.create(machine=machine, **logiciel_data)
                    print(f"✅ Logiciel créé en base: ID={logiciel.id}, Nom={logiciel.nom}, Version={logiciel.version}")
                    
                    logiciels_crees.append({
                        'nom': logiciel.nom,
                        'version': logiciel.version,
                        'editeur': logiciel.editeur
                    })
                except Exception as e:
                    print(f"❌ Erreur création logiciel {logiciel_data.get('nom', 'Inconnu')}: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # Ajouter les interfaces et logiciels aux données de log
            donnees_creation['interfaces_reseau'] = interfaces_creees
            donnees_creation['logiciels'] = logiciels_crees
            donnees_creation['nb_interfaces'] = len(interfaces_creees)
            donnees_creation['nb_logiciels'] = len(logiciels_crees)
            
            # Créer l'historique détaillé
            from .models import HistoriqueMachine
            HistoriqueMachine.objects.create(
                machine=machine,
                type_modification='creation',
                description=f'Machine créée automatiquement depuis l\'application desktop - '
                           f'OS: {donnees_creation.get("info_systeme", {}).get("os", "N/A")}, '
                           f'RAM: {donnees_creation.get("info_systeme", {}).get("ram_gb", 0)}GB, '
                           f'{donnees_creation.get("nb_interfaces", 0)} interface(s), '
                           f'{donnees_creation.get("nb_logiciels", 0)} logiciel(s)',
                utilisateur=user,
                donnees_apres=donnees_creation
            )
            
            print(f"📝 Historique créé avec {len(interfaces_creees)} interfaces et {len(logiciels_crees)} logiciels")
            
            return machine
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la machine: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def update(self, instance, validated_data):
        """Mettre à jour une machine et ses informations"""
        print(f"🔍 Données reçues dans update: {list(validated_data.keys())}")
        info_systeme_data = validated_data.pop('info_systeme', None)
        interfaces_data = validated_data.pop('interfaces_reseau', [])
        logiciels_data = validated_data.pop('logiciels', [])
        print(f"🔍 Logiciels extraits pour mise à jour: {len(logiciels_data)} logiciels")
        
        # Gérer les champs UNIQUE - convertir les chaînes vides en None pour éviter les violations de contrainte
        if 'numero_serie' in validated_data and not validated_data['numero_serie']:
            validated_data['numero_serie'] = None
        if 'numero_inventaire' in validated_data and not validated_data['numero_inventaire']:
            validated_data['numero_inventaire'] = None
        
        user = self.context['request'].user
        
        # Sauvegarder l'état avant modification pour l'historique
        donnees_avant = {
            'machine_id': str(instance.id),
            'nom': instance.nom,
            'derniere_synchronisation': instance.derniere_synchronisation.isoformat() if instance.derniere_synchronisation else None,
            'nb_interfaces_avant': instance.interfaces_reseau.count(),
            'nb_logiciels_avant': instance.logiciels.count()
        }
        
        # Ajouter les infos système avant modification
        if hasattr(instance, 'info_systeme') and instance.info_systeme:
            donnees_avant['info_systeme_avant'] = {
                'os': f"{instance.info_systeme.os_nom} {instance.info_systeme.os_version}",
                'ram_gb': instance.info_systeme.ram_totale_gb,
                'stockage_gb': instance.info_systeme.stockage_total_gb
            }
        
        # Mettre à jour la machine
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Préparer les données après modification
        donnees_apres = {
            'machine_id': str(instance.id),
            'nom': instance.nom,
            'utilisateur': user.username,
            'structure': instance.structure.nom if instance.structure else None,
            'source': 'application_desktop_update'
        }
        
        # Mettre à jour les informations système
        interfaces_creees = []
        logiciels_crees = []
        
        if info_systeme_data:
            info_systeme, created = InformationSysteme.objects.get_or_create(
                machine=instance,
                defaults=info_systeme_data
            )
            if not created:
                for attr, value in info_systeme_data.items():
                    setattr(info_systeme, attr, value)
                info_systeme.save()
            
            # Ajouter les nouvelles infos système aux données de log
            donnees_apres['info_systeme'] = {
                'os': f"{info_systeme_data.get('os_nom', '')} {info_systeme_data.get('os_version', '')}",
                'cpu': info_systeme_data.get('cpu_nom', ''),
                'ram_gb': round(info_systeme_data.get('ram_totale', 0) / (1024**3), 2) if info_systeme_data.get('ram_totale') else 0,
                'stockage_gb': round(info_systeme_data.get('stockage_total', 0) / (1024**3), 2) if info_systeme_data.get('stockage_total') else 0
            }
            
            print(f"✅ Informations système mises à jour pour {instance.nom}")
        
        # Mettre à jour les interfaces réseau (remplacer toutes)
        instance.interfaces_reseau.all().delete()
        interface_names_count = {}
        for interface_data in interfaces_data:
            nom_original = interface_data['nom']
            
            # Gérer les noms dupliqués en ajoutant un suffixe
            if nom_original in interface_names_count:
                interface_names_count[nom_original] += 1
                interface_data['nom'] = f"{nom_original} ({interface_names_count[nom_original]})"
            else:
                interface_names_count[nom_original] = 0
            
            interface = InterfaceReseau.objects.create(machine=instance, **interface_data)
            interfaces_creees.append({
                'nom': interface.nom,
                'type': interface.type_interface,
                'ip': interface.adresse_ip
            })
        
        # Mettre à jour les logiciels (remplacer tous)
        nb_logiciels_avant = instance.logiciels.count()
        print(f"🔍 Suppression de {nb_logiciels_avant} logiciels existants pour {instance.nom}")
        instance.logiciels.all().delete()
        
        print(f"🔍 Nombre de nouveaux logiciels à créer: {len(logiciels_data)}")
        for i, logiciel_data in enumerate(logiciels_data):
            try:
                # Nettoyer et valider les données avant création
                logiciel_clean = {
                    'nom': str(logiciel_data.get('nom', 'Logiciel inconnu'))[:200],  # Limiter à 200 caractères
                    'version': str(logiciel_data.get('version', ''))[:100],  # Limiter à 100 caractères
                    'editeur': str(logiciel_data.get('editeur', ''))[:100],  # Limiter à 100 caractères
                }

                # Ajouter les champs optionnels s'ils existent
                if logiciel_data.get('date_installation'):
                    logiciel_clean['date_installation'] = logiciel_data['date_installation']
                if logiciel_data.get('taille'):
                    logiciel_clean['taille'] = logiciel_data['taille']

                print(f"🔍 Création logiciel {i+1}/{len(logiciels_data)}: {logiciel_clean['nom']}")
                logiciel, created = LogicielInstalle.objects.get_or_create(
                    machine=instance,
                    nom=logiciel_clean['nom'],
                    version=logiciel_clean['version'],
                    defaults=logiciel_clean
                )
                if created:
                    print(f"✅ Logiciel créé en base: ID={logiciel.id}, Nom={logiciel.nom}")
                else:
                    # Mettre à jour les autres champs si le logiciel existe déjà
                    for field, value in logiciel_clean.items():
                        if field not in ['nom', 'version']:  # Ne pas modifier les champs de la contrainte unique
                            setattr(logiciel, field, value)
                    logiciel.save()
                    print(f"✅ Logiciel mis à jour en base: ID={logiciel.id}, Nom={logiciel.nom}")
                
                logiciels_crees.append({
                    'nom': logiciel.nom,
                    'version': logiciel.version,
                    'editeur': logiciel.editeur
                })
            except Exception as e:
                print(f"❌ Erreur mise à jour logiciel {logiciel_data.get('nom', 'Inconnu')}: {str(e)}")
                print(f"🔍 Données du logiciel problématique: {logiciel_data}")
                import traceback
                traceback.print_exc()
        
        # Ajouter les interfaces et logiciels aux données de log
        donnees_apres['interfaces_reseau'] = interfaces_creees
        donnees_apres['logiciels'] = logiciels_crees
        donnees_apres['nb_interfaces'] = len(interfaces_creees)
        donnees_apres['nb_logiciels'] = len(logiciels_crees)
        
        # Créer l'historique détaillé de la mise à jour
        from .models import HistoriqueMachine
        HistoriqueMachine.objects.create(
            machine=instance,
            type_modification='synchronisation',
            description=f'Machine mise à jour depuis l\'application desktop - '
                       f'OS: {donnees_apres.get("info_systeme", {}).get("os", "N/A")}, '
                       f'RAM: {donnees_apres.get("info_systeme", {}).get("ram_gb", 0)}GB, '
                       f'{donnees_apres.get("nb_interfaces", 0)} interface(s) '
                       f'(avant: {donnees_avant.get("nb_interfaces_avant", 0)}), '
                       f'{donnees_apres.get("nb_logiciels", 0)} logiciel(s) '
                       f'(avant: {donnees_avant.get("nb_logiciels_avant", 0)})',
            utilisateur=user,
            donnees_avant=donnees_avant,
            donnees_apres=donnees_apres
        )
        
        print(f"📝 Historique de mise à jour créé pour {instance.nom} avec {len(interfaces_creees)} interfaces et {len(logiciels_crees)} logiciels")
        
        return instance


class HistoriqueMachineSerializer(serializers.ModelSerializer):
    """Serializer pour l'historique des machines"""
    utilisateur_info = UserSerializer(source='utilisateur', read_only=True)
    
    class Meta:
        model = HistoriqueMachine
        fields = '__all__'
        read_only_fields = ['id', 'utilisateur', 'date_modification']