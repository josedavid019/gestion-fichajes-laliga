import os
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from players.models import Player
from vision.api_enricher import APIFootballClient

print('total', Player.objects.count())
print('with value', Player.objects.exclude(market_value_eur__isnull=True).count())
print('sample', list(Player.objects.exclude(market_value_eur__isnull=True).values_list('alias', 'market_value_eur')[:5]))

client = APIFootballClient()
print('client key', bool(client.api_key))

p = Player.objects.filter(market_value_eur__isnull=True).exclude(alias='').first()
print('test player', p.alias if p else None, p.first_name if p else None, p.last_name if p else None)

if p:
    print('search result', client.search_player(f"{p.first_name} {p.last_name}", p.current_club.name if p.current_club else None))
