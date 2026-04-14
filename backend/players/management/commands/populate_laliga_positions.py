from django.core.management.base import BaseCommand
from players.models import Player
import json

class Command(BaseCommand):
    help = "Populate player positions from La Liga dataset"

    # Datos completos de jugadores La Liga con posiciones
    LA_LIGA_POSITIONS = {
        # Real Madrid
        "Thibaut Courtois": "Portero",
        "Andriy Lunin": "Portero",
        "Éder Militão": "Defensa",
        "David Alaba": "Defensa",
        "Antonio Rüdiger": "Defensa",
        "Nacho Fernández": "Defensa",
        "Lucas Vázquez": "Defensa",
        "Ferland Mendy": "Defensa",
        "Federico Valverde": "Centrocampista",
        "Toni Kroos": "Centrocampista",
        "Jude Bellingham": "Centrocampista",
        "Luka Modric": "Centrocampista",
        "Eduardo Camavinga": "Centrocampista",
        "Vinícius Júnior": "Extremo",
        "Kylian Mbappé": "Delantero",
        "Rodrygo Goes": "Extremo",
        
        # FC Barcelona
        "Marc-André ter Stegen": "Portero",
        "Iñaki Peña": "Portero",
        "Sergi Roberto": "Defensa",
        "Gerard Piqué": "Defensa",
        "Albiol": "Defensa",
        "Héctor Bellerín": "Defensa",
        "Alejandro Balde": "Defensa",
        "João Cancelo": "Defensa",
        "Ronald Araújo": "Defensa",
        "Jules Koundé": "Defensa",
        "Frenkie de Jong": "Centrocampista",
        "Pedri": "Centrocampista",
        "Gavi": "Centrocampista",
        "Busquets": "Centrocampista",
        "Raphinha": "Extremo",
        "Robert Lewandowski": "Delantero",
        "Lamine Yamal": "Extremo",
        "Ferran Torres": "Extremo",
        
        # Atlético Madrid
        "Jan Oblak": "Portero",
        "Juan Musso": "Portero",
        "José Giménez": "Defensa",
        "Reinildo Mandava": "Defensa",
        "Nahuel Molina": "Defensa",
        "Aleksa Puric": "Defensa",
        "Gerónimo Spina": "Defensa",
        "Matteo Ruggeri": "Defensa",
        "Jorge Franco Fragela": "Defensa",
        "Javier Moreno": "Defensa",
        "Obed Vargas": "Centrocampista",
        "Taufik": "Centrocampista",
        "Giuliano Simeone": "Centrocampista",
        "Thomas Lemar": "Centrocampista",
        "Rodrigo De Paul": "Centrocampista",
        "Axel Witsel": "Centrocampista",
        "Johnny Hirving Lozano": "Defensa",
        "José María Giménez": "Defensa",
        "Julián Álvarez": "Delantero",
        "Thiago Almada": "Centrocampista",
        "Antonio Griezmann": "Extremo",
        "Ademola Lookman": "Extremo",
        
        # Athletic Club
        "Iñaki Williams": "Delantero",
        "Iker Castilla": "Portero",
        "Unai Simón": "Portero",
        
        # Villarreal
        "Geronimo Rulli": "Portero",
        "Santi Comesaña": "Centrocampista",
        
        # Otros jugadores mencionados
        "Antoine Griezmann": "Extremo",
        "Clément Lenglet": "Defensa",
        "Alexander Sørloth": "Delantero",
        "James Maddison": "Centrocampista",
        "Mohamed Salah": "Extremo",
        "Erling Haaland": "Delantero",
        "Mason Mount": "Centrocampista",
        "Jamal Musiala": "Centrocampista",
        "Florian Wirtz": "Centrocampista",
        "Kobbie Mainoo": "Centrocampista",
        "Alejandro Garnacho": "Extremo",
        "Marcus Rashford": "Extremo",
        "Endrick": "Delantero",
        "Giorgi Mamardashvili": "Portero",
        "Sandro Tonali": "Centrocampista",
        "Pau Cubarsí": "Defensa",
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Populating player positions from La Liga data..."))
        
        updated = 0
        not_found = 0
        already_set = 0
        
        for name, position in self.LA_LIGA_POSITIONS.items():
            try:
                # Try exact match first
                player = Player.objects.filter(alias=name, position="").first()
                
                # If not found, try partial match
                if not player:
                    player = Player.objects.filter(alias__icontains=name.split()[0], position="").first()
                
                if not player:
                    not_found += 1
                    continue
                
                if player.position and player.position.strip():
                    already_set += 1
                    continue
                
                # Update position
                player.position = position
                player.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ {player.alias} → {position}"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Error for {name}: {e}"))
        
        remaining = Player.objects.filter(position="").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Complete!\n"
                f"  Updated: {updated}\n"
                f"  Already set: {already_set}\n"
                f"  Not found: {not_found}\n"
                f"  Still pending: {remaining}"
            )
        )
