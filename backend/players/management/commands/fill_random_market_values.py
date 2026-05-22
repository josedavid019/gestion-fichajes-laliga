import random
from django.core.management.base import BaseCommand
from players.models import Player


class Command(BaseCommand):
    help = 'Fill random market values for all players between 1M and 20M EUR'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min',
            type=int,
            default=1000000,
            help='Minimum market value in EUR (default: 1000000)'
        )
        parser.add_argument(
            '--max',
            type=int,
            default=20000000,
            help='Maximum market value in EUR (default: 20000000)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Override existing market values'
        )

    def handle(self, *args, **options):
        min_value = options['min']
        max_value = options['max']
        force = options['force']

        players = Player.objects.all()
        total = players.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('No players found'))
            return

        updated = 0
        skipped = 0

        for i, player in enumerate(players, 1):
            try:
                player_id = player.id
                self.stdout.write(f"[{i}/{total}] ID {player_id}...", ending=" ")

                if player.market_value_eur and not force:
                    self.stdout.write(self.style.WARNING("SKIP"))
                    skipped += 1
                    continue

                # Assign random value
                random_value = random.randint(min_value, max_value)
                player.market_value_eur = random_value
                player.save()
                updated += 1

                self.stdout.write(
                    self.style.SUCCESS(f"OK - {random_value:,}")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"ERROR - {str(e)[:30]}"))

        self.stdout.write(self.style.SUCCESS(f"\nCompleted:"))
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Total:   {total}")
