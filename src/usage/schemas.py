from pydantic import BaseModel
from typing import List, Dict

class UsageStats(BaseModel):
    total_conversations: int
    total_messages: int
    total_tokens: int
    cost_estimate_usd: float
    models_used: List[str]
