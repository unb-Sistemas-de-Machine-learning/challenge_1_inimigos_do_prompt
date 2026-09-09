import os
import json
from datetime import datetime
from fastapi import APIRouter

from app.schemas.feedback import FeedbackRequest

router = APIRouter()

# No MVP, armazenamos feedbacks em JSONL local
FEEDBACK_LOG_FILE = os.path.join(os.path.dirname(__file__), "../../../../feedback_log.jsonl")

@router.post("/feedback", status_code=201)
async def submit_feedback(payload: FeedbackRequest):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "email_id": payload.email_id,
        "feedback_type": payload.feedback_type,
        "claim_index": payload.claim_index,
        "slider_value": payload.slider_value,
        "comment": payload.comment
    }
    
    # Certifica-se de que o diretório existe
    os.makedirs(os.path.dirname(FEEDBACK_LOG_FILE), exist_ok=True)
    
    with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
    return {"message": "Feedback registrado com sucesso"}
