import { AnalyzeRequest, AnalyzeResponse, ExtensionMessage } from '../types';
import { analyzeText } from '../services/api';

chrome.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
  if (message.type === 'ANALYZE_EMAIL') {
    handleEmailAnalysis(message.payload)
      .then(result => sendResponse({ type: 'ANALYSIS_RESULT', payload: result }))
      .catch(err => sendResponse({ type: 'ERROR', error: err.message }));
    
    return true; // Keep the message channel open for the async response
  }
});

async function handleEmailAnalysis(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const cacheKey = `cache_${payload.subject || ''}_${payload.raw_text.substring(0, 30)}`;
  
  // 1. Verifica no storage local
  const cachedData = await chrome.storage.local.get(cacheKey);
  if (cachedData[cacheKey]) {
    return cachedData[cacheKey] as AnalyzeResponse;
  }

  // 2. Faz requisição à API FastAPI
  const data = await analyzeText(payload);

  // 3. Salva no cache local
  await chrome.storage.local.set({ [cacheKey]: data });

  return data;
}

// Inicializa a ação do Side Panel no clique
chrome.action.onClicked.addListener((tab) => {
  if (tab.id) {
    chrome.sidePanel.setOptions({
      tabId: tab.id,
      path: 'index.html',
      enabled: true
    });
    chrome.sidePanel.open({ tabId: tab.id });
  }
});
