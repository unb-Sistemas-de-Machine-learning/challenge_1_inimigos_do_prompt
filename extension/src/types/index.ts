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

export interface FeedbackRequest {
  email_id: string;
  feedback_type: 'false_positive' | 'confidence_slider';
  claim_index?: number;
  slider_value?: number;
  comment?: string;
}

export interface FeedbackResponse {
  message: string;
}

export interface HealthResponse {
  status: string;
  model_loaded?: boolean;
  model_backend?: string;
}

export type ExtensionMessage = 
  | { type: 'ANALYZE_START' }
  | { type: 'ANALYZE_EMAIL'; payload: AnalyzeRequest }
  | { type: 'ANALYSIS_RESULT'; payload: AnalyzeResponse }
  | { type: 'SUBMIT_FEEDBACK'; payload: FeedbackRequest }
  | { type: 'FEEDBACK_RESULT'; success: boolean; message?: string }
  | { type: 'TRIGGER_EXTRACTION' }
  | { type: 'CHECK_HEALTH' }
  | { type: 'HEALTH_RESULT'; payload: HealthResponse }
  | { type: 'ERROR'; error: string };
