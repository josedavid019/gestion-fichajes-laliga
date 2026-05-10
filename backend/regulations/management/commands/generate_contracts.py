import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from regulations.models import Contract
from players.models import Player, Club


class Command(BaseCommand):
    help = "Generate sample contracts for players"

    def handle(self, *args, **options):
        players = Player.objects.all()
        clubs = Club.objects.all()

        created = 0
        today = date.today()

        for player in players:
            # Skip if already has active contract
            if Contract.objects.filter(player=player, status="active").exists():
                continue

            # Use current club or random club
            club = player.current_club or random.choice(clubs)

            # Generate contract dates
            years_remaining = random.randint(1, 5)
            date_start = today - timedelta(days=random.randint(0, 365))
            date_end = date_start + timedelta(days=years_remaining * 365)

            # Generate salary based on position and market value
            base_salary = 50000  # Minimum salary

            if player.market_value_eur:
                # Salary is roughly 1-5% of market value annually
                market_value = float(player.market_value_eur)
                salary_percentage = random.uniform(0.01, 0.05)
                base_salary = int(market_value * salary_percentage)

            # Position bonuses
            position = player.position or "MF"
            if position in ["FW", "Forward"]:
                base_salary = int(base_salary * 1.2)
            elif position in ["MF", "Midfielder"]:
                base_salary = int(base_salary * 1.1)

            # Add some randomness
            annual_salary = int(base_salary * random.uniform(0.8, 1.5))

            Contract.objects.create(
                player=player,
                club=club,
                status="active",
                date_start=date_start,
                date_end=date_end,
                annual_salary_eur=annual_salary,
            )

            created += 1
            self.stdout.write(
                f"✓ {player.alias or player.first_name}: €{annual_salary:,.0f}/year until {date_end}"
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Generated contracts for {created} players")
        )