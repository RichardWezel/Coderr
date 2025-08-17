from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'

    def ready(self):
        # Importiert die Signal-Handler, sobald die App “ready” ist
        import auth_app.api.signals  # noqa: F401