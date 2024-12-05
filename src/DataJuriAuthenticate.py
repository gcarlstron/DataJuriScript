import http.client
import json
import os
from base64 import b64encode
from dotenv import load_dotenv

def basic_auth(client: str, secret: str) -> str:
    token = b64encode(f"{client}:{secret}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


class DataJuriAuthenticate:
    def __init__(self, host: str):
        self.host = host

    def get_token(self) -> str:
        load_dotenv()
        client = os.getenv('CLIENT')
        secret = os.getenv('SECRET')
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')

        payload = f'grant_type=password&username={username}&password={password}'

        conn = http.client.HTTPSConnection(self.host)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': basic_auth(client, secret)
        }
        conn.request("POST", "/oauth/token", payload, headers)
        res = conn.getresponse()
        data = res.read().decode()
        datajson = json.loads(data)
        return datajson.get('access_token')
