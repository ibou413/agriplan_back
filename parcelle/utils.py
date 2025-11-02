from django.utils import timezone
from django.db import transaction
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification
from .models import CalendrierCulture, NotificationLog

def construire_message(evenement):
    if evenement.etape:
        action = f"Étape : {evenement.etape.nom}"
    elif evenement.fertilisation:
        action = f"Fertilisation : {evenement.fertilisation.type_engrais}"
    elif evenement.traitement:
        action = f"Traitement : {evenement.traitement.type_traitement}"
    else:
        action = "Tâche planifiée"
    return f"📅 {action} prévue aujourd'hui sur la parcelle : {evenement.parcelle.variete.nom}"


def get_image_url(obj, field_name="image"):
    image = getattr(obj, field_name, None)
    if image:
        if hasattr(image, 'url'):
            return image.url
    return None

def construire_data_payload(evenement):
    parcelle = evenement.parcelle
    variete = parcelle.variete

    data = {
        "evenement_id": str(evenement.id),
        "date_prevue": str(evenement.date_prevue),
        "commentaire": evenement.commentaire or "",
        "parcelle": {
            "id": str(parcelle.id),
            "surface_ha": parcelle.surface_ha,
            "type_sol": parcelle.type_sol,
            "climat": parcelle.climat,
            "type_culture": parcelle.type_culture,
            "saison": parcelle.saison,
            "image_url": get_image_url(parcelle, "image_url"),
        },
        "variete": {
            "id": str(variete.id),
            "nom": variete.nom,
            "distance_plantation": variete.distance_plantation,
            "rendement_min": variete.rendement_min,
            "rendement_max": variete.rendement_max,
            "periode_culture": variete.periode_culture,
            "besoins_eau": variete.besoins_eau,
            "image_url": get_image_url(variete)
        },
        "type_evenement": None,
        "details_evenement": None
    }

    if evenement.etape:
        etape = evenement.etape
        data["type_evenement"] = "etape"
        data["details_evenement"] = {
            "id": str(etape.id),
            "nom": etape.nom,
            "description": etape.description,
            "frequence": etape.frequence,
            "delai_apres_plantation": etape.delai_apres_plantation,
            "image_url": get_image_url(etape)
        }

    elif evenement.fertilisation:
        fertilisation = evenement.fertilisation
        data["type_evenement"] = "fertilisation"
        data["details_evenement"] = {
            "id": str(fertilisation.id),
            "jour": fertilisation.jour,
            "type_engrais": fertilisation.type_engrais,
            "dose_ha": fertilisation.dose_ha,
            "mode_application": fertilisation.mode_application or "",
            "image_url": get_image_url(fertilisation, "illustration")
        }

    elif evenement.traitement:
        traitement = evenement.traitement
        produit = traitement.produit
        data["type_evenement"] = "traitement"
        data["details_evenement"] = {
            "id": str(traitement.id),
            "jour": traitement.jour,
            "type_traitement": traitement.type_traitement,
            "cible": traitement.cible,
            "matiere_active": traitement.matiere_active or "",
            "image_url": get_image_url(traitement, "illustration"),
            "produit": {
                "id": str(produit.id) if produit else None,
                "nom_commercial": produit.nom_commercial if produit else "",
                "matiere_active": produit.matiere_active if produit else "",
                "type_produit": produit.type_produit if produit else "",
                "image_url": get_image_url(produit) if produit else None
            } if produit else None
        }

    else:
        data["type_evenement"] = "tache_planifiee"
        data["details_evenement"] = {}

    return data


def envoyer_notification_user(user, message_text, image_url=None, data_payload=None):
    device = FCMDevice.objects.filter(user=user).first()
    if not device:
        print(f"[LOG] Aucun device FCM pour user {user.email}")
        return False, [f"Aucun device FCM enregistré pour l'utilisateur {user.email}"]

    erreurs = []
    notifications_envoyees = 0

    try:
        notif_args = {
            "title": "📢 Alerte Culture",
            "body": message_text,
        }
        if image_url:
            notif_args["image"] = image_url

        notif = Notification(**notif_args)

        message = Message(
            notification=notif,
            token=device.registration_id,
            data={k: str(v) for k, v in data_payload.items()} if data_payload else None,
        )

        response = device.send_message(message)
        notifications_envoyees += 1
        print(f"[LOG] Notification envoyée au device {device.id} de user {user.email} (response: {response})")

    except Exception as e:
        erreurs.append(f"Erreur envoi notification Device {device.id} User {user.email} : {str(e)}")
        print(f"[ERREUR] {str(e)}")

    success = notifications_envoyees > 0
    return success, erreurs if erreurs else None


def envoyer_notifications_culture():
    aujourd_hui = timezone.now().date()
    evenements = CalendrierCulture.objects.filter(
        date_prevue=aujourd_hui,
        alerte_envoyee=False
    ).select_related('parcelle__farm__owner', 'parcelle__variete')

    if not evenements.exists():
        print("Aucune notification à envoyer aujourd'hui.")
        return 0, []

    notifications_envoyees_count = 0
    erreurs_globales = []

    for evenement in evenements:
        message_text = construire_message(evenement)
        farm = evenement.parcelle.farm
        user = farm.owner
        image_url = getattr(evenement.parcelle, 'image_url', None)

        data_payload = construire_data_payload(evenement)
        try:
            with transaction.atomic():
                NotificationLog.objects.create(
                    farm=farm,
                    message=message_text,
                    date_envoi=timezone.now(),
                    canal="app",
                    envoyee=True,
                    data_json=data_payload,
                )
                success, erreurs = envoyer_notification_user(
                    user,
                    message_text,
                    image_url=image_url,
                    data_payload=data_payload
                )
                if success:
                    evenement.alerte_envoyee = True
                    evenement.save()
                    notifications_envoyees_count += 1
                if erreurs:
                    erreurs_globales.extend(erreurs)
        except Exception as e:
            erreurs_globales.append(f"Erreur transaction notification farm {farm.id} : {str(e)}")
    
    return notifications_envoyees_count, erreurs_globales