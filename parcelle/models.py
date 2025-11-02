from django.db import models
from farm_management.models import Farm

# CULTURE
class Culture(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    cycle_min = models.IntegerField(null=True, blank=True)
    cycle_max = models.IntegerField(null=True, blank=True)
    rendement_min_t_ha = models.FloatField(null=True, blank=True)
    rendement_max_t_ha = models.FloatField(null=True, blank=True)
    quantite_semence_g_ha = models.FloatField(null=True, blank=True)

    TYPE_CHOICES = [
        ('conventionnel', 'Conventionnel'),
        ('bio', 'Biologique'),
    ]
    type_culture = models.CharField(max_length=20, choices=TYPE_CHOICES, default='conventionnel')
    saisonnalite = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='cultures/', null=True, blank=True)

    def __str__(self):
        return self.nom


# VARIETE
class Variete(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE, related_name='varietes')
    nom = models.CharField(max_length=100)
    distance_plantation = models.CharField(max_length=50)
    rendement_min = models.FloatField(null=True, blank=True)
    rendement_max = models.FloatField(null=True, blank=True)
    quantite_semence_ha = models.FloatField(null=True, blank=True)
    periode_culture = models.CharField(max_length=100, blank=True, null=True)
    besoins_eau = models.TextField(blank=True, null=True)
    techniques_greffage = models.TextField(blank=True, null=True)
    maladies_frequentes = models.TextField(blank=True, null=True)
    produits_recommandes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='varietes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.culture.nom})"


# PRODUIT PHYTOSANITAIRE
class ProduitPhytosanitaire(models.Model):
    nom_commercial = models.CharField(max_length=100)
    matiere_active = models.CharField(max_length=100)
    type_produit = models.CharField(max_length=50, choices=[
        ('fongicide', 'Fongicide'),
        ('insecticide', 'Insecticide'),
        ('bactericide', 'Bactéricide')
    ])
    image = models.ImageField(upload_to='produits_phytos/', null=True, blank=True)

    def __str__(self):
        return self.nom_commercial


# FERTILISATION
class Fertilisation(models.Model):
    variete = models.ForeignKey(Variete, on_delete=models.CASCADE, related_name='fertilisations')
    jour = models.IntegerField()
    type_engrais = models.CharField(max_length=100)
    dose_ha = models.CharField(max_length=100)
    mode_application = models.CharField(max_length=100, blank=True, null=True)
    illustration = models.ImageField(upload_to='fertilisations/', null=True, blank=True)


# TRAITEMENT PHYTOSANITAIRE
class TraitementPhytosanitaire(models.Model):
    variete = models.ForeignKey(Variete, on_delete=models.CASCADE, related_name='traitements')
    jour = models.IntegerField()
    type_traitement = models.CharField(max_length=100)
    cible = models.CharField(max_length=100)
    produit = models.ForeignKey(
        ProduitPhytosanitaire,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='traitements_utilises'
    )
    matiere_active = models.CharField(max_length=100, blank=True, null=True)
    illustration = models.ImageField(upload_to='traitements/', null=True, blank=True)


# ETAPE CULTURE
class EtapeCulture(models.Model):
    culture = models.ForeignKey(Culture, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    frequence = models.CharField(max_length=50)
    delai_apres_plantation = models.PositiveIntegerField()
    image = models.ImageField(upload_to='etapes/', null=True, blank=True)


# PARCELLE
class Parcelle(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='parcelles')
    variete = models.ForeignKey(Variete, on_delete=models.CASCADE)
    date_plantation = models.DateField()
    climat = models.CharField(max_length=100, blank=True, null=True)
    type_sol = models.CharField(max_length=100, blank=True, null=True)
    surface_ha = models.FloatField(null=True, blank=True)
    type_culture = models.CharField(max_length=20, choices=[('conventionnel', 'Conventionnel'), ('bio', 'Biologique')], null=True, blank=True)
    saison = models.CharField(max_length=50, null=True, blank=True)
    rendement_min = models.FloatField(null=True, blank=True)
    rendement_max = models.FloatField(null=True, blank=True)
    semences_necessaires_g = models.FloatField(null=True, blank=True)
    fertilisations = models.ManyToManyField(Fertilisation, blank=True)
    traitements = models.ManyToManyField(TraitementPhytosanitaire, blank=True)
    etapes = models.ManyToManyField(EtapeCulture, blank=True)

    def __str__(self):
        return f"Parcelle de {self.variete.nom} sur {self.farm.name}"


# CALENDRIER CULTURE - étendu
class CalendrierCulture(models.Model):
    parcelle = models.ForeignKey(Parcelle, on_delete=models.CASCADE)
    date_prevue = models.DateField()
    alerte_envoyee = models.BooleanField(default=False)

    # Champs optionnels selon le type de tâche planifiée
    etape = models.ForeignKey(EtapeCulture, on_delete=models.SET_NULL, null=True, blank=True)
    fertilisation = models.ForeignKey(Fertilisation, on_delete=models.SET_NULL, null=True, blank=True)
    traitement = models.ForeignKey(TraitementPhytosanitaire, on_delete=models.SET_NULL, null=True, blank=True)

    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Calendrier {self.parcelle} - {self.date_prevue}"


# NOTIFICATION
from django.db import models
from farm_management.models import Farm

class NotificationLog(models.Model):
    farm = models.ForeignKey(
        Farm,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()  # texte affiché dans la notif
    date_envoi = models.DateTimeField(auto_now_add=True)  # date de création auto
    canal = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('app', 'App'),
        ],
        default='app',
    )
    envoyee = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)  # Champ pour le statut de lecture
    data_json = models.JSONField(null=True, blank=True)  # pour données personnalisées éventuelles

    @property
    def utilisateur(self):
        """Retourne le propriétaire de la ferme"""
        return self.farm.owner

    def __str__(self):
        return f"Notification pour {self.utilisateur} via {self.canal} le {self.date_envoi.strftime('%Y-%m-%d %H:%M')}"


