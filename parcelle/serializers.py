from rest_framework import serializers
from .models import (
    Culture, NotificationLog, Variete, Fertilisation, TraitementPhytosanitaire,
    ProduitPhytosanitaire, EtapeCulture, Parcelle, CalendrierCulture
)

class CultureSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Culture
        fields = '__all__'


class VarieteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Variete
        fields = '__all__'


class FertilisationSerializer(serializers.ModelSerializer):
    illustration = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Fertilisation
        fields = '__all__'


class ProduitPhytosanitaireSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProduitPhytosanitaire
        fields = '__all__'


class TraitementPhytosanitaireSerializer(serializers.ModelSerializer):
    produit = ProduitPhytosanitaireSerializer(read_only=True)
    produit_id = serializers.PrimaryKeyRelatedField(
        queryset=ProduitPhytosanitaire.objects.all(),
        source='produit',
        write_only=True,
        required=False
    )
    illustration = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = TraitementPhytosanitaire
        fields = '__all__'


class EtapeCultureSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = EtapeCulture
        fields = '__all__'




class ParcelleSerializer(serializers.ModelSerializer):
    variete = VarieteSerializer(read_only=True)
    fertilisations = FertilisationSerializer(many=True, read_only=True)
    traitements = TraitementPhytosanitaireSerializer(many=True, read_only=True)
    etapes = EtapeCultureSerializer(many=True, read_only=True)
    calendrier = serializers.SerializerMethodField()
    farm = serializers.StringRelatedField()

    class Meta:
        model = Parcelle
        fields = [
            'id',
            'variete',
            'date_plantation',
            'climat',
            'type_sol',
            'surface_ha',
            'type_culture',
            'saison',
            'rendement_min',
            'rendement_max',
            'semences_necessaires_g',
            'fertilisations',
            'traitements',
            'etapes',
            'calendrier',
            'farm',
        ]

    def get_calendrier(self, obj):
        calendriers = CalendrierCulture.objects.filter(parcelle=obj).order_by('date_prevue')
        return CalendrierCultureSerializer(calendriers, many=True).data



class CalendrierCultureSerializer(serializers.ModelSerializer):
    etape = EtapeCultureSerializer(read_only=True)
    fertilisation = FertilisationSerializer(read_only=True)
    traitement = TraitementPhytosanitaireSerializer(read_only=True)

    etape_id = serializers.PrimaryKeyRelatedField(
        queryset=EtapeCulture.objects.all(), source='etape', write_only=True, required=False
    )
    fertilisation_id = serializers.PrimaryKeyRelatedField(
        queryset=Fertilisation.objects.all(), source='fertilisation', write_only=True, required=False
    )
    traitement_id = serializers.PrimaryKeyRelatedField(
        queryset=TraitementPhytosanitaire.objects.all(), source='traitement', write_only=True, required=False
    )

    class Meta:
        model = CalendrierCulture
        fields = '__all__'


from rest_framework import serializers

class NotificationLogSerializer(serializers.ModelSerializer):
    utilisateur = serializers.ReadOnlyField(source='utilisateur.email')
    data_json = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = NotificationLog  # ou NotificationLog selon ton import
        # Liste explicite, tu peux aussi mettre '__all__' si tu veux
        fields = [
            'id',
            'farm',
            'message',
            'date_envoi',
            'canal',
            'envoyee',
            'is_read',
            'data_json',
            'utilisateur',
        ]
        read_only_fields = ['id', 'date_envoi', 'utilisateur']
