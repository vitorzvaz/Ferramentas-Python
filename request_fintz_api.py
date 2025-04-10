import os
import pandas as pd
import requests
import urllib.request

os.chdir(r"C:\Users\vitor\Desktop\Ferramentas Python\BaseDadosBR")

HEADERS = {
    'accept': 'application/json',
    'X-API-Key': os.getenv("API_FINTZ")}

URL_BASE = 'https://api.fintz.com.br'

response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/cotacoes/historico/arquivos?classe=ACOES&preencher=true', headers=HEADERS)

link_download = (response.json())['link']
urllib.request.urlretrieve(link_download, f"cotacoes.parquet")

df = pd.read_parquet('cotacoes.parquet')
print(df)