import os
import random
from django.core.management.base import BaseCommand
from players.models import Player


class Command(BaseCommand):
    help = "Generate sample market values for testing (La Liga players)"

    def handle(self, *args, **options):
        """
        Assigns random market values to players for testing purposes
        La Liga realistic value ranges
        """
        players = Player.objects.filter(market_value_eur__isnull=True)
        
        # Define value ranges based on position and tier
        position_ranges = {
            "Goalkeeper": (2000000, 25000000),
            "Defender": (3000000, 80000000),
            "Midfielder": (5000000, 120000000),
            "Forward": (8000000, 200000000),
        }
        
        updated = 0
        
        for player in players:
            try:
                # Get position or use default
                position = player.position or "Midfielder"
                
                # Find matching range
                min_val, max_val = position_ranges.get(position, (2000000, 50000000))
                
                # Generate realistic value (weighted towards lower values)
                market_value = random.randint(min_val, max_val)
                
                # Add some variation
                if random.random() < 0.3:  # 30% chance of higher value
                    market_value = int(market_value * random.uniform(1.5, 2.5))
                
                player.market_value_eur = market_value
                player.save()
                updated += 1
                
                self.stdout.write(
                    f"✓ {player.alias} ({position}): €{market_value:,.0f}"
                )
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {player.alias}: {e}"))
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Generated market values for {updated} players")
        )
