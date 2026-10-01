import { extractEmailContent } from "/src/content/extractor.ts.js";
import { highlightTermsInDOM } from "/src/content/highlighter.ts.js";
let hasAnalyzed = false;
function initAnalysis(force = false) {
	if (hasAnalyzed && !force) return;
	const content = extractEmailContent();
	if (content && content.bodyText.length > 30) {
		hasAnalyzed = true;
		const payload = {
			subject: content.subject,
			raw_text: content.bodyText
		};
		chrome.runtime.sendMessage({
			type: "ANALYZE_EMAIL",
			payload
		}, (response) => {
			if (response && response.type === "ANALYSIS_RESULT") {
				const { highlighted_terms } = response.payload;
				if (highlighted_terms && highlighted_terms.length > 0) {
					highlightTermsInDOM(highlighted_terms);
				}
			}
		});
	} else if (force) {
		chrome.runtime.sendMessage({
			type: "ERROR",
			error: "Não foi possível extrair o texto da mensagem. Certifique-se de estar com um e-mail aberto."
		});
	}
}
// Escuta comandos manuais disparados pelo Side Panel ou Service Worker
chrome.runtime.onMessage.addListener((message) => {
	if (message.type === "TRIGGER_EXTRACTION") {
		initAnalysis(true);
	}
});
// Observa mudanças no DOM para capturar carregamento de e-mails dinâmicos (SPA)
const observer = new MutationObserver(() => {
	// Simple debounce
	setTimeout(() => {
		const gmailBody = document.querySelector(".a3s.aiL");
		const outlookBody = document.querySelector(".x_WordSection1") || document.querySelector("[aria-label=\"Corpo da mensagem\"]");
		if (gmailBody || outlookBody) {
			initAnalysis();
		} else {
			// Se saiu do e-mail, reseta a flag
			hasAnalyzed = false;
		}
	}, 1e3);
});
observer.observe(document.body, {
	childList: true,
	subtree: true
});
// Tenta iniciar caso a página já tenha carregado o e-mail
initAnalysis();
