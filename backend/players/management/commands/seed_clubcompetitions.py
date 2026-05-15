import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Club, Competition, Season, ClubCompetition

LEAGUES = [
    39,  # Premier League
    140,  # La Liga
    135,  # Serie A
    78,  # Bundesliga
    61,  # Ligue 1
]
CURRENT_SEASON = 2025


class Command(BaseCommand):
    help = "Importar relaciones club-competición-temporada desde API-Football"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        created = 0
        skipped = 0

        for league_id in LEAGUES:
            # Buscar Competition y Season en DB
            competition = Competition.objects.filter(external_id=league_id).first()
            if not competition:
                self.stdout.write(
                    self.style.WARNING(
                        f"Competición no encontrada en DB: league_id={league_id}"
                    )
                )
                skipped += 1
                continue

            season = Season.objects.filter(
                name=f"{CURRENT_SEASON}/{CURRENT_SEASON + 1}"
            ).first()
            if not season:
                self.stdout.write(
                    self.style.WARNING(
                        f"Temporada no encontrada en DB: {CURRENT_SEASON}/{CURRENT_SEASON + 1}"
                    )
                )
                skipped += 1
                continue

            url = f"https://v3.football.api-sports.io/standings?league={league_id}&season={CURRENT_SEASON}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"Error liga {league_id}: {response.status_code}")
                )
                continue

            data = response.json().get("response", [])
            if not data:
                self.stdout.write(
                    self.style.WARNING(f"Sin datos para liga {league_id}")
                )
                continue

            # standings viene como lista de grupos, cada grupo tiene lista de equipos
            standings = data[0].get("league", {}).get("standings", [])

            for group in standings:
                for entry in group:
                    team_id = entry.get("team", {}).get("id")
                    if not team_id:
                        skipped += 1
                        continue

                    club = Club.objects.filter(external_id=team_id).first()
                    if not club:
                        team_name = entry.get("team", {}).get("name", f"id={team_id}")
                        self.stdout.write(
                            self.style.WARNING(
                                f"Club no encontrado en DB: '{team_name}'"
                            )
                        )
                        skipped += 1
                        continue

                    try:
                        _, was_created = ClubCompetition.objects.get_or_create(
                            club=club,
                            competition=competition,
                            season=season,
                        )
                        if was_created:
                            created += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"Error con club '{club.name}': {e}")
                        )
                        skipped += 1

            self.stdout.write(f"Liga {league_id} procesada.")

        self.stdout.write(
            self.style.SUCCESS(
                f"ClubCompetition creados: {created} | omitidos: {skipped}"
            )
        )
