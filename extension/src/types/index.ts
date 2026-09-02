export interface HighlightedTerm {
  term: string;
  weight: number;
  category: 'alarmist' | 'clickbait' | 'hype' | 'sensationalist' | string;
}

export interface SuspiciousClaim {
  claim: string;
  explanation: string;
  severity: 'moderate' | 'high';
}

export interface AnalyzeResponse {
  email_id?: string;
  sensationalism_score: number;
  label: 'Sóbrio' | 'Hype Moderado' | 'Hype Elevado' | string;
  confidence: number;
  highlighted_terms: HighlightedTerm[];
  disclaimer: string;
  disinformation_risk: number;
  suspicious_claims: SuspiciousClaim[];
}

export interface AnalyzeRequest {
  email_id?: string;
  sender?: string;
  subject?: string;
  raw_text: string;
}

export type ExtensionMessage = 
  | { type: 'ANALYZE_EMAIL'; payload: AnalyzeRequest }
  | { type: 'ANALYSIS_RESULT'; payload: AnalyzeResponse }
  | { type: 'ERROR'; error: string };
