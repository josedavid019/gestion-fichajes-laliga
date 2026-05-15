import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Match, Player, PlayerMatchStat


class Command(BaseCommand):
    help = "Importar estadísticas de jugadores por partido desde API-Football"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}

        # Solo partidos terminados y con external_id
        matches = Match.objects.filter(
            status="finished",
            external_id__isnull=False,
        )
        total = matches.count()
        created = 0
        updated = 0
        skipped = 0

        self.stdout.write(f"Procesando {total} partidos terminados...")

        for i, match in enumerate(matches, 1):
            url = f"https://v3.football.api-sports.io/fixtures/players?fixture={match.external_id}"

            try:
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{i}/{total}] HTTP {response.status_code} — match id={match.external_id}"
                        )
                    )
                    skipped += 1
                    continue

                data = response.json().get("response", [])
                if not data:
                    skipped += 1
                    continue

                # Response tiene dos entradas: home team y away team
                for team_entry in data:
                    players = team_entry.get("players", [])

                    for player_entry in players:
                        player_data = player_entry.get("player", {})
                        stats_list = player_entry.get("statistics", [])

                        external_id = player_data.get("id")
                        if not external_id or not stats_list:
                            skipped += 1
                            continue

                        player = Player.objects.filter(external_id=external_id).first()
                        if not player:
                            skipped += 1
                            continue

                        stat = stats_list[0]
                        games = stat.get("games", {})
                        goals = stat.get("goals", {})
                        cards = stat.get("cards", {})

                        try:
                            _, was_created = PlayerMatchStat.objects.update_or_create(
                                player=player,
                                match=match,
                                defaults={
                                    "goals": goals.get("total") or 0,
                                    "assists": goals.get("assists") or 0,
                                    "minutes_played": games.get("minutes") or 0,
                                    "yellow_cards": cards.get("yellow") or 0,
                                    "red_cards": cards.get("red") or 0,
                                },
                            )
                            if was_created:
                                created += 1
                            else:
                                updated += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  Error stat {player} — match {match.external_id}: {e}"
                                )
                            )
                            skipped += 1

                if i % 20 == 0:
                    self.stdout.write(f"  [{i}/{total}] partidos procesados...")

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"[{i}/{total}] Error match id={match.external_id}: {e}"
                    )
                )
                skipped += 1

            time.sleep(0.5)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nStats creadas: {created} | actualizadas: {updated} | omitidas: {skipped}"
            )
        )
