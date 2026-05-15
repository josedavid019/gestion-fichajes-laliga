import requests
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from players.models import (
    Player,
    Club,
    PlayerPosition,
)


def parse_height(value):
    """
    '175 cm' -> 175
    """
    try:
        return int(str(value).replace("cm", "").strip())
    except (ValueError, AttributeError):
        return None


def parse_weight(value):
    """
    '68 kg' -> 68
    """
    try:
        return int(str(value).replace("kg", "").strip())
    except (ValueError, AttributeError):
        return None


class Command(BaseCommand):
    help = "Importar jugadores usando /players/squads"

    def handle(self, *args, **kwargs):

        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}

        players_created = 0
        players_updated = 0
        positions_created = 0
        skipped = 0

        clubs = Club.objects.filter(external_id__isnull=False).order_by("id")

        self.stdout.write(self.style.SUCCESS(f"Clubes encontrados: {clubs.count()}"))

        session = requests.Session()
        session.headers.update(headers)

        for club in clubs:

            self.stdout.write(
                f"\nProcesando club: " f"{club.name} " f"(API ID: {club.external_id})"
            )

            url = (
                "https://v3.football.api-sports.io/players/squads"
                f"?team={club.external_id}"
            )

            try:
                response = session.get(url, timeout=30)

            except requests.exceptions.RequestException as e:

                self.stdout.write(
                    self.style.ERROR(f"Error conexión " f"{club.name}: {e}")
                )

                skipped += 1
                continue

            if response.status_code != 200:

                self.stdout.write(
                    self.style.ERROR(
                        f"Error HTTP " f"{club.name}: " f"{response.status_code}"
                    )
                )

                skipped += 1
                continue

            try:
                body = response.json()

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(f"Error parseando JSON " f"{club.name}: {e}")
                )

                skipped += 1
                continue

            api_errors = body.get("errors")

            if api_errors:

                self.stdout.write(
                    self.style.WARNING(f"API errors " f"{club.name}: " f"{api_errors}")
                )

            results = body.get("response", [])

            if not results:

                self.stdout.write(
                    self.style.WARNING(f"Sin jugadores para " f"{club.name}")
                )

                skipped += 1
                continue

            squad_data = results[0]

            players = squad_data.get("players", [])

            self.stdout.write(
                self.style.SUCCESS(f"  {len(players)} jugadores encontrados")
            )

            for player_data in players:

                external_id = player_data.get("id")

                if not external_id:
                    skipped += 1
                    continue

                try:

                    first_name = player_data.get("firstname") or ""

                    last_name = player_data.get("lastname") or ""

                    full_name = (f"{first_name} {last_name}").strip()

                    if not full_name:
                        full_name = player_data.get("name") or ""

                    player, was_created = Player.objects.update_or_create(
                        external_id=external_id,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "alias": (player_data.get("name") or full_name),
                            "full_name": full_name,
                            "photo_url": (player_data.get("photo") or ""),
                            "shirt_number": (player_data.get("number")),
                            "height_cm": parse_height(player_data.get("height")),
                            "weight_kg": parse_weight(player_data.get("weight")),
                            "current_club": club,
                        },
                    )

                    if was_created:
                        players_created += 1
                    else:
                        players_updated += 1

                    # -------------------------
                    # POSICIÓN DEL JUGADOR
                    # -------------------------

                    position_name = player_data.get("position")

                    if position_name:

                        _, pos_created = PlayerPosition.objects.update_or_create(
                            player=player,
                            position=position_name,
                            defaults={"is_primary": True},
                        )

                        if pos_created:
                            positions_created += 1

                except Exception as e:

                    name = player_data.get("name") or f"id={external_id}"

                    self.stdout.write(
                        self.style.WARNING(f"Error guardando jugador " f"'{name}': {e}")
                    )

                    skipped += 1

            # IMPORTANTE:
            # Free plan ≈ 10 requests/min
            time.sleep(7)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nJugadores creados: "
                f"{players_created}\n"
                f"Jugadores actualizados: "
                f"{players_updated}\n"
                f"Posiciones creadas: "
                f"{positions_created}\n"
                f"Omitidos: "
                f"{skipped}"
            )
        )
