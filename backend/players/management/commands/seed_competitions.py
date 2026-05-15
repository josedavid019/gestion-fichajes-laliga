import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Competition, Country


class Command(BaseCommand):
    help = "Importar competiciones desde API-Football"

    def handle(self, *args, **kwargs):
        url = "https://v3.football.api-sports.io/leagues"
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Error API: {response.status_code}"))
            return

        data = response.json().get("response", [])
        created = 0
        updated = 0
        skipped = 0

        for item in data:
            league = item.get("league", {})
            country_data = item.get("country", {})
            seasons = item.get("seasons", [])

            league_id = league.get("id")
            league_name = league.get("name")

            if not league_id or not league_name:
                skipped += 1
                continue

            # Buscar country por name, más confiable que por code
            country = None
            country_name = country_data.get("name")
            if country_name:
                country = Country.objects.filter(name__iexact=country_name).first()
                if not country:
                    self.stdout.write(
                        self.style.WARNING(
                            f"País no encontrado: '{country_name}' (league: {league_name})"
                        )
                    )

            current_season = next(
                (s for s in seasons if s.get("current") is True), None
            )

            try:
                _, was_created = Competition.objects.update_or_create(
                    external_id=league_id,
                    defaults={
                        "name": league_name,
                        "country": country,
                        "type": league.get("type", "").lower(),
                        "code": league.get("code", ""),
                        "logo_url": league.get("logo", ""),
                        "is_current": current_season is not None,
                        "season_year": (
                            current_season.get("year") if current_season else None
                        ),
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Error en league '{league_name}' (id={league_id}): {e}"
                    )
                )
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Competiciones creadas: {created} | actualizadas: {updated} | omitidas: {skipped}"
            )
        )
