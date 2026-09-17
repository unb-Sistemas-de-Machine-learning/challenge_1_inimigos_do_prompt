import { extractEmailContent } from './extractor';
import { highlightTermsInDOM } from './highlighter';
import { AnalyzeRequest } from '../types';

let lastEmailSignature = '';

function initAnalysis() {
  const content = extractEmailContent();
  
  if (content && content.bodyText.length > 50) {
    const signature = `${content.subject}_${content.bodyText.substring(0, 60)}`;
    if (signature === lastEmailSignature) return;
    
    lastEmailSignature = signature;
    
    const payload: AnalyzeRequest = {
      subject: content.subject,
      raw_text: content.bodyText
    };

    chrome.runtime.sendMessage({ type: 'ANALYZE_EMAIL', payload }, (response) => {
      if (response && response.type === 'ANALYSIS_RESULT') {
        const { highlighted_terms } = response.payload;
        if (highlighted_terms && highlighted_terms.length > 0) {
          highlightTermsInDOM(highlighted_terms);
        }
      }
    });
  }
}

// Observa mudanças no DOM para capturar carregamento de e-mails dinâmicos (SPA)
let debounceTimeout: any = null;
const observer = new MutationObserver(() => {
  if (debounceTimeout) clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(() => {
    const gmailBody = document.querySelector('.a3s.aiL');
    const outlookBody = document.querySelector('.x_WordSection1') || document.querySelector('[aria-label="Corpo da mensagem"]');
    
    if (gmailBody || outlookBody) {
      initAnalysis();
    } else {
      // Se saiu do e-mail, reseta a assinatura
      lastEmailSignature = '';
    }
  }, 500);
});

observer.observe(document.body, { childList: true, subtree: true });

// Tenta iniciar caso a página já tenha carregado o e-mail
initAnalysis();

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'REQUEST_ANALYSIS') {
    lastEmailSignature = ''; // força bypass do cache local
    initAnalysis();
    sendResponse({ status: 'started' });
  }
});
