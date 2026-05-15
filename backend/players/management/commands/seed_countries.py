import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from players.models import Country


class Command(BaseCommand):
    help = "Importar países desde API-Football"

    def handle(self, *args, **kwargs):
        url = "https://v3.football.api-sports.io/countries"
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Error API: {response.status_code}"))
            return

        data = response.json()
        created = 0
        updated = 0

        for item in data.get("response", []):
            name = item.get("name")
            code = item.get("code")
            flag = item.get("flag")

            if not name:
                continue

            try:
                _, was_created = Country.objects.update_or_create(
                    name=name,
                    defaults={
                        "code": code or "",
                        "flag_url": flag or "",
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error con país '{name}': {e}"))

        self.stdout.write(
            self.style.SUCCESS(f"Creados: {created} | Actualizados: {updated}")
        )
