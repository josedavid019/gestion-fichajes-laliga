import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Player, PlayerPosition, PlayerNationality, Country


class Command(BaseCommand):
    help = "Importar posiciones y nacionalidades de jugadores desde API-Football"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        players = Player.objects.filter(external_id__isnull=False)
        total = players.count()
        positions_created = 0
        nationalities_created = 0
        skipped = 0

        self.stdout.write(f"Procesando {total} jugadores...")

        for i, player in enumerate(players, 1):
            url = f"https://v3.football.api-sports.io/players/profiles?player={player.external_id}"

            try:
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{i}/{total}] Error HTTP {response.status_code} — {player}"
                        )
                    )
                    skipped += 1
                    continue

                data = response.json().get("response", [])
                if not data:
                    skipped += 1
                    continue

                player_data = data[0].get("player", {})

                # --- PlayerPosition ---
                position = player_data.get("position")
                if position:
                    _, was_created = PlayerPosition.objects.get_or_create(
                        player=player,
                        position=position,
                        defaults={"is_primary": True},
                    )
                    if was_created:
                        positions_created += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"[{i}/{total}] Sin posición — {player}")
                    )

                # --- PlayerNationality ---
                nationality_name = player_data.get("nationality")
                if nationality_name:
                    country = Country.objects.filter(
                        name__iexact=nationality_name
                    ).first()
                    if country:
                        _, was_created = PlayerNationality.objects.get_or_create(
                            player=player,
                            country=country,
                            defaults={"is_primary": True},
                        )
                        if was_created:
                            nationalities_created += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"[{i}/{total}] País no encontrado: '{nationality_name}' — {player}"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"[{i}/{total}] Sin nacionalidad — {player}")
                    )

                if i % 50 == 0:
                    self.stdout.write(f"  [{i}/{total}] procesados...")

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"[{i}/{total}] Error con {player}: {e}")
                )
                skipped += 1

            time.sleep(0.5)

        self.stdout.write(
            self.style.SUCCESS(
                f"Posiciones creadas: {positions_created} | "
                f"Nacionalidades creadas: {nationalities_created} | "
                f"Omitidos: {skipped}"
            )
        )
