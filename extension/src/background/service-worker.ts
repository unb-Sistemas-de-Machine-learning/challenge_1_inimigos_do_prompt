import { AnalyzeRequest, AnalyzeResponse, ExtensionMessage } from '../types';
import { analyzeText, sendFeedback, checkHealth } from '../services/api';

chrome.runtime.onMessage.addListener((message: ExtensionMessage, _sender, sendResponse) => {
  if (message.type === 'ANALYZE_EMAIL') {
    // Notifica views abertas (Side Panel) que a análise começou
    chrome.runtime.sendMessage({ type: 'ANALYZE_START' }).catch(() => {});

    handleEmailAnalysis(message.payload)
      .then(result => {
        // Broadcast para todas as views abertas (Side Panel, etc.)
        chrome.runtime.sendMessage({ type: 'ANALYSIS_RESULT', payload: result }).catch(() => {});
        sendResponse({ type: 'ANALYSIS_RESULT', payload: result });
      })
      .catch(err => {
        chrome.runtime.sendMessage({ type: 'ERROR', error: err.message }).catch(() => {});
        sendResponse({ type: 'ERROR', error: err.message });
      });
    
    return true; // Keep the message channel open for the async response
  }

  if (message.type === 'SUBMIT_FEEDBACK') {
    sendFeedback(message.payload)
      .then(res => {
        sendResponse({ type: 'FEEDBACK_RESULT', success: true, message: res.message });
      })
      .catch(err => {
        sendResponse({ type: 'FEEDBACK_RESULT', success: false, message: err.message });
      });

    return true;
  }

  if (message.type === 'CHECK_HEALTH') {
    checkHealth()
      .then(health => {
        sendResponse({ type: 'HEALTH_RESULT', payload: health });
      })
      .catch(err => {
        sendResponse({ type: 'ERROR', error: err.message });
      });

    return true;
  }

  if (message.type === 'TRIGGER_EXTRACTION') {
    // Repassa ordem de extração para a aba ativa
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs && tabs[0] && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'TRIGGER_EXTRACTION' }).catch(() => {
          sendResponse({ type: 'ERROR', error: 'Nenhum leitor de e-mail compatível detectado na aba ativa.' });
        });
      }
    });
    return true;
  }
});

async function handleEmailAnalysis(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const cacheKey = `cache_${payload.subject || ''}_${payload.raw_text.substring(0, 30)}`;
  
  // 1. Verifica no storage local
  const cachedData = await chrome.storage.local.get(cacheKey);
  if (cachedData[cacheKey]) {
    const data = cachedData[cacheKey] as AnalyzeResponse;
    // Garante que current_analysis está atualizado mesmo quando lido do cache
    await chrome.storage.local.set({ current_analysis: data });
    return data;
  }

  // 2. Faz requisição à API FastAPI
  const data = await analyzeText(payload);

  // 3. Salva no cache local e salva como análise atual
  await chrome.storage.local.set({
    [cacheKey]: data,
    current_analysis: data
  });

  return data;
}

// Configura o Side Panel para abrir nativamente ao clicar no ícone
chrome.runtime.onInstalled.addListener(() => {
  if (chrome.sidePanel && 'setPanelBehavior' in chrome.sidePanel) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
  }
});

chrome.action?.onClicked?.addListener(async (tab) => {
  if (tab?.id && chrome.sidePanel?.open) {
    try {
      await chrome.sidePanel.open({ tabId: tab.id });
    } catch {
      // Ignora erro se a aba for interna (ex: chrome://) ou já estiver aberto
    }
  }
});

