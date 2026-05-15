import requests
import time

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.management.base import BaseCommand

from players.models import (
    Player,
    Club,
    Season,
    Competition,
    SeasonPlayerStat,
)

LEAGUES = [
    39,  # Premier League
    140,  # La Liga
    135,  # Serie A
    78,  # Bundesliga
    61,  # Ligue 1
]

CURRENT_SEASON = 2023


def parse_rating(value):
    """
    Convierte:
    "7.12" -> Decimal("7.12")
    """
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        return None


class Command(BaseCommand):
    help = "Importar estadísticas de jugadores " "usando /players?id="

    def handle(self, *args, **kwargs):

        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}

        stats_created = 0
        stats_updated = 0
        skipped = 0

        session = requests.Session()
        session.headers.update(headers)

        season_obj = Season.objects.filter(
            name=f"{CURRENT_SEASON}/{CURRENT_SEASON + 1}"
        ).first()

        if not season_obj:

            self.stdout.write(
                self.style.ERROR(
                    f"Temporada "
                    f"{CURRENT_SEASON}/{CURRENT_SEASON + 1} "
                    f"no encontrada"
                )
            )

            return

        players = Player.objects.filter(external_id__isnull=False).order_by("id")

        self.stdout.write(
            self.style.SUCCESS(f"Jugadores encontrados: " f"{players.count()}")
        )

        for index, player in enumerate(players, start=1):

            self.stdout.write(f"\n[{index}/{players.count()}] " f"{player.full_name}")

            url = (
                "https://v3.football.api-sports.io/players"
                f"?id={player.external_id}"
                f"&season={CURRENT_SEASON}"
            )

            try:
                response = session.get(url, timeout=30)

            except requests.exceptions.RequestException as e:

                self.stdout.write(
                    self.style.ERROR(f"Error conexión " f"{player.full_name}: {e}")
                )

                skipped += 1
                continue

            if response.status_code != 200:

                self.stdout.write(
                    self.style.ERROR(
                        f"Error HTTP " f"{player.full_name}: " f"{response.status_code}"
                    )
                )

                skipped += 1
                continue

            try:
                body = response.json()

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Error parseando JSON " f"{player.full_name}: {e}"
                    )
                )

                skipped += 1
                continue

            api_errors = body.get("errors")

            if api_errors:

                self.stdout.write(
                    self.style.WARNING(
                        f"API errors " f"{player.full_name}: " f"{api_errors}"
                    )
                )

                skipped += 1
                continue

            response_data = body.get("response", [])

            if not response_data:

                self.stdout.write(
                    self.style.WARNING(f"Sin estadísticas: " f"{player.full_name}")
                )

                skipped += 1
                continue

            player_data = response_data[0]

            statistics = player_data.get("statistics", [])

            if not statistics:

                self.stdout.write(
                    self.style.WARNING(f"Sin statistics[]: " f"{player.full_name}")
                )

                skipped += 1
                continue

            # ---------------------------------
            # UPDATE PLAYER PROFILE
            # ---------------------------------

            api_player = player_data.get("player", {})

            birth = api_player.get("birth", {})

            if birth.get("date"):
                player.date_of_birth = birth.get("date")

            if api_player.get("photo"):
                player.photo_url = api_player.get("photo")

            if api_player.get("height"):
                try:
                    player.height_cm = int(
                        str(api_player.get("height")).replace("cm", "").strip()
                    )
                except:
                    pass

            if api_player.get("weight"):
                try:
                    player.weight_kg = int(
                        str(api_player.get("weight")).replace("kg", "").strip()
                    )
                except:
                    pass

            player.save()

            # ---------------------------------
            # STATS
            # ---------------------------------

            for stat in statistics:

                league_data = stat.get("league", {})

                league_id = league_data.get("id")

                if league_id not in LEAGUES:
                    continue

                competition = Competition.objects.filter(external_id=league_id).first()

                if not competition:
                    skipped += 1
                    continue

                team_data = stat.get("team", {})

                team_id = team_data.get("id")

                if not team_id:
                    skipped += 1
                    continue

                club = Club.objects.filter(external_id=team_id).first()

                if not club:
                    skipped += 1
                    continue

                games = stat.get("games", {})
                goals = stat.get("goals", {})
                cards = stat.get("cards", {})

                try:

                    _, was_created = SeasonPlayerStat.objects.update_or_create(
                        player=player,
                        season=season_obj,
                        club=club,
                        competition=competition,
                        defaults={
                            "appearances": (games.get("appearences") or 0),
                            "minutes": (games.get("minutes") or 0),
                            "goals": (goals.get("total") or 0),
                            "assists": (goals.get("assists") or 0),
                            "yellow_cards": (cards.get("yellow") or 0),
                            "red_cards": (cards.get("red") or 0),
                            "avg_rating": (parse_rating(games.get("rating"))),
                        },
                    )

                    if was_created:
                        stats_created += 1
                    else:
                        stats_updated += 1

                except Exception as e:

                    self.stdout.write(
                        self.style.WARNING(f"Error stat " f"{player.full_name}: {e}")
                    )

                    skipped += 1

            # IMPORTANTE:
            # Free tier rate limit
            time.sleep(7)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nStats creadas: "
                f"{stats_created}\n"
                f"Stats actualizadas: "
                f"{stats_updated}\n"
                f"Omitidos: "
                f"{skipped}"
            )
        )
