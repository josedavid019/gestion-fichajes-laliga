import random
from django.core.management.base import BaseCommand
from players.models import Player, Season, Club, Competition, SeasonPlayerStat


class Command(BaseCommand):
    help = "Generate sample season statistics for players"

    def handle(self, *args, **options):
        # Get all players, seasons, clubs
        players = Player.objects.all()
        seasons = Season.objects.all()
        clubs = Club.objects.all()
        competitions = Competition.objects.all()

        if not seasons.exists():
            self.stdout.write(self.style.ERROR("No seasons found"))
            return

        if not competitions.exists():
            self.stdout.write(self.style.ERROR("No competitions found"))
            return

        # Use the first competition (La Liga)
        competition = competitions.first()
        season = seasons.first()

        created = 0
        for player in players:
            # Skip if already has stats
            if SeasonPlayerStat.objects.filter(player=player, season=season).exists():
                continue

            # Use current club or random club
            club = player.current_club or random.choice(clubs)

            # Generate realistic stats based on position
            position = player.position or "MF"

            if position in ["GK", "Goalkeeper"]:
                appearances = random.randint(10, 38)
                minutes = appearances * random.randint(85, 95)
                goals = random.randint(0, 2)
                assists = random.randint(0, 1)
                yellow_cards = random.randint(0, 3)
                red_cards = random.randint(0, 1)
                avg_rating = round(random.uniform(6.0, 7.5), 2)
            elif position in ["DF", "Defender"]:
                appearances = random.randint(15, 38)
                minutes = appearances * random.randint(70, 90)
                goals = random.randint(0, 5)
                assists = random.randint(0, 3)
                yellow_cards = random.randint(1, 8)
                red_cards = random.randint(0, 2)
                avg_rating = round(random.uniform(6.2, 7.8), 2)
            elif position in ["MF", "Midfielder"]:
                appearances = random.randint(20, 38)
                minutes = appearances * random.randint(60, 85)
                goals = random.randint(1, 12)
                assists = random.randint(2, 15)
                yellow_cards = random.randint(2, 10)
                red_cards = random.randint(0, 1)
                avg_rating = round(random.uniform(6.5, 8.2), 2)
            else:  # Forward
                appearances = random.randint(15, 38)
                minutes = appearances * random.randint(50, 75)
                goals = random.randint(5, 25)
                assists = random.randint(1, 10)
                yellow_cards = random.randint(1, 6)
                red_cards = random.randint(0, 1)
                avg_rating = round(random.uniform(6.8, 8.5), 2)

            # Create stat record
            SeasonPlayerStat.objects.create(
                player=player,
                season=season,
                club=club,
                competition=competition,
                appearances=appearances,
                minutes=minutes,
                goals=goals,
                assists=assists,
                yellow_cards=yellow_cards,
                red_cards=red_cards,
                avg_rating=avg_rating,
            )

            created += 1
            self.stdout.write(
                f"✓ {player.alias or player.first_name}: {appearances} apps, {goals}G {assists}A"
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Generated stats for {created} players")
        )