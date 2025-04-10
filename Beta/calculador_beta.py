import yfinance as yf
import statsmodels.api as sm
from datetime import datetime, timedelta

ativos = ['ABEV3.SA', "^BVSP"]
data = datetime.now()
cinco_anos_atras = data - timedelta(days=365 * 5)

dados_cotacoes = yf.download(ativos, start=cinco_anos_atras, end=data)['Adj Close']

retornos_diarios = dados_cotacoes.pct_change().dropna()

x = retornos_diarios['^BVSP']
y = retornos_diarios[ativos[0]]

X = sm.add_constant(x)

model = sm.OLS(y, X)
results = model.fit()

# Print the model summary
print(results.summary())