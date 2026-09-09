import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from models import AnalyzeResponse, AnalyzeRequest

load_dotenv()

# Configure the API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-pro", # Alternatively gemini-2.5-flash
    generation_config=generation_config,
    system_instruction=(
        "Você é um analista de comunicação especializado em detectar sensacionalismo, "
        "hype tecnológico e desinformação em e-mails e newsletters.\n\n"
        "Sua tarefa é analisar o e-mail fornecido e retornar **estritamente** um JSON "
        "com a seguinte estrutura exata (sem formatação markdown):\n"
        "{\n"
        '  "sensationalism_score": float (0 a 5, onde 5 é o mais sensacionalista),\n'
        '  "label": string ("Sóbrio", "Hype Moderado", ou "Hype Elevado"),\n'
        '  "confidence": float (0 a 1),\n'
        '  "highlighted_terms": [\n'
        '    { "term": string, "weight": float (0 a 1), "category": "alarmist" | "clickbait" | "hype" | "sensationalist" }\n'
        "  ],\n"
        '  "disclaimer": "Resultados gerados por IA baseados no texto do e-mail.",\n'
        '  "disinformation_risk": int (0 a 100),\n'
        '  "suspicious_claims": [\n'
        '    { "claim": string, "explanation": string, "severity": "moderate" | "high" }\n'
        "  ]\n"
        "}\n\n"
        "Seja crítico e detalhista."
    )
)

async def analyze_email_text(request: AnalyzeRequest) -> AnalyzeResponse:
    if not api_key:
        # Modo fallback ou simulado caso não haja API KEY (apenas para evitar erros imediatos)
        raise ValueError("GEMINI_API_KEY não configurada no ambiente.")

    prompt = f"Assunto: {request.subject or 'Sem assunto'}\nCorpo:\n{request.raw_text}"
    
    response = model.generate_content(prompt)
    
    try:
        data = json.loads(response.text)
        # Parse into Pydantic model to guarantee correct types
        return AnalyzeResponse(**data)
    except Exception as e:
        print(f"Erro ao parsear a resposta do LLM: {response.text}")
        raise e
