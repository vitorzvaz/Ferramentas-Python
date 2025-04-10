import quantstats as qs
import pandas as pd
import yfinance as yf

cotacoes = yf.download(['^BVSP'])['Close']

retornos = cotacoes.resample("ME").last().pct_change().dropna()

qs.extend_pandas()

retornos.plot_monthly_heatmap(savefig='bvsp_return_heatmap')