import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np

class market_premium():

    def __init__(self):

        pass

    def calculando_premio(self, caminho_dados='.', caminho_salvar_parquet='.'):

        self.caminho_dados = caminho_dados
        self.caminho_salvar_parquet = caminho_salvar_parquet

        cdi = pd.read_parquet(os.path.join(caminho_dados, "cdi.parquet"))
        cdi['cota'] = (1 + cdi['retorno']).cumprod() - 1
        ibov = pd.read_parquet(os.path.join(caminho_dados, 'ibov.parquet'))

        cdi['data'] = pd.to_datetime(cdi['data']).dt.date
        ibov['data'] = pd.to_datetime(ibov['data']).dt.date
        ibov = ibov.loc[ibov['data'] > dt.date(2000,1,1)].dropna()

        ibov_datas = ibov.sort_values('data', ascending = True)
        ibov_datas = ibov_datas.assign(year = pd.DatetimeIndex(ibov_datas['data']).year)
        ibov_datas = ibov_datas.assign(month = pd.DatetimeIndex(ibov_datas['data']).month)
        datas_final_mes = ibov_datas.groupby(['year', 'month'])['data'].last()
        dias_final_de_mes = datas_final_mes.to_list()

        ibov = ibov[ibov['data'].isin(dias_final_de_mes)]
        cdi = cdi[cdi['data'].isin(dias_final_de_mes)]
        ibov['retorno_ibov'] = ibov['fechamento'].pct_change()
        cdi['retorno_cdi'] = cdi['cota'].pct_change()
        ibov['data'] = ibov['data'].astype(str)
        cdi['data'] = cdi['data'].astype(str)

        df_dados_mercado = pd.merge(ibov, cdi, how = 'inner', on = "data")
        df_dados_mercado['mkt_premium'] = (1 + df_dados_mercado['retorno_ibov'])/(1 + df_dados_mercado['retorno_cdi']) - 1
        df_dados_mercado = df_dados_mercado.dropna()
        df_dados_mercado = df_dados_mercado[['data', 'mkt_premium']]
        df_dados_mercado['data'] = pd.to_datetime(df_dados_mercado['data']).dt.date
        #df_dados_mercado['acumulado'] = (((1 + df_dados_mercado['mkt_premium']).cumprod()) - 1)
        
        serie_movel = pd.Series(data = ((1 + df_dados_mercado['mkt_premium'])).rolling(3).apply(np.prod, raw = True) - 1)
        serie_movel.index = df_dados_mercado['data'].values
        serie_movel = serie_movel.dropna()

        #plt.plot(serie_movel.index, serie_movel.values, label = 'Market Premium')
        #plt.hlines(0, serie_movel.index[0], serie_movel.index[-1], colors='black', linestyles='dashed')
        #plt.plot(df_dados_mercado['data'], df_dados_mercado['acumulado'], label = 'Market Premium')
        #plt.show()

        df_dados_mercado.to_parquet(os.path.join(caminho_salvar_parquet, 'market_premium.parquet'), index = False)


if __name__ == "__main__":

    beta = market_premium()

    beta.calculando_premio(caminho_dados=r"C:\Users\vitor\Desktop\Ferramentas Python\BaseDadosBR",
                           caminho_salvar_parquet=r"C:\Users\vitor\Desktop\Ferramentas Python\BaseDadosBR\PremiosRiscoBR")


    