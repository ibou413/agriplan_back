from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CultureViewSet, PlanificationAutomatiqueAPIView, VarieteViewSet, FertilisationViewSet,
    TraitementPhytosanitaireViewSet, ProduitPhytosanitaireViewSet,
    EtapeCultureViewSet, ParcelleViewSet, CalendrierCultureViewSet,
    NotificationLogViewSet, 
)
from . import views
from django.urls import path

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet


router = DefaultRouter()



router = DefaultRouter()
router.register(r'cultures', CultureViewSet)
router.register(r'varietes', VarieteViewSet)
router.register(r'fertilisations', FertilisationViewSet)
router.register(r'traitements', TraitementPhytosanitaireViewSet)
router.register(r'produits-phytosanitaires', ProduitPhytosanitaireViewSet)
router.register(r'etapes-culture', EtapeCultureViewSet)
router.register(r'parcelles', ParcelleViewSet)
router.register(r'calendrier-culture', CalendrierCultureViewSet)
router.register(r'notifications', NotificationLogViewSet)
router.register('devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('planification-automatique/', PlanificationAutomatiqueAPIView.as_view(), name='planification-automatique'),
    path('notifications-culture/', views.envoyer_notifications_culture_view, name='notifications'),
    path('list-cultures/', views.list_cultures, name='list_cultures'),
    path('list-cultures/<int:culture_id>/varietes/', views.list_varietes_by_culture, name='list_varietes_by_culture'),
    path('notifications/<int:pk>/mark-as-read/', views.mark_notification_as_read, name='notification-mark-as-read'),
   
]





