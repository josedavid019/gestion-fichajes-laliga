import requests
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Player, Injury, Suspension


class Command(BaseCommand):
    help = "Importar lesiones y suspensiones desde API-Football (/sidelined)"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        players = Player.objects.filter(external_id__isnull=False)
        total = players.count()
        injuries_created = 0
        suspensions_created = 0
        skipped = 0

        self.stdout.write(f"Procesando sidelined de {total} jugadores...")

        for i, player in enumerate(players, 1):
            url = f"https://v3.football.api-sports.io/sidelined?player={player.external_id}"

            try:
                response = requests.get(url, headers=headers)

                if response.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[{i}/{total}] HTTP {response.status_code} — {player}"
                        )
                    )
                    skipped += 1
                    continue

                data = response.json().get("response", [])
                if not data:
                    continue

                for entry in data:
                    entry_type = entry.get("type", "")
                    reason = entry.get("reason", "")
                    start_date = entry.get("start")
                    end_date = entry.get("end")

                    if not start_date or not entry_type:
                        skipped += 1
                        continue

                    if end_date in ("Unknown", "", None):
                        end_date = None

                    if entry_type == "Suspension":
                        try:
                            _, was_created = Suspension.objects.get_or_create(
                                player=player,
                                reason=reason or entry_type,
                                start_date=start_date,
                                defaults={
                                    "end_date": end_date,
                                    "matches_suspended": None,
                                },
                            )
                            if was_created:
                                suspensions_created += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  Error suspensión {player} ({start_date}): {e}"
                                )
                            )
                            skipped += 1

                    else:
                        # Cualquier otro type lo tratamos como Injury
                        try:
                            _, was_created = Injury.objects.get_or_create(
                                player=player,
                                injury_type=entry_type,
                                start_date=start_date,
                                defaults={
                                    "end_date": end_date,
                                    "description": reason or "",
                                },
                            )
                            if was_created:
                                injuries_created += 1

                        except Exception as e:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  Error lesión {player} ({start_date}): {e}"
                                )
                            )
                            skipped += 1

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
                f"Lesiones creadas: {injuries_created} | "
                f"Suspensiones creadas: {suspensions_created} | "
                f"Omitidos: {skipped}"
            )
        )
