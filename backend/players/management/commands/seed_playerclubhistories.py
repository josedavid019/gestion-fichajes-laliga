import requests
import time
from datetime import date
from django.conf import settings
from django.core.management.base import BaseCommand
from players.models import Player, Club, Season, PlayerClubHistory


def resolve_season(transfer_date_str):
    """Dado '2017-08-03' devuelve la Season correspondiente."""
    try:
        d = date.fromisoformat(transfer_date_str)
        # Si el mes es julio o posterior, la temporada empieza ese año
        season_start = d.year if d.month >= 7 else d.year - 1
        season_name = f"{season_start}/{season_start + 1}"
        return Season.objects.filter(name=season_name).first()
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = "Importar historial de clubes de jugadores desde API-Football (/transfers)"

    def handle(self, *args, **kwargs):
        headers = {"x-apisports-key": settings.APISPORTS_FOOTBALL_KEY}
        players = Player.objects.filter(external_id__isnull=False)
        total = players.count()
        created = 0
        skipped = 0

        self.stdout.write(f"Procesando transferencias de {total} jugadores...")

        # Limpiar is_current antes de reasignar
        PlayerClubHistory.objects.filter(is_current=True).update(is_current=False)

        for i, player in enumerate(players, 1):
            url = f"https://v3.football.api-sports.io/transfers?player={player.external_id}"

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
                    skipped += 1
                    continue

                transfers = data[0].get("transfers", [])
                if not transfers:
                    skipped += 1
                    continue

                # Ordenar por fecha para saber cuál es el más reciente
                transfers_sorted = sorted(
                    [t for t in transfers if t.get("date")],
                    key=lambda t: t["date"],
                )

                for idx, transfer in enumerate(transfers_sorted):
                    transfer_date = transfer.get("date")
                    transfer_type = transfer.get("type", "")
                    team_in = transfer.get("teams", {}).get("in", {})
                    team_out = transfer.get("teams", {}).get("out", {})

                    club_in_id = team_in.get("id")
                    if not club_in_id or not transfer_date:
                        skipped += 1
                        continue

                    club = Club.objects.filter(external_id=club_in_id).first()
                    if not club:
                        skipped += 1
                        continue

                    season = resolve_season(transfer_date)
                    is_loan = "loan" in transfer_type.lower()
                    is_current = idx == len(transfers_sorted) - 1

                    # date_to es el date_from de la siguiente transferencia
                    if idx < len(transfers_sorted) - 1:
                        date_to = transfers_sorted[idx + 1].get("date")
                    else:
                        date_to = None

                    try:
                        _, was_created = PlayerClubHistory.objects.get_or_create(
                            player=player,
                            club=club,
                            date_from=transfer_date,
                            defaults={
                                "season": season,
                                "date_to": date_to,
                                "loan": is_loan,
                                "transfer_fee": transfer_type or "",
                                "is_current": is_current,
                            },
                        )
                        if was_created:
                            created += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Error registro {player} → {club}: {e}"
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
            self.style.SUCCESS(f"Registros creados: {created} | omitidos: {skipped}")
        )
