from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
#from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm





urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Applications spécifiques
    path('api/auth/', include('users.urls')),
    path('api/productor/', include('farm_management.urls')),
    path('api/parcelle/', include('parcelle.urls')),
    path('api/market/', include('market.urls')),
    

] 
# Ajoutez cette ligne pour permettre à Django de servir des fichiers médias
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

