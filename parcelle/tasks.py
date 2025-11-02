from celery import shared_task
from .utils import envoyer_notifications_culture

@shared_task(name="envoyer_notifications_task")
def envoyer_notifications_task():
    """Tâche Celery pour envoyer les notifications de culture."""
    print("Exécution de la tâche d'envoi de notifications...")
    count, errors = envoyer_notifications_culture()
    if errors:
        print(f"Erreurs lors de l'envoi des notifications: {errors}")
    print(f"{count} notifications envoyées.")