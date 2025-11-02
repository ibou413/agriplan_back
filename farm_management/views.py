from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
import requests
from django.http import JsonResponse
from django.conf import settings
from .models import Farm, Crop, Sensor, SensorReading, WeatherForecast, FarmActivity, Resource
from .serializers import (
    FarmSerializer, CropSerializer, SensorSerializer, 
    SensorReadingSerializer, WeatherForecastSerializer, 
    FarmActivitySerializer, ResourceSerializer
)
from django.db.models import Value
from django.db.models.functions import Lower


class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes= [IsAuthenticated]
    def perform_create(self, serializer):
        """Associe l'utilisateur authentifié comme propriétaire de la ferme."""
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='by-location')
    def farms_by_location(self, request):
        location = request.query_params.get('location')
        if not location:
            return Response({'error': 'Le paramètre "location" est requis.'}, status=400)
        
        farms = Farm.objects.filter(location__iexact=location)
        serializer = self.get_serializer(farms, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='regions')
    def get_regions(self, request):
        regions = (
            Farm.objects.exclude(location__isnull=True)
            .exclude(location__exact='')
            .values_list('location', flat=True)
            .distinct()
        )
    # Optionnel : trier les régions par ordre alphabétique insensible à la casse
        regions = sorted(set(regions), key=lambda r: r.lower())
        return Response(regions)

    @action(detail=True, methods=['get'])
    def crops(self, request, pk=None):
        farm = self.get_object()
        crops = farm.crops.all()
        serializer = CropSerializer(crops, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def sensors(self, request, pk=None):
        farm = self.get_object()
        sensors = farm.sensors.all()
        serializer = SensorSerializer(sensors, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        farm = self.get_object()
        activities = farm.activities.all()
        serializer = FarmActivitySerializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_farms(self, request):
        user = request.user
        farms = Farm.objects.filter(owner=user)
        serializer = FarmSerializer(farms, many=True)
        return Response(serializer.data)


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.all()
    serializer_class = CropSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrer les cultures par l'ID de la ferme.
        """
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            return Crop.objects.filter(farm_id=farm_id)
        return Crop.objects.none()  # Retourner une liste vide si farm_id n'est pas fourni



class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes= [IsAuthenticated]


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        """Permet de filtrer les relevés par capteur si un paramètre 'sensor_id' est passé dans la requête."""
        sensor_id = self.request.query_params.get('sensor_id')
        if sensor_id:
            return self.queryset.filter(sensor__id=sensor_id)
        return self.queryset


class WeatherForecastViewSet(viewsets.ModelViewSet):
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes= [IsAuthenticated]

    def get_queryset(self):
        """Permet de filtrer les prévisions météo par ferme si un paramètre 'farm_id' est passé."""
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            return self.queryset.filter(farm__id=farm_id)
        return self.queryset


class FarmActivityViewSet(viewsets.ModelViewSet):
    queryset = FarmActivity.objects.all()
    serializer_class = FarmActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrer les activités par l'ID de la ferme.
        """
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            return FarmActivity.objects.filter(farm_id=farm_id)
        return FarmActivity.objects.none()


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrer les ressources par l'ID de la ferme.
        """
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            return Resource.objects.filter(farm_id=farm_id)
        return Resource.objects.none()




def get_weather_openweathermap(request, farm_id):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    api_key = settings.OPENWEATHER_API_KEY

    from .models import Farm
    try:
        farm = Farm.objects.get(id=farm_id)
        if farm.latitude and farm.longitude:
            params = {
                'lat': farm.latitude,
                'lon': farm.longitude,
                'appid': api_key,
                'units': 'metric',
                'lang': 'fr'
            }
        elif farm.location:
            params = {
                'q': farm.location,
                'appid': api_key,
                'units': 'metric',
                'lang': 'fr'
            }
        else:
            return JsonResponse({'error': 'No location data available'}, status=400)
    except Farm.DoesNotExist:
        return JsonResponse({'error': 'Farm not found'}, status=404)

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({
            'location': farm.location or f"{farm.latitude},{farm.longitude}",
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind']['deg'],
            'pressure': data['main']['pressure'],
            'feels_like': data['main']['feels_like'],
            'visibility': data['visibility'],
            'cloud_coverage': data['clouds']['all'],
            'sunrise': data['sys']['sunrise'],
            'sunset': data['sys']['sunset']
        })
    else:
        return JsonResponse({'error': 'Unable to fetch weather data'}, status=response.status_code)





def get_weather_weatherapi(request, farm_id):
    # URL de l'API WeatherAPI
    base_url = "https://api.weatherapi.com/v1/current.json" 
    
    # Clé API (à configurer dans les settings Django)
    api_key = settings.WEATHERAPI_API_KEY

    # Récupérer la localisation de la ferme
    from .models import Farm
    try:
        farm = Farm.objects.get(id=farm_id)
        location = farm.location  # Exemple : "Paris" ou coordonnées "48.8566,2.3522"
    except Farm.DoesNotExist:
        return JsonResponse({'error': 'Farm not found'}, status=404)

    # Préparer les paramètres de la requête
    params = {
        'key': api_key,        # Clé API
        'q': location,         # Nom de la ville ou coordonnées
        'lang': 'fr'           # Langue : Français
    }

    # Faire la requête à l’API
    response = requests.get(base_url, params=params)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        data = response.json()
        return JsonResponse({
    'location': location,
    'temperature': data['current']['temp_c'],
    'humidity': data['current']['humidity'],
    'description': data['current']['condition']['text'],
    'wind_speed': data['current']['wind_kph'],
    'wind_direction': data['current']['wind_dir'],
    'pressure': data['current']['pressure_mb'],  # Pression atmosphérique en millibars
    'precipitation': data['current']['precip_mm'],  # Précipitations en millimètres
    'feels_like': data['current']['feelslike_c'],  # Température ressentie en Celsius
    'uv_index': data['current']['uv'],  # Indice UV
    'visibility': data['current']['vis_km'],  # Visibilité en kilomètres
    'cloud_coverage': data['current']['cloud'],  # Pourcentage de couverture nuageuse
    'last_updated': data['current']['last_updated']  # Dernière mise à jour des données
     })
    else:
        return JsonResponse({'error': 'Unable to fetch weather data'}, status=response.status_code)
