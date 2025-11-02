# userapp/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()
from django.conf import settings



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        #fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        # Vérification si les deux mots de passe correspondent
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        # Suppression du champ password2 car non nécessaire pour la création
        validated_data.pop('password2')
        # Création de l'utilisateur avec le mot de passe hashé
        user = User.objects.create_user(
            username=validated_data['username'],
            #first_name=validated_data['first_name'],
            #last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user



# userapp/serializers.py

from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'professional_activity', 'region', 'account_type', 'profile_image', 'profile_image_url']

    def get_profile_image_url(self, obj):
        # Génère l'URL complète pour l'image de profil si elle existe
        request = self.context.get('request')
        if obj.profile_image and request:
            return request.build_absolute_uri(obj.profile_image.url)
        return None

    def update(self, instance, validated_data):
        # Récupérer l'image du profil si elle est présente dans les données validées
        profile_image = validated_data.pop('profile_image', None)

        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Mettre à jour l'image si elle est présente
        if profile_image:
            instance.profile_image = profile_image

        # Sauvegarder l'instance
        instance.save()
        return instance
