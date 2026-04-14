import os
from datetime import datetime
import requests
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from players.models import Country, Club, Player, Competition, Season


class Command(BaseCommand):
    help = "Sync players from multiple competitions via football-data.org API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-key",
            type=str,
            help="Football Data API Key",
        )

    def handle(self, *args, **options):
        api_key = options.get("api_key") or os.getenv("FOOTBALL_DATA_API_KEY")

        if not api_key:
            self.stdout.write(
                self.style.ERROR(
                    "API key required. Set FOOTBALL_DATA_API_KEY env var or pass --api-key"
                )
            )
            return

        headers = {"X-Auth-Token": api_key}

        # Multiple competitions: PD (La Liga), SA (Serie A), PL (Premier League), BL1 (Bundesliga), FL1 (Ligue 1)
        competitions = ["PD", "SA", "PL", "BL1", "FL1"]

        total_players = 0

        for comp_code in competitions:
            self.stdout.write(
                self.style.SUCCESS(f"\n=== Syncing {comp_code} ===")
            )

            try:
                # Get competition
                comp_response = requests.get(
                    f"https://api.football-data.org/v4/competitions/{comp_code}",
                    headers=headers,
                )
                comp_response.raise_for_status()
                comp_data = comp_response.json()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching competition {comp_code}: {e}"))
                continue

            # Create/Update Competition
            competition, _ = Competition.objects.get_or_create(
                name=comp_data["name"],
                defaults={"type": "league"},
            )
            self.stdout.write(self.style.SUCCESS(f"Competition: {competition.name}"))

            # Create/Update Season
            try:
                season_data = comp_data["currentSeason"]
                season, _ = Season.objects.get_or_create(
                    name=season_data["id"],
                    defaults={
                        "year_start": season_data["startDate"][:4],
                        "year_end": season_data["endDate"][:4],
                        "is_current": True,
                    },
                )
            except:
                self.stdout.write(self.style.WARNING(f"Could not get season for {comp_code}"))
                continue

            # Get country for this competition
            try:
                country_code = comp_data.get("area", {}).get("code", "")
                country_name = comp_data.get("area", {}).get("name", "")

                country, _ = Country.objects.get_or_create(
                    code=country_code if country_code else "XX",
                    defaults={"name": country_name},
                )
            except:
                country = None

            # Get teams
            try:
                teams_response = requests.get(
                    f"https://api.football-data.org/v4/competitions/{comp_code}/teams",
                    headers=headers,
                )
                teams_response.raise_for_status()
                teams_data = teams_response.json()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fetching teams for {comp_code}: {e}"))
                continue

            self.stdout.write(
                self.style.SUCCESS(f"Fetching {len(teams_data['teams'])} teams...")
            )

            for team_data in teams_data["teams"]:
                try:
                    # Create/Update Club
                    club, created = Club.objects.get_or_create(
                        name=team_data["name"],
                        defaults={
                            "country": country,
                            "city": team_data.get("area", {}).get("name", ""),
                            "logo_url": team_data.get("crest", ""),
                        },
                    )

                    if not created:
                        club.city = team_data.get("area", {}).get("name", "")
                        club.logo_url = team_data.get("crest", "")
                        club.save()

                    self.stdout.write(f"  {club.name}", ending="")

                    # Get team squad
                    try:
                        squad_response = requests.get(
                            f"https://api.football-data.org/v4/teams/{team_data['id']}",
                            headers=headers,
                        )
                        squad_response.raise_for_status()
                        squad_data = squad_response.json()
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f" - Error fetching squad"))
                        continue

                    players_added = 0
                    for player_data in squad_data.get("squad", []):
                        try:
                            # Get or create nationality
                            nationality_name = player_data.get("nationality", "Unknown")
                            country_code = (
                                nationality_name[:2].upper()
                                if nationality_name and len(nationality_name) >= 2
                                else "XX"
                            )

                            nationality, _ = Country.objects.get_or_create(
                                code=country_code,
                                defaults={"name": nationality_name},
                            )

                            # Create/Update Player
                            name_parts = player_data.get("name", "Unknown").split()
                            first_name = name_parts[0] if name_parts else "Unknown"
                            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

                            player, created = Player.objects.get_or_create(
                                external_id=str(player_data["id"]),
                                defaults={
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "alias": player_data.get("name", ""),
                                    "position": player_data.get("position", ""),
                                    "nationality": nationality,
                                    "current_club": club,
                                    "shirt_number": player_data.get("shirtNumber"),
                                    "date_of_birth": player_data.get("dateOfBirth"),
                                    "status": "active",
                                },
                            )

                            if not created:
                                player.current_club = club
                                player.position = player_data.get("position", "")
                                player.shirt_number = player_data.get("shirtNumber")
                                player.save()

                            players_added += 1

                        except IntegrityError:
                            pass
                        except Exception as e:
                            pass

                    self.stdout.write(f" - {players_added} players")
                    total_players += players_added

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing team: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Sync completed!\n  Total new players: {total_players}"
            )
        )
