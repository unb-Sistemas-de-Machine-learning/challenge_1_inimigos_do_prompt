import { HighlightedTerm } from '../types';

export function highlightTermsInDOM(terms: HighlightedTerm[]) {
  const gmailBody = document.querySelector('.a3s.aiL');
  const outlookBody = document.querySelector('.x_WordSection1') || document.querySelector('[aria-label="Corpo da mensagem"]');
  
  const container = gmailBody || outlookBody;
  if (!container) return;

  // Em uma extensão real, usaríamos algo mais robusto como o range API ou mark.js
  // Esta implementação é simplificada para a PoC
  let html = container.innerHTML;
  
  terms.forEach(termObj => {
    // Escapa o termo para regex
    const escapedTerm = termObj.term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b(${escapedTerm})\\b`, 'gi');
    
    html = html.replace(regex, `<mark class="hype-highlight" title="Sensacionalismo/Hype (${Math.round(termObj.weight * 100)}%)" style="background-color: #fef08a; padding: 0.125rem 0.25rem; border-radius: 0.25rem; border: 1px solid #fde047; cursor: help;">$1</mark>`);
  });

  container.innerHTML = html;
}
