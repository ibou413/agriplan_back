from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import timedelta
from rest_framework import viewsets

from .utils import envoyer_notifications_culture
from .models import (
    Culture, Variete, Fertilisation, TraitementPhytosanitaire,
    ProduitPhytosanitaire, EtapeCulture, Parcelle, CalendrierCulture, NotificationLog
)
from .serializers import (
    CultureSerializer, VarieteSerializer, FertilisationSerializer,
    TraitementPhytosanitaireSerializer, EtapeCultureSerializer,
    ParcelleSerializer, CalendrierCultureSerializer, NotificationLogSerializer, ProduitPhytosanitaireSerializer
)






class CultureViewSet(viewsets.ModelViewSet):
    queryset = Culture.objects.all()
    serializer_class = CultureSerializer

class VarieteViewSet(viewsets.ModelViewSet):
    queryset = Variete.objects.all()
    serializer_class = VarieteSerializer

class FertilisationViewSet(viewsets.ModelViewSet):
    queryset = Fertilisation.objects.all()
    serializer_class = FertilisationSerializer

class TraitementPhytosanitaireViewSet(viewsets.ModelViewSet):
    queryset = TraitementPhytosanitaire.objects.all()
    serializer_class = TraitementPhytosanitaireSerializer

class ProduitPhytosanitaireViewSet(viewsets.ModelViewSet):
    queryset = ProduitPhytosanitaire.objects.all()
    serializer_class = ProduitPhytosanitaireSerializer

class EtapeCultureViewSet(viewsets.ModelViewSet):
    queryset = EtapeCulture.objects.all()
    serializer_class = EtapeCultureSerializer

class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            queryset = queryset.filter(farm__id=farm_id)
        return queryset

class CalendrierCultureViewSet(viewsets.ModelViewSet):
    queryset = CalendrierCulture.objects.all()
    serializer_class = CalendrierCultureSerializer



class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        farm_id = self.request.query_params.get('farm_id')
        queryset = NotificationLog.objects.all()
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        return queryset.order_by('-date_envoi')



class PlanificationAutomatiqueAPIView(APIView):
    ALERTE_JOURS_AVANT = 3  # délai avant envoi de notification

    def post(self, request):
        try:
            # 1. Données reçues
            culture_nom = request.data.get("culture")
            variete_nom = request.data.get("variete")
            surface = float(request.data.get("surface_ha"))
            date_plantation = parse_date(request.data.get("date_plantation"))
            type_culture = request.data.get("type_culture")
            saison = request.data.get("saison")
            farm_id = request.data.get("farm_id")

            # 2. Recherche de la culture et variété
            culture = get_object_or_404(Culture, nom__iexact=culture_nom)
            variete = get_object_or_404(Variete, nom__iexact=variete_nom, culture=culture)

            # 3. Calculs techniques
            rendement_min = culture.rendement_min_t_ha or 0
            rendement_max = culture.rendement_max_t_ha or 0
            semence_ha = culture.quantite_semence_g_ha or 0

            rendement_estime = {
                "min": round(rendement_min * surface, 2),
                "max": round(rendement_max * surface, 2)
            }
            semences_necessaires = round(semence_ha * surface, 2)

            # 4. Récupération des plans associés
            fertilisations = Fertilisation.objects.filter(variete=variete)
            traitements = TraitementPhytosanitaire.objects.filter(variete=variete)
            etapes = EtapeCulture.objects.filter(culture=culture)

            # 5. Création de la parcelle
            parcelle = Parcelle.objects.create(
                farm_id=farm_id,
                variete=variete,
                date_plantation=date_plantation,
                surface_ha=surface,
                type_culture=type_culture,
                saison=saison,
                rendement_min=rendement_estime["min"],
                rendement_max=rendement_estime["max"],
                semences_necessaires_g=semences_necessaires
            )
            parcelle.fertilisations.set(fertilisations)
            parcelle.traitements.set(traitements)
            parcelle.etapes.set(etapes)

            # 6. Génération du calendrier + notifications
            calendrier = []

            # Étapes
            for etape in etapes:
                date_prevue = date_plantation + timedelta(days=etape.delai_apres_plantation)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    etape=etape,
                    date_prevue=date_prevue
                )
               
                calendrier.append(calendrier_entry)

            # Fertilisations
            for ferti in fertilisations:
                date_prevue = date_plantation + timedelta(days=ferti.jour)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    fertilisation=ferti,
                    date_prevue=date_prevue
                )
                calendrier.append(calendrier_entry)

            # Traitements
            for trt in traitements:
                date_prevue = date_plantation + timedelta(days=trt.jour)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    traitement=trt,
                    date_prevue=date_prevue
                )
                
                calendrier.append(calendrier_entry)

            # 7. Réponse
            data = {
                "parcelle": ParcelleSerializer(parcelle).data,
                "culture": CultureSerializer(culture).data,
                "variete": VarieteSerializer(variete).data,
                "fertilisation": FertilisationSerializer(fertilisations, many=True).data,
                "traitements": TraitementPhytosanitaireSerializer(traitements, many=True).data,
                "etapes": EtapeCultureSerializer(etapes, many=True).data,
                "calendrier": CalendrierCultureSerializer(calendrier, many=True).data
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cultures(request):
    cultures = Culture.objects.all()
    return Response(CultureSerializer(cultures, many=True).data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_varietes_by_culture(request, culture_id):
    varietes = Variete.objects.filter(culture_id=culture_id)
    return Response(VarieteSerializer(varietes, many=True).data)


from .utils import envoyer_notifications_culture


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_notifications_culture_view(request):
    notifications_envoyees_count, erreurs_globales = envoyer_notifications_culture()
    if not notifications_envoyees_count and not erreurs_globales:
        return Response({"detail": "Aucune notification à envoyer."}, status=status.HTTP_200_OK)
    
    return Response({
        "notifications_envoyees": notifications_envoyees_count,
        "erreurs": erreurs_globales,
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(NotificationLog, pk=pk)
    # Vérifier si l'utilisateur a le droit de modifier cette notification
    if notification.farm.owner != request.user:
        return Response({"error": "Permission non accordée."}, status=status.HTTP_403_FORBIDDEN)
    
    notification.is_read = True
    notification.save()
    return Response(status=status.HTTP_200_OK)
