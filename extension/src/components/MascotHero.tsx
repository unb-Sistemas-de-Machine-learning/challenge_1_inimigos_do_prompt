import React from 'react';
import { AnalyzeResponse } from '../types';
import { ChevronDown, ChevronUp, Sparkles, AlertOctagon, CheckCircle2, AlertTriangle } from 'lucide-react';

interface MascotHeroProps {
  data: AnalyzeResponse | null;
  loading: boolean;
  showMetrics: boolean;
  onToggleMetrics: () => void;
}

export const MascotHero: React.FC<MascotHeroProps> = ({
  data,
  loading,
  showMetrics,
  onToggleMetrics,
}) => {
  // Determine mascot state
  const getMascotState = () => {
    if (loading) {
      return {
        badge: 'Farejando conteúdo...',
        badgeColor: 'bg-indigo-100 text-indigo-700 border-indigo-200',
        title: 'Farejando a newsletter...',
        message: 'Snif, snif... Estou cheirando cada parágrafo com o BERTimbau atrás de promessas forçadas e termos apelativos!',
        avatarClass: 'animate-bounce scale-105 duration-700',
        icon: <Sparkles className="w-3.5 h-3.5 animate-spin" />
      };
    }

    if (!data) {
      return {
        badge: 'Farejador a Postos',
        badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
        title: 'Pronto para farejar!',
        message: 'Abra um e-mail no Gmail ou Outlook. Assim que a mensagem carregar, vou farejar se ela tem sensacionalismo ou se é séria!',
        avatarClass: 'hover:rotate-2 transition-transform duration-300',
        icon: <Sparkles className="w-3.5 h-3.5 text-amber-600" />
      };
    }

    const score = data.sensationalism_score;
    const isDisinfoHigh = data.disinformation_risk > 50;

    if (score >= 3.8 || isDisinfoHigh) {
      return {
        badge: '🚨 Alerta de Hype Máximo',
        badgeColor: 'bg-rose-100 text-rose-700 border-rose-300 shadow-xs',
        title: 'Para tudo! Muito Hype!',
        message: 'Farejei promessas milagrosas e tom alarmista neste e-mail! Cuidado ao tomar decisões baseadas nessas alegações sem fontes verificáveis.',
        avatarClass: 'filter drop-shadow-[0_4px_12px_rgba(244,63,94,0.35)] animate-pulse',
        icon: <AlertOctagon className="w-3.5 h-3.5 text-rose-600" />
      };
    }

    if (score >= 2.5) {
      return {
        badge: '⚠️ Hype Moderado',
        badgeColor: 'bg-amber-100 text-amber-800 border-amber-300 shadow-xs',
        title: 'Orelha em pé! Atenção...',
        message: 'Hummm... senti um cheirinho de exagero aqui! O autor usou gatilhos apelativos para inflar expectativas. Vale uma leitura crítica.',
        avatarClass: 'filter drop-shadow-[0_4px_10px_rgba(245,158,11,0.25)]',
        icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
      };
    }

    return {
      badge: '✅ Conteúdo Sóbrio',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-300 shadow-xs',
      title: 'Pode ler tranquilo!',
      message: 'Au au! Esse texto é bem pé no chão e informativo. Não encontrei sensacionalismo forçado nem alegações absurdas.',
      avatarClass: 'filter drop-shadow-[0_4px_10px_rgba(16,185,129,0.25)]',
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
    };
  };

  const state = getMascotState();
  const topTerms = data?.highlighted_terms
    ?.slice()
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 3) || [];

  return (
    <div className="bg-gradient-to-b from-indigo-50/70 via-white to-gray-50 border border-indigo-100 rounded-2xl p-4 shadow-sm relative overflow-hidden transition-all duration-300">
      
      {/* Decorative background glow */}
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-indigo-200/30 rounded-full blur-2xl pointer-events-none" />

      {/* Top Status Pill */}
      <div className="flex items-center justify-between mb-3">
        <div className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${state.badgeColor}`}>
          {state.icon}
          <span>{state.badge}</span>
        </div>

        {data && (
          <div className="text-[11px] font-extrabold text-gray-500">
            Score: <span className="text-gray-800 font-black">{data.sensationalism_score.toFixed(1)}</span>/5.0
          </div>
        )}
      </div>

      {/* Mascot & Speech Bubble Layout */}
      <div className="flex items-start gap-3.5">
        
        {/* Mascot Avatar */}
        <div className="flex-shrink-0 relative group">
          <div className="w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center">
            <img 
              src="/mascot.png" 
              alt="Mascote Farejador de Hype" 
              className={`w-full h-full object-contain ${state.avatarClass}`}
            />
          </div>
          <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 bg-gray-800/80 text-white text-[9px] font-bold px-1.5 py-0.2 rounded-full whitespace-nowrap shadow-xs opacity-0 group-hover:opacity-100 transition-opacity">
            Farejador
          </span>
        </div>

        {/* Speech Bubble */}
        <div className="flex-1 relative">
          <div className="bg-white border-2 border-indigo-200/90 rounded-2xl p-3 shadow-md relative text-left">
            {/* Triangular Speech Pointer towards Mascot */}
            <div className="absolute top-6 -left-2.5 w-0 h-0 border-t-[7px] border-t-transparent border-b-[7px] border-b-transparent border-r-[10px] border-r-indigo-200" />
            <div className="absolute top-6 -left-2 w-0 h-0 border-t-[6px] border-t-transparent border-b-[6px] border-b-transparent border-r-[9px] border-r-white" />

            <h3 className="text-xs font-black text-gray-800 mb-1 flex items-center gap-1.5">
              {state.title}
            </h3>
            
            <p className="text-[11.5px] text-gray-600 leading-relaxed font-medium">
              {state.message}
            </p>

            {/* Quick Keyword Pills if detected */}
            {topTerms.length > 0 && (
              <div className="mt-2.5 pt-2 border-t border-gray-100 flex flex-wrap items-center gap-1">
                <span className="text-[9.5px] font-bold text-gray-400 uppercase tracking-wider mr-1">
                  Farejados:
                </span>
                {topTerms.map((t, idx) => (
                  <span 
                    key={idx}
                    className="inline-flex items-center text-[10px] font-semibold bg-rose-50 text-rose-700 px-1.5 py-0.5 rounded border border-rose-200/60"
                  >
                    "{t.term}"
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Progressive Disclosure Toggle Button (Only when data exists) */}
      {data && (
        <div className="mt-3.5 pt-2.5 border-t border-indigo-100/80 flex items-center justify-center">
          <button
            onClick={onToggleMetrics}
            className="flex items-center justify-center gap-1.5 text-xs font-bold text-indigo-700 hover:text-indigo-900 bg-indigo-50/80 hover:bg-indigo-100 px-3.5 py-1.5 rounded-xl border border-indigo-200/80 transition-all shadow-2xs hover:shadow-xs w-full"
          >
            <span>{showMetrics ? 'Ocultar Métricas e Indicadores' : 'Exibir Métricas Numéricas e Gráficos'}</span>
            {showMetrics ? (
              <ChevronUp className="w-4 h-4 text-indigo-600 transition-transform" />
            ) : (
              <ChevronDown className="w-4 h-4 text-indigo-600 transition-transform" />
            )}
          </button>
        </div>
      )}

    </div>
  );
};
