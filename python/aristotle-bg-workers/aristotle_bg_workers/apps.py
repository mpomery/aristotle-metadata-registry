from aristotle_mdr.apps import AristotleExtensionBaseConfig

class AristotleBackgroundWorkersConfig(AristotleExtensionBaseConfig):
    name = 'aristotle_bg_workers'
    verbose_name = "Aristotle Background Workers"
    description = "Adds celery background task support"

    def ready(self):
        # Load worker signals
        from aristotle_bg_workers import signals
