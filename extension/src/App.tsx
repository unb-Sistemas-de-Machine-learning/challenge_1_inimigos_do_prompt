import { useState, useEffect } from 'react';
import { AnalyzeResponse } from './types';
import { ShieldAlert, X, AlertTriangle, CheckCircle2 } from 'lucide-react';

function App() {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Slider State
  const [sliderValue, setSliderValue] = useState<number>(50);
  const [hasInteracted, setHasInteracted] = useState<boolean>(false);
  const [feedbackSent, setFeedbackSent] = useState<boolean>(false);

  useEffect(() => {
    const listener = (msg: any) => {
      if (msg.type === 'ANALYZE_EMAIL') {
        setLoading(true);
        setError(null);
      } else if (msg.type === 'ANALYSIS_RESULT') {
        setData(msg.payload);
        setLoading(false);
      } else if (msg.type === 'ERROR') {
        setError(msg.error);
        setLoading(false);
      }
    };

    chrome.runtime?.onMessage?.addListener(listener);
    return () => {
      chrome.runtime?.onMessage?.removeListener(listener);
    };
  }, []);

  const simulateAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      const mockData: AnalyzeResponse = {
        sensationalism_score: 4.2,
        label: 'Hype Elevado',
        confidence: 0.95,
        highlighted_terms: [
          { term: 'Urgente', weight: 0.4, category: 'hype' },
          { term: 'Revolucionário', weight: 0.9, category: 'hype' },
          { term: 'Substituir 90%', weight: 0.85, category: 'clickbait' },
          { term: 'Pânico', weight: 0.6, category: 'alarmist' }
        ],
        disclaimer: 'Os resultados são baseados em heurísticas.',
        disinformation_risk: 78,
        suspicious_claims: [
          {
            claim: 'A substituição de 90% dos programadores',
            explanation: 'Hype exagerado, projeção não comprovada por fontes técnicas.',
            severity: 'moderate'
          },
          {
            claim: 'O uso de computação quântica para IA',
            explanation: 'Conceito técnico são, não comercial.',
            severity: 'moderate'
          },
          {
            claim: 'O uso de computação quântica para IA',
            explanation: 'Conceito técnico incorreto (quântico é experimental, não comercial).',
            severity: 'high'
          }
        ]
      };
      setData(mockData);
      setLoading(false);
      
      // Save for Dashboard
      if (chrome.storage) {
        chrome.storage.local.set({ current_analysis: mockData });
      }
    }, 1000);
  };

  const getSliderStatus = (val: number) => {
    if (val < 20) return "Reduziu muito";
    if (val < 45) return "Reduziu ligeiramente";
    if (val <= 55) return "Não mudou";
    if (val < 80) return "Aumentou ligeiramente";
    return "Aumentou muito";
  };

  const submitFeedback = () => {
    // Simulando envio de métrica
    setFeedbackSent(true);
  };

  const openDashboard = () => {
    if (chrome.tabs && chrome.runtime) {
      chrome.tabs.create({ url: chrome.runtime.getURL('dashboard.html') });
    } else {
      alert('Modo Dashboard não suportado fora da extensão Chrome.');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-500 p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-4"></div>
        <p>Analisando newsletter...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-red-50 text-red-600 p-4 text-center">
        <AlertTriangle className="h-10 w-10 mb-2" />
        <p className="font-semibold">Erro na Análise</p>
        <p className="text-sm mt-1 text-red-500">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-400 p-6 text-center space-y-6">
        <div className="space-y-4 flex flex-col items-center">
          <ShieldAlert className="h-12 w-12 text-gray-300" />
          <p>Abra um e-mail de newsletter no Gmail ou Outlook para visualizar a análise do Inimigos do Prompt.</p>
        </div>
        
        <button 
          onClick={simulateAnalysis}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-md shadow-sm transition-colors w-full"
        >
          Simular Análise (POC)
        </button>
      </div>
    );
  }

  // Sort terms by weight descending
  const sortedTerms = [...data.highlighted_terms].sort((a, b) => b.weight - a.weight);

  return (
    <div className="bg-gray-100 min-h-screen flex flex-col font-sans">
      {/* Header */}
      <header className="bg-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <h1 className="text-xs font-bold text-gray-700 tracking-wide uppercase">
          RELATÓRIO DETALHADO (IA #2026/02)
        </h1>
        <button className="text-gray-500 hover:text-gray-800 transition-colors">
          <X className="h-4 w-4" />
        </button>
      </header>

      <div className="p-3 space-y-3 flex-1 overflow-y-auto">
        {/* Sensationalism Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-[13px] font-bold text-gray-800 mb-3">
            Análise de Sensacionalismo (Likert {data.sensationalism_score.toFixed(1)}/5)
          </h2>
          
          {/* Gauge Graphic */}
          <div className="flex justify-center mb-4 relative h-24">
            <svg viewBox="0 0 200 100" className="w-48 h-24 overflow-visible">
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e5e7eb" strokeWidth="24" strokeLinecap="round" />
              <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gauge-gradient)" strokeWidth="24" strokeLinecap="round" strokeDasharray="251.2" strokeDashoffset={251.2 * (1 - (data.sensationalism_score / 5))} className="transition-all duration-1000 ease-out" />
              <defs>
                <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#ef4444" />
                  <stop offset="50%" stopColor="#f97316" />
                  <stop offset="100%" stopColor="#facc15" />
                </linearGradient>
              </defs>
              {/* Needle */}
              <g transform={`rotate(${180 * (data.sensationalism_score / 5)} 100 100)`} className="transition-transform duration-1000 ease-out origin-[100px_100px]">
                <polygon points="97,100 103,100 100,20" fill="#4b5563" />
                <circle cx="100" cy="100" r="5" fill="#4b5563" />
              </g>
            </svg>
          </div>

          <div className="space-y-3 mt-2">
            <div className="flex items-center justify-between">
              <h3 className="text-[13px] font-bold text-gray-800">Por que alto?</h3>
            </div>
            
            <div className="bg-gray-50 border border-gray-100 rounded-md p-2">
              <h4 className="text-[11px] font-semibold text-gray-600 mb-2 uppercase tracking-wider">
                Termos com Maior Peso no Score
              </h4>
              <p className="text-[10px] text-gray-400 mb-2 leading-tight">
                Termos extraídos pelo pipeline que elevaram o índice de sensacionalismo.
              </p>
              
              <div className="space-y-2">
                {sortedTerms.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between gap-2">
                    <span className="text-[12px] font-medium text-gray-700 truncate w-1/2">"{item.term}"</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5 overflow-hidden flex items-center">
                      <div 
                        className={`h-full rounded-full ${item.weight > 0.8 ? 'bg-red-500' : (item.weight > 0.5 ? 'bg-orange-400' : 'bg-yellow-400')}`} 
                        style={{ width: `${item.weight * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-[10px] text-gray-500 font-mono">+{item.weight.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-100 space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-[12px] font-bold text-gray-800">Sua confiança mudou após este score?</h3>
              <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${hasInteracted ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'}`}>
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
                }}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-[10px] text-gray-500 mt-1 font-medium">
                <span>Reduziu muito</span>
                <span>Não mudou</span>
                <span>Aumentou</span>
              </div>
            </div>

            {feedbackSent ? (
              <div className="flex items-center justify-center gap-1.5 py-1.5 bg-green-50 text-green-700 rounded-md border border-green-200 mt-2">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-[11px] font-bold">Feedback Enviado!</span>
              </div>
            ) : (
              <button 
                onClick={submitFeedback}
                disabled={!hasInteracted}
                className={`w-full mt-2 py-1.5 rounded-md text-[11px] font-bold transition-colors ${
                  hasInteracted 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm' 
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                }`}
              >
                Confirmar Avaliação
              </button>
            )}
          </div>
        </div>

        {/* Disinformation Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-[13px] font-bold text-gray-800 mb-3">
            Análise de Desinformação/Claims ({data.disinformation_risk}% Risco):
          </h2>
          
          <h3 className="text-[12px] font-bold text-gray-800 mb-2">Alegações Suspeitas:</h3>
          
          <ul className="list-disc pl-5 text-[12px] text-gray-800 space-y-3">
            {data.suspicious_claims.map((claim, idx) => (
              <li key={idx} className="leading-snug">
                <span className={`px-1 rounded font-medium ${claim.severity === 'high' ? 'bg-[#da3e3f] text-white' : 'bg-[#e99a4e] text-black'}`}>
                  {claim.claim}
                </span>
                <br />
                <span className="text-gray-700">
                  {claim.explanation}
                </span>
              </li>
            ))}
          </ul>

          <div className="mt-4">
            <button 
              onClick={openDashboard}
              className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 text-[11px] font-bold py-2 px-3 rounded transition-colors border border-gray-200 shadow-sm"
            >
              Ver checagem completa no painel de controle.
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
