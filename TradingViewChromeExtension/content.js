  // Função para pegar a watchlist da página
  function getWatchlist() {
      const symbols = [];
      const watchlistItems = document.querySelectorAll('div[class^="symbol');
      watchlistItems.forEach(item => {
        const dataSymbolShort = item.getAttribute('data-symbol-short');
        if (dataSymbolShort) {
          symbols.push(dataSymbolShort);
        }
      });
      return symbols;
    }

  window.getWatchlist = getWatchlist;

  // Função para carregar um ticker no gráfico
  function loadTicker(ticker) {
    const searchBox = document.querySelector('#header-toolbar-symbol-search > div[class*="text-"]');
    searchBox.value = ticker;
    searchBox.dispatchEvent(new Event('input')); // Simula digitação
    setTimeout(() => {
      document.querySelector('.suggestion').click(); // Seleciona o primeiro resultado
    }, 500);
  }

  window.loadTicker = loadTicker;
  
  // // Função para rodar o backtest (simplificada)
  // function runBacktest() {
  //   // Aqui você precisaria simular a aplicação da estratégia e abrir o Strategy Tester
  //   setTimeout(() => {
  //     const results = document.querySelector('.strategy-tester-results').innerText;
  //     return results;
  //   }, 2000); // Espera o backtest carregar
  // }
  
  // // Função principal
  // function backtestWatchlist() {
  //   const tickers = getWatchlist();
  //   const results = [];
  
  //   tickers.forEach(ticker => {
  //     loadTicker(ticker);
  //     const result = runBacktest();
  //     results.push({ ticker, result });
  //   });
  
  //   // Exportar como CSV
  //   const csv = results.map(r => `${r.ticker},${r.result}`).join('\n');
  //   const blob = new Blob([csv], { type: 'text/csv' });
  //   const url = URL.createObjectURL(blob);
  //   chrome.runtime.sendMessage({ download: url });
  // }
  
  // console.log("Extensão carregada! Use backtestWatchlist() no console para testar.");