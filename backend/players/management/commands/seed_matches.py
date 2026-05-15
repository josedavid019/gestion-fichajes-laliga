import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Club, Competition, Season, Match

LEAGUES = [
    39,  # Premier League
    140,  # La Liga
    135,  # Serie A
    78,  # Bundesliga
    61,  # Ligue 1
]
CURRENT_SEASON = 2025


class Command(BaseCommand):
    help = "Importar partidos desde API-Football"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        season_obj = Season.objects.filter(
            name=f"{CURRENT_SEASON}/{CURRENT_SEASON + 1}"
        ).first()

        if not season_obj:
            self.stdout.write(
                self.style.ERROR(
                    f"Temporada {CURRENT_SEASON}/{CURRENT_SEASON + 1} no encontrada en DB"
                )
            )
            return

        created = 0
        updated = 0
        skipped = 0

        for league_id in LEAGUES:
            competition = Competition.objects.filter(external_id=league_id).first()
            if not competition:
                self.stdout.write(
                    self.style.WARNING(
                        f"Competición no encontrada: league_id={league_id}"
                    )
                )
                skipped += 1
                continue

            url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={CURRENT_SEASON}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(f"Error liga {league_id}: {response.status_code}")
                )
                continue

            data = response.json().get("response", [])
            self.stdout.write(f"Liga {league_id}: {len(data)} partidos recibidos")

            for item in data:
                fixture = item.get("fixture", {})
                teams = item.get("teams", {})
                goals = item.get("goals", {})

                fixture_id = fixture.get("id")
                fixture_date = fixture.get("date")
                status_short = fixture.get("status", {}).get("short", "NS")

                if not fixture_id or not fixture_date:
                    skipped += 1
                    continue

                home_id = teams.get("home", {}).get("id")
                away_id = teams.get("away", {}).get("id")

                if not home_id or not away_id:
                    skipped += 1
                    continue

                home_club = Club.objects.filter(external_id=home_id).first()
                away_club = Club.objects.filter(external_id=away_id).first()

                if not home_club or not away_club:
                    skipped += 1
                    continue

                status = Match.STATUS_MAP.get(status_short, "scheduled")

                try:
                    _, was_created = Match.objects.update_or_create(
                        external_id=fixture_id,
                        defaults={
                            "competition": competition,
                            "season": season_obj,
                            "home_club": home_club,
                            "away_club": away_club,
                            "match_date": fixture_date,
                            "home_score": goals.get("home"),
                            "away_score": goals.get("away"),
                            "status": status,
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Error partido {home_club} vs {away_club}: {e}"
                        )
                    )
                    skipped += 1

            time.sleep(0.3)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nPartidos creados: {created} | actualizados: {updated} | omitidos: {skipped}"
            )
        )
