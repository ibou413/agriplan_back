from rest_framework import serializers
from .models import Farm, Crop, Sensor, SensorReading, WeatherForecast, FarmActivity, Resource
from users.models import CustomUser
User = CustomUser

class FarmSerializer(serializers.ModelSerializer):
    # Remplace StringRelatedField par PrimaryKeyRelatedField pour permettre l'envoi de l'ID du propriétaire
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    
    # Affichage des relations avec les autres objets (comme les cultures, capteurs, activités, etc.)
    crops = serializers.StringRelatedField(many=True, read_only=True)
    sensors = serializers.StringRelatedField(many=True, read_only=True)
    activities = serializers.StringRelatedField(many=True, read_only=True)
    resources = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Farm
        fields = '__all__'


class CropSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField(write_only=True)  # Accepte l'ID de la ferme

    class Meta:
        model = Crop
        fields = ['id', 'name', 'farm_id', 'planting_date', 'expected_harvest_date', 'area_covered', 'crop_type']
    
    def create(self, validated_data):
        farm_id = validated_data.pop('farm_id')
        farm = Farm.objects.get(id=farm_id)  # Récupérer l'objet farm à partir de l'ID
        crop = Crop.objects.create(farm=farm, **validated_data)
        return crop




from rest_framework import serializers
from .models import Sensor, SensorReading, Farm

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ['id', 'timestamp', 'value']

class SensorSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField(write_only=True)  # Accepte l'ID de la ferme
    readings = SensorReadingSerializer(many=True, read_only=True)

    class Meta:
        model = Sensor
        fields = [
            'id',
            'farm_id',  # ID de la ferme en entrée
            'farm',  # Lien vers l'objet Farm en sortie
            'sensor_type',
            'installation_date',
            'last_reading_value',
            'last_reading_time',
            'readings'
        ]
        read_only_fields = ['farm']  # Empêche la modification directe de l'objet Farm

    def create(self, validated_data):
        farm_id = validated_data.pop('farm_id')  # Extraire l'ID de la ferme
        try:
            farm = Farm.objects.get(id=farm_id)  # Récupérer la ferme associée
        except Farm.DoesNotExist:
            raise serializers.ValidationError({'farm_id': 'Ferme introuvable.'})

        # Créer le capteur en associant la ferme
        sensor = Sensor.objects.create(farm=farm, **validated_data)
        return sensor


class WeatherForecastSerializer(serializers.ModelSerializer):
    farm = serializers.StringRelatedField()
    
    class Meta:
        model = WeatherForecast
        fields = '__all__'


class FarmActivitySerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField(write_only=True)
    crop_id = serializers.IntegerField(write_only=True)  # Accepte l'ID de la ferme

    class Meta:
        model = FarmActivity
        fields = ['id', 'farm_id', 'crop_id', 'activity_type', 'planned_date', 'status']
    
    def create(self, validated_data):
        farm_id = validated_data.pop('farm_id')
        crop_id = validated_data.pop('crop_id')
        farm = Farm.objects.get(id=farm_id)  # Récupérer l'objet farm à partir de l'ID
        crop = Crop.objects.get(id=crop_id)
        activity = FarmActivity.objects.create(farm=farm, crop=crop, **validated_data)
        return activity


class ResourceSerializer(serializers.ModelSerializer):
    farm_id = serializers.IntegerField(write_only=True)  # Accepte l'ID de la ferme

    class Meta:
        model = Resource
        fields = ['id', 'name', 'farm_id', 'quantity', 'unit']
    
    def create(self, validated_data):
        farm_id = validated_data.pop('farm_id')
        farm = Farm.objects.get(id=farm_id)  # Récupérer l'objet farm à partir de l'ID
        resource = Resource.objects.create(farm=farm, **validated_data)
        return resource





    
