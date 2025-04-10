import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
from numpy import linalg as LA

lista_acoes = ['WEGE3', 'PCAR3', 'LREN3', 'PETR4', 'VALE3']
lista_acoes = [acao + ".SA" for acao in lista_acoes]

data_final = dt.datetime.now()
data_inicial = data_final - dt.timedelta(days=300)

precos = yf.download(lista_acoes, data_inicial, data_final)['Close']
retornos = precos.pct_change().dropna()
media_retornos = retornos.mean()
matriz_covariancia = retornos.cov()
pesos_carteira = np.full(len(lista_acoes), 1/len(lista_acoes))
numero_acoes = len(lista_acoes)

print(pesos_carteira)

# retornos sintéticos = média_retornos + Rpdf x L
# retornos sintéticos: simulação de retornos futuros
# média_retornos: média dos retornos passados
# Rpdf: matriz aleatória gerada por alguma função de densidade de probabilidade
# L: Matriz triangular inferior proveniente de uma decomposição de Cholesky, usando como base a covariancia dos dados originais
# Assumimos que a distribuição de retornos é normal multivariada
# Ao gerar retornos aleatórios, criamos vetores descorrelacionados, para corrigir isso, dado que o mercado é correlacionado, usamos a matariz triângular obtida pela covariância

# premissas de montecarlo
numero_simulacoes = 10000
dias_projetados = 252
capital_inicial = 1000

retorno_medio = retornos.mean(axis=0).to_numpy()
matriz_retorno_medio = retorno_medio * np.ones(shape=(dias_projetados, numero_acoes))

L = LA.cholesky(matriz_covariancia)

retornos_carteira = np.zeros([dias_projetados, numero_simulacoes])
montante_final = np.zeros(numero_simulacoes)

for s in range(numero_simulacoes):
    Rpdf = np.random.normal(size=(dias_projetados,numero_acoes))
    retornos_sinteticos = matriz_retorno_medio + np.inner(Rpdf, L)
    retornos_carteira[:, s] = np.cumprod(np.inner(pesos_carteira, retornos_sinteticos) + 1) * capital_inicial
    montante_final[s] = retornos_carteira[-1, s]

# plt.plot(retornos_carteira, linewidth=1)
# plt.ylabel('Dinheiro')
# plt.xlabel('Dias')
# plt.show()

montante_99 = str(np.percentile(montante_final, 1))
montate_95 = str(np.percentile(montante_final, 5))
montante_mediano = str(np.percentile(montante_final, 50))

cenarios_com_lucro = str((len(montante_final[montante_final > 1000]) / len(montante_final)) * 100) + "%"

print(montate_95)
print(montante_99)
print(montante_mediano)
print(cenarios_com_lucro)