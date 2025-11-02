from django.contrib import admin
from .models import Farm, Crop, Sensor, SensorReading, WeatherForecast, FarmActivity, Resource


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name','latitude','longitude', 'location', 'owner', 'size_in_hectares', 'created_at')
    search_fields = ('name', 'location', 'owner__username')
    list_filter = ('created_at',)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'planting_date', 'expected_harvest_date', 'area_covered', 'crop_type')
    search_fields = ('name', 'farm__name')
    list_filter = ('crop_type', 'planting_date')


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'farm', 'installation_date', 'last_reading_value', 'last_reading_time')
    search_fields = ('sensor_type', 'farm__name')
    list_filter = ('sensor_type', 'installation_date')


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'timestamp', 'value')
    search_fields = ('sensor__sensor_type', 'sensor__farm__name')
    list_filter = ('timestamp',)


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ('farm', 'date', 'temperature', 'precipitation', 'wind_speed')
    search_fields = ('farm__name',)
    list_filter = ('date',)


@admin.register(FarmActivity)
class FarmActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'farm', 'crop', 'planned_date', 'status')
    search_fields = ('activity_type', 'farm__name', 'crop__name')
    list_filter = ('activity_type', 'status', 'planned_date')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'quantity', 'unit')
    search_fields = ('name', 'farm__name')
    list_filter = ('unit',)
