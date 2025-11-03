from django.apps import AppConfig

class ParametrageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "parametrage"

    def ready(self):
        # Import ici pour éviter les problèmes de circular import
        from .init_global_variables import initialize_global_variables
        try:
            initialize_global_variables()
        except Exception as e:
            print(f"⚠️ Erreur lors de l'initialisation des variables globales : {e}")
