document.getElementById('start').addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      function: () => {
        // Chama a função que já está no content.js
        tickers = window.getWatchlist();
        return tickers;
      }
    }, (results) => {
      // Pega o resultado da execução

      if (results && results[0] && results[0].result) {
        const tickers = results[0].result[0];
        alert(tickers);
        // alert("Tickers: " + tickers.join(", "));
        // Executa a função loadTicker com os tickers obtidos
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          function: (tickers) => {
            window.loadTicker(tickers);
          },
          args: [tickers]
        });
      } else {
        alert("Erro ao executar getWatchlist. Verifique o console.");
      }
    });
  });
});