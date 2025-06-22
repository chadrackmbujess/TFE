"""
Vues pour l'interface web
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    """Page d'accueil"""
    return render(request, 'web/index.html')


@login_required
def dashboard(request):
    """Tableau de bord principal"""
    return render(request, 'web/dashboard.html')