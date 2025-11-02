from django.db import models

from users.models import CustomUser



class Farm(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)   # Latitude de la ferme
    longitude = models.FloatField(null=True, blank=True)  # Longitude de la ferme
    location = models.CharField(max_length=255, blank=True, help_text="Nom de la ville ou adresse")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    size_in_hectares = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Crop(models.Model):
    name = models.CharField(max_length=100)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='crops')
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    area_covered = models.DecimalField(max_digits=10, decimal_places=2)  # en hectares
    crop_type = models.CharField(max_length=100)  # Exemple : blé, maïs, riz

    def __str__(self):
        return f"{self.name} - {self.farm.name}"

class Sensor(models.Model):
    SENSOR_TYPES = [
        ('temperature', 'Température'),
        ('humidity', 'Humidité'),
        ('soil_moisture', 'Humidité du sol'),
        ('ph', 'PH du sol'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='sensors')
    sensor_type = models.CharField(max_length=50, choices=SENSOR_TYPES)
    installation_date = models.DateField()
    last_reading_value = models.FloatField(null=True, blank=True)
    last_reading_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.sensor_type} - {self.farm.name}"



class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.sensor.sensor_type} - {self.timestamp}"


class WeatherForecast(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='weather_forecasts')
    date = models.DateField()
    temperature = models.FloatField()  # En degrés Celsius
    precipitation = models.FloatField()  # En mm
    wind_speed = models.FloatField()  # En km/h

    def __str__(self):
        return f"Prévisions pour {self.farm.name} - {self.date}"


class FarmActivity(models.Model):
    ACTIVITY_TYPES = [
        ('planting', 'Plantation'),
        ('irrigation', 'Irrigation'),
        ('fertilizing', 'Fertilisation'),
        ('harvesting', 'Récolte'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='activities')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    planned_date = models.DateField()
    status = models.CharField(max_length=50, choices=[('planned', 'Planifié'), ('done', 'Terminé')], default='planned')
    
    def __str__(self):
        return f"{self.activity_type} - {self.farm.name} - {self.planned_date}"


class Resource(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50)  # Exemple : kg, litres

    def __str__(self):
        return f"{self.name} - {self.farm.name}"
