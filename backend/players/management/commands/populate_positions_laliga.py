from django.core.management.base import BaseCommand
from players.models import Player


class Command(BaseCommand):
    help = "Populate player positions with known La Liga data"

    # Mappeo de jugadores conocidos a sus posiciones basado en data de La Liga
    PLAYER_POSITIONS = {
        "Iñaki Williams": "Delantero",
        "Jan Oblak": "Portero",
        "Juan Musso": "Portero",
        "José Giménez": "Defensa",
        "Nahuel Molina": "Defensa",
        "Aleksa Puric": "Defensa",
        "Gerónimo Spina": "Defensa",
        "Johnny": "Defensa",
        "Matteo Ruggeri": "Defensa",
        "Obed Vargas": "Centrocampista",
        "Taufik": "Centrocampista",
        "Ademola Lookman": "Extremo",
        "Giuliano Simeone": "Centrocampista",
        "Julián Álvarez": "Delantero",
        "Thiago Almada": "Centrocampista",
        "Florian Wirtz": "Centrocampista",
        "Jamal Musiala": "Centrocampista",
        "Jude Bellingham": "Centrocampista",
        "Pedri": "Centrocampista",
        "Gavi": "Centrocampista",
        "Lamine Yamal": "Extremo",
        "Marc-André ter Stegen": "Portero",
        "Pau Cubarsí": "Defensa",
        "Alejandro Garnacho": "Extremo",
        "Endrick": "Delantero",
        "Kobbie Mainoo": "Centrocampista",
        "Giorgi Mamardashvili": "Portero",
        "Sandro Tonali": "Centrocampista",
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Populating player positions..."))
        
        updated = 0
        not_found = 0
        already_set = 0
        
        for alias, position in self.PLAYER_POSITIONS.items():
            try:
                # Find player by alias
                player = Player.objects.filter(alias__icontains=alias.split()[0]).first()
                
                if not player:
                    not_found += 1
                    self.stdout.write(f"  ✗ Not found: {alias}")
                    continue
                
                if player.position and player.position.strip():
                    already_set += 1
                    self.stdout.write(f"  ⊘ Already set: {player.alias} = {player.position}")
                    continue
                
                # Update position
                player.position = position
                player.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ {player.alias} → {position}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error for {alias}: {e}"))
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Complete!\n"
                f"  Updated: {updated}\n"
                f"  Already set: {already_set}\n"
                f"  Not found: {not_found}"
            )
        )
