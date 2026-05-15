from datetime import date
from django.core.management.base import BaseCommand
from players.models import Season


class Command(BaseCommand):
    help = "Crear temporadas localmente sin depender de la API"

    # Ajusta este rango según lo que necesites
    FIRST_SEASON = 1966  # 1966 → temporada 1966/1967
    LAST_SEASON = 2025  # 2025 → temporada 2025/2026

    def handle(self, *args, **kwargs):
        current_year = date.today().year  # 2026
        # La temporada actual arranca el año anterior al año en curso
        current_start_year = current_year - 1  # 2025

        created = 0
        updated = 0

        # Quitar is_current de todas antes de asignar la nueva
        Season.objects.filter(is_current=True).update(is_current=False)

        for start_year in range(self.FIRST_SEASON, self.LAST_SEASON + 1):
            end_year = start_year + 1
            season_name = f"{start_year}/{end_year}"
            start_date = date(start_year, 8, 1)
            end_date = date(end_year, 6, 30)
            is_current = start_year == current_start_year

            try:
                _, was_created = Season.objects.update_or_create(
                    name=season_name,
                    defaults={
                        "start_date": start_date,
                        "end_date": end_date,
                        "is_current": is_current,
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Error temporada {season_name}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Temporadas creadas: {created} | actualizadas: {updated}"
            )
        )
