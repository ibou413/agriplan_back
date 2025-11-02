from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand
from parcelle.utils import envoyer_notifications_culture

class Command(BaseCommand):
    help = "Envoie les notifications planifiées du jour pour chaque ferme"

    def handle(self, *args, **kwargs):
        self.stdout.write("Envoi des notifications en cours...")
        count, errors = envoyer_notifications_culture()
        if errors:
            self.stdout.write(self.style.ERROR(f"Des erreurs se sont produites: {errors}"))
        self.stdout.write(self.style.SUCCESS(f"{count} notifications ont été envoyées avec succès."))
