import os
import pandas as pd
from datetime import date, timedelta
from load_data_fintz import dados_fintz
from fazendo_indicador import MakeIndicator

indicadores = ['ValorDeMercado', 'EBITDA_EV', 'momento_12_meses']
liquidez = 2000000
numero_de_ativos = 14

filtro_data = date.today() - timedelta(7)
filtro_data_2 = date.today() - timedelta(14)


def atualizar_parquets():
    lendo_dados = dados_fintz(caminho_dados='Carteiras Fator\dados')
    lendo_dados.pegar_cotacoes()

    lista_indicadores = indicadores[:2]
    for indicador in lista_indicadores:
        lendo_dados.pegando_arquivo_contabil(indicadores=True, nome_dado=indicador)

    os.chdir('..\..')

    atualizar_indicadores = MakeIndicator(caminho_dados='Carteiras Fator\dados')
    atualizar_indicadores.fazer_indicador_momento(meses=12)
    atualizar_indicadores.volume_mediano()

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
for indicador in indicadores:
    lendo_indicador = pd.read_parquet(f'Carteiras Fator\dados\{indicador}.parquet')
    lendo_indicador = lendo_indicador.groupby('ticker').last().reset_index()
    lendo_indicador['data'] = pd.to_datetime(lendo_indicador['data']).dt.date
    lendo_indicador['ticker'] = lendo_indicador['ticker'].astype(str)
    lendo_indicador['valor'] = lendo_indicador['valor'].astype(float)
    lendo_indicador = lendo_indicador[['data', 'ticker', 'valor']]
    lendo_indicador.columns = ['data', 'ticker', f'{indicador}']
    lendo_indicador = lendo_indicador[(lendo_indicador['data'] > filtro_data)]
    lendo_indicador = lendo_indicador.drop(columns=['data'])
    df_indicadores.append(lendo_indicador)

for df in df_indicadores:
    volume_mediano = pd.merge(volume_mediano, df, how='outer', on='ticker')

volume_mediano = volume_mediano.dropna()
df_portfolio = volume_mediano.copy()

df_portfolio = df_portfolio.assign(TICKER_PREFIX = df_portfolio['ticker'].str[:4])
df_portfolio = df_portfolio.loc[df_portfolio.groupby('TICKER_PREFIX')['volume'].idxmax()]
df_portfolio = df_portfolio.drop(columns=['TICKER_PREFIX'])

df_portfolio['RANK_FINAL'] = 0

df_portfolio['RANK_VALOR_DE_MERCADO'] = df_portfolio['ValorDeMercado'].rank(ascending=True)
df_portfolio['RANK_EBITDA_EV'] = df_portfolio['EBITDA_EV'].rank(ascending=False)
df_portfolio['RANK_MOMENTO_12_MESES'] = df_portfolio['momento_12_meses'].rank(ascending=False)

df_portfolio['RANK_FINAL'] = df_portfolio['RANK_VALOR_DE_MERCADO'] + df_portfolio['RANK_EBITDA_EV'] + df_portfolio['RANK_MOMENTO_12_MESES']
df_portfolio['POSITION']  = df_portfolio['RANK_FINAL'].rank(ascending=True)
df_portfolio = df_portfolio[df_portfolio['POSITION'] <= numero_de_ativos]
df_portfolio = df_portfolio.assign(peso = 1/(df_portfolio.groupby('data').transform('size')))
df_portfolio = df_portfolio[['ticker', 'peso']]
df_portfolio.to_excel('k7_lixeiras_voadoras.xlsx')