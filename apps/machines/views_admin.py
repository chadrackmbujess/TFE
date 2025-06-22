"""
Vues personnalisées pour l'administration des machines
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import (
    LogicielReference, AutorisationLogiciel, CategorieLogiciel,
    LogicielInstalle
)
from apps.users.models import Structure, Site, Groupe

User = get_user_model()


@staff_member_required
def blocage_avance_view(request):
    """Vue pour le blocage avancé de logiciels"""
    
    if request.method == 'POST':
        return traiter_blocage_avance(request)
    
    # Récupérer les données pour le formulaire
    context = {
        'categories': CategorieLogiciel.objects.filter(actif=True).order_by('nom'),
        'logiciels': LogicielReference.objects.filter(actif=True).order_by('nom'),
        'structures': Structure.objects.filter(active=True).order_by('nom'),
        'sites': Site.objects.filter(active=True).order_by('nom'),
        'groupes': Groupe.objects.filter(active=True).order_by('nom'),
        'utilisateurs': User.objects.filter(is_active=True).order_by('username'),
        'stats': get_blocage_stats()
    }
    
    return render(request, 'admin/machines/blocage_avance.html', context)


def traiter_blocage_avance(request):
    """Traiter les demandes de blocage avancé"""
    try:
        # Récupérer les paramètres du formulaire
        action = request.POST.get('action')
        logiciels_ids = request.POST.getlist('logiciels')
        categories_ids = request.POST.getlist('categories')
        cible_type = request.POST.get('cible_type')
        cibles_ids = request.POST.getlist('cibles')
        motif = request.POST.get('motif', '')
        
        # Construire la liste des logiciels à traiter
        logiciels = set()
        
        # Logiciels sélectionnés directement
        if logiciels_ids:
            logiciels.update(LogicielReference.objects.filter(id__in=logiciels_ids))
        
        # Logiciels par catégorie
        if categories_ids:
            logiciels.update(LogicielReference.objects.filter(categorie_id__in=categories_ids))
        
        if not logiciels:
            messages.error(request, "Aucun logiciel sélectionné.")
            return redirect('admin:blocage_avance')
        
        # Traiter selon l'action
        if action == 'bloquer':
            count = creer_blocages(logiciels, cible_type, cibles_ids, request.user, motif)
            messages.success(request, f'{count} blocage(s) créé(s) avec succès.')
        elif action == 'autoriser':
            count = creer_autorisations(logiciels, cible_type, cibles_ids, request.user, motif)
            messages.success(request, f'{count} autorisation(s) créée(s) avec succès.')
        elif action == 'interdire':
            count = interdire_logiciels(logiciels, request.user)
            messages.success(request, f'{count} logiciel(s) marqué(s) comme interdit(s).')
        else:
            messages.error(request, "Action non reconnue.")
        
    except Exception as e:
        messages.error(request, f"Erreur lors du traitement: {str(e)}")
    
    return redirect('admin:blocage_avance')


def creer_blocages(logiciels, cible_type, cibles_ids, user, motif):
    """Créer des blocages pour les logiciels et cibles spécifiés"""
    count = 0
    
    for logiciel in logiciels:
        if cible_type == 'utilisateur':
            utilisateurs = User.objects.filter(id__in=cibles_ids)
            for utilisateur in utilisateurs:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    utilisateur=utilisateur,
                    defaults={
                        'type_autorisation': 'utilisateur',
                        'statut': 'refuse',
                        'autorise_par': user,
                        'motif': motif or f'Bloqué via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'refuse':
                    autorisation.statut = 'refuse'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Bloqué via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'structure':
            structures = Structure.objects.filter(id__in=cibles_ids)
            for structure in structures:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    structure=structure,
                    defaults={
                        'type_autorisation': 'structure',
                        'statut': 'refuse',
                        'autorise_par': user,
                        'motif': motif or f'Bloqué via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'refuse':
                    autorisation.statut = 'refuse'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Bloqué via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'site':
            sites = Site.objects.filter(id__in=cibles_ids)
            for site in sites:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    site=site,
                    defaults={
                        'type_autorisation': 'site',
                        'statut': 'refuse',
                        'autorise_par': user,
                        'motif': motif or f'Bloqué via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'refuse':
                    autorisation.statut = 'refuse'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Bloqué via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'groupe':
            groupes = Groupe.objects.filter(id__in=cibles_ids)
            for groupe in groupes:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    groupe=groupe,
                    defaults={
                        'type_autorisation': 'groupe',
                        'statut': 'refuse',
                        'autorise_par': user,
                        'motif': motif or f'Bloqué via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'refuse':
                    autorisation.statut = 'refuse'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Bloqué via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
    
    # Forcer la vérification des autorisations pour les logiciels installés
    logiciels_installes = LogicielInstalle.objects.filter(logiciel_reference__in=logiciels)
    for logiciel_installe in logiciels_installes:
        logiciel_installe.verifier_autorisation()
    
    return count


def creer_autorisations(logiciels, cible_type, cibles_ids, user, motif):
    """Créer des autorisations pour les logiciels et cibles spécifiés"""
    count = 0
    
    for logiciel in logiciels:
        if cible_type == 'utilisateur':
            utilisateurs = User.objects.filter(id__in=cibles_ids)
            for utilisateur in utilisateurs:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    utilisateur=utilisateur,
                    defaults={
                        'type_autorisation': 'utilisateur',
                        'statut': 'autorise',
                        'autorise_par': user,
                        'motif': motif or f'Autorisé via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'autorise':
                    autorisation.statut = 'autorise'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Autorisé via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'structure':
            structures = Structure.objects.filter(id__in=cibles_ids)
            for structure in structures:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    structure=structure,
                    defaults={
                        'type_autorisation': 'structure',
                        'statut': 'autorise',
                        'autorise_par': user,
                        'motif': motif or f'Autorisé via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'autorise':
                    autorisation.statut = 'autorise'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Autorisé via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'site':
            sites = Site.objects.filter(id__in=cibles_ids)
            for site in sites:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    site=site,
                    defaults={
                        'type_autorisation': 'site',
                        'statut': 'autorise',
                        'autorise_par': user,
                        'motif': motif or f'Autorisé via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'autorise':
                    autorisation.statut = 'autorise'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Autorisé via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
                
        elif cible_type == 'groupe':
            groupes = Groupe.objects.filter(id__in=cibles_ids)
            for groupe in groupes:
                autorisation, created = AutorisationLogiciel.objects.get_or_create(
                    logiciel=logiciel,
                    groupe=groupe,
                    defaults={
                        'type_autorisation': 'groupe',
                        'statut': 'autorise',
                        'autorise_par': user,
                        'motif': motif or f'Autorisé via interface avancée par {user.username}'
                    }
                )
                if not created and autorisation.statut != 'autorise':
                    autorisation.statut = 'autorise'
                    autorisation.autorise_par = user
                    autorisation.motif = motif or f'Autorisé via interface avancée par {user.username}'
                    autorisation.save()
                count += 1
    
    # Forcer la vérification des autorisations pour les logiciels installés
    logiciels_installes = LogicielInstalle.objects.filter(logiciel_reference__in=logiciels)
    for logiciel_installe in logiciels_installes:
        logiciel_installe.verifier_autorisation()
    
    return count


def interdire_logiciels(logiciels, user):
    """Marquer les logiciels comme interdits"""
    count = 0
    for logiciel in logiciels:
        if logiciel.niveau_securite != 'interdit':
            logiciel.niveau_securite = 'interdit'
            logiciel.save()
            count += 1
    
    # Forcer la vérification des autorisations pour les logiciels installés
    logiciels_installes = LogicielInstalle.objects.filter(logiciel_reference__in=logiciels)
    for logiciel_installe in logiciels_installes:
        logiciel_installe.verifier_autorisation()
    
    return count


def get_blocage_stats():
    """Récupérer les statistiques de blocage"""
    return {
        'total_logiciels': LogicielReference.objects.filter(actif=True).count(),
        'logiciels_interdits': LogicielReference.objects.filter(niveau_securite='interdit').count(),
        'total_autorisations': AutorisationLogiciel.objects.count(),
        'autorisations_refusees': AutorisationLogiciel.objects.filter(statut='refuse').count(),
        'logiciels_bloques': LogicielInstalle.objects.filter(bloque=True).count(),
        'logiciels_installes': LogicielInstalle.objects.count(),
    }


@staff_member_required
@require_http_methods(["GET"])
def api_logiciels_par_categorie(request):
    """API pour récupérer les logiciels d'une catégorie"""
    categorie_id = request.GET.get('categorie_id')
    
    if not categorie_id:
        return JsonResponse({'error': 'categorie_id requis'}, status=400)
    
    try:
        logiciels = LogicielReference.objects.filter(
            categorie_id=categorie_id,
            actif=True
        ).values('id', 'nom', 'editeur', 'niveau_securite')
        
        return JsonResponse({
            'logiciels': list(logiciels)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_http_methods(["GET"])
def api_stats_blocage(request):
    """API pour récupérer les statistiques de blocage en temps réel"""
    try:
        stats = get_blocage_stats()
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)