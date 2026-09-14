import { AnalyzeRequest, AnalyzeResponse, FeedbackRequest, FeedbackResponse, HealthResponse } from '../types';

export const API_BASE_URL = 'http://localhost:8000';

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
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorDetail = await response.text();
      throw new Error(`Erro na API (${response.status}): ${errorDetail || response.statusText}`);
    }

    const data: AnalyzeResponse = await response.json();
    return data;
  } catch (err: any) {
    if (err.message && err.message.includes('Erro na API')) {
      throw err;
    }
    throw new Error(`Não foi possível conectar ao servidor backend em ${API_BASE_URL}. Verifique se a API está em execução.`);
  }
}

export async function sendFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Erro ao enviar feedback: ${response.statusText}`);
    }

    return await response.json();
  } catch (err: any) {
    if (err.message && err.message.includes('Erro ao enviar')) {
      throw err;
    }
    throw new Error(`Falha ao conectar ao backend para envio de feedback.`);
  }
}

