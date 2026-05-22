from django.core.management.base import BaseCommand
from predictions.train_model import main


class Command(BaseCommand):
    help = 'Entrena el modelo ML para prediccion de valor de mercado'

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS('Iniciando entrenamiento del modelo...')
            )
            ml_model = main()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Modelo entrenado exitosamente (ID: {ml_model.id})'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )

