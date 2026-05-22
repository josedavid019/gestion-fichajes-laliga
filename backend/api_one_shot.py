import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('.env'))
key = os.getenv('APISPORTS_FOOTBALL_KEY')
print('KEY', bool(key), repr(key))
name = 'Kylian Mbappé'
params = {'search': name, 'season': 2024}
url = 'https://v3.football.api-sports.io/players'
r = requests.get(url, headers={'x-apisports-key': key}, params=params, timeout=20)
print('status', r.status_code)
print(r.text[:4000])
