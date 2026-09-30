import { extractEmailContent } from './extractor';

// Variável para armazenar o URL ou ID do último e-mail analisado
let lastProcessedUrl = location.href;

function processCurrentEmail() {
  const content = extractEmailContent();
  if (content) {
    console.log("[Inimigos do Prompt] E-mail extraído com sucesso no Outlook/Gmail.");
    // Envia para o Background/Painel
    chrome.runtime.sendMessage({ type: 'EMAIL_EXTRACTED', payload: content });
  }
}

// 1. O Observador de Mutações (MutationObserver)
const observer = new MutationObserver(() => {
  // A verificação via URL funciona bem nos SPAs de webmail modernos, 
  // pois eles alteram o URL (hash ou path) ao trocar de mensagem.
  if (location.href !== lastProcessedUrl) {
    lastProcessedUrl = location.href;
    console.log("[Inimigos do Prompt] Mudança de e-mail detetada (SPA).");
    
    // Dá um pequeno atraso para o DOM do Outlook Web renderizar o novo texto
    setTimeout(processCurrentEmail, 1500); 
  }
});

// Inicia a observação no corpo inteiro da página assim que possível
function initObserver() {
  const targetNode = document.body;
  const config = { childList: true, subtree: true };
  
  if (targetNode) {
    observer.observe(targetNode, config);
    console.log("[Inimigos do Prompt] MutationObserver injetado com sucesso.");
    
    // Tenta processar o e-mail caso o utilizador tenha aberto a página diretamente na mensagem
    setTimeout(processCurrentEmail, 2000);
  } else {
    // Tenta novamente se o DOM não estiver pronto
    setTimeout(initObserver, 500);
  }
}

// Inicializa a extensão
initObserver();

// Mantém a capacidade de receber comandos manuais do App.tsx (Botão "Nova Análise")
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TRIGGER_EXTRACTION') {
    processCurrentEmail();
  }
});
