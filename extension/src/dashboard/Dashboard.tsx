import { useState, useEffect } from 'react';
import { AnalyzeResponse } from '../types';
import { ShieldAlert, Download, Flag, AlertCircle, CheckCircle } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportedClaims, setReportedClaims] = useState<number[]>([]);

  useEffect(() => {
    // Carrega a última análise salva no storage
    if (chrome.storage) {
      chrome.storage.local.get(['current_analysis'], (result) => {
        if (result.current_analysis) {
          setData(result.current_analysis as AnalyzeResponse);
        }
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const handleReport = (index: number) => {
    if (!reportedClaims.includes(index)) {
      setReportedClaims([...reportedClaims, index]);
      // Simula envio do report
      console.log('Reportado claim índice:', index);
    }
  };

  const handleExport = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio-inimigos-do-prompt-${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center text-gray-500 space-y-4">
        <ShieldAlert className="h-16 w-16 text-gray-300" />
        <h2 className="text-xl font-semibold">Nenhuma análise recente encontrada</h2>
        <p>Volte ao e-mail e realize uma análise antes de abrir o painel de controle.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans pb-12">
      {/* Header NavBar */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 sticky top-0 z-10 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <ShieldAlert className="h-8 w-8 text-indigo-600" />
          <div>
            <h1 className="text-lg font-bold text-gray-800">Inimigos do Prompt</h1>
            <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Painel de Controle de IA</p>
          </div>
        </div>
        
        <button 
          onClick={handleExport}
          className="flex items-center space-x-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg font-semibold text-sm hover:bg-indigo-100 transition-colors"
        >
          <Download className="h-4 w-4" />
          <span>Exportar JSON</span>
        </button>
      </header>

      <main className="max-w-5xl mx-auto mt-8 px-4 space-y-6">
        
        {/* Sumário */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex-1">
            <h2 className="text-sm text-gray-500 font-bold uppercase tracking-wider mb-1">Sumário da Newsletter</h2>
            <h3 className="text-2xl font-bold text-gray-800">Análise de Conteúdo e Discurso</h3>
            <p className="text-gray-500 mt-2 text-sm leading-relaxed">
              O modelo processou a newsletter em busca de padrões linguísticos, verificando o uso de gatilhos emocionais, clickbait, e alegações técnicas de IA que podem configurar desinformação ou hype excessivo.
            </p>
          </div>
          
          <div className="flex gap-4">
            <div className="bg-slate-50 border border-slate-100 p-4 rounded-lg text-center min-w-[140px]">
              <span className="block text-xs text-slate-500 font-bold uppercase mb-1">Score de Hype</span>
              <span className="text-3xl font-black text-indigo-600">{data.sensationalism_score.toFixed(1)}</span>
              <span className="text-sm text-slate-400 font-medium">/ 5.0</span>
            </div>
            
            <div className="bg-slate-50 border border-slate-100 p-4 rounded-lg text-center min-w-[140px]">
              <span className="block text-xs text-slate-500 font-bold uppercase mb-1">Desinformação</span>
              <span className={`text-3xl font-black ${data.disinformation_risk > 70 ? 'text-red-500' : 'text-orange-500'}`}>
                {data.disinformation_risk}%
              </span>
              <span className="text-sm text-slate-400 font-medium block">Risco Geral</span>
            </div>
          </div>
        </div>

        {/* Claims Table / Cards */}
        <div>
          <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-indigo-500" />
            Alegações Suspeitas Analisadas ({data.suspicious_claims.length})
          </h2>
          
          <div className="space-y-4">
            {data.suspicious_claims.map((claim, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className={`h-1.5 w-full ${claim.severity === 'high' ? 'bg-red-500' : 'bg-orange-400'}`}></div>
                <div className="p-5 flex flex-col md:flex-row gap-6">
                  
                  <div className="flex-1 space-y-3">
                    <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider ${claim.severity === 'high' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                      {claim.severity === 'high' ? 'Crítico (Conceitual)' : 'Moderado (Hype)'}
                    </span>
                    
                    <div>
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Trecho Extraído</h4>
                      <p className="text-gray-800 font-medium text-lg border-l-4 border-gray-200 pl-3">"{claim.claim}"</p>
                    </div>

                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 mt-2">
                      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Justificativa Técnica do Modelo</h4>
                      <p className="text-sm text-slate-700">{claim.explanation}</p>
                    </div>
                  </div>

                  <div className="w-full md:w-64 border-t md:border-t-0 md:border-l border-gray-100 pt-4 md:pt-0 md:pl-6 flex flex-col justify-center space-y-4">
                    <div>
                      <span className="text-xs text-gray-500 font-bold block mb-1">Probabilidade (Confiança)</span>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${Math.round(data.confidence * 100)}%` }}></div>
                        </div>
                        <span className="text-sm font-semibold text-gray-700">{Math.round(data.confidence * 100)}%</span>
                      </div>
                    </div>
                    
                    <div>
                      <span className="text-xs text-gray-500 font-bold block mb-2">Conformidade & Ética</span>
                      {reportedClaims.includes(idx) ? (
                        <div className="flex items-center text-green-600 text-sm font-medium gap-1.5">
                          <CheckCircle className="h-4 w-4" /> Feedback Registrado
                        </div>
                      ) : (
                        <button 
                          onClick={() => handleReport(idx)}
                          className="flex items-center text-sm font-medium text-gray-500 hover:text-red-600 transition-colors gap-1.5"
                        >
                          <Flag className="h-4 w-4" /> Reportar Falso Positivo
                        </button>
                      )}
                      <p className="text-[10px] text-gray-400 mt-1 leading-tight">
                        Ajude a mitigar danos a criadores de conteúdo validando a precisão do modelo.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </main>
    </div>
  );
}
