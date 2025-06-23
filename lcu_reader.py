# lcu_reader.py
import requests
import json
from requests.auth import HTTPBasicAuth

def get_custom_lobby_players():
    try:
        response = requests.get(
            'https://127.0.0.1:2999/liveclientdata/playerlist',
            verify=False  # Ignora certificado SSL
        )
        if response.status_code == 200:
            return [player['summonerName'] for player in response.json()]
        else:
            return []
    except Exception as e:
        print("Erro ao acessar o cliente do LoL:", e)
        return []
