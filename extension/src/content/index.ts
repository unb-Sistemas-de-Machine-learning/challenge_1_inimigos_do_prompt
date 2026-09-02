import { extractEmailContent } from './extractor';
import { highlightTermsInDOM } from './highlighter';
import { AnalyzeRequest } from '../types';

let hasAnalyzed = false;

function initAnalysis() {
  if (hasAnalyzed) return;

  const content = extractEmailContent();
  
  if (content && content.bodyText.length > 50) {
    hasAnalyzed = true;
    
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
const observer = new MutationObserver(() => {
  // Simple debounce
  setTimeout(() => {
    const gmailBody = document.querySelector('.a3s.aiL');
    const outlookBody = document.querySelector('.x_WordSection1') || document.querySelector('[aria-label="Corpo da mensagem"]');
    
    if (gmailBody || outlookBody) {
      initAnalysis();
    } else {
      // Se saiu do e-mail, reseta a flag
      hasAnalyzed = false;
    }
  }, 1000);
});

observer.observe(document.body, { childList: true, subtree: true });

// Tenta iniciar caso a página já tenha carregado o e-mail
initAnalysis();
