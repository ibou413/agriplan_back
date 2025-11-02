from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FarmViewSet, CropViewSet, SensorViewSet, 
    SensorReadingViewSet, WeatherForecastViewSet, 
    FarmActivityViewSet, ResourceViewSet, get_weather_openweathermap,
    get_weather_weatherapi
)

router = DefaultRouter()
router.register(r'farms', FarmViewSet)
router.register(r'crops', CropViewSet)
router.register(r'sensors', SensorViewSet)
router.register(r'sensor-readings', SensorReadingViewSet)
router.register(r'weather-forecasts', WeatherForecastViewSet)
router.register(r'farm-activities', FarmActivityViewSet)
router.register(r'resources', ResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('weather/openweathermap/<int:farm_id>/', get_weather_openweathermap, name='weather_openweathermap'),
    path('weather/weatherapi/<int:farm_id>/', get_weather_weatherapi, name='weather_weatherapi'),
]
