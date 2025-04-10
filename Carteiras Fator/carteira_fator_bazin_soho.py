import os
import pandas as pd
from datetime import date, timedelta
from load_data_fintz import dados_fintz
from fazendo_indicador import MakeIndicator

indicadores = ['bazin']
liquidez = 5000000
numero_de_ativos = 14

filtro_data = date.today() - timedelta(7)
filtro_data_2 = date.today() - timedelta(14)


def atualizar_parquets():
    lendo_dados = dados_fintz(caminho_dados='Carteiras Fator\dados')
    lendo_dados.pegar_cotacoes()
    
    os.chdir('..\..')
    
    atualizar_indicadores = MakeIndicator(caminho_dados='Carteiras Fator\dados')
    atualizar_indicadores.volume_mediano()

    os.chdir('..\..')

    atualizar_indicadores.bazin()

    os.chdir('..\..')

#atualizar_parquets()

volume_mediano = pd.read_parquet(r'Carteiras Fator\dados\volume_mediano.parquet')
volume_mediano = volume_mediano.groupby('ticker').last().reset_index()
volume_mediano['data'] = pd.to_datetime(volume_mediano['data']).dt.date
volume_mediano['ticker'] = volume_mediano['ticker'].astype(str)
volume_mediano = volume_mediano[['data', 'ticker', 'valor']]
volume_mediano.columns = ['data', 'ticker', 'volume']
volume_mediano = volume_mediano[volume_mediano['data'] > filtro_data]
volume_mediano = volume_mediano[volume_mediano['volume'] > liquidez]

df_indicadores = []

df_bazin = pd.read_parquet(f'Carteiras Fator\dados\{indicadores[0]}.parquet')
df_bazin = df_bazin.groupby('ticker').last().reset_index()
df_bazin['data'] = pd.to_datetime(df_bazin['data']).dt.date
df_bazin['ticker'] = df_bazin['ticker'].astype(str)
df_bazin['valor'] = df_bazin['valor'].astype(float)
df_bazin = df_bazin[['data', 'ticker', 'valor']]
df_bazin.columns = ['data', 'ticker', f'{indicadores[0]}']
df_bazin = df_bazin[(df_bazin['data'] > filtro_data)]
df_bazin = df_bazin.drop(columns=['data'])

df_portfolio = pd.merge(volume_mediano, df_bazin, how='outer', on='ticker')

df_portfolio = df_portfolio.assign(TICKER_PREFIX = df_portfolio['ticker'].str[:4])
df_portfolio = df_portfolio.loc[df_portfolio.groupby('TICKER_PREFIX')['volume'].idxmax()]
df_portfolio = df_portfolio.drop(columns=['TICKER_PREFIX'])

df_portfolio['RANK_FINAL'] = df_portfolio['bazin'].rank(ascending=True)
df_portfolio['POSITION']  = df_portfolio['RANK_FINAL'].rank(ascending=True)
df_portfolio = df_portfolio[df_portfolio['POSITION'] <= numero_de_ativos]
df_portfolio = df_portfolio.assign(peso = 1/(df_portfolio.groupby('data').transform('size')))
df_portfolio = df_portfolio[['ticker', 'peso']]
df_portfolio.to_excel('bazinportfolio.xlsx')