import { AnalyzeRequest, AnalyzeResponse } from '../types';

const API_URL = 'http://localhost:8000/api/v1/analyze';

export async function analyzeText(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Erro na API: ${response.statusText}`);
  }

  const data: AnalyzeResponse = await response.json();
  return data;
}
