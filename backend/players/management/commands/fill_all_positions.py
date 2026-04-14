from django.core.management.base import BaseCommand
from players.models import Player
import os

class Command(BaseCommand):
    help = "Fill all player positions from comprehensive La Liga database"

    # Base de datos completa de jugadores La Liga con posiciones
    LA_LIGA_DATABASE = {
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
        "Brahim Díaz": "Extremo",
        "Dani Ceballos": "Centrocampista",
        
        # FC Barcelona
        "Marc-André ter Stegen": "Portero",
        "Iñaki Peña": "Portero",
        "Sergi Roberto": "Defensa",
        "Héctor Bellerín": "Defensa",
        "Alejandro Balde": "Defensa",
        "João Cancelo": "Defensa",
        "Ronald Araújo": "Defensa",
        "Jules Koundé": "Defensa",
        "Frenkie de Jong": "Centrocampista",
        "Pedri": "Centrocampista",
        "Gavi": "Centrocampista",
        "Sergio Busquets": "Centrocampista",
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
        "Obed Vargas": "Centrocampista",
        "Taufik": "Centrocampista",
        "Giuliano Simeone": "Centrocampista",
        "Thomas Lemar": "Centrocampista",
        "Rodrigo De Paul": "Centrocampista",
        "Axel Witsel": "Centrocampista",
        "Johnny Hirving Lozano": "Defensa",
        "Julián Álvarez": "Delantero",
        "Thiago Almada": "Centrocampista",
        "Antoine Griezmann": "Extremo",
        "Ademola Lookman": "Extremo",
        "Ángel Correa": "Extremo",
        
        # Athletic Club
        "Iñaki Williams": "Delantero",
        "Iker Castilla": "Portero",
        "Unai Simón": "Portero",
        "Óscar de Marcos": "Defensa",
        "Inigo Martinez": "Defensa",
        "Yuri": "Defensa",
        "Aihen Muñoz": "Defensa",
        
        # Villarreal
        "Gerónimo Rulli": "Portero",
        "Santi Comesaña": "Centrocampista",
        
        # Otros jugadores clave
        "Nicolás González": "Extremo",
        "Dávid Hancko": "Defensa",
        "Alexander Sørloth": "Delantero",
        "Antoine Griezmann": "Extremo",
        "Clément Lenglet": "Defensa",
        "Marcus Rashford": "Extremo",
        "Wojciech Szczęsny": "Portero",
        "Ilias Kostis": "Extremo",
        "Dimitrios Stamatakis": "Defensa",
        "Flavien Boyomo": "Defensa",
        "Valentin Rosier": "Defensa",
        "Ante Budimir": "Delantero",
        "Marko Dmitrović": "Portero",
        "Adama Timera": "Centrocampista",
        "Charles Pickel": "Defensa",
        "Omar El Hilali": "Centrocampista",
        "Clemens Riedel": "Defensa",
        "Tyrhys Dolan": "Extremo",
        "Cyril Ngonge": "Extremo",
        "Leandro Cabrera": "Defensa",
        "Diego Kochen": "Defensa",
        "Roony Bardagji": "Extremo",
        "Raphinha": "Extremo",
        "Ronald Araújo": "Defensa",
        "Jules Koundé": "Defensa",
        "Frenkie de Jong": "Centrocampista",
        "Andreas Christensen": "Defensa",
        "Jiří Letáček": "Portero",
        "Pavel Čech": "Portero",
        
        # Más jugadores detectados en salida anterior
        "Abde Rebbach": "Extremo",
        "Abdelkabir Abqar": "Defensa",
        "Abdul Mumin": "Defensa",
        "Abu Kamara": "Delantero",
        "Adnan Januzaj": "Extremo",
        "Akor Adams": "Delantero",
        "Alan Matturro": "Defensa",
        "Albert Niculaesei": "Defensa",
        "Alexandre Alemão": "Centrocampista",
        "Alexis Sánchez": "Extremo",
        "Alfonso Espino": "Defensa",
        "Allan Nyom": "Defensa",
        "Andrei Rațiu": "Defensa",
        "André Almeida": "Portero",
        "André Silva": "Portero",
        "Arda Guler": "Extremo",
        "Arnaut Danjuma": "Extremo",
        "Augusto Batalla": "Portero",
        "Aurélien Tchouameni": "Centrocampista",
        "Azzedine Ounahi": "Centrocampista",
        "Baptiste Santamaria": "Centrocampista",
        "Batista Mendy": "Centrocampista",
        "Bema Sina": "Defensa",
        "Calebe": "Defensa",
        "Carl Starfelt": "Defensa",
        "Carlos Benavidez": "Centrocampista",
        "Chidera Ejuke": "Extremo",
        "Claudio Echeverri": "Centrocampista",
        "Cristhian Stuani": "Delantero",
        "Dakonam Djené": "Defensa",
        "Daley Blind": "Defensa",
        "David Affengruber": "Defensa",
        "David Carmo": "Defensa",
        "Dimitri Foulquier": "Defensa",
        "Djibril Sow": "Centrocampista",
        "Domingos Duarte": "Defensa",
        "Donny van de Beek": "Centrocampista",
        "Eray Cömert": "Defensa",
        "Eric Bailly": "Centrocampista",
        "Facundo Garcés": "Defensa",
        "Federico Redondo": "Centrocampista",
        "Federico Viñas": "Centrocampista",
        "Filip Ugrinic": "Centrocampista",
        "Franco Cervi": "Defensa",
        "Franco Mastantuono": "Delantero",
        "Fábio Cardoso": "Defensa",
        "Gabriel Suazo": "Defensa",
        "Grady Diangana": "Extremo",
        "Gregoire Swiderski": "Delantero",
        "Guido Rodríguez": "Centrocampista",
        "Haissem Hassan": "Centrocampista",
        "Horaţiu Moldovan": "Portero",
        "Ibrahim Diabaté": "Centrocampista",
        "Ilaix Moriba": "Centrocampista",
        "Ilias Akhomach": "Extremo",
        "Ilyas Chaira": "Defensa",
        "Ionuț Radu": "Portero",
        "Ismael Bekhoucha": "Defensa",
        "Iván Balliu": "Defensa",
        "Jeremy Toljan": "Defensa",
        "Jones El-Abdellaoui": "Extremo",
        "Joseph Aidoo": "Defensa",
        "Jozhua Vertrouwd": "Defensa",
        "Karl Etta Eyong": "Centrocampista",
        "Kervin Arriaga": "Centrocampista",
        "Kwasi Sibo": "Extremo",
        "Largie Ramazani": "Extremo",
        "Leander Dendoncker": "Defensa",
        "Loren Luchino": "Delantero",
        "Lucas Boyé": "Delantero",
        "Lucas Cepeda": "Defensa",
        "Lucien Agoume": "Centrocampista",
        "Luis Vázquez": "Delantero",
        "Luiz Felipe": "Defensa",
        "Léo Pétrot": "Portero",
        "Marcão": "Defensa",
        "Mariano Díaz": "Delantero",
        "Martim Neto": "Extremo",
        "Martin Satriano": "Delantero",
        "Martín Krug": "Delantero",
        "Matias Moreno": "Defensa",
        "Maty Ryan": "Portero",
        "Matías Dituro": "Portero",
        "Matías Vecino": "Centrocampista",
        "Mauro Arambarri": "Centrocampista",
        "Mihajlo Ristić": "Defensa",
        "Mouctar Diakhaby": "Defensa",
        "Mykyta Alexandrov": "Extremo",
        "Neal Maupay": "Delantero",
        "Nemanja Gudelj": "Centrocampista",
        "Nianzou Kouassi": "Defensa",
        "Nicolas Fonseca": "Defensa",
        "Nobel Mendy": "Centrocampista",
        "Odisseas Vlachodimos": "Portero",
        "Ovie Ejaria": "Centrocampista",
        "Papa Ba": "Extremo",
        "Pathé Ciss": "Centrocampista",
        "Rahim Alhassane": "Extremo",
        "Randy Ntekja": "Defensa",
        "Renzo Saravia": "Defensa",
        "Ruben Vargas": "Extremo",
        "Sebastián Boselli": "Defensa",
        "Stole Dimitrievski": "Portero",
        "Tai Abed": "Defensa",
        "Thiago Borbas": "Centrocampista",
        "Thierry Correia": "Defensa",
        "Trent Alexander-Arnold": "Defensa",
        "Ugo Raghouber": "Defensa",
        "Umar Sadiq": "Delantero",
        "Veljko Birmančević": "Extremo",
        "Viktor Tsyhankov": "Extremo",
        "Ville Koski": "Portero",
        "Vinicius Junior": "Extremo",
        "Vitor Reis": "Defensa",
        "Vladyslav Krapyvtsov": "Extremo",
        "Vladyslav Vanat": "Centrocampista",
        "Williot Swedberg": "Extremo",
        "Yassin Tallal": "Centrocampista",
        "Zaid Romero": "Defensa",
        "Óscar Trejo": "Defensa",
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Filling all player positions from database..."))
        
        players_without_position = Player.objects.filter(position="").order_by('alias')
        total = players_without_position.count()
        
        self.stdout.write(
            self.style.WARNING(f"\nFound {total} players without position\n")
        )
        
        updated = 0
        not_found = []
        
        for i, player in enumerate(players_without_position, 1):
            # Búsqueda exacta
            position = self.LA_LIGA_DATABASE.get(player.alias)
            
            # Si no encuentra, intenta búsqueda parcial (por primer nombre)
            if not position:
                first_name = player.alias.split()[0] if player.alias else ""
                for db_name, pos in self.LA_LIGA_DATABASE.items():
                    if first_name.lower() in db_name.lower() or db_name.lower() in player.alias.lower():
                        position = pos
                        break
            
            if position:
                player.position = position
                player.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"[{i}/{total}] ✓ {player.alias} → {position}")
                )
            else:
                not_found.append(player.alias)
                self.stdout.write(
                    self.style.WARNING(f"[{i}/{total}] ⚠ {player.alias}: not in database")
                )
        
        remaining = Player.objects.filter(position="").count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Complete!\n"
                f"  Updated: {updated}\n"
                f"  Not found in database: {len(not_found)}\n"
                f"  Still pending: {remaining}"
            )
        )
        
        if not_found and len(not_found) <= 20:
            self.stdout.write("\nPlayers not found:")
            for name in not_found:
                self.stdout.write(f"  - {name}")

