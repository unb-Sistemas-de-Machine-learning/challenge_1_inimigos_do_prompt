from typing import Optional, Literal
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    email_id: str
    feedback_type: Literal["false_positive", "confidence_slider"]
    claim_index: Optional[int] = None
    slider_value: Optional[int] = None
    comment: Optional[str] = None
