import requests
import pandas as pd
import os
import urllib.request

class dados_fintz:

    def __init__(self, caminho_dados):
        
        self.chave_api = os.getenv("API_FINTZ")
        self.headers = {'accept': 'application/json',
                        'X-API-Key': self.chave_api}
        os.chdir(caminho_dados)

    def cdi(self):

        response = requests.get('https://api.fintz.com.br/taxas/historico?codigo=12&dataInicio=1994-06-30&ordem=ASC',
                                headers=self.headers)
    
        cdi = pd.DataFrame(response.json())
        cdi = cdi.drop(["dataFim", 'nome'], axis = 1)
        cdi.columns = ['data', 'retorno']
        cdi['retorno'] = cdi['retorno']/100 
        cdi.to_parquet('cdi.parquet', index = False)


    def ibov(self):

        response = requests.get('https://api.fintz.com.br/indices/historico?indice=IBOV&dataInicio=1994-06-30',
                                headers=self.headers)
        df = pd.DataFrame(response.json())
        df = df.sort_values('data', ascending=True)
        df.columns = ['indice', 'data', 'fechamento']
        df = df.drop('indice', axis = 1)
        df.to_parquet('ibov.parquet', index = False)          

    def pegar_cotacoes(self):
        
        
        response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/cotacoes/historico/arquivos?classe=ACOES&preencher=true', 
                                headers=self.headers)
        

        link_download = (response.json())['link']
        urllib.request.urlretrieve(link_download, f"cotacoes.parquet")
        df = pd.read_parquet('cotacoes.parquet')
        colunas_pra_ajustar = ['preco_abertura', 'preco_maximo', 'preco_medio', 'preco_minimo']

        for coluna in colunas_pra_ajustar:

            df[f'{coluna}_ajustado'] = df[coluna] * df['fator_ajuste']

        df['preco_fechamento_ajustado'] = df.groupby('ticker')['preco_fechamento_ajustado'].transform('ffill')
        df = df.sort_values('data', ascending=True)
        df.to_parquet('cotacoes.parquet', index = False) 


    def pegando_arquivo_contabil(self, demonstracao = False, bp = False, indicadores = False, nome_dado = ''):

        if demonstracao:

            if bp:

                PARAMS = {'item': nome_dado, 'tipoPeriodo': 'TRIMESTRAL'}

            else:

                PARAMS = {'item': nome_dado, 'tipoPeriodo': '12M'}

            try:

                response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/itens-contabeis/point-in-time/arquivos',
                                        headers=self.headers, params=PARAMS)
            
            except:

                print("Demonstração não encontrada!")
                exit()

            link_download = (response.json())['link']
            urllib.request.urlretrieve(link_download, f"{nome_dado}.parquet")

        elif indicadores:

            PARAMS = {'indicador': nome_dado}

            try:

                response = requests.get(f'https://api.fintz.com.br/bolsa/b3/avista/indicadores/point-in-time/arquivos',
                                        headers=self.headers, params=PARAMS)
            
            except:

                print("Indicador não encontrado!")
                exit()

            link_download = (response.json())['link']
            urllib.request.urlretrieve(link_download, f"{nome_dado}.parquet")

        else:

            print("Escolha uma demonstração ou indicador.")


if __name__ == "__main__":

    lendo_dados = dados_fintz(caminho_dados='./dados')

    lendo_dados.pegar_cotacoes()
    lendo_dados.cdi()
    lendo_dados.ibov()










