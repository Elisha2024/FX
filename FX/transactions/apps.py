from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'

    def ready(self):
        """
        Ensure that the signals are imported when the app is ready.
        """
        import transactions.signals
