from django.contrib import admin
from .models import (
    Culture, Variete, Fertilisation, TraitementPhytosanitaire,
    ProduitPhytosanitaire, EtapeCulture, Parcelle, CalendrierCulture,
    NotificationLog
)

admin.site.register(Culture)
admin.site.register(Variete)
admin.site.register(Fertilisation)
admin.site.register(TraitementPhytosanitaire)
admin.site.register(ProduitPhytosanitaire)
admin.site.register(EtapeCulture)
admin.site.register(Parcelle)
admin.site.register(CalendrierCulture)
admin.site.register(NotificationLog)
