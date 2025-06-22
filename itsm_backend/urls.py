"""
Configuration des URLs principales du projet ITSM
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

# Configuration du routeur principal pour l'API
router = DefaultRouter()

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # Authentification Django
    path('accounts/', include('django.contrib.auth.urls')),
    
    # API Authentication
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # API Routes
    path('api/v1/', include(router.urls)),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/machines/', include('apps.machines.urls')),
    path('api/v1/tickets/', include('apps.tickets.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/monitoring/', include('apps.monitoring.urls')),
    path('api/v1/maintenance/', include('apps.maintenance.urls')),
    path('api/v1/remote-control/', include('apps.remote_control.urls')),
    path('api/v1/knowledge-base/', include('apps.knowledge_base.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    
    # Endpoint direct pour les notifications (contournement)
    path('api/v1/notifications/', include([
        path('', include('apps.tickets.urls')),
    ])),
    
    # Interface Web (optionnelle)
    path('', include('apps.web.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuration de l'admin
admin.site.site_header = "Administration ITSM"
admin.site.site_title = "ITSM Admin"
admin.site.index_title = "Gestion du système ITSM"