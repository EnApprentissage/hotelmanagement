from django.db import transaction
from .models import GlobalVariables

def initialize_global_variables():
    """
    Insère automatiquement les variables globales par défaut
    lors du premier lancement du projet.
    """

    default_variables = [
        # Informations générales de l'hôtel
        {"group": "hotel", "cle": "nom", "valeur": "Hôtel Paradis", "description": "Nom de l'hôtel"},
        {"group": "hotel", "cle": "slogan", "valeur": "Le confort au cœur de la ville", "description": "Slogan de l'hôtel"},
        {"group": "hotel", "cle": "adresse", "valeur": "Avenue du Lac, Bujumbura", "description": "Adresse de l'hôtel"},
        {"group": "hotel", "cle": "telephone", "valeur": "+257 79 123 456", "description": "Téléphone de l'hôtel"},
        {"group": "hotel", "cle": "email", "valeur": "contact@hotelparadis.bi", "description": "Email de contact de l'hôtel"},
        {"group": "hotel", "cle": "devise", "valeur": "BIF", "description": "Devise principale utilisée"},
        {"group": "hotel", "cle": "check_in", "valeur": "12:00", "description": "Heure standard de check-in"},
        {"group": "hotel", "cle": "check_out", "valeur": "11:00", "description": "Heure standard de check-out"},
        {"group": "hotel", "cle": "tva", "valeur": "18", "description": "Taux de TVA appliqué sur les factures (%)"},
        {"group": "hotel", "cle": "site_web", "valeur": "https://hotelparadis.bi", "description": "Site web officiel"},

        # Informations de l’entreprise propriétaire
        {"group": "entreprise", "cle": "nom", "valeur": "NEVIDEC SARL", "description": "Nom de l'entreprise propriétaire"},
        {"group": "entreprise", "cle": "nif", "valeur": "4000123456", "description": "Numéro d'identification fiscale"},
        {"group": "entreprise", "cle": "registre_commerce", "valeur": "RC-BJM-2025-001", "description": "Numéro du registre du commerce"},
        {"group": "entreprise", "cle": "adresse", "valeur": "Quartier Industriel, Bujumbura", "description": "Adresse du siège social"},
        {"group": "entreprise", "cle": "telephone", "valeur": "+257 79 654 321", "description": "Téléphone du siège"},
        {"group": "entreprise", "cle": "email", "valeur": "info@nevidec.bi", "description": "Email professionnel"},
        {"group": "entreprise", "cle": "site_web", "valeur": "https://nevidec.bi", "description": "Site web de l'entreprise"},
        {"group": "entreprise", "cle": "responsable", "valeur": "Augustin Nduwimana", "description": "Nom du responsable principal"},
        {"group": "entreprise", "cle": "copyright", "valeur": "© 2025 NEVIDEC SARL. Tous droits réservés.", "description": "Mention légale sur les documents"},
    ]

    with transaction.atomic():
        for item in default_variables:
            obj, created = GlobalVariables.objects.get_or_create(
                group=item["group"],
                cle=item["cle"],
                defaults={
                    "valeur": item["valeur"],
                    "description": item["description"]
                }
            )
            if created:
                print(f"✅ Ajouté : {item['group']} - {item['cle']}")
            else:
                print(f"⚠️ Déjà existant : {item['group']} - {item['cle']}")
