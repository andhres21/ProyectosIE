from django.apps import AppConfig

class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'

    def ready(self):
        # Importar los filtros personalizados
        import gestion.templatetags.custom_filters
