from django.core.management.base import BaseCommand
from django.db import connection
from players.models import Player
import requests
from datetime import date
import os


class Command(BaseCommand):
    help = "Fill player positions from RapidAPI Football Data"

    def handle(self, *args, **options):
        """
        Fills missing player positions using free-api-live-football-data RapidAPI endpoint
        """
        self.stdout.write(self.style.SUCCESS("Starting position fill..."))

        # RapidAPI credentials
        RAPIDAPI_HOST = "free-api-live-football-data.p.rapidapi.com"
        RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
        
        if not RAPIDAPI_KEY:
            self.stdout.write(
                self.style.ERROR(
                    "❌ RAPIDAPI_KEY not found in environment variables.\n"
                    "Set it with: $env:RAPIDAPI_KEY = 'your_key_here'\n"
                    "Get it from: https://rapidapi.com/api-sports/api/api-football"
                )
            )
            return

        headers = {
            "X-Rapidapi-Key": RAPIDAPI_KEY,
            "X-Rapidapi-Host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        
        players_updated = 0
        players_without_position = Player.objects.filter(position="")
        total = players_without_position.count()
        
        self.stdout.write(
            self.style.WARNING(f"Found {total} players without position\n")
        )
        
        try:
            for i, player in enumerate(players_without_position[:50], 1):  # Limit to avoid rate limits
                try:
                    # Search for player using the free API endpoint
                    search_url = f"https://{RAPIDAPI_HOST}/football-players-search"
                    querystring = {"search": player.alias}
                    
                    response = requests.get(search_url, headers=headers, params=querystring, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Parse response - adjust based on actual API response structure
                        if isinstance(data, dict) and "response" in data:
                            results = data.get("response", [])
                        elif isinstance(data, list):
                            results = data
                        else:
                            results = []
                        
                        if results:
                            # Try to find the best match
                            player_data = results[0]
                            position = player_data.get("position") or player_data.get("pos")
                            
                            if position:
                                player.position = position
                                player.save()
                                players_updated += 1
                                self.stdout.write(
                                    self.style.SUCCESS(f"  [{i}/{total}] ✓ {player.alias}: {position}")
                                )
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f"  [{i}/{total}] ⚠ {player.alias}: no position in response")
                                )
                        else:
                            self.stdout.write(
                                self.style.WARNING(f"  [{i}/{total}] ⚠ {player.alias}: not found")
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"  [{i}/{total}] ✗ {player.alias}: API error {response.status_code}")
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  [{i}/{total}] ✗ {player.alias}: {str(e)[:60]}")
                    )
                    continue

            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Updated {players_updated} players with positions")
            )
            self.stdout.write(
                self.style.WARNING(
                    f"Remaining: {total - players_updated} players still need positions"
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
