import { useState } from 'react';
import { supabase } from './lib/supabase';

// URL pública para onde o Supabase vai redirecionar após verificação de e-mail.
// NUNCA deve ser localhost — a extensão não tem uma URL acessível publicamente.
const SITE_URL = import.meta.env.VITE_SITE_URL || 'https://unb-sistemas-de-machine-learning.github.io/challenge_1_inimigos_do_prompt';

export function Auth({ onSession }: { onSession: (session: any) => void }) {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (isLogin) {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        if (data.session) onSession(data.session);
      } else {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            // Redireciona para o site público após clicar no link do e-mail.
            // Isso evita que o Supabase use localhost como destino.
            emailRedirectTo: `${SITE_URL}`,
          },
        });
        if (error) throw error;
        setMessage('Cadastro realizado! Verifique seu e-mail para confirmar a conta.');
      }
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro durante a autenticação.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6 font-sans">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-lg border border-gray-100 p-8 flex flex-col items-center">
        
        {/* Logo Redonda */}
        <div className="w-24 h-24 mb-6 rounded-full overflow-hidden border-4 border-indigo-50 shadow-sm flex items-center justify-center bg-white">
          <img 
            src="/logo.png" 
            alt="Inimigos do Prompt" 
            className="w-full h-full object-cover"
          />
        </div>

        <h2 className="text-xl font-black text-gray-800 mb-1 text-center tracking-tight">
          Inimigos do Prompt
        </h2>
        <p className="text-xs text-gray-500 mb-6 text-center font-medium">
          {isLogin ? 'Faça login para continuar' : 'Crie sua conta para começar'}
        </p>

        <form onSubmit={handleAuth} className="w-full space-y-4">
          <div>
            <label className="block text-[11px] font-bold text-gray-700 mb-1">E-mail</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              placeholder="seu@email.com"
            />
          </div>
          <div>
            <label className="block text-[11px] font-bold text-gray-700 mb-1">Senha</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-[11px] text-red-500 text-center font-medium bg-red-50 p-2 rounded">{error}</p>}
          {message && <p className="text-[11px] text-emerald-600 text-center font-medium bg-emerald-50 p-2 rounded">{message}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-[#3f51b5] hover:bg-[#303f9f] text-white text-sm font-bold rounded-lg shadow-md transition-all disabled:opacity-70 flex justify-center items-center"
          >
            {loading ? (
              <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
            ) : (
              isLogin ? 'Entrar' : 'Cadastrar'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
              setMessage(null);
            }}
            className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold"
          >
            {isLogin ? 'Não tem uma conta? Cadastre-se' : 'Já tem conta? Faça login'}
          </button>
        </div>
      </div>
    </div>
  );
}
