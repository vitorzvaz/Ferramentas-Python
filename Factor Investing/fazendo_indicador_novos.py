import pandas as pd
import os
import numpy as np
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm

#A COLUNA COM O INDICADOR TEM QUE SE CHAMAR "valor"

class MakeIndicator():

    def __init__(self, caminho_dados):

        os.chdir(caminho_dados)

    def jurik_moving_average_proporcao(self, jma_curta, jma_longa, phase, power):
        
        phaseRatio = 0
        def nz(x, val=0.0):
            return val if pd.isnull(x) else x

        data = {
            'data': pd.date_range(start='2010-01-01', end='2024-07-19', freq='D')
        }
        df = pd.DataFrame(data)
        df['dia_da_semana'] = df['data'].dt.weekday
        df_uteis = df[df['dia_da_semana'] < 5]
        df_uteis.drop(columns=['dia_da_semana'], axis= 1, inplace=True)
        ultimo_dia_da_semana = df_uteis['data'].to_list()

        

        cotacoes = pd.read_parquet('cotacoes.parquet')
        cotacoes['data'] = pd.to_datetime(cotacoes['data'])
        cotacoes = cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]
        cotacoes = cotacoes[cotacoes['data'].isin(ultimo_dia_da_semana)]

        if (phase < -100):
            phaseRatio = 0.5
        elif (phase > 100):
            phaseRatio = 2.5
        else:
            phaseRatio = (phase / 100) + 1.5
        
        beta_curta = 0.45 * (jma_curta - 1) / (0.45 * (jma_curta - 1) + 2)
        beta_longa = 0.45 * (jma_longa - 1) / (0.45 * (jma_longa - 1) + 2)

        alpha_curta = np.power(beta_curta, power)
        alpha_longa = np.power(beta_longa, power)

        cotacoes.loc[:,'jma_curta'] = np.zeros(len(cotacoes))
        cotacoes.loc[:,'e0_curta'] = np.zeros(len(cotacoes))
        cotacoes.loc[:,'e1_curta'] = np.zeros(len(cotacoes))
        cotacoes.loc[:,'e2_curta'] = np.zeros(len(cotacoes))
        cotacoes.reset_index(inplace=True)

        for i in range(len(cotacoes)):
            cotacoes.loc[i, 'e0_curta'] = ((1 - alpha_curta) * cotacoes.loc[i, 'preco_fechamento_ajustado']) + (alpha_curta * nz(cotacoes.loc[i-1,'e0_curta'] if i > 0 else 0))
            cotacoes.loc[i, 'e1_curta'] = (cotacoes.loc[i, 'preco_fechamento_ajustado'] - cotacoes.loc[i, 'e0_curta']) * (1 - beta_curta) + beta_curta * nz(cotacoes.loc[i-1, 'e1_curta'] if i > 0 else 0)
            cotacoes.loc[i, 'e2_curta'] = (cotacoes.loc[i, 'e0_curta'] + phaseRatio * cotacoes.loc[i, 'e1_curta'] - nz(cotacoes.loc[i-1, 'jma_curta'] if i > 0 else 0)) * np.power(1 - alpha_curta, 2) + (np.power(alpha_curta, 2) * nz(cotacoes.loc[i-1, 'e2_curta'] if i > 0 else 0))
            cotacoes.loc[i, 'jma_curta'] = cotacoes.loc[i, 'e2_curta'] + nz(cotacoes.loc[i-1, 'jma_curta'] if i > 0 else 0)
            cotacoes.loc[i, 'e0_longa'] = ((1 - alpha_longa) * cotacoes.loc[i, 'preco_fechamento_ajustado']) + (alpha_longa * nz(cotacoes.loc[i-1,'e0_longa'] if i > 0 else 0))
            cotacoes.loc[i, 'e1_longa'] = (cotacoes.loc[i, 'preco_fechamento_ajustado'] - cotacoes.loc[i, 'e0_longa']) * (1 - beta_longa) + beta_longa * nz(cotacoes.loc[i-1, 'e1_longa'] if i > 0 else 0)
            cotacoes.loc[i, 'e2_longa'] = (cotacoes.loc[i, 'e0_longa'] + phaseRatio * cotacoes.loc[i, 'e1_longa'] - nz(cotacoes.loc[i-1, 'jma_longa'] if i > 0 else 0)) * np.power(1 - alpha_longa, 2) + (np.power(alpha_longa, 2) * nz(cotacoes.loc[i-1, 'e2_longa'] if i > 0 else 0))
            cotacoes.loc[i, 'jma_longa'] = cotacoes.loc[i, 'e2_longa'] + nz(cotacoes.loc[i-1, 'jma_longa'] if i > 0 else 0)
        
        cotacoes['valor'] = cotacoes['jma_curta']/cotacoes['jma_longa']

        valor = cotacoes[['data', 'ticker', 'valor']]
        valor = valor.dropna()
        valor.to_parquet(f'jma_{jma_curta}_{jma_longa}.parquet', index = False)

    def john_neff(self):

        df_pl = pd.read_parquet('P_L.parquet')
        df_pl[df_pl['valor'] < 0] = pd.NA
        df_pl = df_pl.dropna()
        df_pl = df_pl.assign(id_dado = df_pl['ticker'].astype(str) + "_" + df_pl['data'].astype(str))
        df_pl['valor'] = df_pl['valor'].astype(float)
        df_pl = df_pl[['data', 'ticker', 'valor', 'id_dado']]
        df_pl.columns = ['data', 'ticker', 'preco_lucro', 'id_dado']

        df_roe = pd.read_parquet('ROE.parquet')
        df_roe[df_roe['valor'] < 0] = pd.NA
        df_roe = df_roe.dropna()
        df_roe = df_roe.assign(id_dado = df_roe['ticker'].astype(str) + "_" + df_roe['data'].astype(str))
        df_roe['valor'] = df_roe['valor'].astype(float)
        df_roe = df_roe[['id_dado', 'valor']]
        df_roe['valor'] = df_roe['valor'] * 100
        df_roe.columns = ['id_dado', 'roe']

        df_dy = pd.read_parquet('DividendYield.parquet')
        df_dy = df_dy.dropna()
        df_dy = df_dy.assign(id_dado = df_dy['ticker'].astype(str) + "_" + df_dy['data'].astype(str))
        df_dy['valor'] = df_dy['valor'].astype(float)
        df_dy = df_dy[['id_dado', 'valor']]
        df_dy['valor'] = df_dy['valor'] * 100
        df_dy.columns = ['id_dado', 'dy']

        df_indicadores = pd.merge(df_pl, df_roe, how = 'inner', on = 'id_dado')
        df_indicadores = pd.merge(df_indicadores, df_dy, how = 'inner', on = 'id_dado')
        df_indicadores['ROE_DY'] = pd.NA
        df_indicadores['NAFF'] = pd.NA

        # sum colum roe + dy
        df_indicadores['ROE_DY'] = df_indicadores['roe'] + df_indicadores['dy']
        df_indicadores['NAFF'] = df_indicadores['ROE_DY'] / df_indicadores['preco_lucro']

        df_indicadores = df_indicadores[['data', 'ticker', 'NAFF']]
        df_indicadores.columns = ['data', 'ticker', 'valor'] 

        df_indicadores.to_parquet('naff.parquet', index = False)

    def john_neff_vMHT(self):

        df_pl = pd.read_parquet('EV_EBITDA.parquet')
        df_pl[df_pl['valor'] < 0] = pd.NA
        df_pl = df_pl.dropna()
        df_pl = df_pl.assign(id_dado = df_pl['ticker'].astype(str) + "_" + df_pl['data'].astype(str))
        df_pl['valor'] = df_pl['valor'].astype(float)
        df_pl = df_pl[['data', 'ticker', 'valor', 'id_dado']]
        df_pl.columns = ['data', 'ticker', 'ev_ebitda', 'id_dado']

        df_roe = pd.read_parquet('ROE.parquet')
        df_roe[df_roe['valor'] < 0] = pd.NA
        df_roe = df_roe.dropna()
        df_roe = df_roe.assign(id_dado = df_roe['ticker'].astype(str) + "_" + df_roe['data'].astype(str))
        df_roe['valor'] = df_roe['valor'].astype(float)
        df_roe = df_roe[['id_dado', 'valor']]
        df_roe['valor'] = df_roe['valor'] * 100
        df_roe.columns = ['id_dado', 'roe']

        df_dy = pd.read_parquet('DividendYield.parquet')
        df_dy = df_dy.dropna()
        df_dy = df_dy.assign(id_dado = df_dy['ticker'].astype(str) + "_" + df_dy['data'].astype(str))
        df_dy['valor'] = df_dy['valor'].astype(float)
        df_dy = df_dy[['id_dado', 'valor']]
        df_dy['valor'] = df_dy['valor'] * 100
        df_dy.columns = ['id_dado', 'dy']

        df_indicadores = pd.merge(df_pl, df_roe, how = 'inner', on = 'id_dado')
        df_indicadores = pd.merge(df_indicadores, df_dy, how = 'inner', on = 'id_dado')
        df_indicadores['ROE_DY'] = pd.NA
        df_indicadores['NAFF'] = pd.NA

        # sum colum roe + dy
        df_indicadores['ROE_DY'] = df_indicadores['roe'] + df_indicadores['dy']
        df_indicadores['NAFF'] = df_indicadores['ROE_DY'] / df_indicadores['ev_ebitda']

        df_indicadores = df_indicadores[['data', 'ticker', 'NAFF']]
        df_indicadores.columns = ['data', 'ticker', 'valor']

        df_indicadores.to_parquet('naffvMHT.parquet', index = False)

    def bazin(self):
        
        df_cotacoes = pd.read_parquet('cotacoes.parquet')
        df_cotacoes['data'] = pd.to_datetime(df_cotacoes['data']).dt.date
        df_cotacoes = df_cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]

        df_yield = pd.read_parquet('DividendYield.parquet')
        df_yield['data'] = pd.to_datetime(df_yield['data']).dt.date

        df_indicadores = pd.merge(df_cotacoes, df_yield, how = 'inner', on = ['data', 'ticker'])
        df_indicadores['dividendo_em_real'] = df_indicadores['preco_fechamento_ajustado'] * df_indicadores['valor']
        df_indicadores['preço_alvo'] = df_indicadores['dividendo_em_real'] * 100 / 10
        df_indicadores['valor'] = df_indicadores['preço_alvo'] / df_indicadores['preco_fechamento_ajustado'] -1
        df_indicadores = df_indicadores[df_indicadores['valor'] > 0]
        df_indicadores = df_indicadores[['data', 'ticker', 'valor']]
        df_indicadores.to_parquet('bazin.parquet', index = False)
    
    def price_range(self):

        df_cotacoes = pd.read_parquet('cotacoes.parquet')
        df_cotacoes['data'] = pd.to_datetime(df_cotacoes['data']).dt.date
        df_cotacoes = df_cotacoes[['data', 'ticker', 'preco_fechamento_ajustado']]

        df_cotacoes['preco_maximo'] = df_cotacoes.groupby('ticker')['preco_fechamento_ajustado'].rolling(365).max().reset_index(0,drop=True)
        df_cotacoes['preco_minimo'] = df_cotacoes.groupby('ticker')['preco_fechamento_ajustado'].rolling(365).min().reset_index(0,drop=True)

        df_cotacoes['valor'] = (df_cotacoes['preco_fechamento_ajustado'] - df_cotacoes['preco_minimo']) / (df_cotacoes['preco_maximo'] - df_cotacoes['preco_minimo'])

        valor = df_cotacoes[['data', 'ticker', 'valor']]
        valor = valor.dropna()
        valor.to_parquet('price_range.parquet', index = False)

if __name__ == "__main__":

    indicador = MakeIndicator(caminho_dados=r"C:\Users\vitor\Desktop\Ferramentas Python\BaseDadosBR")
    #indicador.bazin()
    #indicador.jurik_moving_average_proporcao(jma_curta=7, jma_longa=20, phase=50, power=2)
    #indicador.john_neff()
    indicador.john_neff_vMHT()
    #indicador.price_range()

