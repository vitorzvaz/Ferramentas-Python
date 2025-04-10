from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Lista de ativos da watchlist
watchlist = ["AAPL", "GOOGL", "TSLA"]

# Configurar o navegador
driver = webdriver.Chrome()  # Você precisa do ChromeDriver instalado
driver.get("https://www.tradingview.com/chart/")

# Fazer login (se necessário, adicione os passos aqui)

for ticker in watchlist:
    # Carregar o ticker no gráfico
    driver.find_element(By.ID, "header-toolbar-symbol-search").click()
    driver.find_element(By.CLASS_NAME, "input").send_keys(ticker)
    driver.find_element(By.CLASS_NAME, "suggestion").click()
    
    # Aplicar a estratégia (simulando cliques ou Pine Script)
    driver.find_element(By.ID, "header-toolbar-pine-script").click()
    # Aqui você precisaria injetar sua estratégia ou selecioná-la
    
    # Abrir o Strategy Tester
    driver.find_element(By.ID, "footer-chart-panel").click()
    time.sleep(5)  # Esperar os resultados carregarem
    
    # Extrair os resultados (ajuste conforme o HTML do TradingView)
    results = driver.find_element(By.CLASS_NAME, "strategy-tester-results").text
    print(f"Resultados para {ticker}: {results}")
    
    # Salvar em um arquivo (adapte conforme necessário)
    with open("backtest_results.csv", "a") as f:
        f.write(f"{ticker},{results}\n")

driver.quit()