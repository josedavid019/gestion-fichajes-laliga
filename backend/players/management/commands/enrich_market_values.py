import os
import requests
from django.core.management.base import BaseCommand
from players.models import Player


class Command(BaseCommand):
    help = "Enrich player data with market values from transfermarkt-api"

    def handle(self, *args, **options):
        """
        Fetches market values from transfermarkt-api and updates player records
        API endpoint: https://transfermarkt-api.com/ (requires API key)
        """
        api_key = os.getenv("TRANSFERMARKT_API_KEY")
        
        if not api_key:
            self.stdout.write(
                self.style.WARNING(
                    "TRANSFERMARKT_API_KEY not set. Using alternative method..."
                )
            )
            self.enrich_from_alternative_source()
            return

        self.enrich_from_transfermarkt(api_key)

    def enrich_from_transfermarkt(self, api_key):
        """Fetch from Transfermarkt API"""
        headers = {
            "accept": "application/json",
            "x-acsrftoken": api_key,
        }
        
        players = Player.objects.filter(market_value_eur__isnull=True)
        updated = 0
        
        for player in players[:100]:  # Limit to avoid rate limiting
            try:
                # Search for player
                search_url = f"https://transfermarkt-api.com/players/search"
                params = {
                    "query": f"{player.first_name} {player.last_name}",
                }
                
                response = requests.get(search_url, headers=headers, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        player_data = data[0]
                        if "market_value" in player_data:
                            market_value = player_data["market_value"]
                            player.market_value_eur = market_value
                            player.save()
                            updated += 1
                            self.stdout.write(f"Updated {player.alias}: €{market_value}")
                        
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error fetching {player.alias}: {e}"))
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Updated {updated} players with market values")
        )

    def enrich_from_alternative_source(self):
        """
        Alternative method: Use free API or manual data entry
        You can replace this with any public API that provides market values
        """
        self.stdout.write(
            self.style.WARNING(
                "Please provide market values through one of these methods:\n"
                "1. Set TRANSFERMARKT_API_KEY environment variable\n"
                "2. Manually update player market_value_eur in the database\n"
                "3. Use another API that provides market values"
            )
        )
