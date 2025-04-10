import pandas as pd
import numpy as np
import yfinance as yf

# tickers = [
#     "ABCB4.SA", "ABEV3.SA", "AERI3.SA", "AGRO3.SA", "ALOS3.SA", "ALPA4.SA", "ALUP11.SA", "ANIM3.SA", "AZZA3.SA",
#     "ASAI3.SA", "AURE3.SA", "B3SA3.SA", "BBAS3.SA", "BBDC4.SA", "BBSE3.SA", "BEEF3.SA", "BMOB3.SA", "BPAC11.SA",
#     "BRAP4.SA", "BRBI11.SA", "BRFS3.SA", "BRST3.SA", "BRSR6.SA", "CEAB3.SA", "CMIG4.SA", "CMIN3.SA", "CPFE3.SA",
#     "CPLE6.SA", "CSAN3.SA", "CSMG3.SA", "CSNA3.SA", "CVCB3.SA", "CYRE3.SA", "DIVO11.SA", "ECOR3.SA", "ELET6.SA",
#     "ENEV3.SA", "ENGI11.SA", "EQTL3.SA", "ESPA3.SA", "EVEN3.SA", "EZTC3.SA", "FIQE3.SA", "FLRY3.SA", "GGPS3.SA",
#     "GMAT3.SA", "GGBR4.SA", "GUAR3.SA", "HAPV3.SA", "HBSA3.SA", "HYPE3.SA", "INTB3.SA", "ITSA4.SA", "ITUB4.SA",
#     "JALL3.SA", "JBSS3.SA", "JHSF3.SA", "KEPL3.SA", "KLBN11.SA", "LAVV3.SA", "LEVE3.SA", "LREN3.SA", "MLAS3.SA",
#     "MOVI3.SA", "MRFG3.SA", "MRVE3.SA", "MULT3.SA", "MYPK3.SA", "NEOE3.SA", "NGRD3.SA", "NTCO3.SA", "ODPV3.SA",
#     "OPCT3.SA", "PETR4.SA", "PETZ3.SA", "PRIO3.SA", "RADL3.SA", "RAIL3.SA", "RAIZ4.SA", "RANI3.SA", "RAPT4.SA",
#     "RENT3.SA", "SANB11.SA", "SAPR11.SA", "SBSP3.SA", "SLCE3.SA", "SMAL11.SA", "SMTO3.SA", "STBP3.SA", "SUZB3.SA",
#     "TFCO4.SA", "TGMA3.SA", "TIMS3.SA", "TOTS3.SA", "UGPA3.SA", "UNIP6.SA", "USIM5.SA", "VALE3.SA", "VIVA3.SA",
#     "VIVT3.SA", "VULC3.SA", "YDUQ3.SA", "^BVSP"
# ]

ticker = "DIRR3.SA"

cotacoes = yf.download(ticker, start='2025-01-01', end='2025-04-07', auto_adjust=True)['Close']
cotacoes = cotacoes[cotacoes.index.dayofweek < 5]
cotacoes_retorno = cotacoes.iloc[-21:]
cotacoes_retorno = cotacoes_retorno.pct_change().dropna()

total_return = ((1 + cotacoes_retorno).prod() -1) * 100
volatility = cotacoes_retorno.std() * 100
vams_score = total_return / volatility

results = pd.DataFrame({
    "Total Return": total_return,
    "Volatility": volatility,
    "VAMS Score": vams_score
})

results['Total Return'] = results["Total Return"].round(2)
results['Volatility'] = results["Volatility"].round(2)
results['VAMS Score'] = results["VAMS Score"].round(2)

results = results.sort_values(by="VAMS Score", ascending=False)

# results.to_excel("vams_score.xlsx", index_label="Ticker")

print(results)