import { AnalyzeRequest, AnalyzeResponse, FeedbackRequest, FeedbackResponse, HealthResponse } from '../types';
import { supabase } from '../lib/supabase';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getAuthHeaders() {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  return headers;
}

export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`Status de saúde inválido: ${response.statusText}`);
    }

    return await response.json();
  } catch (err: any) {
    throw new Error(`Backend offline ou inacessível em ${API_BASE_URL}. Inicie o servidor FastAPI.`);
  }
}

export async function analyzeText(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Não autorizado. Faça login na extensão.");
      }
      const errorDetail = await response.text();
      throw new Error(`Erro na API (${response.status}): ${errorDetail || response.statusText}`);
    }

    const data: AnalyzeResponse = await response.json();
    return data;
  } catch (err: any) {
    if (err.message && err.message.includes('Erro na API')) {
      throw err;
    }
    if (err.message && err.message.includes('Não autorizado')) {
      throw err;
    }
    throw new Error(`Não foi possível conectar ao servidor backend em ${API_BASE_URL}. Verifique se a API está em execução.`);
  }
}

export async function sendFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  try {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Não autorizado. Faça login na extensão.");
      }
      throw new Error(`Erro ao enviar feedback: ${response.statusText}`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.message && (err.message.includes('Erro ao enviar') || err.message.includes('Não autorizado'))) {
      throw err;
    }
    throw new Error(`Falha ao conectar ao backend para envio de feedback.`);
  }
}

