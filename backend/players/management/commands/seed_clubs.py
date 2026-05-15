import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from players.models import Club, Country

LEAGUES = [
    140,  # La Liga
    39,  # Premier League
    135,  # Serie A
    78,  # Bundesliga
    61,  # Ligue 1
]

# Intentar desde la más reciente hasta la más vieja
SEASONS_TO_TRY = [2025, 2024, 2023, 2022, 2021]


class Command(BaseCommand):
    help = "Importar clubes desde API-Football"

    def handle(self, *args, **kwargs):

        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}

        created = 0
        updated = 0
        skipped = 0

        for league_id in LEAGUES:

            data = []
            used_season = None

            # Intentar seasons hasta encontrar una válida
            for season in SEASONS_TO_TRY:

                url = (
                    f"https://v3.football.api-sports.io/teams"
                    f"?league={league_id}&season={season}"
                )

                try:
                    response = requests.get(url, headers=headers, timeout=30)

                except requests.exceptions.RequestException as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error de conexión liga "
                            f"{league_id} season {season}: {e}"
                        )
                    )
                    continue

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error HTTP liga "
                            f"{league_id} season {season}: "
                            f"{response.status_code}"
                        )
                    )
                    continue

                try:
                    json_data = response.json()

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error parseando JSON liga "
                            f"{league_id} season {season}: {e}"
                        )
                    )
                    continue

                # Mostrar errores reales de la API
                api_errors = json_data.get("errors")

                if api_errors:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Liga {league_id} season {season}: " f"{api_errors}"
                        )
                    )

                temp_data = json_data.get("response", [])

                # Si encontró clubes, usar esta season
                if temp_data:
                    data = temp_data
                    used_season = season
                    break

            # Si no encontró nada en ninguna season
            if not data:
                self.stdout.write(
                    self.style.ERROR(
                        f"No se encontraron clubes " f"para liga {league_id}"
                    )
                )
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"Liga {league_id}: "
                    f"{len(data)} clubes recibidos "
                    f"(season {used_season})"
                )
            )

            # Guardar clubes
            for item in data:

                team = item.get("team", {})
                venue = item.get("venue", {})

                team_id = team.get("id")
                team_name = team.get("name")

                if not team_id or not team_name:
                    skipped += 1
                    continue

                # Buscar país
                country = None
                country_name = team.get("country")

                if country_name:
                    country = Country.objects.filter(name__iexact=country_name).first()

                    if not country:
                        self.stdout.write(
                            self.style.WARNING(
                                f"País no encontrado: "
                                f"'{country_name}' "
                                f"(club: {team_name})"
                            )
                        )

                try:

                    _, was_created = Club.objects.update_or_create(
                        external_id=team_id,
                        defaults={
                            "name": team_name,
                            "country": country,
                            "city": venue.get("city") or "",
                            "founded_year": team.get("founded"),
                            "stadium": venue.get("name") or "",
                            "stadium_capacity": venue.get("capacity"),
                            "stadium_image": venue.get("image") or "",
                            "logo_url": team.get("logo") or "",
                            "code": team.get("code") or "",
                            "national": team.get("national", False),
                        },
                    )

                    if was_created:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Error guardando club "
                            f"'{team_name}' "
                            f"(id={team_id}): {e}"
                        )
                    )

                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nClubes creados: {created} | "
                f"actualizados: {updated} | "
                f"omitidos: {skipped}"
            )
        )
