from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Pedidos'

    def ready(self):
        # Importa os signals para que sejam registrados
        import apps.orders.signals  # noqa: F401