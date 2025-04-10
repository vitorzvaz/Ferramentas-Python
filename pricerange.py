import pandas as pd
import datetime as dt

hoje = dt.date.today()
dias_atras = 7 * 52
tempo_de_calculo = hoje - dt.timedelta(days = dias_atras)

ativo_objeto = 'VALE3'
dados = pd.read_parquet('./BaseDadosBR/cotacoes.parquet')
dados['data'] = pd.to_datetime(dados['data']).dt.date

dados = dados[['data', 'ticker', 'preco_fechamento_ajustado']]
dados = dados.loc[dados['data'] > tempo_de_calculo]

dados['preço_maximo'] = dados.groupby('ticker')['preco_fechamento_ajustado'].cummax() # get the max price per ticker
dados['preço_minimo'] = dados.groupby('ticker')['preco_fechamento_ajustado'].cummin()

dados['price_range'] = (dados['preco_fechamento_ajustado'] - dados['preço_minimo']) / (dados['preço_maximo'] - dados['preço_minimo'])

print(dados)