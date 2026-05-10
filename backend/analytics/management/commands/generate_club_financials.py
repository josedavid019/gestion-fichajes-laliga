import random
from django.core.management.base import BaseCommand
from analytics.models import ClubFinancial
from players.models import Club, Season


class Command(BaseCommand):
    help = "Generate sample club financial data"

    def handle(self, *args, **options):
        clubs = Club.objects.all()
        seasons = Season.objects.all()

        if not seasons.exists():
            self.stdout.write(self.style.ERROR("No seasons found"))
            return

        season = seasons.first()
        created = 0

        for club in clubs:
            # Skip if already has financial data
            if ClubFinancial.objects.filter(club=club, season=season).exists():
                continue

            # Generate realistic financial data based on club size
            # La Liga clubs have revenues between 50M and 800M euros
            revenue = random.randint(50000000, 800000000)

            # Wage bill is typically 50-70% of revenue
            wage_bill_ratio = random.uniform(0.5, 0.7)
            wage_bill = int(revenue * wage_bill_ratio)

            # Transfer income/expenses
            transfer_income = random.randint(0, 200000000)
            transfer_expenditure = random.randint(0, 200000000)

            # Net debt (can be positive or negative)
            net_debt = random.randint(-100000000, 200000000)

            ClubFinancial.objects.create(
                club=club,
                season=season,
                total_revenue_eur=revenue,
                wage_bill_eur=wage_bill,
                transfer_income_eur=transfer_income,
                transfer_expenditure_eur=transfer_expenditure,
                net_debt_eur=net_debt,
                wage_to_revenue_ratio=wage_bill / revenue if revenue > 0 else 0,
            )

            created += 1
            self.stdout.write(
                f"✓ {club.name}: Revenue €{revenue:,.0f}M, Wage bill €{wage_bill:,.0f}M"
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Generated financial data for {created} clubs")
        )