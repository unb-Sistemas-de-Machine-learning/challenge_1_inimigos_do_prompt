import { useState, useEffect, useCallback } from 'react';
import { AnalyzeResponse } from './types';
import { analyzeText, sendFeedback, checkHealth } from './services/api';
import { 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  FileText, 
  Send, 
  ExternalLink, 
  Sparkles,
  Loader2
} from 'lucide-react';

function App() {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Backend health status
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [backendBackend, setBackendBackend] = useState<string>('sklearn');

  // Slider State
  const [sliderValue, setSliderValue] = useState<number>(50);
  const [hasInteracted, setHasInteracted] = useState<boolean>(false);
  const [feedbackSending, setFeedbackSending] = useState<boolean>(false);
  const [feedbackSent, setFeedbackSent] = useState<boolean>(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const verifyHealth = useCallback(async () => {
    try {
      setBackendStatus('checking');
      const health = await checkHealth();
      setBackendStatus('online');
      if (health.model_backend) {
        setBackendBackend(health.model_backend);
      }
    } catch {
      setBackendStatus('offline');
    }
  }, []);

  useEffect(() => {
    // 1. Verifica conexão com o backend FastAPI
    verifyHealth();

    // 2. Carrega última análise do cache local se disponível
    if (chrome.storage?.local) {
      chrome.storage.local.get(['current_analysis'], (result) => {
        if (result.current_analysis) {
          setData(result.current_analysis as AnalyzeResponse);
        }
      });
    }

    // 3. Ouve mensagens em tempo real do Content Script e do Background Worker
    const listener = (msg: any) => {
      if (msg.type === 'ANALYZE_START' || msg.type === 'ANALYZE_EMAIL') {
        setLoading(true);
        setError(null);
      } else if (msg.type === 'ANALYSIS_RESULT') {
        setData(msg.payload);
        setLoading(false);
        setError(null);
      } else if (msg.type === 'ERROR') {
        setError(msg.error);
        setLoading(false);
      }
    };

    chrome.runtime?.onMessage?.addListener(listener);
    return () => {
      chrome.runtime?.onMessage?.removeListener(listener);
    };
  }, [verifyHealth]);

  // Dispara extração e análise do e-mail aberto na aba ativa
  const handleAnalyzeActiveTab = () => {
    setLoading(true);
    setError(null);

    if (chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs[0]?.id) {
          chrome.tabs.sendMessage(tabs[0].id, { type: 'TRIGGER_EXTRACTION' }, () => {
            if (chrome.runtime.lastError) {
              setError('Abra uma aba com webmail (Gmail ou Outlook) para analisar o e-mail aberto.');
              setLoading(false);
            }
          });
        } else {
          setError('Nenhuma aba ativa identificada.');
          setLoading(false);
        }
      });
    } else {
      setError('Ambiente de extensão não disponível.');
      setLoading(false);
    }
  };

  // Testa diretamente contra o backend FastAPI com payload real
  const handleDemoAnalysis = async (type: 'hype' | 'sobrio') => {
    setLoading(true);
    setError(null);

    const demoPayloads = {
      hype: {
        email_id: `demo-hype-${Date.now()}`,
        subject: 'URGENTE: Nova Inteligência Artificial vai substituir 90% dos programadores!',
        raw_text: 'ATENÇÃO URGENTE! Pesquisadores anunciam que uma nova Inteligência Artificial com computação quântica vai substituir 90% dos programadores em ritmo assustador e gerar pânico no mercado global de tecnologia. O colapso dos empregos de programação é inevitável e revolucionário!'
      },
      sobrio: {
        email_id: `demo-sobrio-${Date.now()}`,
        subject: 'Consórcio de tecnologia define novos padrões para infraestrutura de telecomunicações',
        raw_text: 'O consórcio internacional de telecomunicações anunciou hoje a publicação das diretrizes de arquitetura para implementação de redes corporativas. Os testes operacionais iniciam no próximo trimestre com foco em sustentabilidade e redução de consumo de energia.'
      }
    };

    try {
      const payload = demoPayloads[type];
      const result = await analyzeText(payload);
      setData(result);
      
      // Salva no storage local
      if (chrome.storage?.local) {
        chrome.storage.local.set({ current_analysis: result });
      }
    } catch (err: any) {
      setError(err.message || 'Falha ao consultar a API de análise.');
    } finally {
      setLoading(false);
    }
  };

  const getSliderStatus = (val: number) => {
    if (val < 20) return "Reduziu muito";
    if (val < 45) return "Reduziu ligeiramente";
    if (val <= 55) return "Não mudou";
    if (val < 80) return "Aumentou ligeiramente";
    return "Aumentou muito";
  };

  // Envio de feedback real para POST /api/v1/feedback
  const submitFeedback = async () => {
    if (!data || !hasInteracted) return;

    setFeedbackSending(true);
    setFeedbackError(null);

    try {
      await sendFeedback({
        email_id: data.email_id || `email-${Date.now()}`,
        feedback_type: 'confidence_slider',
        slider_value: sliderValue,
        comment: `Confiança declarada: ${getSliderStatus(sliderValue)} (${sliderValue}/100)`
      });
      setFeedbackSent(true);
    } catch (err: any) {
      setFeedbackError('Erro ao registrar no backend.');
      console.error(err);
    } finally {
      setFeedbackSending(false);
    }
  };

  const handleClearAnalysis = () => {
    setData(null);
    setError(null);
    setHasInteracted(false);
    setFeedbackSent(false);
    if (chrome.storage?.local) {
      chrome.storage.local.remove(['current_analysis']);
    }
  };

  const openDashboard = () => {
    if (chrome.tabs && chrome.runtime) {
      chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
    } else {
      window.open('/dashboard.html', '_blank');
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col font-sans text-gray-800">
      {/* Header */}
      <header className="bg-gray-200 px-4 py-2.5 flex items-center justify-between shadow-sm border-b border-gray-300">
        <div>
          <h1 className="text-xs font-black text-gray-800 tracking-wider uppercase">
            INIMIGOS DO PROMPT
          </h1>
          <p className="text-[10px] text-gray-500 font-medium">Relatório de IA & Hype Tech</p>
        </div>

        {/* Backend Status Indicator */}
        <div className="flex items-center gap-1.5 bg-white/70 px-2 py-1 rounded-full border border-gray-300 text-[10px] font-semibold">
          <span 
            className={`w-2 h-2 rounded-full ${
              backendStatus === 'online' ? 'bg-emerald-500 animate-pulse' : 
              backendStatus === 'checking' ? 'bg-amber-400 animate-ping' : 'bg-red-500'
            }`} 
          />
          <span className="text-gray-600">
            {backendStatus === 'online' ? `API Online (${backendBackend})` :
             backendStatus === 'checking' ? 'Conectando...' : 'API Offline'}
          </span>
          {backendStatus === 'offline' && (
            <button 
              onClick={verifyHealth} 
              title="Tentar reconectar"
              className="text-gray-400 hover:text-indigo-600 ml-0.5"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          )}
        </div>
      </header>

      {/* Backend Offline Warning Banner */}
      {backendStatus === 'offline' && (
        <div className="bg-amber-50 border-b border-amber-200 px-3 py-2 text-[11px] text-amber-800 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-bold">Backend FastAPI desconectado.</span> Inicie o servidor localmente com <code className="bg-amber-100 px-1 py-0.5 rounded text-[10px] font-mono">uvicorn app.main:app --port 8000</code>.
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-3">
          <Loader2 className="h-9 w-9 text-indigo-600 animate-spin" />
          <p className="font-bold text-sm text-gray-700">Analisando conteúdo da newsletter...</p>
          <p className="text-xs text-gray-400">Consultando o modelo de Machine Learning e extraindo termos suspeitos</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="m-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 space-y-2">
          <div className="flex items-center gap-2 font-bold text-xs">
            <AlertTriangle className="h-4 w-4 text-red-600" />
            <span>Erro no processamento</span>
          </div>
          <p className="text-xs text-red-600 leading-relaxed">{error}</p>
          <button 
            onClick={() => setError(null)}
            className="text-[11px] text-red-700 underline font-semibold mt-1"
          >
            Fechar aviso
          </button>
        </div>
      )}

      {/* Empty State / Welcome Screen */}
      {!data && !loading && (
        <div className="flex-1 flex flex-col items-center justify-center p-5 text-center space-y-5">
          <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center border border-indigo-100 shadow-sm">
            <ShieldAlert className="h-9 w-9 text-indigo-600" />
          </div>

          <div className="space-y-1.5 max-w-xs">
            <h2 className="text-sm font-bold text-gray-800">Detector de Sensacionalismo</h2>
            <p className="text-xs text-gray-500 leading-relaxed">
              Abra um e-mail no <strong>Gmail</strong> ou <strong>Outlook</strong> para que a extensão avalie o texto automaticamente, ou teste agora mesmo com o backend:
            </p>
          </div>

          <div className="w-full space-y-2 pt-2">
            <button 
              onClick={handleAnalyzeActiveTab}
              className="w-full py-2.5 px-3 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white text-xs font-bold rounded-lg shadow-sm transition-all flex items-center justify-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Analisar E-mail da Aba Aberta</span>
            </button>

            <div className="pt-2 border-t border-gray-200 text-left">
              <span className="text-[10px] uppercase font-bold text-gray-400 block mb-2 tracking-wider">
                Testes Rápidos de Integração (API Real):
              </span>
              <div className="grid grid-cols-2 gap-2">
                <button 
                  onClick={() => handleDemoAnalysis('hype')}
                  className="py-2 px-2.5 bg-white hover:bg-rose-50 border border-gray-200 hover:border-rose-300 text-rose-700 text-[11px] font-bold rounded-lg shadow-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5 text-rose-500" />
                  <span>Exemplo Hype</span>
                </button>

                <button 
                  onClick={() => handleDemoAnalysis('sobrio')}
                  className="py-2 px-2.5 bg-white hover:bg-emerald-50 border border-gray-200 hover:border-emerald-300 text-emerald-700 text-[11px] font-bold rounded-lg shadow-xs transition-colors flex items-center justify-center gap-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Exemplo Sóbrio</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Result Screen */}
      {data && !loading && (
        <div className="p-3 space-y-3 flex-1 overflow-y-auto">
          {/* Action Bar */}
          <div className="flex items-center justify-between px-1">
            <span className="text-[10px] font-mono text-gray-500 truncate max-w-[180px]">
              ID: {data.email_id?.substring(0, 16) || 'análise-local'}...
            </span>
            <button 
              onClick={handleClearAnalysis}
              className="text-[10px] font-bold text-indigo-600 hover:text-indigo-800 transition-colors flex items-center gap-1"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Nova Análise</span>
            </button>
          </div>

          {/* Sensationalism Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-[13px] font-bold text-gray-800">
                Análise de Sensacionalismo
              </h2>
              <span className={`text-[11px] font-extrabold px-2.5 py-0.5 rounded-full ${
                data.sensationalism_score >= 3.8 ? 'bg-rose-100 text-rose-700' :
                data.sensationalism_score >= 2.5 ? 'bg-amber-100 text-amber-700' :
                'bg-emerald-100 text-emerald-700'
              }`}>
                {data.label}
              </span>
            </div>
            
            {/* Gauge Graphic */}
            <div className="flex justify-center mb-4 relative h-24">
              <svg viewBox="0 0 200 100" className="w-48 h-24 overflow-visible">
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e5e7eb" strokeWidth="24" strokeLinecap="round" />
                <path 
                  d="M 20 100 A 80 80 0 0 1 180 100" 
                  fill="none" 
                  stroke="url(#gauge-gradient)" 
                  strokeWidth="24" 
                  strokeLinecap="round" 
                  strokeDasharray="251.2" 
                  strokeDashoffset={251.2 * (1 - (data.sensationalism_score / 5))} 
                  className="transition-all duration-1000 ease-out" 
                />
                <defs>
                  <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="45%" stopColor="#f59e0b" />
                    <stop offset="100%" stopColor="#ef4444" />
                  </linearGradient>
                </defs>
                {/* Needle */}
                <g transform={`rotate(${180 * (data.sensationalism_score / 5)} 100 100)`} className="transition-transform duration-1000 ease-out origin-[100px_100px]">
                  <polygon points="97,100 103,100 100,20" fill="#374151" />
                  <circle cx="100" cy="100" r="5" fill="#374151" />
                </g>
              </svg>

              <div className="absolute bottom-0 text-center">
                <span className="text-2xl font-black text-gray-800">
                  {data.sensationalism_score.toFixed(1)}
                </span>
                <span className="text-xs text-gray-400 font-bold"> / 5.0</span>
              </div>
            </div>

            {/* Feature Importance Section */}
            <div className="space-y-3 mt-2">
              <div className="bg-gray-50 border border-gray-100 rounded-md p-2.5">
                <h4 className="text-[11px] font-bold text-gray-700 mb-1 uppercase tracking-wider">
                  Termos com Maior Peso no Score
                </h4>
                <p className="text-[10px] text-gray-400 mb-2 leading-tight">
                  Palavras e gatilhos linguísticos extraídos pelo pipeline que elevaram o índice.
                </p>
                
                <div className="space-y-2">
                  {data.highlighted_terms.length === 0 ? (
                    <p className="text-[11px] text-gray-500 italic">Nenhum termo alarmista ou de hype detectado.</p>
                  ) : (
                    [...data.highlighted_terms]
                      .sort((a, b) => b.weight - a.weight)
                      .slice(0, 6)
                      .map((item, idx) => (
                        <div key={idx} className="flex items-center justify-between gap-2">
                          <span className="text-[12px] font-semibold text-gray-700 truncate w-2/5">
                            "{item.term}"
                          </span>
                          <div className="flex-1 bg-gray-200 rounded-full h-1.5 overflow-hidden flex items-center">
                            <div 
                              className={`h-full rounded-full ${
                                item.weight > 0.7 ? 'bg-rose-500' : (item.weight > 0.4 ? 'bg-amber-500' : 'bg-yellow-400')
                              }`} 
                              style={{ width: `${Math.min(item.weight * 100, 100)}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-gray-500 font-mono font-bold">
                            +{item.weight.toFixed(2)}
                          </span>
                        </div>
                      ))
                  )}
                </div>
              </div>
            </div>

            {/* Confidence Slider */}
            <div className="mt-5 pt-4 border-t border-gray-100 space-y-3">
              <div className="flex justify-between items-center">
                <h3 className="text-[12px] font-bold text-gray-800">Sua confiança mudou após este score?</h3>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                  hasInteracted ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500'
                }`}>
                  {getSliderStatus(sliderValue)}
                </span>
              </div>
              
              <div className="px-2">
                <input 
                  type="range" 
                  min="0" max="100" 
                  value={sliderValue}
                  onChange={(e) => {
                    setSliderValue(Number(e.target.value));
                    setHasInteracted(true);
                    setFeedbackSent(false);
                    setFeedbackError(null);
                  }}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <div className="flex justify-between text-[10px] text-gray-500 mt-1 font-medium">
                  <span>Reduziu muito</span>
                  <span>Não mudou</span>
                  <span>Aumentou</span>
                </div>
              </div>

              {feedbackSent ? (
                <div className="flex items-center justify-center gap-1.5 py-2 bg-emerald-50 text-emerald-700 rounded-md border border-emerald-200 mt-2">
                  <CheckCircle2 className="h-4 w-4" />
                  <span className="text-[11px] font-bold">Feedback Registrado no Backend!</span>
                </div>
              ) : (
                <button 
                  onClick={submitFeedback}
                  disabled={!hasInteracted || feedbackSending}
                  className={`w-full mt-2 py-2 rounded-md text-[11px] font-bold transition-all flex items-center justify-center gap-1.5 ${
                    hasInteracted && !feedbackSending
                      ? 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white shadow-sm' 
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {feedbackSending ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Enviando avaliação...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>Confirmar Avaliação</span>
                    </>
                  )}
                </button>
              )}

              {feedbackError && (
                <p className="text-[10px] text-red-500 text-center">{feedbackError}</p>
              )}
            </div>
          </div>

          {/* Disinformation Card */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-[13px] font-bold text-gray-800">
                Análise de Desinformação
              </h2>
              <span className={`text-[11px] font-black px-2 py-0.5 rounded ${
                data.disinformation_risk > 70 ? 'bg-red-100 text-red-700' :
                data.disinformation_risk > 30 ? 'bg-amber-100 text-amber-700' :
                'bg-emerald-100 text-emerald-700'
              }`}>
                {data.disinformation_risk}% Risco
              </span>
            </div>
            
            <h3 className="text-[11px] font-bold text-gray-600 uppercase tracking-wider mb-2">
              Alegações Suspeitas ({data.suspicious_claims?.length || 0}):
            </h3>
            
            {(!data.suspicious_claims || data.suspicious_claims.length === 0) ? (
              <p className="text-xs text-gray-500 italic bg-gray-50 p-2.5 rounded border border-gray-100">
                Nenhuma alegação suspeita detectada neste texto.
              </p>
            ) : (
              <ul className="space-y-2.5">
                {data.suspicious_claims.map((claim, idx) => (
                  <li key={idx} className="bg-gray-50 p-2.5 rounded-lg border border-gray-100 text-xs space-y-1">
                    <div className="flex items-start gap-1.5">
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                        claim.severity === 'high' ? 'bg-rose-600 text-white' : 'bg-amber-500 text-white'
                      }`}>
                        {claim.severity === 'high' ? 'Crítico' : 'Moderado'}
                      </span>
                      <span className="font-semibold text-gray-800 leading-snug">
                        "{claim.claim}"
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-600 pl-1 pt-0.5 leading-tight">
                      {claim.explanation}
                    </p>
                  </li>
                ))}
              </ul>
            )}

            <div className="mt-4">
              <button 
                onClick={openDashboard}
                className="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-bold py-2.5 px-3 rounded-lg transition-colors border border-indigo-200 shadow-xs flex items-center justify-center gap-1.5"
              >
                <span>Ver checagem completa no Painel de Controle</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <footer className="text-[10px] text-gray-400 text-center py-2 px-3 leading-tight">
            {data.disclaimer}
          </footer>
        </div>
      )}
    </div>
  );
}

export default App;
