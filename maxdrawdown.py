import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.ticker as mtick
import matplotlib.dates as mdate

hoje = dt.date.today()
dias_atras = 365 * 3
tempo_de_calculo = hoje - dt.timedelta(days = dias_atras)

ativo_objeto = 'VALE3'
dados = pd.read_parquet('./BaseDadosBR/cotacoes.parquet')
dados_ibov = pd.read_parquet('./BaseDadosBR/ibov.parquet')
dados['data'] = pd.to_datetime(dados['data']).dt.date
dados_ibov['data'] = pd.to_datetime(dados_ibov['data']).dt.date

dados = dados[['data', 'ticker', 'preco_fechamento_ajustado']]
dados = dados.loc[dados['ticker'] == ativo_objeto]
dados = dados.loc[dados['data'] > tempo_de_calculo]
dados = dados.set_index('data')

preço_maximo = dados['preco_fechamento_ajustado'].cummax()
drawdown = (dados['preco_fechamento_ajustado'])/preço_maximo - 1

fig, ax = plt.subplots(figsize = (12,6))
ax.plot(drawdown.index, drawdown)
ax.set_title(f'Max Drawdown {ativo_objeto} - Últimos {dias_atras} dias')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.xaxis.set_major_locator(mdate.MonthLocator(interval = 1))

plt.show()