import os
from decimal import Decimal
import requests
from django.core.management.base import BaseCommand
from players.models import Player
from vision.api_enricher import APIFootballClient


class Command(BaseCommand):
    help = "Enrich player data with market values from transfermarkt-api or API Football"

    def handle(self, *args, **options):
        """
        Fetches market values from external APIs and updates player records.
        """
        transfermarkt_key = os.getenv("TRANSFERMARKT_API_KEY")
        football_key = os.getenv("APISPORTS_FOOTBALL_KEY") or os.getenv(
            "RAPIDAPI_FOOTBALL_KEY"
        )

        if transfermarkt_key:
            self.enrich_from_transfermarkt(transfermarkt_key)

        if football_key:
            self.enrich_from_api_football(football_key)
        elif not transfermarkt_key:
            self.stdout.write(
                self.style.WARNING(
                    "No market value API key found. Set TRANSFERMARKT_API_KEY or APISPORTS_FOOTBALL_KEY."
                )
            )
            self.enrich_from_alternative_source()

    def enrich_from_transfermarkt(self, api_key):
        """Fetch market values from Transfermarkt API"""
        headers = {
            "accept": "application/json",
            "x-acsrftoken": api_key,
        }

        players = Player.objects.filter(market_value_eur__isnull=True)
        updated = 0

        for player in players[:100]:
            try:
                search_url = "https://transfermarkt-api.com/players/search"
                params = {
                    "query": f"{player.first_name} {player.last_name}",
                }
                response = requests.get(
                    search_url, headers=headers, params=params, timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        player_data = data[0]
                        market_value = player_data.get("market_value")
                        if market_value is not None:
                            player.market_value_eur = Decimal(str(market_value))
                            player.save(update_fields=["market_value_eur"])
                            updated += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Updated {player.alias or player.full_name}: €{player.market_value_eur:,.0f}"
                                )
                            )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Error fetching {player.alias or player.full_name}: {e}"
                    )
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Updated {updated} players with Transfermarkt market values"
            )
        )

    def enrich_from_api_football(self, api_key):
        """Fetch market values from API Football"""
        football_client = APIFootballClient(api_key)
        players = Player.objects.filter(market_value_eur__isnull=True)
        updated = 0

        for player in players[:100]:
            try:
                search_name = f"{player.first_name} {player.last_name}".strip()
                if not search_name:
                    search_name = player.alias or player.full_name

                team_name = player.current_club.name if player.current_club else None
                team_id = (
                    player.current_club.external_id
                    if player.current_club and player.current_club.external_id
                    else None
                )
                football_data = football_client.search_player(
                    search_name, team_name=team_name, team_id=team_id
                )

                if football_data and football_data.get("market_value_eur") is not None:
                    player.market_value_eur = Decimal(
                        str(football_data["market_value_eur"])
                    )
                    if football_data.get("external_id") and not player.external_id:
                        player.external_id = football_data["external_id"]
                    player.save(update_fields=["market_value_eur", "external_id"])
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated {player.alias or player.full_name}: €{player.market_value_eur:,.0f}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"No market value found for {player.alias or player.full_name}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"Error fetching {player.alias or player.full_name}: {e}"
                    )
                )
                continue

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Updated {updated} players with API Football market values"
            )
        )

    def enrich_from_alternative_source(self):
        """
        Alternative method: Use manual data entry or another market value source.
        """
        self.stdout.write(
            self.style.WARNING(
                "Please provide market values through one of these methods:\n"
                "1. Set TRANSFERMARKT_API_KEY environment variable\n"
                "2. Set APISPORTS_FOOTBALL_KEY environment variable\n"
                "3. Manually update player.market_value_eur in the database"
            )
        )
